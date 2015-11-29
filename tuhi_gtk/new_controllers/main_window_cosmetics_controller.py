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

from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.util import ignore_all_args_function, ignore_sender_function
from tuhi_gtk.new_controllers import SubwindowInterfaceController

log = get_log_for_prefix_tuple(("ui", "main_w"))

class MainWindowCosmeticsController(SubwindowInterfaceController):
    def do_init(self):
        self.window.register_controller("main_window_cosmetics", self)
        self.window.connect("view-activated", ignore_all_args_function(self.view_activate))

    def do_first_view_activate(self):
        log.debug("Falling back icons that are note available")
        log.debug("Keeping sizes in sync")
        self.side_hb = self.window.get_object("side_hb")
        self.side_hb.props.width_request = self.window.get_object("hb_sizes_box").get_allocated_width()
        self._hb_synced_width = 0
        self.window.get_object("hb_sizes_box").connect("size-allocate", ignore_sender_function(self.synchronize_hb_size_callback))

    def synchronize_hb_size_callback(self, allocation):
        if allocation.width != self._hb_synced_width:
            self.side_hb.set_size_request(allocation.width+2, -1)
            self._hb_synced_width = allocation.width
            # TODO: TESTING ONLY: Debug size allocation print statements
            log.debug("Width allocation: Listbox <-> HeaderBar: %d %d",
                      allocation.width, self.side_hb.get_allocation().width)

