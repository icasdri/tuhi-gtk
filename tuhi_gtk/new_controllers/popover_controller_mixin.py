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
from tuhi_gtk.util import ignore_all_args_function


class PopoverControllerMixin(object):
    def __init__(self, parent, toggle_button_id, popover_ui_name):
        self.__parent = parent
        self.__toggle_button_id = toggle_button_id
        self.__popover_ui_name = popover_ui_name

    def connect_popover_toggle_button(self):
        self.popover_toggle_button = self.__parent.get_object(self.__toggle_button_id)
        self.popover_toggle_button.connect("toggled", self.__popover_button_toggled)

    def init_popover(self):
        self.builder = Gtk.Builder.new_from_file(get_ui_file(self.__popover_ui_name))
        self.popover = self.builder.get_object(self.__popover_ui_name)
        self.popover.set_relative_to(self.popover_toggle_button)
        self.popover.connect("closed", self.__handle_popover_closed)

    def show_popover(self):
        self.popover.show_all()

    def hide_popover(self, *_):
        self.popover.hide()

    def __popover_button_toggled(self, toggle_button):
        if toggle_button.get_active():
            self.view_activate()

    def __handle_popover_closed(self, _):
        self.popover_toggle_button.set_active(False)
