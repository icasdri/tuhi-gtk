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

from gi.repository import Gtk, GObject, GtkSource
from tuhi_gtk import note_row_view
from tuhi_gtk.config import get_ui_file

class Handlers:
    def __init__(self, builder):
        self.builder = builder
        self.side_hb = builder.get_object("side_hb")
        self.search_bar = builder.get_object("search_bar")
        self.search_button = builder.get_object("search_button")
        self.list = builder.get_object("list")
        self._hb_synced_width = 0

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


def get_window():
    GObject.type_register(GtkSource.View)
    GObject.type_register(note_row_view.NoteRow)
    builder = Gtk.Builder.new_from_file(get_ui_file("main_window"))
    builder.connect_signals(Handlers(builder))
    from tuhi_gtk.note_row_old_testing import _testing_only_list_elements
    _testing_only_list_elements(builder.get_object("list"), test_spinners=True)
    window = builder.get_object("main_window")
    window.connect("delete-event", Gtk.main_quit)
    return window

