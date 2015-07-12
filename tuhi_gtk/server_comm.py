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
from sqlalchemy.orm.exc import NoResultFound, FlushError

from tuhi_gtk.database import kv_store, get_current_date, \
    note_change_tracker, note_notonserver_tracker, note_content_notonserver_tracker, \
    note_store, note_content_store
from tuhi_gtk.config import SYNCSERVER_NOTES_ENDPOINT

class ServerAccessPoint(object):
    def __init__(self):
        self.sync_url = kv_store["SYNCSERVER_URL"].rstrip("/") + SYNCSERVER_NOTES_ENDPOINT
        self.auth = (kv_store["SYNCSERVER_USERNAME"], kv_store["SYNCSERVER_PASSWORD"])

    def sync(self):
        self.pull()
        self.push()

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
            for serialized_note in data["notes"]:
                note = note_store.get(serialized_note)
                if note is not None:
                    # I have a note that has the same id as the one coming in.
                    if note in note_notonserver_tracker:
                        # There is a new note on the server that conflicts with a new note I've made.
                        # We are talking about different notes. Conflict with server. Must change id of notonserver note
                        old_id, new_id = note_store.rename_to_new_uuid(note)
                        note_notonserver_tracker.register_rename(old_id, new_id)
                        note_store.add_new(serialized_note)
                    elif note in note_change_tracker:
                        # There is change to a note I previously pushed to the server, but I have since changed the note as well.
                        # We are talking about the same note. See who is newer.
                        if note.date_modified < serialized_note["date_modified"]:
                            # Server is newer, discard my change.
                            note.update(serialized_note)
                            note_change_tracker.discard(note)  # This commits the session.
                        # Otherwise, I am newer, and I ignore the change
                    else:
                        # This is an update to a note that I previously pushed, but I have not since changed.
                        note_store.update(note, serialized_note)
                else:
                    # This is a new note that I am unaware of.
                    note_store.add_new(serialized_note)

            for serialized_note_content in data["note_contents"]:
                note_content = note_content_store.get(serialized_note_content)
                if note_content is not None:
                    # I have a note content that has same id as the one coming in.
                    if note_content in note_content_notonserver_tracker:
                        # This note content from the server conflicts with one that I've made but not pushed
                        old_id, new_id = note_content_store.rename_to_new_uuid(note_content)
                        note_content_notonserver_tracker.register_rename(old_id, new_id)
                        note_content_store.add_new(serialized_note_content)
                    # Otherwise, something is awry with server. Server should not send conflicting NoteContents
                    # (which are immutable) -- thus, I ignore the change
                else:
                    # This is a new note content that I am unaware of.
                    note_content_store.add_new(serialized_note_content)

            # Recalculate date_content_modified on Note instances
            for note_id in {nc["note_id"] for nc in data["note_contents"]}:
                note_store.get(note_id).get_head_content()

            kv_store["LAST_PULL_DATE"] = get_current_date()

    def push(self):
        tried_notes = note_change_tracker.get_all_as_query() \
                                         .union(note_notonserver_tracker.get_all_as_query())
        tried_note_contents = note_content_notonserver_tracker.get_all_as_query()
        data_dict = {"notes": [n.serialize() for n in tried_notes.all()],
                     "note_contents": [nc.serialize() for nc in tried_note_contents.all()]}
        data = json.dumps(data_dict)

        try:
            r = requests.post(self.sync_url, data, auth=self.auth)
        except ConnectionError:
            # TODO: try again, Gobject.timeout_add probably
            pass
        else:
            if r.status_code in (400, 401, 500):
                # TODO: Actual error handling for Bad Request, Unauthorized, and Server Error
                pass
                return

            if r.status_code == 200:
                note_change_tracker.discard_all()
                note_notonserver_tracker.discard_all()
                note_content_notonserver_tracker.discard_all()
                return

            if r.status_code == 202:
                response = r.json()

                failed_notes = response["notes"] if "notes" in response else []
                failed_note_contents = response["note_contents"] if "note_contents" in response else []
                failed_notes = [x["note_id"] for x in failed_notes]
                failed_note_contents = [x["note_content_id"] for x in failed_note_contents]

                note_change_tracker.discard_all_but_failures(failed_notes)
                note_notonserver_tracker.discard_all_but_failures(failed_notes)
                note_content_notonserver_tracker.discard_all_but_failures(failed_note_contents)

                # TODO: Actually read the error codes for each failure

            print(r.json())
