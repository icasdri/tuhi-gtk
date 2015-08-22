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
from tuhi_gtk.config import get_ui_file
from tuhi_gtk.app_logging import get_log_for_prefix_tuple

log = get_log_for_prefix_tuple(("ui", "note_row"))

# dict mapping feature_name -> (feature_widget_id, show_func, hide_func)
FEATURES = {
    "spinner": ("spinner", lambda w: w.start(), lambda w: w.stop()),
    "failure_label": ("failure_label", None, None)
}

class NoteRow(Gtk.ListBoxRow):
    def initialize(self, builder, note):
        self.builder = builder
        self._label = builder.get_object("label")
        self._box = builder.get_object("box")
        self._spinner = builder.get_object("spinner")
        self.note = note
        self._current_feature = None
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
            self._spinner.show()
            self._spin_status = True

    def spinner_stop(self):
        if self._spin_status is True:
            self._spinner.stop()
            self._box.remove(self.spinner)
            self._spin_status = False

    def show_feature(self, feature):
        if self._current_feature == feature:
            return
        self.hide_feature()
        widget_id, show_func, _ = FEATURES[feature]
        widget = self.builder.get_object(widget_id)
        self._box.pack_end(widget, expand=False, fill=False, padding=12)
        widget.show()
        if show_func is not None:
            show_func(widget)
        self._current_feature = feature

    def hide_feature(self, feature=None):
        if self._current_feature is None:
            return
        if feature is not None and feature != self._current_feature:
            return
        widget_id, _, hide_func = FEATURES[self._current_feature]
        widget = self.builder.get_object(widget_id)
        if hide_func is not None:
            hide_func(widget)
        widget.hide()
        self._box.remove(widget)
        self._current_feature = None

    def refresh(self):
        log.debug("Refreshing NoteRow: (%s) '%s'", self.note.note_id, self.note.title)
        self._label.set_text(self.note.title)
        self.changed()

    def mark(self, mark):
        if mark == "saved":
            print("Mark saved called: (%s) '%s'" % (self.note.note_id, self.note.title))
            # self.spinner_start()
            self.refresh()
        else:
            log.warn("Unknown NoteRow mark: %s", mark)

