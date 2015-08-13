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
    # _ is sender var.
    def new_func(_, *pos):
        func(*pos)
    return new_func


def ignore_all_args_function(func):
    def new_func(*_):
        func()
    return new_func


def property_change_function(func):
    def new_func(sender, g_property_spec):
        prop_value = sender.get_property(g_property_spec.name)
        return func(prop_value)
    return new_func


def underscore_camelcase(camel_str):
    last_index = 0
    result = ""
    for i, l in enumerate(camel_str):
        if i == 0:
            continue
        if l.isupper():
            result += camel_str[last_index:i].lower() + "_"
            last_index = i
    return result + camel_str[last_index:].lower()
