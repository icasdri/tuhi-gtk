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

from gi.repository import Gtk, Pango
from tuhi_gtk.new_controllers import SubwindowInterfaceController
from tuhi_gtk.database import kv_store
from tuhi_gtk.config import get_ui_file
from tuhi_gtk.app_logging import get_log_for_prefix_tuple

log = get_log_for_prefix_tuple(("co", "opts"))

DEFAULT_PREFERENCES_VALUES = {
    "SYNCSERVER_URL": "http://test.local/",
    "SYNCSERVER_FINGERPRINT": "11:22:33:44:55:66",
    "SYNCSERVER_USERNAME": "username",
    "SYNCSERVER_PASSWORD": "password",
    "AUTOSAVE_INACTIVITY_INTERVAL": 5,
    "AUTOSAVE_CONTINUOUS_ACTIVITY_INTERVAL": 30,
    "AUTOSYNC_AFTER_SAVE_INTERVAL": 30,
    "EDITOR_USE_CUSTOM_FONT": False,
    "EDITOR_DISPLAY_FONT": "Sans Regular 12",
    "EDITOR_BORDER_WIDTH": 5
}

class OptionsController(SubwindowInterfaceController):
    def do_init(self):
        self.window.register_controller("options", self)
        self.init_default_preferences_in_db()
        self._make_sibling_controllers([
            "OptionsPopoverController"
        ])

    def do_first_view_activate(self):
        self.builder = Gtk.Builder.new_from_file(get_ui_file("options_window"))
        self.builder.connect_signals(self)
        self.get_object("options_window").set_transient_for(self.window.get_object("main_window"))
        self.do_view_activate()

    def do_view_activate(self):
        self.get_object("options_window").show_all()
        self.populate_preferences_from_db()
        self.get_object("options_window").present()

    def option_window_closed(self, window, event):
        self.save_preferences_to_db()
        window.hide()
        return True  # Stop event from propagating

    def editor_use_custom_font_switch_toggled(self, widget, property_object, first_call=False):
        use_custom_font_switch = self.get_object("editor_use_custom_font_switch")
        box = self.get_object("editor_font_selection_box")
        placeholder = self.get_object("editor_font_selection_placeholder")
        font_button = self.get_object("editor_font_selection_button")
        if use_custom_font_switch.props.active is True:
            box.remove(placeholder)
            if not first_call:
                box.add(font_button)
        else:
            box.remove(font_button)
            if not first_call:
                box.add(placeholder)

    def init_default_preferences_in_db(self):
        log.debug("Initializing preferences with default values in database.")
        for pref_name in DEFAULT_PREFERENCES_VALUES:
            if pref_name not in kv_store:
                log.debug("Setting preference %s with defaults.", pref_name)
                kv_store[pref_name] = DEFAULT_PREFERENCES_VALUES[pref_name]

    def populate_preferences_from_db(self):
        log.debug("Populating preferences from database.")
        self.get_object("sync_url_entry").set_text(kv_store["SYNCSERVER_URL"])
        self.get_object("sync_server_fingerprint_entry").set_text(kv_store["SYNCSERVER_FINGERPRINT"])
        self.get_object("sync_username_entry").set_text(kv_store["SYNCSERVER_USERNAME"])
        self.get_object("sync_password_entry").set_text(kv_store["SYNCSERVER_PASSWORD"])
        self.get_object("autosave_inactivity_interval_spinbutton").set_value(float(kv_store["AUTOSAVE_INACTIVITY_INTERVAL"]))
        self.get_object("autosave_continuous_activity_interval_spinbutton").set_value(float(kv_store["AUTOSAVE_CONTINUOUS_ACTIVITY_INTERVAL"]))
        self.get_object("autosync_interval_spinbutton").set_value(float(kv_store["AUTOSYNC_AFTER_SAVE_INTERVAL"]))
        self.get_object("editor_use_custom_font_switch").props.active = kv_store["EDITOR_USE_CUSTOM_FONT"]
        self.get_object("editor_font_selection_button").set_font_name(kv_store["EDITOR_DISPLAY_FONT"])
        self.get_object("editor_border_width_spinbutton").set_value(float(kv_store["EDITOR_BORDER_WIDTH"]))
        self.editor_use_custom_font_switch_toggled(None, None, first_call=True)

    def save_preferences_to_db(self):
        log.debug("Saving preferences to database.")
        kv_store["SYNCSERVER_URL"] = self.get_object("sync_url_entry").get_text()
        kv_store["SYNCSERVER_FINGERPRINT"] = self.get_object("sync_server_fingerprint_entry").get_text()
        kv_store["SYNCSERVER_USERNAME"] = self.get_object("sync_username_entry").get_text()
        kv_store["SYNCSERVER_PASSWORD"] = self.get_object("sync_password_entry").get_text()
        kv_store["AUTOSAVE_INACTIVITY_INTERVAL"] = int(self.get_object("autosave_inactivity_interval_spinbutton").get_value())
        kv_store["AUTOSAVE_CONTINUOUS_ACTIVITY_INTERVAL"] = int(self.get_object("autosave_continuous_activity_interval_spinbutton").get_value())
        kv_store["AUTOSYNC_AFTER_SAVE_INTERVAL"] = int(self.get_object("autosync_interval_spinbutton").get_value())
        kv_store["EDITOR_USE_CUSTOM_FONT"] = self.get_object("editor_use_custom_font_switch").props.active
        kv_store["EDITOR_DISPLAY_FONT"] = self.get_object("editor_font_selection_button").get_font_name()
        kv_store["EDITOR_BORDER_WIDTH"] = int(self.get_object("editor_border_width_spinbutton").get_value())
        self.global_r.emit("preference_changed", "SYNCSERVER_URL")
        self.global_r.emit("preference_changed", "SYNCSERVER_FINGERPRINT")
        self.global_r.emit("preference_changed", "SYNCSERVER_USERNAME")
        self.global_r.emit("preference_changed", "SYNCSERVER_PASSWORD")
        self.global_r.emit("preference_changed", "AUTOSAVE_INACTIVITY_INTERVAL")
        self.global_r.emit("preference_changed", "AUTOSAVE_CONTINUOUS_ACTIVITY_INTERVAL")
        self.global_r.emit("preference_changed", "AUTOSAVE_AFTER_SYNC_INTERVAL")
        self.global_r.emit("preference_changed", "EDITOR_USE_CUSTOM_FONT")
        self.global_r.emit("preference_changed", "EDITOR_DISPLAY_FONT")
        self.global_r.emit("preference_changed", "EDITOR_BORDER_WIDTH")
