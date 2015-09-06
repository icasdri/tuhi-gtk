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
    def __init__(self, liststore, columns, default_query, item_id_func):
        self.__liststore = liststore
        self.__columns = columns  # Column mapping list. List of functions in column positions to pass in item to get value.
        self.__default_query = default_query
        self.__item_id_func = item_id_func
        self.__lookup_it = {}
        self.__lookup_item = {}

    def initial_populate(self):
        for item in self.__default_query.all():
            self.add_item(item)

    def __get_it(self, item):
        return self.__lookup_it[self.__item_id_func(item)]

    def get_item(self, it):
        return self.__lookup_item[it.stamp]

    def add_item(self, item):
        values = list(map(lambda x: x(item), self.__columns))
        it = self.__liststore.append(values)
        self.__lookup_it[self.__item_id_func(item)] = it
        self.__lookup_item[it.stamp] = item

    def remove_item(self, item):
        it = self.__get_it(item)
        self.__liststore.remove(it)
        del self.__lookup_it[self.__item_id_func(item)]
        del self.__lookup_item[it.stamp]

    def refresh_item(self, item):
        it = self.__get_it(item)
        for col, val in enumerate(self.__columns):
            self.__liststore.set_value(it, col, val(item))

