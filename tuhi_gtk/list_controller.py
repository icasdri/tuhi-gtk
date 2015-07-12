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

from gi.repository import Gtk, GObject
from sqlalchemy import event
from tuhi_gtk.config import log, BUFFER_ACTIVITY_TIMEOUT, BUFFER_ACTIVITY_TARGET_COUNT
from tuhi_gtk.database import db_session, kv_store, Note, NoteContent
from tuhi_gtk.note_row_view import NoteRow


class CurrentStateContainer(object):
    note = None
    inactivity_count = 0
    activity_checker_id = None


class NoteListController(object):
    def __init__(self, main_list, source_view):
        self.current = CurrentStateContainer()
        self.list = main_list
        self.source_view = source_view
        self.note_set = set()
        self.noterow_lookup = {}
        self.initial_populate()
        event.listen(db_session, "before_commit", self.db_changed)

    def initial_populate(self):
        for note in Note.non_deleted().all():
            self.add_note(note)
        last_note_selected = None
        if "LAST_NOTE_SELECTED" in kv_store:
            last_note_selected = Note.query.filter(Note.note_id == kv_store["LAST_NOTE_SELECTED"]).first()
        if last_note_selected is None:
            last_note_selected = Note.non_deleted().order_by(Note.date_content_modified.desc()).first()
        self.select_note(last_note_selected)

    def shutdown(self):
        log.co.debug("List Controller shutdown")
        selected_note_row = self.list.get_selected_row()
        if selected_note_row is None:
            if "LAST_NOTE_SELECTED" in kv_store:
                log.co.debug("Clearing LAST_NOTE_SELECTED")
                del kv_store["LAST_NOTE_SELECTED"]
        else:
            log.co.debug("Setting LAST_NOTE_SELECTED: (%s): %s",
                         selected_note_row.note.note_id, selected_note_row.note.title)
            kv_store["LAST_NOTE_SELECTED"] = selected_note_row.note.note_id

    def db_changed(self, session):
        log.db.debug("Commit: session.new %s; session.deleted %s; session.dirty %s",
                     session.new, session.deleted, session.dirty)
        for obj in session.new:
            if isinstance(obj, Note):
                self.add_note(obj)
        for obj in session.deleted:
            if isinstance(obj, Note):
                self.remove_note(obj)
        for obj in session.dirty:
            if isinstance(obj, Note):
                if obj.deleted is True:
                    self.remove_note(obj)
                else:
                    self.refresh_note(obj)

    def _noterow(self, note):
        if note is None:
            return None
        if note.note_id in self.noterow_lookup:
            noterow = self.noterow_lookup[note.note_id]
        else:
            noterow = NoteRow.get_note_row(note)
            self.noterow_lookup[note.note_id] = noterow
        noterow.show_all()
        return noterow

    def add_note(self, note):
        noterow = self._noterow(note)
        if noterow not in self.list:
            self.list.add(noterow)
            self._refresh_list()

    def remove_note(self, note):
        noterow = self._noterow(note)
        # self.list.remove(noterow)
        noterow.destroy()
        del self.noterow_lookup[note.note_id]
        self._refresh_list()

    def refresh_note(self, note):
        noterow = self._noterow(note)
        noterow.refresh()
        self._refresh_list()

    def _refresh_list(self):
        pass
        # The below causes exit code 139 for some reason, segfault in kernel logs
        # self.list.invalidate_sort()
        # self.list.invalidate_filter()

    def select_note(self, note):
        noterow = self._noterow(note)
        self.list.select_row(noterow)
        self.activate_note(note)

    def select_newer(self, note):
        target_note = Note.non_deleted().filter(Note.date_content_modified > note.date_content_modified) \
                                        .order_by(Note.date_content_modified.asc()) \
                                        .first()
        if target_note is None:
            target_note = Note.non_deleted().filter(Note.date_content_modified < note.date_content_modified) \
                                            .order_by(Note.date_content_modified.desc()) \
                                            .first()
        self.select_note(target_note)

    def activate_note(self, note):
        if note is None:
            self.current.note = None
            if self.current.activity_checker_id is not None:
                log.co.debug("Detaching activity checker")
                GObject.source_remove(self.current.activity_checker_id)
            log.ui.debug("Disabling SourceView")
            self.source_view.set_sensitive(False)
            self.source_view.hide()
            return

        if self.current.activity_checker_id is None:
            log.co.debug("Attaching activity checker")
            self.current.activity_checker_id = GObject.timeout_add(BUFFER_ACTIVITY_TIMEOUT, self.activity_checker_callback)

        self.current.note = note
        self.source_view.set_sensitive(True)
        self.source_view.show()
        log.co.debug("Activating Note: (%s): '%s'", note.note_id, note.title)
        content = NoteContent.query.filter(NoteContent.note_id == note.note_id) \
                                   .order_by(NoteContent.date_created.desc()) \
                                   .first()
        if content is not None:
            self.buffer = Gtk.TextBuffer(text=content.data)
        else:
            self.buffer = Gtk.TextBuffer()

        self.source_view.set_buffer(self.buffer)
        self.buffer.connect("changed", self.buffer_changed)

    def buffer_changed(self, buffer):
        self.current.inactivity_count = 1
        print("Buffer changed!")

    def activity_checker_callback(self):
        print("Activty Checker Callback %d" % self.current.inactivity_count)
        if self.current.inactivity_count > 0:
            if self.current.inactivity_count >= BUFFER_ACTIVITY_TARGET_COUNT:
                self.current.inactivity_count = 0
                self.inactivity_endpoint()
            else:
                self.current.inactivity_count += 1
        return True

    def inactivity_endpoint(self):
        print("INACTIVITY: current note: %s" % self.current.note)
        pass


def sort_func(a, b):
    return b.note.date_content_modified - a.note.date_content_modified