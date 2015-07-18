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

from tuhi_gtk.controllers.list_controller import ModelListController
from tuhi_gtk.database import NoteContent
from tuhi_gtk.history_content_row import HistoryContentRow


class HistoryContentListController(ModelListController):
    log_prefix_tuple = ("co", "hist_c_l")
    list_name = "History Content List"
    controller_name = "History Content List Controller"
    model = NoteContent
    default_query = None

    def __init__(self, list_widget, note):
        self.default_query = NoteContent.query_for_note(note)
        list_widget.set_sort_func(sort_func)
        super(HistoryContentListController, self).__init__(list_widget)

    @staticmethod
    def _item_id(note_content):
        return note_content.note_content_id if note_content is not None else None

    def _create_row(self, note_content):
        hc_row = HistoryContentRow.get_history_content_row(note_content)
        hc_row.show_all()
        return hc_row

def sort_func(a, b):
    return b.note_content.date_created - a.note_content.date_created
