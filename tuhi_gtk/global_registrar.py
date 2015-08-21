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
from tuhi_gtk.sync_control import SyncControl
from tuhi_gtk.util import ignore_sender_function
from tuhi_gtk.app_logging import get_log_for_prefix_tuple

log = get_log_for_prefix_tuple(("global_r",))

class GlobalRegistrar(GObject.Object):
    __gsignals__ = {
        "preference_changed": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),

        "note_added": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, GObject.TYPE_STRING)),
        # Reasons: user, sync
        "note_content_added": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, GObject.TYPE_STRING)),
        # Reasons: user, sync
        "note_metadata_changed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, GObject.TYPE_STRING)),
        # Metadata signal fired from logic here as a response to note_content_added signals

        "application_shutdown": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))
    }

    def __init__(self):
        GObject.Object.__init__(self)
        GObject.type_register(type(self))
        self.connect("application_shutdown", ignore_sender_function(self.application_shutdown))
        self.connect("note_content_added", ignore_sender_function(self.handle_note_content_added))
        # event.listen(db_session, "before_commit", self._db_changed_callback)
        self.conroller_types = set()

        self.sync_control = SyncControl(self)

    def handle_note_content_added(self, note_content, reason):
        # Emit a note_metadata_changed signal if necessary
        if note_content is not None:
            note = note_content.note
            if note_content.date_created >= note.date_content_modified:
                if note_content.date_created > note.date_content_modified:
                    #log.warn("The creator of a new note content was not diligent enough to refresh note metadata. Doing that now.")
                    note.refresh_metadata()
                log.debug("Firing a note_metadata_change signal")
                self.emit("note_metadata_changed", note, reason)

    def instance_register(self, controller):
        GObject.Object.__init__(controller)
        type_ = type(controller)
        if type_ not in self.conroller_types:
            log.debug("Registering GObject type %s", type_)
            GObject.type_register(type_)
            self.conroller_types.add(type_)

    def application_shutdown(self, reason):
        log.debug("Application Shutting Down for reason: %s", reason)
        Gtk.main_quit()

