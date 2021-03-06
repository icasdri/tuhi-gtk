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

import sys
from gi.repository import Gtk
from tuhi_gtk.config import set_directories, config_directories
from tuhi_gtk.app_logging import get_log_for_prefix_tuple

log = get_log_for_prefix_tuple(("main",))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        set_directories(sys.argv[1], None)
    config_directories()

    from tuhi_gtk.database import config_database
    from tuhi_gtk.global_registrar import GlobalRegistrar
    from tuhi_gtk.controllers.main_window_controller import MainWindowController
    config_database()
    global_r = GlobalRegistrar()
    main_window_controller = MainWindowController(global_r)
    main_window_controller.view_activate()
    log.info("Entering Gtk main loop")
    Gtk.main()

