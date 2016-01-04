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

from gi.repository import GObject, Gtk
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.config import get_ui_file
from tuhi_gtk.util import ignore_all_args_function, ignore_sender_function, property_change_function
from tuhi_gtk.database import NoteContent
from tuhi_gtk.controllers import SubwindowInterfaceController
from tuhi_gtk.controllers.list_controller_mixin import ListControllerMixin
from tuhi_gtk.history_content_row import HistoryContentRow

log = get_log_for_prefix_tuple(("co", "hist_c_l"))

class HistoryContentListController(SubwindowInterfaceController, ListControllerMixin):
    def do_init(self):
        self.window.register_controller("history_content_list", self)
        self.window.connect("notify::current-note", property_change_function(self.current_note_changed))
        self.window.get_controller("history").connect("view-activated", ignore_all_args_function(self.view_activate))
        self.current_note = None
        self.signal_listener_id = None
        self.selection_signal_listener_id = None
        self.list = None

    def current_note_changed(self, note):
        if note != self.current_note:
            self.was_activated_before = False
            if self.signal_listener_id is not None:
                GObject.source_remove(self.signal_listener_id)
                self.signal_listener_id = None
            if self.selection_signal_listener_id is not None:
                GObject.source_remove(self.selection_signal_listener_id)
                self.selection_signal_listener_id = None
            if self.list is not None:
                self.list.destroy()
            self.list = None
            self.current_note = note

    def do_first_view_activate(self):
        self.builder = Gtk.Builder.new_from_file(get_ui_file("history_content_list"))
        self.list = self.builder.get_object("history_content_list")
        self.list.set_sort_func(sort_func)
        self.list.show_all()
        self.window.get_controller("history").get_object("history_popover_box").add(self.list)
        if self.current_note is None:
            self.current_note_changed(self.window.current_note)
        if self.current_note is None:  # if it's is still None
            log.error("History content popover should not be able to be activated for no Note (current_note is None).")
        else:
            default_query = NoteContent.query_for_note(self.current_note)
            ListControllerMixin.__init__(self, self.list, self._create_row, lambda x: x.note_content_id, default_query)
            self.signal_listener_id = self.global_r.connect("note-content-added", ignore_sender_function(self.handle_new_note_content))
            self.initial_populate()
            self.selection_signal_listener_id = self.list.connect("row-selected", ignore_sender_function(self.row_selected_callback))

    def do_view_activate(self):
        content = self.window.current_note_content
        log.debug("Selecting window.current_note_content (%s)", content.note_content_id)
        self.select_item(content)

    def handle_new_note_content(self, note_content, _):
        if self.list is not None:
            #if note_content is not None and note_content.note
            self.add_item(note_content)

    def row_selected_callback(self, row):
        if row is not None:
            self.window.current_note_content = row.note_content

    def do_shutdown(self):
        if self.list is not None:
            self.list.destroy()

    def _create_row(self, note_content):
        hc_row = HistoryContentRow.get_history_content_row(note_content)
        hc_row.show_all()
        return hc_row

def sort_func(a, b):
    return b.note_content.date_created - a.note_content.date_created
