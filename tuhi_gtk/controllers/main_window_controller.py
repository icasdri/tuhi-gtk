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

from gi.repository import GObject, Gtk, GtkSource
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.config import get_ui_file
from tuhi_gtk.controllers.controller import WindowController

log = get_log_for_prefix_tuple(("w", "main"))

class MainWindowController(WindowController):
    def do_init(self):
        log.debug("Registering GObject types for MainWindow")
        GObject.type_register(GtkSource.View)
        log.debug("Building Main Window")
        self.builder = Gtk.Builder.new_from_file(get_ui_file("main_window"))

        self.side_hb = self.get_object("side_hb")
        self._hb_synced_width = 0
        log.debug("Binding Main Window Handlers")
        self.builder.connect_signals(self)
        self.window = self.get_object("main_window")

    def do_init_subcontrollers(self):
        pass

    def do_first_view_activate(self):
        self.fallback_icons()
        self.window.show_all()

    def do_view_activate(self):
        pass

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

    def fallback_icons(self):
        for icon_id in ("icon_new_note",):
            icon = self.builder.get_object(icon_id)
            if not Gtk.IconTheme.get_default().has_icon(icon.props.icon_name):
                icon.props.icon_name = self.builder.get_object(icon_id + "_fallback").props.icon_name
            pass

