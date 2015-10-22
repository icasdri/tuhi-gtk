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
from tuhi_gtk.config import get_ui_file, SYNC_FAILURE_FATAL, SYNC_FAILURE_CONNECTION, \
    SYNC_FAILURE_AUTHENTICATION, SYNC_FAILURE_FINGERPRINT
from tuhi_gtk.database import kv_store
from tuhi_gtk.util import ignore_all_args_function, ignore_sender_function
from tuhi_gtk.new_controllers import SubwindowInterfaceController

log = get_log_for_prefix_tuple(("co", "sync_dialogs"))

TYPE_FORM_MAPPING = {
    SYNC_FAILURE_FATAL: ("Fatal Sync Error", "Details..."),
    SYNC_FAILURE_CONNECTION: ("Connection Error", "Details..."),
    SYNC_FAILURE_AUTHENTICATION: ("Authentication Error", "Options..."),
    SYNC_FAILURE_FINGERPRINT: ("Fingerprint Error", "Options...")
}

class SyncDialogsStateHolder:
    failure_type = None
    message = None


class SyncDialogsController(SubwindowInterfaceController):
    def do_init(self):
        self.window.register_controller("sync_dialogs", self)
        self.window.connect("view-activated", ignore_all_args_function(self.init_after_window_activate))

    def init_after_window_activate(self):
        self.global_r.sync_control.connect("global_sync_action", ignore_sender_function(self.handle_global_sync_action))
        self.global_r.sync_control.connect("sync_failure", ignore_sender_function(self.handle_sync_failure))
        self.window_object = self.window.get_object("main_window")
        self.state = SyncDialogsStateHolder()
        # dialog = Gtk.MessageDialog(self.window_object, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Hahahaha")
        # dialog.format_secondary_text("I am laughing at you. At you! HAHAHAH!")
        # dialog.show()

    def do_first_view_activate(self):
        self.builder = Gtk.Builder.new_from_file(get_ui_file("sync_dialogs"))
        self.get_object("error_bar_action").connect("clicked", self.error_bar_action_handler_intermediary)

    def view_activate(self):
        # Activates error bar dropdown thingy
        title, button_label = TYPE_FORM_MAPPING[self.state.failure_type]
        self.get_object("error_bar_text").set_label(title)
        self.get_object("error_bar_action").set_label(button_label)
        bar = self.get_object("error_bar")
        self.window.get_object("hb_sizes_box").pack_start(bar, expand=False, fill=False, padding=0)
        bar.show_all()
        pass

    def error_bar_action_handler_intermediary(self, button):
        self.error_bar_action_handler(button)

    def handle_global_sync_action(self, sync_action, by_who):
        pass

    def handle_sync_failure(self, failure_type, by_who, extra):
        self.state.failure_type = failure_type

        if failure_type == SYNC_FAILURE_FATAL:
            message = extra
        elif failure_type == SYNC_FAILURE_CONNECTION:
            e, sync_url = extra
            message = "Could not connect to the server at {}.\n{}.".format(sync_url, e)
        elif failure_type == SYNC_FAILURE_AUTHENTICATION:
            sync_url = ""  # TODO: pull from extras
            message = "The server at {} rejected our login credentials.".format(sync_url)
        elif failure_type == SYNC_FAILURE_FINGERPRINT:
            title = "Fingerprint Error"
            e, observed_fingerprint = extra
            if "SERVER_FINGERPRINT" in kv_store:
                message = "The server is presenting an untrusted certificate with fingerprint {}, " \
                          "which does NOT match the trusted fingerprint {}.\n" \
                          "You should only trust this certificate if you are expecting a different certificate or server.\n\n" \
                          "".format(observed_fingerprint, kv_store["SERVER_FINGERPRINT"])
            else:
                message = "The server is presenting a certificate with fingerprint {}.\n" \
                          "You should only trust this certificate if you are absolutely " \
                          "certain it's fingerprint matches that of your server." \
                          "".format(observed_fingerprint)
        else:
            return

        self.state.message = message
        self.view_activate()


    def push_infobar(self, message, button_text):
        pass


class Dialog(Gtk.Dialog):
    pass