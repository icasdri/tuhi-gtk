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

from tuhi_gtk.database import db_session, kv_store, Note, NoteContent, get_current_date, new_uuid, \
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
                        note.update(serialized_note)
                        db_session.commit()
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

            kv_store["LAST_PULL_DATE"] = get_current_date()


    def push(self):
        notes_list = [note.serialize() for note in Note.query.filter(or_(Note.pushed == False, )).all()]
        note_contents_list = [note.serialize() for note in NoteContent.query.filter(NoteContent.pushed == False).all()]
        data_dict = {"notes": notes_list, "note_contents": note_contents_list}
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

            tried_notes = Note.query.filter(Note.note_id.in_((note["note_id"] for note in notes_list))) \
                if len(notes_list) > 0 else Note.query.filter(1 == 0)
            tried_note_contents = NoteContent.query.filter(NoteContent.note_content_id.in_((note_content["note_content_id"] for note_content in note_contents_list))) \
                if len(note_contents_list) > 0 else NoteContent.query.filter(1 == 0)

            if r.status_code == 200:
                tried_notes.update({Note.pushed: True}, synchronize_session='fetch')
                tried_note_contents.update({NoteContent.pushed: True}, synchronize_session='fetch')
                db_session.commit()
                return

            if r.status_code == 202:
                response = r.json()
                failed_notes = response["notes"] if "notes" in response else []
                failed_note_contents = response["note_contents"] if "note_contents" in response else []
                tried_notes.filter(Note.note_id.notin_((note["note_id"] for note in failed_notes))) \
                           .update({Note.pushed: True}, synchronize_session='fetch')
                tried_note_contents.filter(NoteContent.note_content_id.notin_((note_content["note_content_id"] for note_content in failed_note_contents))) \
                                   .update({NoteContent.pushed: True}, synchronize_session='fetch')
                db_session.commit()
                # TODO: Conflict checks here
            print(r.json())
