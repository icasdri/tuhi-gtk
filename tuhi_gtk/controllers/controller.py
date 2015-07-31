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

from gi.repository import GObject
from tuhi_gtk.app_logging import LogInjectedObject

class Controller(LogInjectedObject):
    log_prefix_tuple = ("co",)

    def startup(self):
        pass

    def set_intercontroller_dependency(self):
        pass

    def shutdown(self):
        pass


class ActivatableViewController(Controller):
    was_activated_before = False

    def view_activate(self):
        if not self.was_activated_before:
            self.do_first_view_activate()
            self.was_activated_before = True
        else:
            self.do_view_activate()

    def do_first_view_activate(self):
        # Initialize your own builder and widgets here (this may change to adding to a passed-in builder)
        # Or if you have nothing to initialize. Leave this unimplemented.
        self.do_view_activate()

    def do_view_activate(self):
        pass


class NewActivatableViewController(GObject.Object):
    was_activated_before = False
    builder = None  # Subclasses should override in constructor, if they want get_object proxy to work

    def view_activate(self):
        if not self.was_activated_before:
            self.do_first_view_activate()
            self.was_activated_before = True
        else:
            self.do_view_activate()

    def do_first_view_activate(self):
        # Initialize your own builder and widgets here (this may change to adding to a passed-in builder)
        # Or if you have nothing to initialize. Leave this unimplemented.
        self.do_view_activate()

    def do_view_activate(self):
        pass

    def get_object(self, object_id):
        return self.builder.get_object(object_id)


class WindowController(NewActivatableViewController):
    def __init__(self, global_registrar):
        self.global_r = global_registrar
        self.subcontrollers = {}
        self.do_init()

    def do_init(self):
        pass

    def register_controller(self, name, controller):
        self.subcontrollers[name] = controller

    def get_controller(self, name):
        return self.subcontrollers[name]


class SubwindowInterfaceController(NewActivatableViewController):
    def __init__(self, window_controller):
        self.window = window_controller
        self.global_r = self.window.global_r
        self.do_init()

    def do_init(self):
        pass

