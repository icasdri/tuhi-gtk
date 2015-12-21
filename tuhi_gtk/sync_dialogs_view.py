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
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.config import get_ui_file, SYNC_BY_USER
from tuhi_gtk.database import kv_store
from tuhi_gtk.util import hide_window_on_delete, populate_rendered_view_from, save_rendered_view_to

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


class PrefBasedSyncDialog(SyncDialog):
    render_relationships = None # need to be set by subclasses

    def initialize(self, controller):
        self.controller = controller

    def show_dialog(self):
        populate_rendered_view_from(kv_store, self.render_relationships, self.builder)
        self.builder.connect_signals(self)
        self.show_all()

    def cancel_button_clicked(self, _):
        self.hide()

    def preferences_button_clicked(self, _):
        self.hide()
        self.controller.window.get_controller("preferences").view_activate()

    def retry_button_clicked(self, _):
        save_rendered_view_to(kv_store, self.render_relationships, self.builder, global_r=self.controller.global_r)
        self.hide()
        self.controller.global_r.sync_control.sync(SYNC_BY_USER)


class AuthenticationSyncDialog(PrefBasedSyncDialog):
    ui_builder_file_name = "dialog_authentication"
    built_root_name = "authentication_sync_dialog"
    render_relationships = {
        "SYNCSERVER_USERNAME": ("sync_username_entry", "set_text", "get_text", None, None),
        "SYNCSERVER_PASSWORD": ("sync_password_entry", "set_text", "get_text", None, None)
    }


class ConnectionSyncDialog(PrefBasedSyncDialog):
    ui_builder_file_name = "dialog_connection"
    built_root_name = "connection_sync_dialog"
    render_relationships = {
        "SYNCSERVER_URL": ("sync_url_entry", "set_text", "get_text", None, None)
    }


class FatalSyncDialog(SyncDialog):
    ui_builder_file_name = "dialog_fatal"
    built_root_name = "fatal_sync_dialog"

    def initialize(self, controller):
        self.message_text = "The following fatal error was encountered during sync:\n\n{}'{}'\n\n{}".format(
            6*" ", controller.state.extra,
            "This is likely a bug or an issue with the sync server's configuration. Please retry sync.")

    def show_dialog(self):
        self.builder.connect_signals(self)
        self.props.secondary_text = self.message_text
        self.show_all()

    def close_button_clicked(self, _):
        self.hide()

    def retry_button_clicked(self, _):
        self.hide()
        self.controller.global_r.sync_control.sync(SYNC_BY_USER)


class FingerprintSyncDialog(SyncDialog):
    ui_builder_file_name = "dialog_fingerprint"
    built_root_name = "fingerprint_sync_dialog"
