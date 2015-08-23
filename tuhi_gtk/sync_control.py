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
    note_store, note_content_store, Note
from tuhi_gtk.config import SYNCSERVER_NOTES_ENDPOINT, REASON_SYNC, \
    SYNC_ACTION_BEGIN, SYNC_ACTION_FAILURE, SYNC_ACTION_SUCCESS
from tuhi_gtk.util import ignore_sender_function

log = get_log_for_prefix_tuple(("sync",))

class SyncControl(GObject.Object):
    __gsignals__ = {
        "global_sync_action": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        # Action names: begin, success, failure
        "sync_action_for_note_id": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING, GObject.TYPE_STRING)),
        # Action names: begin, success, failure
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

        pull_thread = threading.Thread(target=self._pull_comm, args=(after,))
        pull_thread.start()

    def _pull_comm(self, after):
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
            post_pull_comm_gen = self._post_pull_comm(data)
            GObject.idle_add(lambda x: next(post_pull_comm_gen, False), GObject.PRIORITY_LOW)

    def _post_pull_comm(self, res):
        if not isinstance(res, dict):
            log.error("Something went wrong with pull.")
            return

        data = res
        yield from self._merge_change(data["notes"], note_store, note_notonserver_tracker, "note_added", "Note", "note_id")
        yield from self._merge_change(data["note_contents"], note_content_store, note_content_notonserver_tracker, "note_content_added", "NoteContent", "note_content_id")
        kv_store["LAST_PULL_DATE"] = get_current_date()

        pre_push_comm_gen = self._pre_push_comm()
        GObject.idle_add(lambda x: next(pre_push_comm_gen, False), GObject.PRIORITY_LOW)

    def _merge_change(self, serialized_data_blocks, model_store, notonserver_tracker, syncadd_signal_name, instance_name, pk_name):
        log.debug("Merging changes from pull into %s.", model_store)
        for serialized_data in serialized_data_blocks:
            instance = model_store.get(serialized_data)
            if instance is not None:
                # I have a instance that has the same id as the one coming in.
                if instance in notonserver_tracker:
                    # There is a new instance on the server that conflicts with a new note I've made.
                    # We are talking about different instances. Conflict with server. Must change id of notonserver instance
                    log.warn("UUID conflict detected in pull data for %s, %s. Trying to overcome.", instance_name, serialized_data[pk_name])
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

    def _pre_push_comm(self):
        notonserver_notes = note_notonserver_tracker.get_all()
        notonserver_note_contents = note_content_notonserver_tracker.get_all()
        yield True

        notonserver_note_ids = {note.note_id for note in notonserver_notes}
        notonserver_note_content_ids = {note_content.note_content_id for note_content in notonserver_note_contents}
        affected_note_ids = notonserver_note_ids | {note_content.note_id for note_content in notonserver_note_contents}
        yield True

        for note_id in affected_note_ids:
            self.emit("sync_action_for_note_id", note_id, SYNC_ACTION_BEGIN)
        yield True

        data_dict = {"notes": [n.serialize() for n in notonserver_notes],
                     "note_contents": [nc.serialize() for nc in notonserver_note_contents]}
        yield True

        data = json.dumps(data_dict)
        yield True

        push_thread = threading.Thread(target=self._push_comm, args=(data,))
        push_thread.start()

    def _emit_note_sync_action_on_all(self, all_affected, except_affected, all_sig_action, except_sig_action):
        for note in all_affected:
            if except_affected is None or note.note_id not in except_affected:
                self.emit("note_sync_action", note, all_sig_action)
            else:
                self.emit("note_sync_action", note, except_sig_action)
            yield True

    def _push(self):
        tried_notes = note_notonserver_tracker.get_all_as_query()
        tried_note_contents = note_content_notonserver_tracker.get_all_as_query()

        affected_notes = tried_notes.union(Note.query.join(tried_note_contents)).all()
        self._emit_note_sync_action_on_all(affected_notes, None, SYNC_ACTION_BEGIN, None)

        data_dict = {"notes": [n.serialize() for n in tried_notes.all()],
                     "note_contents": [nc.serialize() for nc in tried_note_contents.all()]}
        data = json.dumps(data_dict)

        try:
            r = requests.post(self.sync_url, data, auth=self.auth)
        except requests.exceptions.ConnectionError as e:
            # TODO: Actual error handling logic for service unavailable, wrong network, etc.
            log.error("ConnectionError: %s", e)
            self._emit_note_sync_action_on_all(affected_notes, None, SYNC_ACTION_FAILURE, None)
            return
        else:
            if r.status_code in (400, 401, 500):
                # TODO: Actual error handling for Bad Request, Unauthorized, and Server Error
                self._emit_note_sync_action_on_all(affected_notes, None, SYNC_ACTION_FAILURE, None)
                return

            if r.status_code == 200:
                note_notonserver_tracker.discard_all()
                note_content_notonserver_tracker.discard_all()
                self._emit_note_sync_action_on_all(affected_notes, None, SYNC_ACTION_SUCCESS, None)
                return True

            if r.status_code == 202:
                response = r.json()

                failed_notes = [x["note_id"] for x in response["notes"]] if "notes" in response else []
                failed_note_contents = [x["note_content_id"] for x in response["note_contents"]] if "note_contents" in response else []

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

    def _process_push_comm(self, res):
        self.emit("sync_action", SYNC_ACTION_SUCCESS)  # need to use actual logic here for whether success or not
        self.sync_lock.release()
