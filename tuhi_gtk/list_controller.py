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

from sqlalchemy import event
from tuhi_gtk.database import db_session, Note
from tuhi_gtk.note_row_view import NoteRow


class NoteListController(object):
    def __init__(self, main_list):
        self.list = main_list
        self.note_set = set()
        self.noterow_lookup = {}
        self.db_changed(db_session)
        event.listen(db_session, "after_commit", self.db_changed)

    def db_changed(self, session):
        old_set = self.note_set
        new_set = {note for note in Note.query.filter(Note.deleted == False).all()}
        removed_items = old_set - new_set
        new_items = new_set - old_set
        for note in new_items:
            self.add_note(note)
        for note in removed_items:
            self.remove_note(note)

    def _noterow(self, note):
        if note.note_id in self.noterow_lookup:
            return self.noterow_lookup[note.note_id]
        else:
            noterow = NoteRow.get_note_row(note)
            self.noterow_lookup[note.note_id] = noterow
            return noterow

    def add_note(self, note):
        noterow = self._noterow(note)
        self.list.add(noterow)

    def remove_note(self, note):
        noterow = self._noterow(note)
        self.list.remove(noterow)
        del self.noterow_lookup[note.note_id]


def sort_func(a, b):
    return b.note.date_modified - a.note.date_modified