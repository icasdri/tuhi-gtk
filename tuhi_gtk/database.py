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

import os.path
import uuid
import time
from sqlalchemy import create_engine, Column, CHAR, String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.ext.declarative import declarative_base
from tuhi_gtk.config import DATABASE_URI

engine = create_engine(DATABASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()

def init_db():
    Base.metadata.create_all(bind=engine)

def config_database():
    if not os.path.exists(DATABASE_URI):
        init_db()


TYPE_LOOKUP = {
    'int': int
}

# Last synced date field implemented as key-value pair in kv_store :)

class KeyValueStore(object):
    def _get_object(self, key):
        try:
            return KeyValueModel.query.filter_by(key=key).one()
        except NoResultFound:
            raise KeyError(key)

    def __getitem__(self, key):
        obj = self._get_object(key)
        try:
            return TYPE_LOOKUP[obj.type](obj.value)
        except KeyError:
            return obj.value

    def __contains__(self, key):
        try:
            self._get_object(key)
        except KeyError:
            return False
        else:
            return True

    def __setitem__(self, key, value):
        try:
            obj = self._get_object(key)
        except KeyError:
            obj = KeyValueModel(key=key)
        obj.value = str(value)
        obj.type = type(value).__name__
        db_session.add(obj)
        db_session.commit()

    def __delitem__(self, key):
        obj = self._get_object(key)
        db_session.delete(obj)
        db_session.commit()


kv_store = KeyValueStore()

class KeyValueModel(Base):
    __tablename__ = 'kv_store'
    key = Column(String, primary_key=True)
    value = Column(String)
    type = Column(String)


def directly_serialize(model_object, fields):
    result = {}
    for field in fields:
        result[field] = getattr(model_object, field)
    return result


def get_current_date():
    return int(time.time())

def new_uuid():
    return str(uuid.uuid4())


class Note(Base):
    __tablename__ = 'notes'
    note_id = Column(CHAR(36), primary_key=True)
    title = Column(String)
    deleted = Column(Boolean, default=False)
    date_modified = Column(Integer, index=True, onupdate=get_current_date)  # Seconds from epoch
    pushed = Column(Boolean, default=False, index=True)

    def __init__(self, **kwargs):
        self.note_id = new_uuid()
        self.date_modified = get_current_date()
        super(Note, self).__init__(**kwargs)

    def serialize(self):
        return directly_serialize(self, ("note_id", "title", "deleted", "date_modified"))

    def update(self, serialized_dict):
        for field in ("title", "deleted", "date_modified"):
            setattr(self, field, serialized_dict[field])

    @classmethod
    def deserialize(cls, serialized_dict):
        # TODO: safety checks on server response
        return cls(**serialized_dict)


class NoteContent(Base):
    __tablename__ = 'note_contents'
    note_content_id = Column(CHAR(36), primary_key=True)
    note_id = Column(CHAR(36), ForeignKey('notes.note_id'), index=True)
    data = Column(Text)
    date_created = Column(Integer, index=True)  # Seconds from epoch
    pushed = Column(Boolean, default=False, index=True)

    note = relationship("Note")

    def __init__(self, **kwargs):
        self.note_content_id = new_uuid()
        self.date_created = get_current_date()
        super(NoteContent, self).__init__(**kwargs)

    def serialize(self):
        s = directly_serialize(self, ("note_content_id", "data", "date_created"))
        s["note"] = self.note_id
        return s

    @classmethod
    def deserialize(cls, serialized_dict):
        serialized_dict["note_id"] = serialized_dict["note"]
        del serialized_dict["note"]
        return cls(**serialized_dict)
