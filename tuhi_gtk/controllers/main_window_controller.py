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

from gi.repository import GObject, Gtk, GtkSource
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.config import get_ui_file
from tuhi_gtk.util import ignore_all_args_function
from tuhi_gtk.controllers import WindowController

log = get_log_for_prefix_tuple(("w", "main"))

class MainWindowController(WindowController):
    current_note = GObject.Property(type=object)
    current_note_content = GObject.Property(type=object)

    def do_init(self):
        self._make_subcontrollers([
            "MainWindowCosmeticsController",
            "SourceViewController",
            "NoteListController",
            "HistoryController",
            "NoteDetailsController",
            "OptionsPopoverController",
            "NewNoteController",
            "SyncButtonController",
            "PreferencesController",
            "TrashController",
            "SyncDialogsController"
        ])

    def do_first_view_activate(self):
        log.debug("Registering GObject types for MainWindow")
        GObject.type_register(GtkSource.View)
        log.debug("Building Main Window")
        self.builder = Gtk.Builder.new_from_file(get_ui_file("main_window"))
        self.get_object("main_window").connect("delete-event", ignore_all_args_function(self.shutdown))

    def do_view_activate(self):
        self.get_object("main_window").show_all()

    def do_shutdown(self):
        log.debug("Main Window Controller Shutdown")
        self.global_r.emit("application_shutdown", "Main Window Closed")

