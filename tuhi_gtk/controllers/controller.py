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


NO_AUTO_CALL_DO_VIEW_ACTIVATE = "NO_AUTO_CALL_DO_VIEW_ACTIVATE"

class NewActivatableViewController(GObject.Object):
    __gsignals__ = {
        "view_activated_for_first_time": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        "view_activated": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }
    was_activated_before = False
    builder = None  # Subclasses should override in constructor, if they want get_object proxy to work
    # property_dict = {}
    #
    # def _get_signal_name(self, property_name):
    #     signal_name = "notify_" + property_name
    #     gsignals = getattr(self, "__gsignals__", None)
    #     if gsignals is not None:
    #         if signal_name in gsignals:
    #             return signal_name
    #     return None
    #
    # def __getattr__(self, item):
    #     if item in self.property_dict:
    #         return self.property_dict[item]
    #     elif item != "__gsignals__" and self._get_signal_name(item) is not None:
    #         return None  # Default value for unset but existant properties
    #     else:
    #         raise AttributeError
    #
    # def __setattr__(self, key, value):
    #     signal_name = self._get_signal_name(key)
    #     if signal_name is not None:
    #         self.property_dict[key] = value
    #         self.emit(signal_name, value)
    #         return
    #     super(NewActivatableViewController, self).__setattr__(key, value)

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


class WindowController(NewActivatableViewController):
    def __init__(self, global_registrar):
        self.global_r = global_registrar
        self.global_r.instance_register(self)
        self.subcontrollers = {}
        self.do_init()
        self.do_init_subcontrollers()

    def do_init(self):
        pass

    def do_init_subcontrollers(self):
        pass

    def shutdown(self):
        for controller in self.subcontrollers:
            controller.shutdown()
        super(WindowController, self).shutdown()

    def register_controller(self, name, controller):
        self.subcontrollers[name] = controller

    def get_controller(self, name):
        return self.subcontrollers[name]


class SubwindowInterfaceController(NewActivatableViewController):
    def __init__(self, window_controller):
        self.window = window_controller
        self.global_r = self.window.global_r
        self.global_r.instance_register(self)
        self.do_init()

    def do_init(self):
        pass

