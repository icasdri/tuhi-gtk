# Copyright 2015-2016 icasdri
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

from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.config import REASON_USER
from tuhi_gtk.util import ignore_all_args_function
from tuhi_gtk.database import Note, db_session
from tuhi_gtk.controllers import SubwindowInterfaceController

log = get_log_for_prefix_tuple(("co", "new_note"))

class NewNoteController(SubwindowInterfaceController):
    def do_init(self):
        self.window.register_controller("new_note", self)
        self.window.connect("view-activated", ignore_all_args_function(self.init_after_window_activate))

    def init_after_window_activate(self):
        self.new_note_button = self.window.get_object("new_note_button")
        self.new_note_button.connect("clicked", ignore_all_args_function(self.view_activate))

    def do_view_activate(self):
        log.debug("New note logic activated")
        note = Note(title="New Note")
        db_session.add(note)
        db_session.commit()
        self.global_r.emit("note_added", note, REASON_USER)
        self.window.current_note = note

