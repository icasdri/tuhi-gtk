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

from gi.repository import GObject, Gtk, GtkSource
from tuhi_gtk.config import BUFFER_ACTIVITY_CHECKERS_RESOLUTION, REASON_USER
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.util import property_change_function, ignore_all_args_function
from tuhi_gtk.database import db_session, NoteContent, kv_store
from tuhi_gtk.new_controllers import SubwindowInterfaceController

log = get_log_for_prefix_tuple(("co", "srcview"))

class SourceViewController(SubwindowInterfaceController):
    def do_init(self):
        self.window.register_controller("source_view", self)
        self.window.connect("view-activated", ignore_all_args_function(self.view_activate))
        self._make_sibling_controllers([
            "SourceViewCosmeticsController"
        ])

    def do_first_view_activate(self):
        log.debug("View activated for first time")
        self.source_view = self.window.get_object("source_view")
        self.current_note = None
        self.current_note_content = None

        self.checker_id = None
        self.inactivity_count = 0
        self.activity_count = 0
        self.current_buffer = None
        self.window.connect("notify::current-note", property_change_function(self.activate_note))
        self.window.connect("notify::current-note-content", property_change_function(self.activate_note_content))

    def do_shutdown(self):
        self.save_current_note()

    def activate_note(self, note):
        self.save_current_note()

        if note is None:
            self.current_note = None
            if self.checker_id is not None:
                log.debug("Detaching activity + inactivity checker")
                GObject.source_remove(self.checker_id)
            log.debug("Disabling SourceView")
            self.source_view.set_sensitive(False)
            self.source_view.hide()
            return

        log.debug("Activating Note: (%s) '%s'", note.note_id, note.title)
        self.current_note = note

        if self.checker_id is None:
            log.debug("Attaching activity + inactivity checker")
            self.checker_id = GObject.timeout_add(BUFFER_ACTIVITY_CHECKERS_RESOLUTION, self.checker_callback)

        self.source_view.set_sensitive(True)
        self.source_view.show()

    def activate_note_content(self, content):
        if content is not None and content == self.current_note_content:
            return

        log.debug("Activating Note Content: %s", content.note_content_id if content is not None else "None")
        self.current_note_content = content

        if content is not None:
            self.current_buffer = GtkSource.Buffer()
            self.current_buffer.begin_not_undoable_action()
            self.current_buffer.set_text(content.data)
            self.current_buffer.end_not_undoable_action()
        else:
            self.current_buffer = Gtk.TextBuffer()

        self.source_view.set_buffer(self.current_buffer)
        self.current_buffer.connect("changed", self.buffer_changed)

    def buffer_changed(self, buffer):
        self.inactivity_count = 1
        if self.activity_count < 1:
            self.activity_count = 1

    def checker_callback(self):
        # print("Checker Callback: activity %d | inactivity %d" % (self.current.activity_count, self.current.inactivity_count))
        if self.inactivity_count > 0:
            if self.inactivity_count >= kv_store["AUTOSAVE_INACTIVITY_INTERVAL"]:
                self.inactivity_count = 0
                self.activity_count = 0
                self.inactivity_endpoint()
            else:
                self.inactivity_count += 1
        if self.activity_count > 0:
            if self.activity_count >= kv_store["AUTOSAVE_CONTINUOUS_ACTIVITY_INTERVAL"]:
                self.activity_count = 0
                self.inactivity_count = 0
                self.activity_endpoint()
            else:
                self.activity_count += 1
        return True

    def activity_endpoint(self):
        log.info("Detected extended activity on current note: (%s) '%s'",
                 self.current_note.note_id, self.current_note.title)
        self.save_current_note()

    def inactivity_endpoint(self):
        log.info("Detected inactivity on current note: (%s) '%s'",
                 self.current_note.note_id, self.current_note.title)
        self.save_current_note()

    def save_current_note(self):
        log.debug("Logic for save note called, performing validation")
        note = self.current_note
        if note is None:
            return

        old_content = self.current_note_content

        old_data = old_content.data if old_content is not None else ""
        new_data = self.current_buffer.props.text if self.current_buffer is not None else ""

        if new_data != old_data:
            log.info("Saving note: (%s) '%s'", note.note_id, note.title)
            new_content = NoteContent(note=note, data=new_data, type=10000000)
            db_session.add(new_content)
            db_session.commit()

            self.current_note_content = new_content
            self.global_r.emit("note_content_added", self.current_note_content, REASON_USER)
            self.window.current_note_content = self.current_note_content
            # self.global_r.emit("note-saved", note)
