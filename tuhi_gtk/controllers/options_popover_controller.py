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
from tuhi_gtk.controllers.controller import ActivatableViewController
from tuhi_gtk.app_logging import get_log_for_prefix_tuple

log = get_log_for_prefix_tuple(("co", "opts_p"))

class OptionsPopoverController(ActivatableViewController):
    def __init__(self, options_popover_toggle_button):
        self.toggle_button = options_popover_toggle_button
        self.toggle_button.connect("toggled", self.options_popover_button_toggled)

    def set_intercontroller_dependency(self, options_controller):
        self.options_controller = options_controller

    def do_first_view_activate(self):
        self.builder = Gtk.Builder.new_from_file(get_ui_file("options_popover"))
        self.options_popover = self.builder.get_object("options_popover")
        self.options_popover.set_relative_to(self.toggle_button)
        self.builder.connect_signals(self)
        self.do_view_activate()

    def do_view_activate(self):
        self.options_popover.show_all()

    def options_popover_button_toggled(self, toggle_button):
        if toggle_button.get_active():
            self.view_activate()

    def options_popover_closed(self, popover):
        self.toggle_button.set_active(False)

    def preferences_option_button_clicked(self, preferences_option_button):
        self.options_controller.view_activate()
        self.options_popover.hide()
