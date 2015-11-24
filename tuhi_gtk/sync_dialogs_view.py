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

from gi.repository import Gtk
from tuhi_gtk.config import get_ui_file
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.util import hide_window_on_delete

log = get_log_for_prefix_tuple(("ui", "sync_dialogs"))

class SyncDialog(Gtk.MessageDialog):
    ui_builder_file_name = None  # need to be set by subclasses
    built_root_name = None  # need to be set by subclasses
    builder = None
    instance = None

    def initialize(self, controller):  # subclasses should override to do their initialization
        pass

    def show_dialog(self):
        self.show_all()

    @classmethod
    def get_instance(cls, controller, transient_for=None):
        if cls.builder is None:
            cls.builder = Gtk.Builder.new_from_file(get_ui_file("sync_dialogs/" + cls.ui_builder_file_name))
            cls.instance = cls.builder.get_object(cls.built_root_name)
            cls.instance.connect("delete-event", hide_window_on_delete)
        if transient_for is not None:
            cls.instance.set_transient_for(transient_for)
        cls.instance.initialize(controller)
        return cls.instance


class AuthenticationSyncDialog(SyncDialog):
    ui_builder_file_name = "dialog_authentication"
    built_root_name = "authentication_sync_dialog"


class ConnectionSyncDialog(SyncDialog):
    ui_builder_file_name = "dialog_connection"
    built_root_name = "connection_sync_dialog"


class FatalSyncDialog(SyncDialog):
    ui_builder_file_name = "dialog_fatal"
    built_root_name = "fatal_sync_dialog"


class FingerprintSyncDialog(SyncDialog):
    ui_builder_file_name = "dialog_fingerprint"
    built_root_name = "fingerprint_sync_dialog"
