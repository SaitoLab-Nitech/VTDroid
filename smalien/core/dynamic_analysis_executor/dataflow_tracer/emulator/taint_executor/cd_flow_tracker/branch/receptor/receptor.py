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


class Receptor():
    def __init__(self, line, kind, var, value, value_before_branch):
        self.line = line
        self.kind = kind
        self.var = var
        self.values = []
        self.update_round(value, value_before_branch)
        self.taint = False
        self.da_receptors = {}

    def get_line(self):
        return self.line

    def get_kind(self):
        return self.kind

    def get_var(self):
        return self.var

    def update_round(self, value, value_before_branch):
        self.values.append({
            'branch': value,
            'receptor': [],
            'value_before_branch': value_before_branch,
        })

    def add_value(self, value):
        if (value is not None):
            self.values[-1]['receptor'].append(value)

    def get_values(self):
        result = [ ','.join(round['receptor']) for round in self.values ]
        return result

    def get_branch_values(self):
        result = [ round['branch'] for round in self.values ]
        return result

    def get_values_before_branch(self):
        result = { round['value_before_branch'] for round in self.values }
        return result

    def __get_the_newest_value(self):
        if (len(self.values[-1]['receptor']) > 0):
            return self.values[-1]['receptor'][-1]

    def update_taint(self, taint):
        self.taint = taint

    def get_taint(self):
        return self.taint

    def test_and_add_da_receptor(self, da_receptor_id, da_receptor_value):
        newest = self.__get_the_newest_value()
        if (newest is not None and newest == da_receptor_value):
            if (da_receptor_id not in self.da_receptors.keys()):
                self.da_receptors[da_receptor_id] = {
                    'values': [],
                    'matched': 0,
                }
            self.da_receptors[da_receptor_id]['values'].append(da_receptor_value)
            self.da_receptors[da_receptor_id]['matched'] += 1
            return self.da_receptors[da_receptor_id]
        elif (da_receptor_id in self.da_receptors.keys()):
            self.da_receptors[da_receptor_id]['values'].append(da_receptor_value)
            return self.da_receptors[da_receptor_id]
