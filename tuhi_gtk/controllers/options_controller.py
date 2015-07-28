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
from tuhi_gtk.controllers.controller import ActivatableViewController
from tuhi_gtk.config import get_ui_file
from tuhi_gtk.app_logging import get_log_for_prefix_tuple

log = get_log_for_prefix_tuple(("co", "opts"))

class OptionsController(ActivatableViewController):
    def __init__(self, main_window):
        self.main_window = main_window

    def do_first_view_activate(self):
        self.builder = Gtk.Builder.new_from_file(get_ui_file("options_window"))
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("options_window")
        self.window.set_transient_for(self.main_window)
        self.do_view_activate()

    def do_view_activate(self):
        self.window.show_all()
        self.window.present()

    def option_window_closed(self, window, event):
        window.hide()
        return True  # Stop event from propagating
