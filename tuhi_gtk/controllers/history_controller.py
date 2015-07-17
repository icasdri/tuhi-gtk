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
from tuhi_gtk.controllers.controller import Controller
from tuhi_gtk.controllers.history_content_list_controller import HistoryContentListController

class HistoryController(Controller):
    log_prefix_tuple = ("co", "hist")

    def __init__(self, history_popover_builder):
        super(HistoryController, self).__init__()
        self.history_popover = history_popover_builder.get_object("history_popover")
        self.history_popover_box = history_popover_builder.get_object("history_popover_box")
        self.hc_list = None
        self.hcl_controller = None
        self.current_note = None
        self.current_note_content = None

    def set_intercontroller_dependency(self, source_view_controller):
        self.source_view_controller = source_view_controller

    def register_current_note(self, note):
        if note == self.current_note:
            return
        self.current_note = note
        self.current_note_content = None

    def activate_history_view(self):
        if self.hc_list is not None:
            self.hc_list.destroy()

        self.hc_list = get_history_content_list()
        self.hc_list.connect("row_selected", self.history_content_row_selected)
        self.history_popover_box.add(self.hc_list)
        self.hc_list.show_all()

        self.hcl_controller = HistoryContentListController(self.hc_list, self.current_note)
        self.hcl_controller.startup()

        self.history_popover.show_all()

    def history_content_row_selected(self, hc_list, row):
        print("HISTORY CONTENT ROW SELECTED", row.note_content.note_content_id)

def get_history_content_list():
    builder = Gtk.Builder.new_from_file(get_ui_file("history_content_list"))
    return builder.get_object("history_content_list")
