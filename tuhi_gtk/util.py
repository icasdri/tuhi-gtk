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

# Wrappers for handling GObject callback signals with extra parameters

def ignore_sender_function(func):
    def new_func(sender, *pos):
        func(*pos)
    return new_func


def ignore_all_args_function(func):
    def new_func(*pos):
        func()
    return new_func


def property_change_function(func):
    def new_func(sender, g_property_spec):
        prop_value = sender.get_property(g_property_spec.name)
        return func(prop_value)
    return new_func

