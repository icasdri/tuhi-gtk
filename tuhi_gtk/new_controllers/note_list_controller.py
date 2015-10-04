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

from tuhi_gtk.config import REASON_SYNC, \
    SYNC_ACTION_BEGIN, SYNC_ACTION_FAILURE, SYNC_ACTION_SUCCESS
from tuhi_gtk.app_logging import get_log_for_prefix_tuple
from tuhi_gtk.util import ignore_all_args_function, ignore_sender_function, property_change_function
from tuhi_gtk.database import note_notonserver_tracker, note_content_notonserver_tracker, kv_store, Note
from tuhi_gtk.new_controllers import SubwindowInterfaceController
from tuhi_gtk.note_row_view import NoteRow
from tuhi_gtk.new_controllers.list_controller_mixin import ListControllerMixin

log = get_log_for_prefix_tuple(("co", "note_l"))

class NoteListController(SubwindowInterfaceController, ListControllerMixin):
    def do_init(self):
        self.window.register_controller("note_list", self)
        self.window.connect("view-activated", ignore_all_args_function(self.view_activate))

    def do_first_view_activate(self):
        self.list = self.window.get_object("list")
        self.list.set_sort_func(sort_func)
        ListControllerMixin.__init__(self, self.list, self._create_row, lambda x: x.note_id, Note.non_deleted())
        self.global_r.connect("note-added", ignore_sender_function(self.handle_new_note))
        #self.global_r.connect("note-content-added", ignore_sender_function(self.handle_new_note_content))
        self.initial_populate()
        for note in note_notonserver_tracker.get_all():
            row = self.get_row(note)
            if row is not None:
                row.show_feature("unsynced_emblem")
        for note_content in note_content_notonserver_tracker.get_all():
            row = self.get_row(note_content.note)
            if row is not None:
                row.show_feature("unsynced_emblem")
        self.list.connect("row-selected", ignore_sender_function(self.row_selected_callback))
        self.window.connect("notify::current-note", property_change_function(self.handle_window_current_note_change))
        self.global_r.connect("note-metadata-changed", ignore_sender_function(self.handle_note_metadata_change))
        self.global_r.sync_control.connect("sync-action-for-note", ignore_sender_function(self.handle_sync_action_for_note))
        last_note_selected = None
        if "LAST_NOTE_SELECTED" in kv_store:
            last_note_selected = Note.query.filter(Note.note_id == kv_store["LAST_NOTE_SELECTED"]).first()
        if last_note_selected is None:
            last_note_selected = Note.non_deleted().order_by(Note.date_content_modified.desc()).first()
        log.debug("Selecting last note selected")
        self.select_item(last_note_selected)

    def handle_sync_action_for_note(self, note, sync_action):
        log.debug("Recieved Note Sync Action: %s", note.note_id)
        row = self.get_row(note)
        if row is not None:
            if sync_action == SYNC_ACTION_BEGIN:
                row.show_feature("spinner")
            elif sync_action == SYNC_ACTION_SUCCESS:
                row.hide_feature("spinner")
                row.hide_feature("unsynced_emblem")
            elif sync_action == SYNC_ACTION_FAILURE:
                row.show_feature("failure_label")

    def handle_window_current_note_change(self, note):
        if self.list.get_selected_row() != note:
            self.select_item(note)
        row = self.get_row(note)
        if row is not None:
            row.hide_feature("synced_in_emblem")

    def handle_note_metadata_change(self, note, reason):
        if note is not None:
            if note.type > 0:
                self.add_item(note)  # if not already added (e.g. newly restored note)
                row = self.get_row(note)
                if reason == REASON_SYNC:
                    row.show_feature("synced_in_emblem")
                else:
                    row.show_feature("unsynced_emblem")
                row.refresh()
            else:  # note.type < 0 (including perma delete!)
                self.remove_item(note)

    def handle_new_note(self, note, reason):
        self.handle_note_metadata_change(note, reason)

    def row_selected_callback(self, row):
        if row is None:
            self.window.current_note = None
        else:
            self.window.current_note = row.note
            content = row.note.get_head_content()
            self.window.current_note_content = content

    def do_shutdown(self):
        selected_note_row = self.list.get_selected_row()
        if selected_note_row is None:
            if "LAST_NOTE_SELECTED" in kv_store:
                log.debug("Clearing LAST_NOTE_SELECTED")
                del kv_store["LAST_NOTE_SELECTED"]
        else:
            log.debug("Setting LAST_NOTE_SELECTED: (%s): %s",
                         selected_note_row.note.note_id, selected_note_row.note.title)
            kv_store["LAST_NOTE_SELECTED"] = selected_note_row.note.note_id

    def _create_row(self, note):
        noterow = NoteRow.get_note_row(note)
        noterow.show_all()
        return noterow

    def select_newer(self, note):
        target_note = Note.non_deleted().filter(Note.date_content_modified > note.date_content_modified) \
                                        .filter(Note.note_id != note.note_id) \
                                        .order_by(Note.date_content_modified.asc()) \
                                        .first()
        if target_note is None:
            target_note = Note.non_deleted().filter(Note.date_content_modified <= note.date_content_modified) \
                                            .filter(Note.note_id != note.note_id) \
                                            .order_by(Note.date_content_modified.desc()) \
                                            .first()
        self.select_item(target_note)

def sort_func(a, b):
    return b.note.date_content_modified - a.note.date_content_modified