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


from sqlalchemy import event
from tuhi_gtk.database import db_session
from tuhi_gtk.controllers.controller import Controller

class ModelListController(Controller):
    list_name = "Base List"
    controller_name = "Base List Controller"
    model = None
    default_query = None

    def __init__(self, list_widget):
        super(ModelListController, self).__init__()
        self.log.info("Initializing %s", self.controller_name)
        self.list = list_widget
        self.lookup = {}
        event.listen(db_session, "before_commit", self._db_changed_callback)

    def startup(self):
        self.log.info("%s startup", self.controller_name)
        self.initial_populate()

    def shutdown(self):
        self.log.debug("%s shutdown", self.controller_name)

    def initial_populate(self):
        self.log.info("Populating %s", self.list_name)
        for note in self.default_query.all():
            self.add_item(note)

    def db_new(self, item):
        self.add_item(item)

    def db_deleted(self, item):
        self.remove_item(item)

    def db_dirty(self, item):
        self.refresh_item(item)

    def _db_changed_callback(self, session):
        for obj in session.new:
            if isinstance(obj, self.model):
                self.db_new(obj)
        for obj in session.deleted:
            if isinstance(obj, self.model):
                self.db_deleted(obj)
        for obj in session.dirty:
            if isinstance(obj, self.model):
                self.db_dirty(obj)

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

    def _select_item(self, item):
        row = self._get_row(item)
        self.list.select_row(row)

