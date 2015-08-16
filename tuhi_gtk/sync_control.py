# Copyright 2015 icasdri
#
# This file is part of tuhi-gtk.
#
# tuhi-gtk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tuhi-gtk is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tuhi-gtk.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject
import requests, json
import requests.exceptions
import threading
import time
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.database import kv_store, get_current_date, \
    note_notonserver_tracker, note_content_notonserver_tracker, \
    note_store, note_content_store
from tuhi_gtk.config import SYNCSERVER_NOTES_ENDPOINT, REASON_SYNC, \
    SYNC_ACTION_BEGIN, SYNC_ACTION_FAILURE, SYNC_ACTION_SUCCESS
from tuhi_gtk.util import ignore_sender_function

log = get_log_for_prefix_tuple(("sync",))

class SyncControl(GObject.Object):
    __gsignals__ = {
        "sync_action": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        # Action names: begin, success, failure
        "note_sync_action": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, GObject.TYPE_STRING)),
        # Action names: begin, success, failure
        "server_comm_pull_complete": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),
        # this signal is only used internally in this class
        "server_comm_push_complete": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))
        # this signal is only used internally in this class
    }

    def __init__(self, global_r):
        self.global_r = global_r
        self.global_r.instance_register(self)
        self.sync_lock = threading.Lock()
        self.connect("server_comm_pull_complete", ignore_sender_function(self._process_pull_comm))
        self.connect("server_comm_push_complete", ignore_sender_function(self._process_push_comm))

    def sync(self):
        lock_acquired = self.sync_lock.acquire(blocking=False)
        if not lock_acquired:
            log.info("Failed to acquire lock for sync.")
            return False
        log.debug("Sync started.")
        self.emit("sync_action", SYNC_ACTION_BEGIN)
        log.debug("Retrieving server connection preferences.")
        self.sync_url = kv_store["SYNCSERVER_URL"].rstrip("/") + SYNCSERVER_NOTES_ENDPOINT
        self.auth = (kv_store["SYNCSERVER_USERNAME"], kv_store["SYNCSERVER_PASSWORD"])

        try:
            after = kv_store["LAST_PULL_DATE"]
        except KeyError:
            after = None

        pull_thread = threading.Thread(target=self._pull, args=(after,))
        pull_thread.start()

    def _pull(self, after):
        log.debug("Executing pull thread")
        if after is None:
            params = {}
        else:
            params = {"after": after if isinstance(after, str) else str(after)}

        try:
            log.debug("Connecting to server for GET.")
            r = requests.get(self.sync_url, params=params, auth=self.auth)
        except requests.exceptions.ConnectionError as e:
            # TODO: try again, Gobject.timeout_add probably
            log.error("ConnectionError: %s", e)
        else:
            data = r.json()
            pull_process_gen = self._process_pull_comm(data)
            GObject.idle_add(lambda x: next(pull_process_gen, False), GObject.PRIORITY_LOW)

    def _process_pull_comm(self, res):
        if not isinstance(res, dict):
            log.error("Something went wrong with pull.")
            return

        data = res
        yield from self._merge_change(data["notes"], note_store, note_notonserver_tracker, "note_added", "Note", "note_id")
        yield from self._merge_change(data["note_contents"], note_content_store, note_content_notonserver_tracker, "note_content_added", "NoteContent", "note_content_id")
        kv_store["LAST_PULL_DATE"] = get_current_date()

        push_thread = threading.Thread(target=self._push)
        push_thread.start()

    def _merge_change(self, serialized_data_blocks, model_store, notonserver_tracker, syncadd_signal_name, instance_name, pk_name):
        log.debug("Merging changes from pull into %s.", model_store)
        for serialized_data in serialized_data_blocks:
            instance = model_store.get(serialized_data)
            if instance is not None:
                # I have a instance that has the same id as the one coming in.
                if instance in notonserver_tracker:
                    # There is a new instance on the server that conflicts with a new note I've made.
                    # We are talking about different instances. Conflict with server. Must change id of notonserver instance
                    log.debug("UUID conflict detected in pull data for %s, %s. Trying to overcome.", instance_name, serialized_data[pk_name])
                    old_id, new_id = model_store.rename_to_new_uuid(instance)
                    log.debug("Attempted local rename %s --> %s", old_id, new_id)
                    note_notonserver_tracker.register_rename(old_id, new_id)
                    log.debug("Creating new %s instance for %s", instance_name, serialized_data[pk_name])
                    new_instance = model_store.add_new(serialized_data)
                    self.global_r.emit(syncadd_signal_name, new_instance, REASON_SYNC)
                    # Otherwise, something is awry with server. Server should not send conflicting instances
                    # (which are immutable) -- thus, I ignore the change
            else:
                # This is a new instance that I am unaware of.
                log.debug("Creating new %s instance for %s", instance_name, serialized_data[pk_name])
                new_instance = model_store.add_new(serialized_data)
                self.global_r.emit(syncadd_signal_name, new_instance, REASON_SYNC)
            yield True


    def _process_push_comm(self, res):
        self.emit("sync_action", SYNC_ACTION_SUCCESS)  # need to use actual logic here for whether success or not
        self.sync_lock.release()

    def _push(self):
        tried_notes = note_notonserver_tracker.get_all_as_query().all()
        tried_note_contents = note_content_notonserver_tracker.get_all_as_query().all()
        for note in tried_notes:
            self.emit("note_sync_action", note, SYNC_ACTION_BEGIN)
        for note_content in tried_note_contents:
            self.emit("note_sync_action", note_content.note, SYNC_ACTION_BEGIN)

        data_dict = {"notes": [n.serialize() for n in tried_notes],
                     "note_contents": [nc.serialize() for nc in tried_note_contents]}
        data = json.dumps(data_dict)

        try:
            r = requests.post(self.sync_url, data, auth=self.auth)
        except requests.exceptions.ConnectionError as e:
            # TODO: Actual error handling logic for service unavailable, wrong network, etc.
            log.error("ConnectionError: %s", e)
            for note in tried_notes:
                self.emit("note_sync_action", note, SYNC_ACTION_FAILURE)
            for note_content in tried_note_contents:
                self.emit("note_sync_action", note_content.note, SYNC_ACTION_FAILURE)
            return
        else:
            if r.status_code in (400, 401, 500):
                # TODO: Actual error handling for Bad Request, Unauthorized, and Server Error
                for note in tried_notes:
                    self.emit("note_sync_action", note, SYNC_ACTION_FAILURE)
                for note_content in tried_note_contents:
                    self.emit("note_sync_action", note_content.note, SYNC_ACTION_FAILURE)
                return

            if r.status_code == 200:
                note_notonserver_tracker.discard_all()
                note_content_notonserver_tracker.discard_all()
                for note in tried_notes:
                    self.emit("note_sync_action", note, SYNC_ACTION_SUCCESS)
                for note_content in tried_note_contents:
                    self.emit("note_sync_action", note_content.note, SYNC_ACTION_SUCCESS)
                return True

            if r.status_code == 202:
                response = r.json()

                failed_notes = response["notes"] if "notes" in response else []
                failed_note_contents = response["note_contents"] if "note_contents" in response else []
                failed_notes = [x["note_id"] for x in failed_notes]
                failed_note_contents = [x["note_content_id"] for x in failed_note_contents]

                for note in tried_notes:
                    if note.note_id in failed_notes:
                        self.emit("note_sync_action", note, SYNC_ACTION_FAILURE)
                    else:
                        self.emit("note_sync_action", note, SYNC_ACTION_SUCCESS)

                failed_notes_from_contents = set()
                success_notes_from_contents = set()
                for note_content in tried_note_contents:
                    if note_content.note_content_id in failed_note_contents:
                        failed_notes_from_contents.add(note_content.note)
                    else:
                        success_notes_from_contents.add(note_content.note)
                for note in failed_notes_from_contents:
                    self.emit("note_sync_action", note, SYNC_ACTION_FAILURE)
                for note in success_notes_from_contents:
                    self.emit("note_sync_action", note, SYNC_ACTION_SUCCESS)

                note_notonserver_tracker.discard_all_but_failures(failed_notes)
                note_content_notonserver_tracker.discard_all_but_failures(failed_note_contents)

                # TODO: Actually read the error codes for each failure

            print(r.json())
