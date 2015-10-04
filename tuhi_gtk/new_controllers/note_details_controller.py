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

from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.config import REASON_USER
from tuhi_gtk.new_controllers import SubwindowInterfaceController
from tuhi_gtk.new_controllers.popover_controller_mixin import PopoverControllerMixin
from tuhi_gtk.util import ignore_all_args_function, property_change_function, format_date

log = get_log_for_prefix_tuple(("co", "note_details"))

class NoteDetailsController(SubwindowInterfaceController, PopoverControllerMixin):
    def do_init(self):
        self.window.register_controller("note_details", self)
        PopoverControllerMixin.__init__(self, self.window, "note_details_toggle_button", "note_details_popover")
        self.window.connect("view-activated", ignore_all_args_function(self.init_after_window_activate))

    def init_after_window_activate(self):
        self.connect_popover_toggle_button()
        self.window.connect("notify::current-note", property_change_function(self.current_note_changed))
        self.current_note_changed(self.window.current_note)

    def do_first_view_activate(self):
        self.init_popover()
        self.builder.connect_signals(self)
        self.get_object("delete_current_note_button").connect("clicked", ignore_all_args_function(self.delete_current_note))

    def do_view_activate(self):
        self.window.get_controller("source_view").save_current_note()
        current_note = self.window.current_note
        self.get_object("date_created_label").set_text(format_date(current_note.date_created))
        self.get_object("date_modified_label").set_text(format_date(current_note.date_content_modified))
        self.show_popover()

    def current_note_changed(self, note):
        self.popover_toggle_button.set_sensitive(note is not None)

    def delete_current_note(self):
        current_note = self.window.current_note
        if current_note is not None:
            deletion_nc = current_note.delete_to_trash()
            self.global_r.emit("note_content_added", deletion_nc, REASON_USER)
