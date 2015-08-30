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

class FeatureViewMixin(object):
    def __init__(self, feature_dict, box, builder, padding=3):
        self.__feature_dict = feature_dict
        self.__box = box
        self.__builder = builder
        self.__current_feature = None
        self.__padding = padding

    def show_feature(self, feature):
        if self.__current_feature == feature:
            return
        self.hide_feature()
        widget_id, show_func, _ = self.__feature_dict[feature]
        widget = self.__builder.get_object(widget_id)
        self.__box.pack_end(widget, expand=False, fill=False, padding=self.__padding)
        widget.show()
        if show_func is not None:
            show_func(widget)
        self.__current_feature = feature

    def hide_feature(self, feature=None):
        if self.__current_feature is None:
            return
        if feature is not None and feature != self.__current_feature:
            return
        widget_id, _, hide_func = self.__feature_dict[self.__current_feature]
        widget = self.__builder.get_object(widget_id)
        if hide_func is not None:
            hide_func(widget)
        widget.hide()
        self.__box.remove(widget)
        self.__current_feature = None
