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

from gi.repository import Gtk, GObject, GtkSource, Gio
from tuhi_gtk import note_row_view
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.config import get_ui_file
from tuhi_gtk.database import Note, db_session
from tuhi_gtk.controllers import NoteListController, SourceViewController

log_main = get_log_for_prefix_tuple(("main",))
log = get_log_for_prefix_tuple(("ui", "handler"))

class Handlers:
    def __init__(self, builder):
        log_main.debug("Initializing Main Window Handlers")
        self.builder = builder
        self.side_hb = builder.get_object("side_hb")
        self.search_bar = builder.get_object("search_bar")
        self.search_button = builder.get_object("search_button")
        self.history_popover_toggle_button = builder.get_object("history_popover_toggle_button")
        self._hb_synced_width = 0

        self._init_sourceview()
        self._init_notelist()

        self.source_view_controller.set_intercontroller_dependency(self.list_controller)

        self.list_controller.startup()
        self.source_view_controller.startup()

    def _init_sourceview(self):
        log_main.debug("Initializing SourceView components and handlers")
        self.source_view = self.builder.get_object("source_view")
        self.source_view_controller = SourceViewController(self.source_view)

    def _init_notelist(self):
        log_main.debug("Initializing NoteList components and handlers")
        self.list = self.builder.get_object("list")
        self.list_controller = NoteListController(self.list)

    def shutdown(self, window, event):
        log_main.debug("Main Window Handlers shutdown")
        self.list_controller.shutdown()
        Gtk.main_quit(window, event)

    def synchronize_hb_size_callback(self, widget, allocation):
        if allocation.width != self._hb_synced_width:
            self.side_hb.set_size_request(allocation.width+2, -1)
            # hb_alloc = self.side_hb.get_allocation()
            # hb_alloc.width = allocation.width + 2
            # self.side_hb.set_allocation(hb_alloc)
            self._hb_synced_width = allocation.width
            # TODO: TESTING ONLY: Debug size allocation print statements
            log.debug("Width allocation: Listbox <-> HeaderBar: %d %d",
                         allocation.width, self.side_hb.get_allocation().width)

    def toggle_search(self, toggle_button):
        log.debug("Search button toggled: %s", toggle_button.get_active())
        self.search_bar.set_search_mode(toggle_button.get_active())

    def stop_search(self, search_entry):
        log.debug("Search entry exitted")
        self.search_button.set_active(False)

    def new_note_clicked(self, new_note_button):
        log.debug("New note button clicked")
        note = Note(title="New Note")
        db_session.add(note)
        db_session.commit()
        self.list_controller.select_item(note)

    def delete_note_clicked(self, delete_note_button):
        # TODO: Add target to this when adding menu (original button now used for history popover)
        log.debug("Delete button clicked")
        selected_row = self.list.get_selected_row()
        if selected_row is not None:
            note = selected_row.note
            note.deleted = True
            self.list_controller.select_newer(note)
            db_session.commit()

    def row_activated(self, listbox, row):
        if row is None:
            log.debug("All NoteRows have been deselected")
            self.source_view_controller.activate_note(None)
        else:
            log.debug("NoteRow selected: (%s) '%s'", row.note.note_id, row.note.title)
            self.source_view_controller.activate_note(row.note)

    def toggle_history_popover(self, toggle_button):
        log.debug("History popover toggle button toggled: %s", toggle_button.get_active())
        if toggle_button.get_active() is True:
            log.debug("Building history popover")
            history_popover_builder = Gtk.Builder.new_from_file(get_ui_file("history_popover"))
            history_popover = history_popover_builder.get_object("history_popover")
            history_popover.set_relative_to(toggle_button)
            history_popover.connect("closed", self.history_popover_closed)
            log.debug("Showing history popover")
            history_popover.show_all()

    def history_popover_closed(self, history_popover):
        log.debug("History popover closed")
        self.history_popover_toggle_button.set_active(False)


def get_window():
    log_main.debug("Registering GObject types")
    GObject.type_register(GtkSource.View)
    GObject.type_register(note_row_view.NoteRow)
    log_main.debug("Building Main Window")
    builder = Gtk.Builder.new_from_file(get_ui_file("main_window"))
    handler = Handlers(builder)
    log_main.debug("Binding Main Window Handlers")
    builder.connect_signals(handler)
    window = builder.get_object("main_window")
    window.connect("delete-event", handler.shutdown)
    return window

