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
from gi.repository import GObject, Gtk
from tuhi_gtk.config import BUFFER_ACTIVITY_CHECKERS_RESOLUTION, BUFFER_ACTIVITY_TARGET_COUNT, \
    BUFFER_INACTIVITY_TARGET_COUNT, USE_SESSION_BASED_AUTOSAVE, SESSION_TIMEOUT
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.database import db_session, NoteContent

log = get_log_for_prefix_tuple(("co", "srcview"))

class SourceViewController(object):
    def __init__(self, source_view):
        self.source_view = source_view

        self.checker_id = None
        self.inactivity_count = 0
        self.activity_count = 0

        self.current_note = None
        self.current_buffer = None

        self.session_timed_out = False
        self.session_contents = set()
        GObject.timeout_add(SESSION_TIMEOUT, self.session_timeout_callback)

    def set_intercontroller_dependency(self, list_controller):
        # This method should be called as close to __init__ as possible
        log.debug("Source View Controller - Intercontroller Dependencies Set")
        self.list_controller = list_controller

    def startup(self):
        log.info("Starting up Source View")
        pass

    def shutdown(self):
        self.save_current_note()

    def activate_note(self, note):
        self.save_current_note()

        if note is None:
            self.current_note = None
            if self.checker_id is not None:
                log.debug("Detaching activity + inactivity checker")
                GObject.source_remove(self.checker_id)
            log.ui.debug("Disabling SourceView")
            self.source_view.set_sensitive(False)
            self.source_view.hide()
            return

        if self.checker_id is None:
            log.debug("Attaching activity + inactivity checker")
            self.checker_id = GObject.timeout_add(BUFFER_ACTIVITY_CHECKERS_RESOLUTION, self.checker_callback)

        self.current_note = note
        self.source_view.set_sensitive(True)
        self.source_view.show()
        log.debug("Activating Note: (%s) '%s'", note.note_id, note.title)
        content = note.get_head_content()
        if content is not None:
            self.current_buffer = Gtk.TextBuffer(text=content.data)
        else:
            self.current_buffer = Gtk.TextBuffer()

        self.source_view.set_buffer(self.current_buffer)
        self.current_buffer.connect("changed", self.buffer_changed)

    def buffer_changed(self, buffer):
        self.inactivity_count = 1
        if self.activity_count < 1:
            self.activity_count = 1

    def session_timeout_callback(self):
        log.info("Session has timed out")
        self.session_timed_out = True
        return True

    def checker_callback(self):
        # print("Checker Callback: activity %d | inactivity %d" % (self.current.activity_count, self.current.inactivity_count))
        if self.inactivity_count > 0:
            if self.inactivity_count >= BUFFER_INACTIVITY_TARGET_COUNT:
                self.inactivity_count = 0
                self.activity_count = 0
                self.inactivity_endpoint()
            else:
                self.inactivity_count += 1
        if self.activity_count > 0:
            if self.activity_count >= BUFFER_ACTIVITY_TARGET_COUNT:
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
        if not USE_SESSION_BASED_AUTOSAVE or self.session_timed_out:
            log.info("Resolving timed out session")
            self.session_contents.clear()

        note = self.current_note
        if note is None:
            return

        old_content = note.get_head_content()

        old_data = old_content.data if old_content is not None else ""
        new_data = self.current_buffer.props.text

        if new_data != old_data:
            log.info("Saving note: (%s) '%s'", note.note_id, note.title)
            if old_content is None or old_content.note_content_id not in self.session_contents:
                new_content = NoteContent(note=note, data=new_data)
                db_session.add(new_content)
                db_session.commit()
            else:
                old_content.data = new_data
                db_session.commit()

            note.get_head_content()
            self.list_controller.mark_note(note, "saved")

        if old_content is not None and old_content.note_content_id not in self.session_contents:
            self.session_contents.add(old_content.note_content_id)