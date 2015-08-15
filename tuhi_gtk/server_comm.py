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

import requests, json
from tuhi_gtk.database import kv_store, get_current_date, \
    note_notonserver_tracker, note_content_notonserver_tracker, \
    note_store, note_content_store
from tuhi_gtk.config import SYNCSERVER_NOTES_ENDPOINT, REASON_SYNC, \
    SYNC_ACTION_BEGIN, SYNC_ACTION_FAILURE, SYNC_ACTION_SUCCESS


class ServerAccessPoint(object):
    def __init__(self, global_r):
        self.global_r = global_r
        self.sync_url = kv_store["SYNCSERVER_URL"].rstrip("/") + SYNCSERVER_NOTES_ENDPOINT
        self.auth = (kv_store["SYNCSERVER_USERNAME"], kv_store["SYNCSERVER_PASSWORD"])

    def sync(self):
        self.pull()
        self.push()

    def _merge_change(self, serialized_data_blocks, model_store, notonserver_tracker, syncadd_signal_name):
        for serialized_data in serialized_data_blocks:
            instance = note_store.get(serialized_data)
            if instance is not None:
                # I have a instance that has the same id as the one coming in.
                if instance in notonserver_tracker:
                    # There is a new instance on the server that conflicts with a new note I've made.
                    # We are talking about different instances. Conflict with server. Must change id of notonserver instance
                    old_id, new_id = model_store.rename_to_new_uuid(instance)
                    note_notonserver_tracker.register_rename(old_id, new_id)
                    new_instance = model_store.add_new(serialized_data)
                    self.global_r.emit(syncadd_signal_name, new_instance, REASON_SYNC)
                    # Otherwise, something is awry with server. Server should not send conflicting instances
                    # (which are immutable) -- thus, I ignore the change
            else:
                # This is a new instance that I am unaware of.
                new_instance = model_store.add_new(serialized_data)
                self.global_r.emit(syncadd_signal_name, new_instance, REASON_SYNC)

    def pull(self):
        try:
            params = {"after": str(kv_store["LAST_PULL_DATE"])}
        except KeyError:
            params = {}

        try:
            r = requests.get(self.sync_url, params=params, auth=self.auth)
        except ConnectionError:
            # TODO: try again, Gobject.timeout_add probably
            pass
        else:
            data = r.json()
            self._merge_change(data["notes"], note_store, note_notonserver_tracker, "note_added")
            self._merge_change(data["note_contents"], note_content_store, note_content_notonserver_tracker, "note_content_added")

            kv_store["LAST_PULL_DATE"] = get_current_date()

    def push(self):
        tried_notes = note_notonserver_tracker.get_all_as_query().all()
        tried_note_contents = note_content_notonserver_tracker.get_all_as_query().all()
        for note in tried_notes:
            self.global_r.emit("note_sync_action", note, SYNC_ACTION_BEGIN)
        for note_content in tried_note_contents:
            self.global_r.emit("note_sync_action", note_content.note, SYNC_ACTION_BEGIN)

        data_dict = {"notes": [n.serialize() for n in tried_notes],
                     "note_contents": [nc.serialize() for nc in tried_note_contents]}
        data = json.dumps(data_dict)

        try:
            r = requests.post(self.sync_url, data, auth=self.auth)
        except ConnectionError:
            # TODO: try again, Gobject.timeout_add probably
            pass
        else:
            if r.status_code in (400, 401, 500):
                # TODO: Actual error handling for Bad Request, Unauthorized, and Server Error
                for note in tried_notes:
                    self.global_r.emit("note_sync_action", note, SYNC_ACTION_FAILURE)
                for note_content in tried_note_contents:
                    self.global_r.emit("note_sync_action", note_content.note, SYNC_ACTION_FAILURE)
                return

            if r.status_code == 200:
                note_notonserver_tracker.discard_all()
                note_content_notonserver_tracker.discard_all()
                for note in tried_notes:
                    self.global_r.emit("note_sync_action", note, SYNC_ACTION_SUCCESS)
                for note_content in tried_note_contents:
                    self.global_r.emit("note_sync_action", note_content.note, SYNC_ACTION_SUCCESS)
                return

            if r.status_code == 202:
                response = r.json()

                failed_notes = response["notes"] if "notes" in response else []
                failed_note_contents = response["note_contents"] if "note_contents" in response else []
                failed_notes = [x["note_id"] for x in failed_notes]
                failed_note_contents = [x["note_content_id"] for x in failed_note_contents]

                for note in tried_notes:
                    if note.note_id in failed_notes:
                        self.global_r.emit("note_sync_action", note, SYNC_ACTION_FAILURE)
                    else:
                        self.global_r.emit("note_sync_action", note, SYNC_ACTION_SUCCESS)

                failed_notes_from_contents = {}
                success_notes_from_contents = {}
                for note_content in tried_note_contents:
                    if note_content.note_content_id in failed_note_contents:
                        failed_notes_from_contents[note_content.note.note_id] = note_content.note
                    else:
                        success_notes_from_contents[note_content.note.note_id] = note_content.note
                for note in failed_notes_from_contents.values():
                    self.global_r.emit("note_sync_action", note, SYNC_ACTION_FAILURE)
                for note in success_notes_from_contents.values():
                    self.global_r.emit("note_sync_action", note, SYNC_ACTION_SUCCESS)

                note_notonserver_tracker.discard_all_but_failures(failed_notes)
                note_content_notonserver_tracker.discard_all_but_failures(failed_note_contents)

                # TODO: Actually read the error codes for each failure

            print(r.json())
