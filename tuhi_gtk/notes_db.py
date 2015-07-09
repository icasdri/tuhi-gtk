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

from sqlalchemy import create_engine, Column, CHAR, String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///../test.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()

def init_db():
    Base.metadata.create_all(bind=engine)


class Note(Base):
    __tablename__ = 'notes'
    note_id = Column(CHAR(36), primary_key=True)
    title = Column(String)
    deleted = Column(Boolean, default=False)
    date_modified = Column(Integer, index=True)  # Seconds from epoch
    def __init__(self, title):
        self.title = title


class NoteContent(Base):
    __tablename__ = 'note_contents'
    note_content_id = Column(CHAR(36), primary_key=True)
    note_id = Column(CHAR(36), ForeignKey('notes.note_id'), index=True)
    data = Column(Text)
    date_created = Column(Integer, index=True)  # Seconds from epoch

# TODO: Last synced date field (global or per Note/NoteContent?

class NotesDB:
    def __init__(self, db_url, server_url):
        # TODO: TESTING ONLY: fake note data
        fake_note_data = [
            "Test Note", "My little pony", "Canes Chicken",
            "Test Note 2", "Random Crap", "Welcome to Tuhi",
            "More Stuff", "Cool things!", "Blah blah blah",
            "Untitled", "Some cool note", "My not-so-little pony",
            "More and more stuff", "Hello world", "The language",
            "Blah blah blah blah blah blah blah blah blah"
        ]
        self.notes = {i: Note(j) for i, j in enumerate(fake_note_data)}

    def get_note(self, note_id):
        return self.notes[note_id]

def db():
    return global_instance

def init_global_instance(*args, **kwargs):
    global global_instance
    global_instance = NotesDB(*args, **kwargs)

global_instance = None
