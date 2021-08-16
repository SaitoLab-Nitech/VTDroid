# -*- coding: utf-8 -*-
#
#----------------------------------------------------------------
#
#    VTDroid
#    Copyright (C) 2021  Nagoya Institute of Technology, Hiroki Inayoshi
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>."
#
#----------------------------------------------------------------
#


class Records():
    def __init__(self):
        self.records = {}

    def insert_rec(self, rec):
        data = self.get_a_field(rec, 'data')
        data.append(rec)

    def get_a_field(self, r, field_name):
        if (r['path'] not in self.records.keys()):
            self.records[r['path']] = {}
        if (r['method'] not in self.records[r['path']].keys()):
            self.records[r['path']][r['method']] = {}
        if (r['pid'] not in self.records[r['path']][r['method']].keys()):
            self.records[r['path']][r['method']][r['pid']] = {}
        if (r['tid'] not in self.records[r['path']][r['method']][r['pid']].keys()):
            self.records[r['path']][r['method']][r['pid']][r['tid']] = {
                'data': [],
                'tracked': {},
                'snapshot': {},  # Save status of tracking for ivks
            }
        return self.records[r['path']][r['method']][r['pid']][r['tid']][field_name]
