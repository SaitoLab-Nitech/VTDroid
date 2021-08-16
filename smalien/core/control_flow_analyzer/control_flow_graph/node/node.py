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


class Node():
    def __init__(self, id, start, end):
        self.id = id
        self.start = start
        self.end = end
        self.label = str(id) + '_' + str(start) + '_' + str(end)
        self.succs = set()
        self.preds = set()
        self.dominators = set()
        self.post_dominators = set()

        # For try-catch analysis
        self.exception_succs = set()
        self.exception_preds = set()
        self.exception_dominators = set()
        self.exception_post_dominators = set()

        # Used for Loop Identification
        self.traversed = False
        self.dfsp_pos = 0
        self.iloop_header = None
        self.loop_header = False
        self.reentry_to = None
        self.reentry_from = None
        self.loop_irreducible = False

        # Used for Control-Dependence Analysis
        self.loop_body = None
        self.exit_nodes = None
        self.control_dependent_branch = set()

    def line_is_the_edge(self, line):
        if (self.start == line or self.end == line):
            return True
        return False

    def line_in_node(self, line):
        if (self.start <= line <= self.end):
            return True
        return False
