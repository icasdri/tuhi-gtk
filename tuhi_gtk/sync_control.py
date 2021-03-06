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
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.database import kv_store, get_current_date, \
    note_notonserver_tracker, note_content_notonserver_tracker, \
    note_store, note_content_store
from tuhi_gtk.config import SYNCSERVER_NOTES_ENDPOINT, REASON_SYNC, \
    SYNC_ACTION_BEGIN, SYNC_ACTION_FAILURE, SYNC_ACTION_SUCCESS, \
    SYNC_FAILURE_FATAL, SYNC_FAILURE_CONNECTION, SYNC_FAILURE_AUTHENTICATION, SYNC_FAILURE_FINGERPRINT, SYNC_FAILURE_SSLHANDSHAKE

log = get_log_for_prefix_tuple(("sync",))

class SyncControl(GObject.Object):
    __gsignals__ = {
        "global_sync_action": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING, GObject.TYPE_STRING,)),
        # Action names: begin, success, failure
        # Sync by: user, auto
        "sync_action_for_note": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, GObject.TYPE_STRING)),
        # Action names: begin, success, failure
        "sync_failure": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_PYOBJECT)),
        # Failure types: fatal, connection, authentication, fingerprint, sslhandshake
        # Sync by: user, auto
        # "Extra information" field containing any pyobject
    }

    def __init__(self, global_r):
        self.global_r = global_r
        self.global_r.instance_register(self)
        self.sync_lock = threading.Lock()

    def sync(self, by_who):
        lock_acquired = self.sync_lock.acquire(blocking=False)
        if not lock_acquired:
            log.info("Failed to acquire lock for sync.")
            return False
        log.debug("Sync started.")
        self.by_who = by_who
        self.emit("global_sync_action", SYNC_ACTION_BEGIN, self.by_who)
        log.debug("Retrieving server connection preferences.")
        self.sync_url = kv_store["SYNCSERVER_URL"].rstrip("/") + SYNCSERVER_NOTES_ENDPOINT
        self.auth = (kv_store["SYNCSERVER_USERNAME"], kv_store["SYNCSERVER_PASSWORD"])

        log.debug("Entering logic for pull.")
        try:
            after = kv_store["LAST_PULL_DATE"]
        except KeyError:
            after = None

        self.session = requests.Session()
        pull_thread = threading.Thread(target=self._pull_comm, args=(after,))
        pull_thread.start()

    def _pull_comm(self, after):  # Runs in separate thread
        log.debug("Executing pull thread.")
        if after is None:
            params = {}
        else:
            params = {"after": after if isinstance(after, str) else str(after)}

        try:
            log.debug("Connecting to server for GET.")
            r = self.session.get(self.sync_url, params=params, auth=self.auth)
        except requests.exceptions.ConnectionError as e:
            log.error("ConnectionError: %s", e)
            e_ = e  # Avoid reference-before-assignment error
            GObject.idle_add(lambda x: self._handle_pull_connection_error(e_), GObject.PRIORITY_LOW)
        else:
            post_pull_comm_gen = self._post_pull_comm(r)
            GObject.idle_add(lambda x: next(post_pull_comm_gen, False), GObject.PRIORITY_LOW)

    def _handle_pull_connection_error(self, e):
        self.emit("global_sync_action", SYNC_ACTION_FAILURE, self.by_who)
        self.emit("sync_failure", SYNC_FAILURE_CONNECTION, self.by_who, (e, self.sync_url))
        self.sync_lock.release()
        return False

    def _post_pull_comm(self, r):
        if r.status_code in (400, 500):  # Bad Request and Server Error
            log.critical("Server responded with HTTP %s", r.status_code)
            self.emit("global_sync_action", SYNC_ACTION_FAILURE, self.by_who)
            self.emit("sync_failure", SYNC_FAILURE_FATAL, self.by_who, "Server responded with HTTP {}".format(r.status_code))
            self.sync_lock.release()
            return

        if r.status_code == 401:  # Unauthorized
            log.error("Could not pull from server due to an authentication issue. Server responded with HTTP 401.")
            self.emit("global_sync_action", SYNC_ACTION_FAILURE, self.by_who)
            self.emit("sync_failure", SYNC_FAILURE_AUTHENTICATION, self.by_who, None)
            self.sync_lock.release()
            return

        try:
            data = r.json()
        except ValueError:
            log.critical("Server responded with malformed or missing JSON data on pull.")
            self.emit("global_sync_action", SYNC_ACTION_FAILURE, self.by_who)
            self.emit("sync_failure", SYNC_FAILURE_FATAL, self.by_who, "Server responded with missing or malformed JSON data on pull.")
            self.sync_lock.release()
            return
        else:
            yield from self._merge_change(data["notes"], note_store, note_notonserver_tracker, "note_added", "Note", "note_id")  # py3 # noqa
            yield from self._merge_change(data["note_contents"], note_content_store, note_content_notonserver_tracker, "note_content_added", "NoteContent", "note_content_id")  # py3 # noqa
            kv_store["LAST_PULL_DATE"] = get_current_date()

            pre_push_comm_gen = self._pre_push_comm()
            GObject.idle_add(lambda x: next(pre_push_comm_gen, False), GObject.PRIORITY_LOW)

    def _merge_change(self, serialized_data_blocks, model_store, notonserver_tracker, syncadd_signal_name, instance_name, pk_name):
        if len(serialized_data_blocks) > 0:
            log.debug("Retrieved %d %s objects from server.", len(serialized_data_blocks), instance_name)
            log.debug("Merging changes from new %s objects on server.", instance_name)
            for serialized_data in serialized_data_blocks:
                instance = model_store.get(serialized_data)
                if instance is not None:
                    # I have a instance that has the same id as the one coming in.
                    if instance in notonserver_tracker:
                        # There is a new instance on the server that conflicts with a new note I've made.
                        # We are talking about different instances. Conflict with server. Must change id of notonserver instance
                        log.warn("UUID conflict detected in pull data for %s, %s. Trying to overcome.", instance_name, serialized_data[pk_name])
                        old_id, new_id = model_store.rename_to_new_uuid(instance)
                        log.debug("UUID local rename %s --> %s", old_id, new_id)
                        notonserver_tracker.register_rename(old_id, new_id)
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
        else:
            log.info("No new %s objects on server.", instance_name)
            yield True

    def _pre_push_comm(self):
        log.debug("Entering logic for push.")
        notonserver_notes = note_notonserver_tracker.get_all()
        notonserver_note_contents = note_content_notonserver_tracker.get_all()
        yield True

        if len(notonserver_notes) > 0 or len(notonserver_note_contents) > 0:
            log.info("There are %d unsynced Note objects.", len(notonserver_notes))
            log.info("There are %d unsynced NoteContent objects.", len(notonserver_note_contents))
            notonserver_notes_dict = {note.note_id: note for note in notonserver_notes}
            notonserver_note_contents_dict = {note_content.note_content_id: note_content for note_content in notonserver_note_contents}
            affected_notes_dict = {note_content.note_id: note_content.note for note_content in notonserver_note_contents}
            affected_notes_dict.update(notonserver_notes_dict)
            yield True

            for note in affected_notes_dict.values():
                self.emit("sync_action_for_note", note, SYNC_ACTION_BEGIN)
            yield True

            data_dict = {"notes": [n.serialize() for n in notonserver_notes],
                         "note_contents": [nc.serialize() for nc in notonserver_note_contents]}
            yield True

            data = json.dumps(data_dict)
            yield True

            raw_tracker_dicts = (notonserver_notes_dict, notonserver_note_contents_dict, affected_notes_dict)
            push_thread = threading.Thread(target=self._push_comm, args=(data, raw_tracker_dicts))
            push_thread.start()
        else:
            log.info("No unsynced changes to push. Skipping push.")
            self.emit("global_sync_action", SYNC_ACTION_SUCCESS, self.by_who)
            self.sync_lock.release()

    def _push_comm(self, data, raw_tracker_dicts):  # Runs in separate thread
        log.debug("Executing push thread.")
        try:
            log.debug("Connecting to server for POST.")
            r = self.session.post(self.sync_url, data, auth=self.auth)
        except requests.exceptions.ConnectionError as e:
            # TODO: Actual error handling logic for service unavailable, wrong network, etc.
            log.error("ConnectionError: %s", e)
            e_ = e  # Avoid reference-before-assignment error
            GObject.idle_add(lambda x: self._handle_push_connection_error(raw_tracker_dicts, e_), GObject.PRIORITY_LOW)
            return
        else:
            post_push_comm_gen = self._post_push_comm(r, raw_tracker_dicts)
            GObject.idle_add(lambda x: next(post_push_comm_gen, False), GObject.PRIORITY_LOW)

    def _handle_push_connection_error(self, raw_tracker_dicts, e):
        _, _, affected_notes_dict = raw_tracker_dicts
        for note in affected_notes_dict.values():
            self.emit("sync_action_for_note", note, SYNC_ACTION_FAILURE)
        self.emit("global_sync_action", SYNC_ACTION_FAILURE, self.by_who)
        self.emit("sync_failure", SYNC_FAILURE_CONNECTION, self.by_who, (e, self.sync_url))
        self.sync_lock.release()
        return False

    def _post_push_comm(self, r, raw_tracker_dicts):
        notes_tracking_dict, note_contents_tracking_dict, affected_notes_dict = raw_tracker_dicts
        yield True

        if r.status_code in (400, 500):  # Bad Request and Server Error
            log.critical("Server responded with HTTP %s", r.status_code)
            for note in affected_notes_dict.values():
                self.emit("sync_action_for_note", note, SYNC_ACTION_FAILURE)
            self.emit("global_sync_action", SYNC_ACTION_FAILURE, self.by_who)
            self.emit("sync_failure", SYNC_FAILURE_FATAL, self.by_who, "Server responded with HTTP {}".format(r.status_code))
            self.sync_lock.release()
            return

        if r.status_code == 401:  # Unauthorized
            log.error("Server rejected push due to an authentication issue. Server responded with HTTP 401.")
            for note in affected_notes_dict.values():
                self.emit("sync_action_for_note", note, SYNC_ACTION_FAILURE)
            self.emit("global_sync_action", SYNC_ACTION_FAILURE, self.by_who)
            self.emit("sync_failure", SYNC_FAILURE_AUTHENTICATION, self.by_who, None)
            self.sync_lock.release()
            return

        if r.status_code == 200:
            log.info("Server accepted push for all unsynced Notes and Note Contents")
            for note in affected_notes_dict.values():
                self.emit("sync_action_for_note", note, SYNC_ACTION_SUCCESS)
            self.emit("global_sync_action", SYNC_ACTION_SUCCESS, self.by_who)
            note_notonserver_tracker.discard_successes(notes_tracking_dict.keys())
            note_content_notonserver_tracker.discard_successes(note_contents_tracking_dict.keys())
            self.sync_lock.release()
            return

        if r.status_code == 202:
            try:
                response = r.json()
                notes_in_response = response["notes"]
                note_contents_in_response = response["note_contents"]
            except (KeyError, ValueError):
                log.critical("Server responded with malformed or missing JSON data on push.")
                for note in affected_notes_dict.values():
                    self.emit("sync_action_for_note", note, SYNC_ACTION_FAILURE)
                self.emit("global_sync_action", SYNC_ACTION_FAILURE, self.by_who)
                self.emit("sync_failure", SYNC_FAILURE_FATAL, self.by_who, "Server responded with missing or malformed JSON data on push.")
                self.sync_lock.release()
                return
            else:
                unknown_error_count = 0

                for note_res in notes_in_response:
                    note_id = note_res["note_id"]
                    note = notes_tracking_dict[note_id]
                    log.warn("Server rejected push of Note: %s. Further processing underway.", note_id)
                    del notes_tracking_dict[note_id]
                    del affected_notes_dict[note_id]
                    self.emit("sync_action_for_note", note, SYNC_ACTION_FAILURE)

                    if "note_id_errors" in note_res:
                        if note_res["note_id_errors"] == 90:  # Forbidden
                            log.warn("Server returned Forbidden for unsynced Note: %s. Most likely a UUID conflict. Attempting resolution.", note_id)
                            old_id, new_id = note_store.rename_to_new_uuid(note)
                            log.debug("UUID local rename %s --> %s", old_id, new_id)
                            note_notonserver_tracker.register_rename(old_id, new_id)
                        elif note_res["note_id_errors"] == 19:  # Conflict
                            # TODO: decide if we want UUID conflict resolution logic here
                            pass
                        else:
                            unknown_error_count += 1

                for note_content_res in note_contents_in_response:
                    note_content_id = note_content_res["note_content_id"]
                    note_content = note_contents_tracking_dict[note_content_id]
                    log.warn("Server rejected push of Note Content: %s. Further processing underway.", note_content_id)
                    del note_contents_tracking_dict[note_content_id]
                    del affected_notes_dict[note_content.note_id]
                    self.emit("sync_action_for_note", note_content.note, SYNC_ACTION_FAILURE)

                    if "note_content_id_errors" in note_content_res:
                        if note_content_res["note_content_id_errors"] == 90:  # Forbidden
                            log.warn("Server returned Forbidden for unsynced Note Content: %s. Most likely a UUID conflict. Attempting resolution.", note_content_id)
                            old_id, new_id = note_content_store.rename_to_new_uuid(note_content)
                            log.debug("UUID local rename %s --> %s", old_id, new_id)
                            note_content_notonserver_tracker.register_rename(old_id, new_id)
                        elif note_content_res["note_content_id_errors"] == 19:  # Conflict
                            # TODO: decide if we want UUID conflict resolution logic here
                            pass
                        else:
                            unknown_error_count += 1

                for note in affected_notes_dict.values():
                    self.emit("sync_action_for_note", note, SYNC_ACTION_SUCCESS)
                note_notonserver_tracker.discard_successes(notes_tracking_dict.keys())
                note_content_notonserver_tracker.discard_successes(note_contents_tracking_dict.keys())
                self.emit("global_sync_action", SYNC_ACTION_FAILURE, self.by_who)
                if unknown_error_count > 0:
                    self.emit("sync_failure", SYNC_FAILURE_FATAL, self.by_who,
                              "{} unknown error codes or formatting issues were encountered when processing"
                              " server's response to an attempt to push unsynced notes.".format(unknown_error_count))
                self.sync_lock.release()

