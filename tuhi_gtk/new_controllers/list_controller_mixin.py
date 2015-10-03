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
    def __init__(self, listbox, row_creation_func, item_id_func, default_query):
        self.__lookup = {}
        self.__listbox = listbox
        self.__create_row = row_creation_func
        self.__item_id = lambda x: item_id_func(x) if x is not None else None
        self.__default_query = default_query

    def initial_populate(self):
        for item in self.__default_query.all():
            self.add_item(item)

    def get_row(self, item):
        return self.__lookup.get(self.__item_id(item), None)

    def add_item(self, item):
        item_id = self.__item_id(item)
        if item_id is not None and item_id not in self.__lookup:
            row = self.__create_row(item)
            self.__lookup[item_id] = row
            self.__listbox.add(row)

    def remove_item(self, item):
        row = self.get_row(item)
        if row is not None:
            row.destroy()
            del self.__lookup[self.__item_id(item)]

    def select_item(self, item):
        if item is None:
            self.__listbox.select_row(None)
        else:
            row = self.get_row(item)
            if row is not None:
                self.__listbox.select_row(row)

