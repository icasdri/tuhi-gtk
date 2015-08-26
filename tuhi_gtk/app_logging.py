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

import logging
import sys

log_lookup = {}
LOG_LEVEL = logging.DEBUG

def get_log_for_prefix_tuple(log_prefix_tuple):
    if log_prefix_tuple in log_lookup:
        return log_lookup[log_prefix_tuple]
    else:
        log = logging.getLogger("tuhi_gtk." + ".".join(log_prefix_tuple))
        log.setLevel(LOG_LEVEL)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(LOG_LEVEL)
        handler.setFormatter(PrefixTupleFormatter(log_prefix_tuple))
        log.addHandler(handler)
        log_lookup[log_prefix_tuple] = log
        return log

class PrefixTupleFormatter(logging.Formatter):
    def __init__(self, log_prefix_tuple):
        self.log_prefix_tuple = log_prefix_tuple
        super(PrefixTupleFormatter, self).__init__()

    def format(self, record):
        wrapped_prefixes = [self._wrap(prefix) for prefix in self.log_prefix_tuple]
        if record.levelno in (logging.WARNING, logging.ERROR, logging.CRITICAL):
            wrapped_prefixes.insert(0, record.levelname)
        record.msg = " ".join(wrapped_prefixes) + " " + record.msg
        return super(PrefixTupleFormatter, self).format(record)

    @staticmethod
    def _wrap(s):
        return "[" + s + "]"


