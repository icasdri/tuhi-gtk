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

from gi.repository import Gtk
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.config import get_ui_file, SYNC_FAILURE_FATAL, SYNC_FAILURE_CONNECTION, \
    SYNC_FAILURE_AUTHENTICATION, SYNC_FAILURE_FINGERPRINT
from tuhi_gtk.database import kv_store
from tuhi_gtk.util import ignore_all_args_function, ignore_sender_function
from tuhi_gtk.controllers import SubwindowInterfaceController
from tuhi_gtk.sync_dialogs_view import AuthenticationSyncDialog, ConnectionSyncDialog, FatalSyncDialog, FingerprintSyncDialog

log = get_log_for_prefix_tuple(("co", "sync_dialogs"))

TYPE_FORM_MAPPING = {
    SYNC_FAILURE_FATAL: ("Fatal Sync Error", "Details...", FatalSyncDialog),
    SYNC_FAILURE_CONNECTION: ("Connection Error", "Details...", ConnectionSyncDialog),
    SYNC_FAILURE_AUTHENTICATION: ("Authentication Error", "Options...", AuthenticationSyncDialog),
    SYNC_FAILURE_FINGERPRINT: ("Fingerprint Error", "Options...", FingerprintSyncDialog)
}

class StateHolder:
    failure_type = None
    extra = None


class SyncDialogsController(SubwindowInterfaceController):
    def do_init(self):
        self.window.register_controller("sync_dialogs", self)
        self.window.connect("view-activated", ignore_all_args_function(self.init_after_window_activate))

    def init_after_window_activate(self):
        self.global_r.sync_control.connect("global_sync_action", ignore_sender_function(self.handle_global_sync_action))
        self.global_r.sync_control.connect("sync_failure", ignore_sender_function(self.handle_sync_failure))
        self.window_object = self.window.get_object("main_window")
        self.dialogs_builder = None
        self.state = StateHolder()
        # dialog = Gtk.MessageDialog(self.window_object, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Hahahaha")
        # dialog.format_secondary_text("I am laughing at you. At you! HAHAHAH!")
        # dialog.show()

    def do_first_view_activate(self):
        self.builder = Gtk.Builder.new_from_file(get_ui_file("sync_error_bar"))
        self.get_object("error_bar_action").connect("clicked", self.error_bar_action_handler)

    def do_view_activate(self):
        # Activates error bar dropdown thingy
        title, button_label, _ = TYPE_FORM_MAPPING[self.state.failure_type]
        self.get_object("error_bar_text").set_label(title)
        self.get_object("error_bar_action").set_label(button_label)
        bar = self.get_object("error_bar")
        self.window.get_object("hb_sizes_box").pack_start(bar, expand=False, fill=False, padding=0)
        bar.show_all()
        pass

    def error_bar_action_handler(self, button):
        # Dispatch and display the appropriate dialog (retrieving the appropriate instance from the view module)
        self.get_object("error_bar").hide()
        self.window.get_controller("sync_button").show_feature("normal_icon")
        _, _, dialog_class = TYPE_FORM_MAPPING[self.state.failure_type]
        dialog = dialog_class.get_instance(controller=self, transient_for=self.window_object)
        dialog.show_dialog()

    def handle_global_sync_action(self, sync_action, by_who):
        pass

    def handle_sync_failure(self, failure_type, by_who, extra):
        self.state = StateHolder()
        self.state.failure_type = failure_type
        self.state.extra = extra
        self.view_activate()
