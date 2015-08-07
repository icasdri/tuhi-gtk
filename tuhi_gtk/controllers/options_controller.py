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
from tuhi_gtk.controllers.controller import ActivatableViewController
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

class OptionsController(ActivatableViewController):
    def __init__(self, main_window, source_view):
        self.main_window = main_window
        self.source_view = source_view
        self.current_editor_display_font_name = None
        self.init_default_preferences_in_db()
        self.apply_preferences()

    def do_first_view_activate(self):
        self.builder = Gtk.Builder.new_from_file(get_ui_file("options_window"))
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("options_window")
        self.window.set_transient_for(self.main_window)
        self.do_view_activate()

    def do_view_activate(self):
        self.window.show_all()
        self.populate_preferences_from_db()
        self.window.present()

    def option_window_closed(self, window, event):
        self.save_preferences_to_db()
        self.apply_preferences()
        window.hide()
        return True  # Stop event from propagating

    def editor_use_custom_font_switch_toggled(self, widget, property_object, first_call=False):
        use_custom_font_switch = self.builder.get_object("editor_use_custom_font_switch")
        box = self.builder.get_object("editor_font_selection_box")
        placeholder = self.builder.get_object("editor_font_selection_placeholder")
        font_button = self.builder.get_object("editor_font_selection_button")
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
        self.builder.get_object("sync_url_entry").set_text(kv_store["SYNCSERVER_URL"])
        self.builder.get_object("sync_server_fingerprint_entry").set_text(kv_store["SYNCSERVER_FINGERPRINT"])
        self.builder.get_object("sync_username_entry").set_text(kv_store["SYNCSERVER_USERNAME"])
        self.builder.get_object("sync_password_entry").set_text(kv_store["SYNCSERVER_PASSWORD"])
        self.builder.get_object("autosave_inactivity_interval_spinbutton").set_value(float(kv_store["AUTOSAVE_INACTIVITY_INTERVAL"]))
        self.builder.get_object("autosave_continuous_activity_interval_spinbutton").set_value(float(kv_store["AUTOSAVE_CONTINUOUS_ACTIVITY_INTERVAL"]))
        self.builder.get_object("autosync_interval_spinbutton").set_value(float(kv_store["AUTOSYNC_AFTER_SAVE_INTERVAL"]))
        self.builder.get_object("editor_use_custom_font_switch").props.active = kv_store["EDITOR_USE_CUSTOM_FONT"]
        self.builder.get_object("editor_font_selection_button").set_font_name(kv_store["EDITOR_DISPLAY_FONT"])
        self.builder.get_object("editor_border_width_spinbutton").set_value(float(kv_store["EDITOR_BORDER_WIDTH"]))
        self.editor_use_custom_font_switch_toggled(None, None, first_call=True)

    def save_preferences_to_db(self):
        log.debug("Saving preferences to database.")
        kv_store["SYNCSERVER_URL"] = self.builder.get_object("sync_url_entry").get_text()
        kv_store["SYNCSERVER_FINGERPRINT"] = self.builder.get_object("sync_server_fingerprint_entry").get_text()
        kv_store["SYNCSERVER_USERNAME"] = self.builder.get_object("sync_username_entry").get_text()
        kv_store["SYNCSERVER_PASSWORD"] = self.builder.get_object("sync_password_entry").get_text()
        kv_store["AUTOSAVE_INACTIVITY_INTERVAL"] = int(self.builder.get_object("autosave_inactivity_interval_spinbutton").get_value())
        kv_store["AUTOSAVE_CONTINUOUS_ACTIVITY_INTERVAL"] = int(self.builder.get_object("autosave_continuous_activity_interval_spinbutton").get_value())
        kv_store["AUTOSYNC_AFTER_SAVE_INTERVAL"] = int(self.builder.get_object("autosync_interval_spinbutton").get_value())
        kv_store["EDITOR_USE_CUSTOM_FONT"] = self.builder.get_object("editor_use_custom_font_switch").props.active
        kv_store["EDITOR_DISPLAY_FONT"] = self.builder.get_object("editor_font_selection_button").get_font_name()
        kv_store["EDITOR_BORDER_WIDTH"] = int(self.builder.get_object("editor_border_width_spinbutton").get_value())

    def apply_preferences(self):
        if kv_store["EDITOR_USE_CUSTOM_FONT"]:
            font_name = kv_store["EDITOR_DISPLAY_FONT"]
            if font_name != self.current_editor_display_font_name:
                font_description = Pango.FontDescription(font_name)
                self.source_view.override_font(font_description)
                self.current_editor_display_font_name = font_name
        else:
            self.current_editor_display_font_name = None
            self.source_view.override_font(None)
        self.source_view.set_border_width(kv_store["EDITOR_BORDER_WIDTH"])
