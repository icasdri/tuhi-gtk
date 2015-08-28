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
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.config import get_ui_file
from tuhi_gtk.new_controllers import SubwindowInterfaceController
from tuhi_gtk.util import ignore_all_args_function, property_change_function

log = get_log_for_prefix_tuple(("co", "hist"))

class HistoryController(SubwindowInterfaceController):
    def do_init(self):
        self.window.register_controller("history", self)
        self.window.connect("view-activated", ignore_all_args_function(self.init_after_window_activate))
        self._make_sibling_controllers([
            "HistoryContentListController"
        ])

    def init_after_window_activate(self):
        self.toggle_button = self.window.get_object("history_popover_toggle_button")
        self.toggle_button.connect("toggled", self.history_popover_button_toggled)
        self.window.connect("notify::current-note", property_change_function(self.current_note_changed))
        self.current_note_changed(self.window.current_note)

    def do_first_view_activate(self):
        self.builder = Gtk.Builder.new_from_file(get_ui_file("history_popover"))
        self.history_popover = self.builder.get_object("history_popover")
        self.history_popover.set_relative_to(self.toggle_button)
        self.builder.connect_signals(self)

    def do_view_activate(self):
        self.window.get_controller("source_view").save_current_note()
        self.history_popover.show_all()

    def current_note_changed(self, note):
        self.toggle_button.set_sensitive(note is not None)

    def history_popover_button_toggled(self, toggle_button):
        if toggle_button.get_active():
            self.view_activate()

    def history_popover_closed(self, popover):
        self.toggle_button.set_active(False)

