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

import copy
from .receptor import receptor


class Branch():
    def __init__(self, r, var_tracked):
        #print('Initializing a branch')
        self.line = r['line']
        self.var_tracked = var_tracked
        self.values_with_true_condition = []
        self.values_with_false_condition = []
        self.node = None
        self.control_dependent_nodes = None
        self.receptors = {}
        self.body_running = False

    def get_line(self):
        return self.line

    def get_var_tracked(self):
        return self.var_tracked

    def set_self_node(self, node):
        self.node = node

    def set_control_dependent_nodes(self, nodes):
        self.control_dependent_nodes = nodes

    def get_control_dependent_nodes(self):
        return self.control_dependent_nodes

    def set_body_running(self, state):
        self.body_running = state

    def get_body_running(self):
        return self.body_running

    def set_value_with_false_condition(self, value):
        self.values_with_false_condition.append(value)

    def get_values_with_both_conditions(self):
        return set(self.values_with_false_condition) | set(self.get_values())

    def update_branch_round_with_true_condition(self, value, compared_value, receptor_values, tracked):
        self.set_body_running(True)
        self.values_with_true_condition.append({
            'branch': value,
            'compared': compared_value,
            'values_before_branch': tracked,
        })
        for receptor in self.receptors.values():
            receptor.update_round(value, receptor_values[receptor.get_var()])

    def update_receptor(self, line, kind, var, value, taint):
        receptor_key = str(line) + '_' + var
        if (receptor_key not in self.receptors.keys()):
            value_before_branch = self.__get_receptor_value_before_branch(var)
            self.receptors[receptor_key] = receptor.Receptor(
                line,
                kind,
                var,
                self.values_with_true_condition[-1]['branch'],
                value_before_branch
            )
        self.receptors[receptor_key].add_value(value)
        self.receptors[receptor_key].update_taint(taint)

    def __get_receptor_value_before_branch(self, var):
        if (var in self.values_with_true_condition[-1]['values_before_branch'].keys()):
            return self.values_with_true_condition[-1]['values_before_branch'][var][5]

    def get_values(self):
        result = [ round['branch'] for round in self.values_with_true_condition ]
        return result

    def get_compared_values(self):
        result = [ round['compared'] for round in self.values_with_true_condition ]
        return result

    def get_receptors(self):
        return self.receptors
