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
from tuhi_gtk.database import Note


class TreeListStoreControllerMixin(object):
    def __init__(self, liststore, columns, default_query):
        self.__liststore = liststore
        # Column mapping list. List of functions in column positions to pass in item to get value.
        # First column must be "item_id" column, which is unique for all rows as this column will be used internally
        # as the key to the mapping between item <-> iter
        self.__columns = columns
        self.__default_query = default_query
        self.__item_id_func = self.__columns[0]
        # Internal mapping of item_id <-> (item, iter)
        self.__lookup = {}

    def initial_populate(self):
        for item in self.__default_query.all():
            self.add_item(item)

    def get_treeiter(self, item):
        return self.__lookup[self.__item_id_func(item)][1]

    def get_item(self, it):
        return self.__lookup[self.__liststore.get_value(it, 0)][0]

    def add_item(self, item):
        if item is None:
            return
        item_id = self.__item_id_func(item)
        if item_id not in self.__lookup:
            values = list(map(lambda x: x(item), self.__columns))
            it = self.__liststore.append(values)
            self.__lookup[item_id] = (item, it)

    def remove_item(self, item):
        if item is None:
            return
        item_id = self.__item_id_func(item)
        if item_id in self.__lookup:
            it = self.get_treeiter(item)
            self.__liststore.remove(it)
            del self.__lookup[item_id]

    def refresh_item(self, item):
        it = self.get_treeiter(item)
        for col, val in enumerate(self.__columns):
            self.__liststore.set_value(it, col, val(item))

