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
from tuhi_gtk.config import get_ui_file
from tuhi_gtk.database import Note, db_session
from tuhi_gtk.list_controller import sort_func, NoteListController
from tuhi_gtk.note_row_view import NoteRow


class Handlers:
    def __init__(self, builder):
        self.builder = builder
        self.side_hb = builder.get_object("side_hb")
        self.search_bar = builder.get_object("search_bar")
        self.search_button = builder.get_object("search_button")
        self.source_view = builder.get_object("source_view")
        self._hb_synced_width = 0
        self._init_list()

    def _init_list(self):
        self.list = self.builder.get_object("list")
        self.list_controller = NoteListController(self.list, self.source_view)
        self.list.set_sort_func(sort_func)

    def synchronize_hb_size_callback(self, widget, allocation):
        if allocation.width != self._hb_synced_width:
            self.side_hb.set_size_request(allocation.width+2, -1)
            # hb_alloc = self.side_hb.get_allocation()
            # hb_alloc.width = allocation.width + 2
            # self.side_hb.set_allocation(hb_alloc)
            self._hb_synced_width = allocation.width
            # TODO: TESTING ONLY: Debug size allocation print statements
            print(allocation.width, self.side_hb.get_allocation().width)

    def toggle_search(self, toggle_button):
        self.search_bar.set_search_mode(toggle_button.get_active())

    def stop_search(self, search_entry):
        self.search_button.set_active(False)

    def new_note_clicked(self, new_note_button):
        # TODO: Testing Only
        note = Note(title="New Note")
        db_session.add(note)
        db_session.commit()
        self.list_controller.select_note(note)

    def delete_note_clicked(self, delete_note_button):
        # TODO: Testing Only
        x = Note.query.filter(Note.deleted == False).filter(Note.title == "The Tester Note").first()
        if x is not None:
            x.deleted = True
            x.register_change()
            db_session.commit()

    def row_activated(self, listbox, row):
        self.list_controller.activate_note(row.note)


main_list = None

def get_window():
    GObject.type_register(GtkSource.View)
    GObject.type_register(note_row_view.NoteRow)
    builder = Gtk.Builder.new_from_file(get_ui_file("main_window"))
    builder.connect_signals(Handlers(builder))
    window = builder.get_object("main_window")
    window.connect("delete-event", Gtk.main_quit)
    return window

