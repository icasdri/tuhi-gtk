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

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class NoteContent(Base):
    __tablename__ = 'content'
    id = Column(String, primary_key=True)
    data = Column(String, nullable=False)


class Note(Base):
    __tablename__ = 'note'
    id = Column(String, primary_key=True)
    title = Column(String)  # Dynamically set from NoteContent's first line, cached here
    content = Column(String, ForeignKey('content.id'))
    # def __init__(self, title=None):
    #     self.title = title
    #     self.data = ""


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
