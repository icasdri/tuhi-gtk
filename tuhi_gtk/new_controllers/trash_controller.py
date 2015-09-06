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
from tuhi_gtk.database import Note
from tuhi_gtk.new_controllers import SubwindowInterfaceController
from tuhi_gtk.config import get_ui_file
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.new_controllers.tree_list_store_controller_mixin import TreeListStoreControllerMixin
from tuhi_gtk.util import ignore_all_args_function, format_date

log = get_log_for_prefix_tuple(("co", "trash"))

MODEL_COLUMN_MAPPING = [lambda x: format_date(x.date_content_modified), lambda x: x.title]


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
        self.liststore = Gtk.ListStore(str, str)
        self.get_object("treeview").set_model(self.liststore)
        self.builder.expose_object("liststore", self.liststore)
        self.builder.connect_signals(self)

        # Make our columns. Text corresponds to position of column in liststore model.
        self.get_object("treeview").append_column(Gtk.TreeViewColumn("Date Deleted", Gtk.CellRendererText(), text=0))
        self.get_object("treeview").append_column(Gtk.TreeViewColumn("Ttile", Gtk.CellRendererText(), text=1))

        TreeListStoreControllerMixin.__init__(self, self.liststore, MODEL_COLUMN_MAPPING, Note.soft_deleted(), lambda x: x.note_id)
        self.initial_populate()

        self.get_object("trash_window").set_transient_for(self.window.get_object("main_window"))
        self.do_view_activate()

    def do_view_activate(self):
        self.get_object("trash_window").show_all()
        self.get_object("trash_window").present()

    def trash_window_closed(self, window, event):
        # TODO: Should we reconstruct this window every time?
        window.hide()
        return True  # Stop event from propagating

