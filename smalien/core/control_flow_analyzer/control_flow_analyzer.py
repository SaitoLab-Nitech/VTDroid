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

import sys

from .control_flow_graph import control_flow_graph as cfg
from .dominator_analyzer import dominator_analyzer as da
from .loop_identifier import loop_identifier as li


class ControlFlowAnalyzer(da.DominatorAnalyzer, li.LoopIdentifier):
    CFATAG = '[ CFA ]'

    def analyze_control_flows(self, path, method, method_code, tag = None):
        self.printer.print(f'{self.CFATAG} Analyzing control flows for {path} {method}')
        if (tag is not None):
            self.printer.print(f'{self.CFATAG}  {tag = }')
        graph = cfg.ControlFlowGraph(
            method_code['start'],
            method_code['end'],
            method_code['vars']
        )
        self.analyze_dominators(graph)
        self.identify_loops(graph)
        #graph.show_cfg()
        return graph
