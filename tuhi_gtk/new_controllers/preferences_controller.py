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
from tuhi_gtk.new_controllers import SubwindowInterfaceController
from tuhi_gtk.database import kv_store
from tuhi_gtk.config import get_ui_file
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.util import ignore_all_args_function

log = get_log_for_prefix_tuple(("co", "prefs"))

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

# dict mapping preference name -> (ui_object_id, setter_name, getter_name, native_type, wanted_type)
RENDER_RELATIONSHIPS = {
    "SYNCSERVER_URL": ("sync_url_entry", "set_text", "get_text", None, None),
    "SYNCSERVER_FINGERPRINT": ("sync_server_fingerprint_entry", "set_text", "get_text", None, None),
    "SYNCSERVER_USERNAME": ("sync_username_entry", "set_text", "get_text", None, None),
    "SYNCSERVER_PASSWORD": ("sync_password_entry", "set_text", "get_text", None, None),
    "AUTOSAVE_INACTIVITY_INTERVAL": ("autosave_inactivity_interval_spinbutton", "set_value", "get_value", float, int),
    "AUTOSAVE_CONTINUOUS_ACTIVITY_INTERVAL": ("autosave_continuous_activity_interval_spinbutton", "set_value", "get_value", float, int),
    "AUTOSYNC_AFTER_SAVE_INTERVAL": ("autosync_interval_spinbutton", "set_value", "get_value", float, int),
    "EDITOR_USE_CUSTOM_FONT": ("editor_use_custom_font_switch", "props.active", "props.active", None, None),
    "EDITOR_DISPLAY_FONT": ("editor_font_selection_button", "set_font_name", "get_font_name", None, None),
    "EDITOR_BORDER_WIDTH": ("editor_border_width_spinbutton", "set_value", "get_value", float, int)
}

class PreferencesController(SubwindowInterfaceController):
    def do_init(self):
        self.window.register_controller("preferences", self)
        self.init_default_preferences_in_db()
        self.window.get_controller("options_popover").connect("view_activated_for_first_time",
                                                              ignore_all_args_function(self.init_after_popover_first_activate))

    def init_after_popover_first_activate(self):
        self.window.get_controller("options_popover") \
            .get_object("preferences_button").connect("clicked", ignore_all_args_function(self.view_activate))

    def do_first_view_activate(self):
        self.builder = Gtk.Builder.new_from_file(get_ui_file("preferences_window"))
        self.builder.connect_signals(self)
        self.get_object("preferences_window").set_transient_for(self.window.get_object("main_window"))
        self.do_view_activate()

    def do_view_activate(self):
        self.get_object("preferences_window").show_all()
        self.populate_preferences_from_db()
        self.get_object("preferences_window").present()

    def preferences_window_closed(self, window, _):
        self.save_preferences_to_db()
        window.hide()
        return True  # Stop event from propagating

    def editor_use_custom_font_switch_toggled(self, *_, first_call=False):
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

    def _ui_set(self, pref, val):
        ui_object_id, setter_name, _, native_type, _ = RENDER_RELATIONSHIPS[pref]
        target_val = native_type(val) if native_type is not None else val
        ui_object = self.get_object(ui_object_id)
        if setter_name.startswith("props."):
            setattr(ui_object.props, setter_name.split(".")[1], target_val)
        else:
            getattr(ui_object, setter_name)(target_val)

    def _ui_get(self, pref):
        ui_object_id, _, getter_name, _, wanted_type = RENDER_RELATIONSHIPS[pref]
        ui_object = self.get_object(ui_object_id)

        sens = ui_object.get_sensitive()
        if sens is True:
            ui_object.set_sensitive(False)

        if getter_name.startswith("props."):
            raw_val = getattr(ui_object.props, getter_name.split(".")[1])
        else:
            raw_val = getattr(ui_object, getter_name)()

        if sens is True:
            ui_object.set_sensitive(True)
        return wanted_type(raw_val) if wanted_type is not None else raw_val

    def init_default_preferences_in_db(self):
        log.debug("Initializing preferences with default values in database.")
        for pref_name in DEFAULT_PREFERENCES_VALUES:
            if pref_name not in kv_store:
                log.debug("Setting preference %s with defaults.", pref_name)
                kv_store[pref_name] = DEFAULT_PREFERENCES_VALUES[pref_name]

    def populate_preferences_from_db(self):
        log.debug("Populating preferences from database.")
        for pref in RENDER_RELATIONSHIPS:
            self._ui_set(pref, kv_store[pref])
        self.editor_use_custom_font_switch_toggled(None, None, first_call=True)

    def save_preferences_to_db(self):
        log.debug("Saving preferences to database.")
        for pref in RENDER_RELATIONSHIPS:
            kv_store[pref] = self._ui_get(pref)
        for pref in RENDER_RELATIONSHIPS:
            self.global_r.emit("preference_changed", pref)
