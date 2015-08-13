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

class ListControllerMixin(object):
    list_name = "Base List"
    controller_name = "Base List Controller"
    model = None
    default_query = None

    def __init__(self):
        self.lookup = {}

    def initial_populate(self):
        for note in self.default_query.all():
            self.add_item(note)

    @staticmethod
    def _item_id(item):
        return item.id

    def _create_row(self, item):
        return None

    def _get_row(self, item):
        item_id = self._item_id(item)
        if item_id is None:
            return None
        if item_id in self.lookup:
            row = self.lookup[item_id]
        else:
            row = self._create_row(item)
            self.lookup[item_id] = row
        return row

    def add_item(self, item):
        row = self._get_row(item)
        if row not in self.list:
            self.list.add(row)

    def remove_item(self, item):
        row = self._get_row(item)
        # self.list.remove(item)
        row.destroy()
        del self.lookup[self._item_id(item)]

    def refresh_item(self, item):
        row = self._get_row(item)
        row.refresh()

    def select_item(self, item):
        row = self._get_row(item)
        self.list.select_row(row)

