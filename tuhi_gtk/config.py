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

from pkg_resources import resource_filename
import os.path

USERDATA_DIR = os.path.expanduser("~/.local/share/tuhi-gtk")
USERCONFIG_DIR = os.path.expanduser("~/.config/tuhi-gtk")

def config_directories():
    for directory in (USERDATA_DIR, USERCONFIG_DIR):
        os.makedirs(directory, mode=0o751, exist_ok=True)

DATABASE_PATH = os.path.join(USERDATA_DIR, "tuhi_gtk_notes.db")
DATABASE_URI = "sqlite:///" + DATABASE_PATH

DATA_BASEDIR = ""
UI_BASEDIR = os.path.join(DATA_BASEDIR, "ui")
UI_EXTENSION = ".xml"

SYNCSERVER_NOTES_ENDPOINT = "/notes"

SESSION_TIMEOUT = 10 * 60 * 1000  # 10 minutes
BUFFER_ACTIVITY_CHECKERS_RESOLUTION = 1000
BUFFER_INACTIVITY_TARGET_COUNT = 5
BUFFER_ACTIVITY_TARGET_COUNT = 30

USE_SESSION_BASED_AUTOSAVE = False

REASON_USER = "user"
REASON_SYNC = "sync"

SYNC_ACTION_BEGIN = "begin"
SYNC_ACTION_SUCCESS = "success"
SYNC_ACTION_FAILURE = "failure"

def get_ui_file(ui_name):
    return resource_filename(__name__, os.path.join(UI_BASEDIR, ui_name + UI_EXTENSION))

