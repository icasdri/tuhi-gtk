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
from tuhi_gtk.controllers.list_controller import ModelListController
from tuhi_gtk.database import db_session, kv_store, Note
from tuhi_gtk.note_row_view import NoteRow


class NoteListController(ModelListController):
    log_prefix_tuple = ("co", "note_l")
    list_name = "Note List"
    controller_name = "Note List Controller"
    model = Note
    default_query = Note.non_deleted()

    def __init__(self, main_list):
        super(NoteListController, self).__init__(main_list)
        self.list.set_sort_func(sort_func)

    def initial_populate(self):
        super(NoteListController, self).initial_populate()
        last_note_selected = None
        if "LAST_NOTE_SELECTED" in kv_store:
            last_note_selected = Note.query.filter(Note.note_id == kv_store["LAST_NOTE_SELECTED"]).first()
        if last_note_selected is None:
            last_note_selected = Note.non_deleted().order_by(Note.date_content_modified.desc()).first()
        self.log.debug("Selecting last note selected")
        self.select_item(last_note_selected)

    def shutdown(self):
        selected_note_row = self.list.get_selected_row()
        if selected_note_row is None:
            if "LAST_NOTE_SELECTED" in kv_store:
                self.log.debug("Clearing LAST_NOTE_SELECTED")
                del kv_store["LAST_NOTE_SELECTED"]
        else:
            self.log.debug("Setting LAST_NOTE_SELECTED: (%s): %s",
                         selected_note_row.note.note_id, selected_note_row.note.title)
            kv_store["LAST_NOTE_SELECTED"] = selected_note_row.note.note_id

    def db_dirty(self, note):
        if note.deleted is True:
            self.remove_item(note)
        else:
            self.refresh_item(note)

    @staticmethod
    def _item_id(note):
        return note.note_id

    def _create_row(self, note):
        noterow = NoteRow.get_note_row(note)
        noterow.show_all()
        return noterow

    def select_newer(self, note):
        target_note = Note.non_deleted().filter(Note.date_content_modified > note.date_content_modified) \
                                        .filter(Note.note_id != note.note_id) \
                                        .order_by(Note.date_content_modified.asc()) \
                                        .first()
        if target_note is None:
            target_note = Note.non_deleted().filter(Note.date_content_modified <= note.date_content_modified) \
                                            .filter(Note.note_id != note.note_id) \
                                            .order_by(Note.date_content_modified.desc()) \
                                            .first()
        self.select_item(target_note)

    def mark_note(self, note, mark):
        noterow = self._get_row(note)
        noterow.mark(mark)


def sort_func(a, b):
    return b.note.date_content_modified - a.note.date_content_modified