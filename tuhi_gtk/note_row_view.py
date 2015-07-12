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

from gi.repository import Gtk
from tuhi_gtk.config import get_ui_file, log


class NoteRow(Gtk.ListBoxRow):
    def initialize(self, builder, note):
        self.builder = builder
        self._label = builder.get_object("label")
        self._box = builder.get_object("box")
        self._spinner = builder.get_object("spinner")
        self._spin_status = False
        self.note = note
        self.refresh()

    @staticmethod
    def get_note_row(note):
        builder = Gtk.Builder.new_from_file(get_ui_file("note_row"))
        note_row = builder.get_object("note_row")
        note_row.initialize(builder, note)
        return note_row

    def spinner_start(self):
        if self._spin_status is False:
            self._spinner.start()
            self._box.pack_end(self._spinner, expand=False, fill=False, padding=12)
            self._spin_status = True

    def spinner_stop(self):
        if self._spin_status is True:
            self._spinner.stop()
            self._box.remove(self.spinner)
            self._spin_status = False

    def refresh(self):
        log.ui.debug("Refreshing NoteRow: (%s) '%s'", self.note.note_id, self.note.title)
        self._label.set_text(self.note.title)

    def mark_unsaved(self):
        pass

    def mark_saved(self):
        self.spinner_start()
