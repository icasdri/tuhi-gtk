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
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.config import SYNC_ACTION_BEGIN, SYNC_ACTION_SUCCESS, SYNC_ACTION_FAILURE, EMBLEM_SHOW_TIMEOUT, \
    SYNC_BY_USER
from tuhi_gtk.util import ignore_all_args_function, ignore_sender_function
from tuhi_gtk.controllers import SubwindowInterfaceController
from tuhi_gtk.feature_view_mixin import FeatureViewMixin

log = get_log_for_prefix_tuple(("co", "sync_button"))

FEATURES = {
    "normal_icon": ("icon_sync_notes", None, None),
    "failed_icon": ("icon_sync_notes_failed", None, None),
    "success_icon": ("icon_sync_notes_success", None, None),
    "spinner": ("sync_button_spinner", lambda w: w.start(), lambda w: w.stop()),
}

class SyncButtonController(SubwindowInterfaceController, FeatureViewMixin):
    def do_init(self):
        self.window.register_controller("sync_button", self)
        self.window.connect("view-activated", ignore_all_args_function(self.init_after_window_activate))

    def init_after_window_activate(self):
        self.normal_icon_reinstate_timeout_source = None
        FeatureViewMixin.__init__(self, FEATURES, self.window.get_object("sync_button_box"), self.window)
        self.show_feature("normal_icon")
        self.sync_button = self.window.get_object("sync_button")
        self.sync_button.connect("clicked", ignore_all_args_function(self.view_activate))
        self.global_r.sync_control.connect("global_sync_action", ignore_sender_function(self.handle_global_sync_action))

    def do_view_activate(self):
        log.debug("Sync logic activated")
        self.global_r.sync_control.sync(SYNC_BY_USER)

    def handle_global_sync_action(self, action, _):
        if action == SYNC_ACTION_BEGIN:
            self.show_feature("spinner")
            self.sync_button.set_sensitive(False)
        elif action == SYNC_ACTION_SUCCESS:
            self.show_feature("success_icon")
            self.normal_icon_reinstate_timeout_source = GObject.timeout_add(EMBLEM_SHOW_TIMEOUT, ignore_all_args_function(self.reinstate_normal_icon_callback))
            self.sync_button.set_sensitive(True)
        elif action == SYNC_ACTION_FAILURE:
            if self.normal_icon_reinstate_timeout_source is not None:
                GObject.source_remove(self.normal_icon_reinstate_timeout_source)
            self.show_feature("failed_icon")
            self.sync_button.set_sensitive(True)

    def reinstate_normal_icon_callback(self):
        self.normal_icon_reinstate_timeout_source = None
        self.show_feature("normal_icon")
