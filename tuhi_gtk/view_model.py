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
from gi.repository import Gio, GObject
from tuhi_gtk.database import db_session, Note
from tuhi_gtk.note_row_view import NoteRow

class NoteWrapper(GObject.GObject):
    def __init__(self, note_to_wrap):
        self._wrapped_note = note_to_wrap

    def unwrap(self):
        return self._wrapped_note


class NoteListModel(GObject.GObject, Gio.ListModel):
    def __init__(self):
        # GObject.type_register(Note)
        self.internal_rep = []
        self.db_changed(db_session)
        event.listen(db_session, "after_commit", self.db_changed)

    def db_changed(self, session):
        old_len = len(self.internal_rep)
        self.internal_rep = [NoteWrapper(note) for note in Note.query.filter(Note.deleted == False).all()]
        self.items_changed(0, old_len, self.get_n_items())

    def get_item_type(self):
        return NoteWrapper

    def get_item(self, position):
        return self.internal_rep[position]

    def get_n_items(self):
        return len(self.internal_rep)


def create_widget_func(item, user_data):
    return NoteRow.get_note_row(item)


def sort_func(a, b, user_data):
    return b.date_modified - a.date_modified