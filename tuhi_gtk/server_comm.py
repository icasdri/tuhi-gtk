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

import requests, json

from tuhi_gtk.database import db_session, kv_store, Note, NoteContent, get_current_date
from tuhi_gtk.config import SYNCSERVER_NOTES_ENDPOINT, SYNCSERVER_AFTER_PARAM

class ServerAccessPoint(object):
    def __init__(self):
        self.sync_url = kv_store["SYNCSERVER_URL"].rstrip("/") + SYNCSERVER_NOTES_ENDPOINT
        self.auth = (kv_store["SYNCSERVER_USERNAME"], kv_store["SYNCSERVER_PASSWORD"])

    def pull(self):
        last_sync_date = kv_store["LAST_SYNC_DATE"]
        target_url = self.sync_url + SYNCSERVER_AFTER_PARAM + str(last_sync_date)

    def push(self):
        last_sync_date = kv_store["LAST_SYNC_DATE"]
        notes_list = list(map(lambda x: x.serialize(), Note.query.filter(Note.date_modified > last_sync_date).all()))
        note_contents_list = list(map(lambda x: x.serialize(), NoteContent.query.filter(NoteContent.date_created > last_sync_date).all()))
        data_dict = {"notes": notes_list, "note_contents": note_contents_list}
        data = json.dumps(data_dict)

        try:
            r = requests.post(self.sync_url, data, auth=self.auth)
        except ConnectionError:
            # TODO: try again, Gobject.timeout_add probably
            pass
        else:
            print(r.json)
