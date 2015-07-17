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
from datetime import datetime
from gi.repository import Gtk
from tuhi_gtk.config import get_ui_file


class HistoryContentListController(object):
    def __init__(self, history_popover_box):
        self.history_popover_box = history_popover_box
        self.history_content_list = None
        self.history_content_lookup = None
        self.current_note = None

    def load_note(self, note):
        if note == self.current_note:
            return

        if self.history_content_list is not None:
            self.history_popover_box.remove(self.history_content_list)

        self.history_content_list = get_history_content_list()
        self.history_content_list.show_all()
        self.history_popover_box.add(self.history_content_list)

        self.initial_populate()

    def initial_populate(self):
        pass

    def add_note_content(self, note_content):
        pass

    def remove_note_content(self, note_content):
        pass

    def refresh_note_content(self, note_content):
        pass


class HistoryContentRow(Gtk.ListBoxRow):
    def initialize(self, builder, note_content):
        self.builder = builder
        self.label = builder.get_object("label")
        self.note_content = note_content
        self.refresh()

    @staticmethod
    def get_history_content_row(note_content):
        builder = Gtk.Builder.new_from_file(get_ui_file("history_content_row"))
        history_content_row = builder.get_object("history_content_row")
        history_content_row.initialize(builder, note_content)
        return history_content_row

    def refresh(self):
        self.label.set_text(datetime.fromtimestamp(self.note_content.date_created).strftime("%b %d, %I:%m %p"))


def get_history_content_list():
    builder = Gtk.Builder.new_from_file(get_ui_file("history_content_list"))
    return builder.get_object("history_content_list")