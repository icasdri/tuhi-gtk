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

from gi.repository import GObject, Gtk

class GlobalRegistrar(GObject.Object):
    __gsignals__ = {
        "preference_changed": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        "note_added": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        "note_content_added": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        "note_state_changed": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        "note_edited": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        "note_saved": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        "note_sync_begin": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        "note_sync_success": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        "note_sync_failed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))
    }

    def __init__(self):
        GObject.Object.__init__(self)
        GObject.type_register(type(self))


class TestTestTest:
    def __init__(self, global_r):
        self.global_r = global_r
        self.window = Gtk.Window()
        self.window.props.title = "My Window"
        self.window.set_default_size(50, 50)
        self.button = Gtk.Button()
        self.button.props.label = "Click Me!"
        self.button.connect("clicked", self.button_clicked)
        self.window.add(self.button)
        self.window.show_all()

    def button_clicked(self, *pos, **kwargs):
        print("Button clicked!")
        self.global_r.emit("note_sync_begin", "my-special-note-id")


class SuperSuperTest:
    def __init__(self, global_r):
        self.global_r = global_r
        self.global_r.connect("note_sync_begin", self.sync_began)

    def sync_began(self, dafu, note_id):
        print(dafu)
        print("Sync has begun for note: ", note_id)

if __name__ == "__main__":
    global_r = GlobalRegistrar()
    TestTestTest(global_r)
    SuperSuperTest(global_r)
    Gtk.main()
