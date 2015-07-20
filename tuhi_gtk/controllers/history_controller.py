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
        self.row_active_handler = None

    def set_intercontroller_dependency(self, source_view_controller):
        self.source_view_controller = source_view_controller

    def activate_history_view(self):
        if self.hc_list is not None:
            self.log.debug("Destroying previous history content list")
            self.hc_list.disconnect(self.row_active_handler)
            self.hc_list.destroy()

        self.log.debug("Creating a new history content list")
        self.hc_list = get_history_content_list()
        self.row_active_handler = \
            self.hc_list.connect("row_selected", self.history_content_row_selected)
        self.history_popover_box.add(self.hc_list)
        self.hc_list.show_all()

        current_note = self.source_view_controller.get_current_note()
        if current_note is not None:
            self.hcl_controller = HistoryContentListController(self.hc_list, current_note)
            self.hcl_controller.startup()
            self.source_view_controller.save_current_note()
            current_note_content = self.source_view_controller.get_current_note_content()
            self.hcl_controller.select_item(current_note_content)

        self.history_popover.show_all()

    def history_content_row_selected(self, hc_list, row):
        content = row.note_content if row is not None else None
        self.log.debug("History content row selected: %s", content.note_content_id if content is not None else "None")
        self.source_view_controller.activate_note_content(content)

def get_history_content_list():
    builder = Gtk.Builder.new_from_file(get_ui_file("history_content_list"))
    return builder.get_object("history_content_list")
