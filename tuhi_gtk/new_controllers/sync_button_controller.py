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
from tuhi_gtk.util import ignore_all_args_function
from tuhi_gtk.new_controllers import SubwindowInterfaceController

log = get_log_for_prefix_tuple(("co", "sync_button"))

class SyncButtonController(SubwindowInterfaceController):
    def do_init(self):
        self.window.register_controller("sync_button", self)
        self.window.connect("view-activated", ignore_all_args_function(self.init_after_window_activate))

    def init_after_window_activate(self):
        self.sync_button = self.window.get_object("sync_button")
        self.sync_button.connect("clicked", ignore_all_args_function(self.view_activate))

    def do_view_activate(self):
        log.debug("Sync logic activated")
        self.global_r.sync_control.sync()

