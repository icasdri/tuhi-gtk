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
from datetime import datetime


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


def hide_window_on_delete(widget, _):
    widget.hide()
    return True


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


def format_date(epoch_int):
    return datetime.fromtimestamp(epoch_int).strftime("%b %d, %I:%m:%S %p")


def pref_helper_ui_set(render_relationships, builder, pref, val):
    ui_object_id, setter_name, _, native_type, _ = render_relationships[pref]
    target_val = native_type(val) if native_type is not None else val
    ui_object = builder.get_object(ui_object_id)
    if setter_name.startswith("props."):
        setattr(ui_object.props, setter_name.split(".")[1], target_val)
    else:
        getattr(ui_object, setter_name)(target_val)


def pref_helper_ui_get(render_relationships, builder, pref):
    ui_object_id, _, getter_name, _, wanted_type = render_relationships[pref]
    ui_object = builder.get_object(ui_object_id)

    sens = ui_object.get_sensitive()
    if sens is True:
        ui_object.set_sensitive(False)

    if getter_name.startswith("props."):
        raw_val = getattr(ui_object.props, getter_name.split(".")[1])
    else:
        raw_val = getattr(ui_object, getter_name)()

    if sens is True:
        ui_object.set_sensitive(True)
    return wanted_type(raw_val) if wanted_type is not None else raw_val
