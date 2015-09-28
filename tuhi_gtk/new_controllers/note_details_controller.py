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
from tuhi_gtk.config import get_ui_file, REASON_USER
from tuhi_gtk.database import NoteContent, db_session, NC_TYPE_PLAIN
from tuhi_gtk.new_controllers import SubwindowInterfaceController
from tuhi_gtk.new_controllers.popover_controller_mixin import PopoverControllerMixin
from tuhi_gtk.util import ignore_all_args_function, property_change_function

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
        self.show_popover()

    def current_note_changed(self, note):
        self.popover_toggle_button.set_sensitive(note is not None)

    def delete_current_note(self):
        current_note = self.window.current_note
        if current_note is not None:
            head_content = current_note.get_head_content()
            if head_content is not None:
                hc_type = head_content.type
                hc_data = head_content.data
            else:
                hc_type = NC_TYPE_PLAIN
                hc_data = ""

            if hc_type > 0:
                deletion = NoteContent(note=current_note, data=hc_data, type=-hc_type)
                db_session.add(deletion)
                db_session.commit()
                self.global_r.emit("note_content_added", deletion, REASON_USER)
