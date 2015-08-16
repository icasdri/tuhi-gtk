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
import threading
import time
import copy
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.config import REASON_USER, REASON_SYNC
from tuhi_gtk.util import ignore_all_args_function
from tuhi_gtk.database import kv_store, Note, db_session, note_store
from tuhi_gtk.new_controllers import SubwindowInterfaceController

log = get_log_for_prefix_tuple(("co", "new_note"))

class NewNoteController(SubwindowInterfaceController):
    __gsignals__ = {
        "test_signal": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),
    }
    def do_init(self):
        self.window.register_controller("new_note", self)
        self.window.connect("view-activated", ignore_all_args_function(self.init_after_window_activate))

    def init_after_window_activate(self):
        self.new_note_button = self.window.get_object("new_note_button")
        self.new_note_button.connect("clicked", ignore_all_args_function(self.view_activate))
        self.connect("test_signal", self.process_data)

    def do_view_activate(self):
        log.debug("New note logic activated")
        # self.emit("test_signal", None)
        #self.process_data(None, None)
        thread = threading.Thread(target=self.inside_thread)
        thread.start()

    def inside_thread(self):
        time.sleep(1)
        # GObject.idle_add(lambda: self.emit("test_signal", None))
        data = {"note_id": "7c9f8a53-f350-4e78-8d96-355b9655fb3f", "date_created": 1439701187}
        # self.emit("test_signal", data)
        GObject.idle_add(lambda: self.emit("test_signal", data))

    def process_data(self, sender, data):
        note = note_store.add_new(data)
        self.global_r.emit("note_added", note, REASON_SYNC)
        self.window.current_note = note

