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

from gi.repository import GObject
import importlib
from tuhi_gtk.util import underscore_camelcase

NO_AUTO_CALL_DO_VIEW_ACTIVATE = "NO_AUTO_CALL_DO_VIEW_ACTIVATE"

class ActivatableViewController(GObject.Object):
    __gsignals__ = {
        "view_activated_for_first_time": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        "view_activated": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }
    was_activated_before = False
    builder = None  # Subclasses should override in constructor, if they want get_object proxy to work

    def view_activate(self):
        if not self.was_activated_before:
            first_view_activate_result = self.do_first_view_activate()
            self.emit("view_activated_for_first_time")
            self.was_activated_before = True
            if first_view_activate_result != NO_AUTO_CALL_DO_VIEW_ACTIVATE:
                self.do_view_activate()
                self.emit("view_activated")
        else:
            self.do_view_activate()
            self.emit("view_activated")

    def do_first_view_activate(self):
        # Initialize your own builder and widgets here (this may change to adding to a passed-in builder)
        # Or if you have nothing to initialize. Leave this unimplemented.

        # return NO_AUTO_CALL_DO_VIEW_ACTIVATE to not have do_view_activate called afterwards.
        pass

    def do_view_activate(self):
        pass

    def shutdown(self):
        self.do_shutdown()

    def do_shutdown(self):
        pass

    def get_object(self, object_id):
        return self.builder.get_object(object_id)


def _make_subwindow_interface_controller(name, window):
    module_path = "." + underscore_camelcase(name)
    getattr(importlib.import_module(module_path, __name__), name)(window)


class WindowController(ActivatableViewController):
    def __init__(self, global_registrar):
        self.global_r = global_registrar
        self.global_r.instance_register(self)
        self.subcontrollers = {}
        self.do_init()

    def do_init(self):
        pass

    def _make_subcontrollers(self, controller_name_list):
        for controller_name in controller_name_list:
            _make_subwindow_interface_controller(controller_name, self)

    def shutdown(self):
        for controller in self.subcontrollers.values():
            controller.shutdown()
        super(WindowController, self).shutdown()

    def register_controller(self, name, controller):
        self.subcontrollers[name] = controller

    def get_controller(self, name):
        return self.subcontrollers[name]


class SubwindowInterfaceController(ActivatableViewController):
    def __init__(self, window_controller):
        self.window = window_controller
        self.global_r = self.window.global_r
        self.global_r.instance_register(self)
        self.do_init()

    def do_init(self):
        pass

    def _make_sibling_controllers(self, controller_name_list):
        for controller_name in controller_name_list:
            _make_subwindow_interface_controller(controller_name, self.window)


