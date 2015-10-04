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
from tuhi_gtk.util import ignore_all_args_function, property_change_function
from tuhi_gtk.new_controllers import SubwindowInterfaceController
from tuhi_gtk.new_controllers.popover_controller_mixin import PopoverControllerMixin

log = get_log_for_prefix_tuple(("co", "hist"))

class HistoryController(SubwindowInterfaceController, PopoverControllerMixin):
    def do_init(self):
        self.window.register_controller("history", self)
        PopoverControllerMixin.__init__(self, self.window, "history_popover_toggle_button", "history_popover")
        self.window.connect("view-activated", ignore_all_args_function(self.init_after_window_activate))
        self._make_sibling_controllers([
            "HistoryContentListController"
        ])

    def init_after_window_activate(self):
        self.connect_popover_toggle_button()
        self.window.connect("notify::current-note", property_change_function(self.current_note_changed))
        self.current_note_changed(self.window.current_note)

    def do_first_view_activate(self):
        self.init_popover()
        self.builder.connect_signals(self)

    def do_view_activate(self):
        self.window.get_controller("source_view").save_current_note()
        self.show_popover()

    def current_note_changed(self, note):
        self.popover_toggle_button.set_sensitive(note is not None)

