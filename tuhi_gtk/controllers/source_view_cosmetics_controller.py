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

from gi.repository import Pango
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.util import ignore_all_args_function, ignore_sender_function
from tuhi_gtk.database import kv_store
from tuhi_gtk.controllers import SubwindowInterfaceController

log = get_log_for_prefix_tuple(("ui", "srcview"))

class SourceViewCosmeticsController(SubwindowInterfaceController):
    def do_init(self):
        self.window.register_controller("source_view_cosmetics", self)
        self.window.connect("view-activated", ignore_all_args_function(self.view_activate))

    def do_first_view_activate(self):
        log.debug("Tracking source view cosmetic preferences")
        self.source_view = self.window.get_object("source_view")
        self.current_editor_display_font_name = None
        self.handle_preference_changed("EDITOR_DISPLAY_FONT")
        self.handle_preference_changed("EDITOR_BORDER_WIDTH")
        self.global_r.connect("preference_changed", ignore_sender_function(self.handle_preference_changed))

    def handle_preference_changed(self, preference_name):
        if preference_name in ("EDITOR_USE_CUSTOM_FONT", "EDITOR_DISPLAY_FONT"):
            if kv_store["EDITOR_USE_CUSTOM_FONT"]:
                font_name = kv_store["EDITOR_DISPLAY_FONT"]
                if font_name != self.current_editor_display_font_name:
                    font_description = Pango.FontDescription(font_name)
                    self.source_view.override_font(font_description)
                    self.current_editor_display_font_name = font_name
            else:
                self.current_editor_display_font_name = None
                self.source_view.override_font(None)
        elif preference_name == "EDITOR_BORDER_WIDTH":
            self.source_view.set_border_width(kv_store["EDITOR_BORDER_WIDTH"])

