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
from tuhi_gtk.database import Note, NC_TYPE_PERMA_DELETE
from tuhi_gtk.new_controllers import SubwindowInterfaceController
from tuhi_gtk.config import get_ui_file
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.new_controllers.tree_list_store_controller_mixin import TreeListStoreControllerMixin
from tuhi_gtk.util import ignore_all_args_function, format_date, ignore_sender_function

log = get_log_for_prefix_tuple(("co", "trash"))

MODEL_COLUMN_MAPPING = [lambda x: x.note_id, lambda x: format_date(x.date_content_modified), lambda x: x.title]


class TrashController(SubwindowInterfaceController, TreeListStoreControllerMixin):
    def do_init(self):
        self.window.register_controller("trash", self)
        self.window.get_controller("options_popover").connect("view_activated_for_first_time",
                                                              ignore_all_args_function(self.init_after_popover_first_activate))

    def init_after_popover_first_activate(self):
        self.window.get_controller("options_popover") \
                   .get_object("trash_view_button").connect("clicked", ignore_all_args_function(self.view_activate))

    def do_first_view_activate(self):
        self.builder = Gtk.Builder.new_from_file(get_ui_file("trash_window"))
        self.liststore = Gtk.ListStore(str, str, str)
        self.get_object("treeview").set_model(self.liststore)
        self.builder.expose_object("liststore", self.liststore)
        self.builder.connect_signals(self)

        # Make our columns. Text corresponds to position of column in liststore model.
        id_col = Gtk.TreeViewColumn("id")  # Hidden column for storing application data
        id_col.set_visible(False)
        self.get_object("treeview").append_column(id_col)
        self.get_object("treeview").append_column(Gtk.TreeViewColumn("Date Deleted", Gtk.CellRendererText(), text=1))
        self.get_object("treeview").append_column(Gtk.TreeViewColumn("Ttile", Gtk.CellRendererText(), text=2))

        TreeListStoreControllerMixin.__init__(self, self.liststore, MODEL_COLUMN_MAPPING, Note.soft_deleted())
        self.initial_populate()

        self.global_r.connect("note_metadata_changed", ignore_sender_function(self.handle_note_metadata_changed))

        self.builder.connect_signals(self)

        self.get_object("trash_window").set_transient_for(self.window.get_object("main_window"))
        self.do_view_activate()

    def do_view_activate(self):
        self.get_object("trash_window").show_all()
        self.get_object("trash_window").present()

    def trash_window_closed(self, window, event):
        # TODO: Should we reconstruct this window every time?
        window.hide()
        return True  # Stop event from propagating

    def handle_note_metadata_changed(self, note, reason):
        if note.type == NC_TYPE_PERMA_DELETE or note.type > 0:
            self.remove_item(note)
        else:
            self.add_item(note)

    def restore_button_clicked(self, _):
        # TODO: TESTING ONLY: this is NOT the actual restore logic. Just some testing code to show that get_item is working.
        _, it = self.get_object("treeview").get_selection().get_selected()
        if it is not None:
            note = self.get_item(it)
            print(note.note_id, ": ", note.title)

    def delete_permanently_button_clicked(self, _):
        pass

