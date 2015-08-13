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
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound, FlushError
from sqlalchemy.ext.declarative import declarative_base
from tuhi_gtk.config import DATABASE_URI, DATABASE_PATH
from tuhi_gtk.app_logging import get_log_for_prefix_tuple

log = get_log_for_prefix_tuple(("db",))

log.info("Initializing database engine")
engine = create_engine(DATABASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()

def init_db():
    Base.metadata.create_all(bind=engine)

def config_database():
    # TODO: Sanity checks on trackers (make sure targets references still exists, etc.)
    if not os.path.exists(DATABASE_PATH):
        log.info("Creating database %s", DATABASE_URI)
        init_db()
    else:
        for note in Note.non_deleted().all():
            log.debug("Recalculating date_content_modified for: (%s) '%s'", note.note_id, note.title)
            note.refresh_title()
            # note.get_head_content()


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

# x = 22
#
# def get_date_ignore_pushed(context):
#     print(dir(context))
#     print(context.result_column_struct)
#     print(context.returning_cols)
#     # print(context.result())
#     print(context.current_parameters)
#     global x
#     x = context
#     c = context.current_parameters
#     if "pushed" in c and c["pushed"] in (True, False):
#         pass
#     else:
#         return get_current_date()

class Note(Base):
    __tablename__ = 'notes'
    note_id = Column(CHAR(36), primary_key=True)
    title = Column(String)
    # Use a NoteContent with type = deleted
    deleted = Column(Boolean, default=False)
    date_modified = Column(Integer, index=True, nullable=False)  # Seconds from epoch
    date_content_modified = Column(Integer, index=True, nullable=False)  # Seconds from epoch

    def __init__(self, external=False, **kwargs):
        if not external:
            self.note_id = new_uuid()
            self.date_modified = get_current_date()
            self.date_content_modified = get_current_date()
            note_notonserver_tracker.register(self)
        super(Note, self).__init__(**kwargs)

    def register_change(self):
        # Call this when making a change to this Note
        self.date_modified = get_current_date()
        note_change_tracker.register(self)

    def serialize(self):
        return directly_serialize(self, ("note_id", "deleted", "date_modified"))

    def update(self, serialized_dict):
        for field in ("title", "deleted", "date_modified"):
            setattr(self, field, serialized_dict[field])

    def get_head_content(self):
        note_content = NoteContent.query.filter(NoteContent.note_id == self.note_id) \
                                  .order_by(NoteContent.date_created.desc()) \
                                  .first()
        if note_content is not None:
            if self.date_content_modified < note_content.date_created:
                self.date_content_modified = note_content.date_created
            self.deleted = note_content.type in (NC_TYPE_TRASHED, NC_TYPE_PERMA_DELETE)
            db_session.commit()
        return note_content

    def refresh_title(self):
        log.debug("Refreshing Title for: (%s) '%s'", self.note_id, self.title)
        content = self.get_head_content()
        if content is not None:
            new_title = content.get_title()
            if new_title.strip() == "":
                self.title = "Untitled Note"
            elif self.title != new_title:
                self.title = new_title
                db_session.commit()
            return new_title, content
        return self.title, content

    @classmethod
    def deserialize(cls, serialized_dict):
        # TODO: safety checks on server response
        return cls(external=True, **serialized_dict)

    def __hash__(self):
        return hash(self.note_id)

    @classmethod
    def non_deleted(cls):
        return cls.query.filter(Note.deleted == False)


NC_TYPE_PERMA_DELETE = -2
NC_TYPE_TRASHED = -10000000
NC_TYPE_PLAIN = 10000000

class NoteContent(Base):
    __tablename__ = 'note_contents'
    note_content_id = Column(CHAR(36), primary_key=True)
    note_id = Column(CHAR(36), ForeignKey('notes.note_id'), index=True)
    type = Column(Integer)  # used currently for deletion flags
    data = Column(Text)
    date_created = Column(Integer, index=True, default=get_current_date)  # Seconds from epoch

    note = relationship("Note")

    def __init__(self, external=False, **kwargs):
        if not external:
            self.note_content_id = new_uuid()
            self.date_created = get_current_date()
            note_content_notonserver_tracker.register(self)
        super(NoteContent, self).__init__(**kwargs)

    def get_title(self):
        return self.data.partition("\n")[0]

    def serialize(self):
        s = directly_serialize(self, ("note_content_id", "data", "date_created"))
        s["note"] = self.note_id
        return s

    @classmethod
    def deserialize(cls, serialized_dict):
        serialized_dict["note_id"] = serialized_dict["note"]
        del serialized_dict["note"]
        return cls(external=True, **serialized_dict)

    @classmethod
    def query_for_note(cls, note):
        return cls.query.filter(NoteContent.note_id == note.note_id)

### STORES ###

class Store(object):
    model = None
    pk_name = None

    def add_new(self, new_item):
        if isinstance(new_item, self.model):
            m = new_item
        else:
            m = self.model.deserialize(new_item)
        db_session.add(m)
        db_session.commit()
        return m

    def rename_to_new_uuid(self, old):
        new_id = new_uuid()
        while new_id in self:
            new_id = new_uuid()
        if isinstance(old, self.model):
            target = old
        else:
            target = self.get(old)
        old_id = getattr(target, self.pk_name)
        setattr(target, self.pk_name, new_id)
        db_session.commit()
        return old_id, new_id

    def update(self, item, serialized_data):
        item.update(serialized_data)
        db_session.commit()

    def get(self, id_or_serialized):
        if isinstance(id_or_serialized, dict):
            id = id_or_serialized[self.pk_name]
        else:
            id = id_or_serialized

        try:
            return self.model.query.filter(getattr(self.model, self.pk_name) == id).one()
        except NoResultFound:
            return None

    def __contains__(self, item):
        if isinstance(item, self.model):
            item = getattr(item, self.pk_name)
        return self.get(item) is not None

class NoteStore(Store):
    model = Note
    pk_name = "note_id"

class NoteContentStore(Store):
    model = NoteContent
    pk_name = "note_content_id"


note_store = NoteStore()
note_content_store = NoteContentStore()


### TRACKERS ###

class NoteChangeTrackingModel(Base):
    __tablename__ = "note_change_tracking"
    note_id = Column(CHAR(36), ForeignKey("notes.note_id"), primary_key=True)


class NoteNotOnServerTrackingModel(Base):
    __tablename__ = "note_notonserver_tracking"
    note_id = Column(CHAR(36), ForeignKey("notes.note_id"), primary_key=True)


class NoteContentNotOnServerTrackingModel(Base):
    __tablename__ = "note_content_notonserver_tracking"
    note_content_id = Column(CHAR(36), ForeignKey("note_contents.note_content_id"), primary_key=True)


class Tracker(object):
    model = None
    tracking_model = None
    pk_name = "pk"

    def register(self, note):
        if note not in self:
            t = self.tracking_model()
            setattr(t, self.pk_name, getattr(note, self.pk_name))
            try:
                db_session.add(t)
                db_session.commit()
            except FlushError:  # This should not happen anymore. But just in case.
                db_session.rollback()

    def get_all_as_query(self):
        return self.model.query.join(self.tracking_model)

    def get_all(self):
        return self.get_all_as_query().all()

    def discard(self, depr):
        tracking_depr = self._get(depr)
        db_session.delete(tracking_depr)
        db_session.commmit()

    def discard_successes(self, successes):
        self.tracking_model.query.filter(getattr(self.tracking_model, self.pk_name).in_(successes)).delete()
        db_session.commit()

    def discard_all_but_failures(self, failures):
        self.tracking_model.query.filter(getattr(self.tracking_model, self.pk_name).notin_(failures))\
                                 .delete(synchronize_session='fetch')
        db_session.commit()

    def discard_all(self):
        self.tracking_model.query.delete()
        db_session.commit()

    def register_rename(self, old_id, new_id):
        setattr(self._get(old_id), self.pk_name, new_id)
        db_session.commit()

    def _get(self, item):
        if isinstance(item, self.model):
            pk = getattr(item, self.pk_name)
        else:
            pk = item
        try:
            return self.tracking_model.query.filter(getattr(self.tracking_model, self.pk_name) == pk).one()
        except NoResultFound:
            return None

    def __contains__(self, item):
        return self._get(item) is not None


class NoteChangeTracker(Tracker):
    model = Note
    tracking_model = NoteChangeTrackingModel
    pk_name = "note_id"

class NoteNotOnServerTracker(Tracker):
    model = Note
    tracking_model = NoteNotOnServerTrackingModel
    pk_name = "note_id"

class NoteContentNotOnServerTracker(Tracker):
    model = NoteContent
    tracking_model = NoteContentNotOnServerTrackingModel
    pk_name = "note_content_id"

note_change_tracker = NoteChangeTracker()
note_notonserver_tracker = NoteNotOnServerTracker()
note_content_notonserver_tracker = NoteContentNotOnServerTracker()