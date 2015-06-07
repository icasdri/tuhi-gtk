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

DATA_BASEDIR = ""
UI_BASEDIR = os.path.join(DATA_BASEDIR, "ui")
UI_EXTENSION = ".xml"

def get_ui_file(ui_name):
    return resource_filename(__name__, os.path.join(UI_BASEDIR, ui_name + UI_EXTENSION))
