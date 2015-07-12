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

from gi.repository import Gtk, GObject
from sqlalchemy import event
from tuhi_gtk.database import db_session, kv_store, Note, NoteContent
from tuhi_gtk.note_row_view import NoteRow


class NoteListController(object):
    def __init__(self, main_list, source_view):
        self.list = main_list
        self.source_view = source_view
        self.note_set = set()
        self.noterow_lookup = {}
        self.initial_populate()
        event.listen(db_session, "before_commit", self.db_changed)

    def initial_populate(self):
        for note in Note.query.filter(Note.deleted == False).all():
            self.add_note(note)

    def db_changed(self, session):
        print("WTF Why no Event")
        print(session.deleted)
        print(session.dirty)
        for obj in session.new:
            if isinstance(obj, Note):
                self.add_note(obj)
        for obj in session.deleted:
            print("Cane Cane Cane")
            if isinstance(obj, Note):
                print("Recieved deletion from db_session: " + obj.title)
                self.remove_note(obj)
        for obj in session.dirty:
            if isinstance(obj, Note):
                if obj.deleted is True:
                    self.remove_note(obj)
                else:
                    self.refresh_note(obj)

    def _noterow(self, note):
        if note.note_id in self.noterow_lookup:
            noterow = self.noterow_lookup[note.note_id]
        else:
            noterow = NoteRow.get_note_row(note)
            self.noterow_lookup[note.note_id] = noterow
        noterow.show_all()
        return noterow

    def add_note(self, note):
        noterow = self._noterow(note)
        if noterow not in self.list:
            self.list.add(noterow)
            self._refresh_list()

    def remove_note(self, note):
        noterow = self._noterow(note)
        # self.list.remove(noterow)
        noterow.destroy()
        del self.noterow_lookup[note.note_id]
        self._refresh_list()

    def refresh_note(self, note):
        noterow = self._noterow(note)
        noterow.refresh()
        self._refresh_list()

    def _refresh_list(self):
        pass
        # The below causes exit code 139 for some reason, segfault in kernel logs
        # self.list.invalidate_sort()
        # self.list.invalidate_filter()

    def select_note(self, note):
        noterow = self._noterow(note)
        self.list.select_row(noterow)

    def activate_note(self, note):
        print("Note activated: " + note.title)
        content = NoteContent.query.filter(NoteContent.note_id == note.note_id) \
                                   .order_by(NoteContent.date_created.desc()) \
                                   .first()
        if content is not None:
            self.buffer = Gtk.TextBuffer(text=content.data)
            self.source_view.set_buffer(self.buffer)


def sort_func(a, b):
    return b.note.date_modified - a.note.date_modified