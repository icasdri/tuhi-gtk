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

from tuhi_gtk.database import db_session, kv_store, Note, NoteContent, get_current_date, new_uuid
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
                try:
                    note = Note.query.filter(Note.note_id == serialized_note["note_id"]).one()
                    if note.pushed is True:
                        note.update(serialized_note)
                    else:
                        # Conflict from server with unsynced Note, must rename the one that was going to be pushed, and
                        # refactor it's associated NoteContents
                        old_note_id = note.note_id
                        new_note_id = new_uuid()
                        note.note_id = new_note_id
                        NoteContent.query.filter(NoteContent.note_id == old_note_id) \
                                         .update({Note.note_id: new_note_id})
                        db_session.commit()
                        # Create new note_id like that from the server
                        note = Note.deserialize(serialized_note)
                except NoResultFound:
                    note = Note.deserialize(serialized_note)
                note.pushed = True
                db_session.add(note)
                db_session.commit()

            for serialized_note_content in data["note_contents"]:
                note_content = NoteContent.deserialize(serialized_note_content)
                note_content.pushed = True
                try:
                    db_session.add(note_content)
                    db_session.commit()
                except FlushError as e:
                    db_session.rollback()
                    persisted_note_content = NoteContent.query.filter(NoteContent.note_content_id == note_content.note_content_id).one()
                    if persisted_note_content.pushed is True:
                        # Something is awry with server. Server should not send conflicting NoteContents (which are immutable)
                        pass
                    else:
                        # Conflict from server with unsynced Note Content, must rename one that was going to be pushed
                        persisted_note_content.note_content_id = new_uuid()
                        db_session.add(persisted_note_content)
                        db_session.commit()
                        db_session.add(note_content)
                        db_session.commit()
            kv_store["LAST_PULL_DATE"] = get_current_date()




    def push(self):
        notes_list = [note.serialize() for note in Note.query.filter(Note.pushed == False).all()]
        note_contents_list = [note.serialize() for note in NoteContent.query.filter(NoteContent.pushed == False).all()]
        data_dict = {"notes": notes_list, "note_contents": note_contents_list}
        data = json.dumps(data_dict)

        try:
            r = requests.post(self.sync_url, data, auth=self.auth)
        except ConnectionError:
            # TODO: try again, Gobject.timeout_add probably
            pass
        else:
            if r.status_code in (400, 401):
                # TODO: Actual error handling
                pass
                return

            tried_notes = Note.query.filter(Note.note_id.in_((note["note_id"] for note in notes_list)))
            tried_note_contents = NoteContent.query.filter(NoteContent.note_content_id.in_((note_content["note_content_id"] for note_content in note_contents_list)))

            if r.status_code == 200:
                tried_notes.update({Note.pushed: True})
                tried_note_contents.update({NoteContent.pushed: True})
                return

            if r.status_code == 202:
                response = r.json()
                failed_notes = response["notes"] if "notes" in response else []
                failed_note_contents = response["note_contents"] if "note_contents" in response else []
                tried_notes.filter(Note.note_id.notin_((note["note_id"] for note in failed_notes))) \
                           .update({Note.pushed: True})
                tried_note_contents.filter(NoteContent.note_content_id.notin_((note_content["note_content_id"] for note_content in failed_note_contents))) \
                                   .update({NoteContent.pushed: True})
            print(r.json())
