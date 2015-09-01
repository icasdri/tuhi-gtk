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
from tuhi_gtk.feature_view_mixin import FeatureViewMixin

log = get_log_for_prefix_tuple(("ui", "note_row"))

# dict mapping feature_name -> (feature_widget_id, show_func, hide_func)
FEATURES = {
    "spinner": ("spinner", lambda w: w.start(), lambda w: w.stop()),
    "failure_label": ("failure_label", None, None),
    "synced_in_emblem": ("synced_in_emblem", None, None),
    "unsynced_emblem": ("unsynced_emblem", None, None)
}

class NoteRow(Gtk.ListBoxRow, FeatureViewMixin):
    def initialize(self, builder, note):
        self.builder = builder
        self._label = builder.get_object("label")
        self._box = builder.get_object("box")
        self.note = note
        FeatureViewMixin.__init__(self, FEATURES, self._box, self.builder, padding=12)
        self.refresh()

    @staticmethod
    def get_note_row(note):
        builder = Gtk.Builder.new_from_file(get_ui_file("note_row"))
        note_row = builder.get_object("note_row")
        note_row.initialize(builder, note)
        return note_row

    def refresh(self):
        log.debug("Refreshing NoteRow: (%s) '%s'", self.note.note_id, self.note.title)
        self._label.set_text(self.note.title)
        self.changed()

    def mark(self, mark):
        if mark == "saved":
            print("Mark saved called: (%s) '%s'" % (self.note.note_id, self.note.title))
            self.refresh()
        else:
            log.warn("Unknown NoteRow mark: %s", mark)

