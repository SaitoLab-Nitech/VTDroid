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

#from graphviz import Digraph

from .node import node
from .edge import edge


class ControlFlowGraph():
    LOGGING = False

    def __init__(self, mstart, mend, vdata):
        if (ControlFlowGraph.LOGGING): print('Initializing CFG', mstart, mend)
        self.mstart = mstart
        self.mend = mend
        self.vdata = vdata
        self.nodes = set()
        self.edges = set()
        self.node_counter = -1
        self.edge_counter = 0
        self.tail = self.__add_node(mend, mend)  # node id = -1
        self.head = self.__add_node(mstart, mstart)  # node id = 0
        self.__add_edge(mstart, mstart + 1, False)

        self.__generate_cfg()
        if (self.node_counter == 1):
            self.__add_node(mstart + 1, mend - 1)
            self.__add_edge(mend - 1, mend, False)

        self.__calculate_succs_and_preds()
        if (ControlFlowGraph.LOGGING): print('Generated:')
        #self.show_cfg()

    def __add_node(self, start, end):
        new_node = node.Node(self.node_counter, start, end)
        self.nodes.add(new_node)
        self.node_counter += 1
        return new_node

    def __add_edge(self, start, end, try_catch):
        new_edge = edge.Edge(self.edge_counter, start, end, try_catch)
        self.edges.add(new_edge)
        self.edge_counter += 1

    def __add_try_catch_edge(self, start, try_dsts):
        for try_dst in try_dsts:
            assert try_dst is not None
            new_edge = edge.Edge(self.edge_counter, start, try_dst, True)
            self.edges.add(new_edge)
            self.edge_counter += 1

    def __generate_cfg(self):
        if (ControlFlowGraph.LOGGING): print('Generating a CFG')
        next_bstart = self.mstart + 1
        for i in range(self.mstart + 1, self.mend):
            if (i in self.vdata.keys()):
                if (ControlFlowGraph.LOGGING): print(i, self.vdata[i].keys())
                kind = self.vdata[i]['kind']
                if (
                    kind in [
                        'goto_label',
                        'cond',
                        'switch_label',
                        'catch_label',
                        'try_start',
                        'try_end',
                    ]
                ):
                    if (next_bstart != -1):
                        self.__add_node(next_bstart, i - 1)
                        self.__add_edge(i - 1, i, False)
                        self.__add_try_catch_edge(i - 1, self.vdata[i]['try_dsts'])
                    next_bstart = i
                elif (kind in ['if', 'switch']):
                    # Include this branch
                    self.__add_node(next_bstart, i)
                    # Between this block and the next block immediately following this branch
                    self.__add_edge( i, i + 1, False)
                    self.__add_try_catch_edge(i, self.vdata[i]['try_dsts'])
                    next_bstart = i + 1
                    if (kind == 'if'):
                        # Between this block and the target of this branch
                        self.__add_edge(i, self.vdata[i]['cond_line'], False)
                    else:
                        switch_targets = self.__get_switch_targets(self.vdata[i]['label'])
                        for target in switch_targets:
                            self.__add_edge(i, target, False)
                #elif (kind in ['catch']):
                #  self.__add_try_catch_edge(self.vdata[i], self.vdata)
                elif (kind in ['goto', 'ret', 'throw']):
                    self.__add_node(next_bstart, i)
                    next_bstart = -1
                    if (kind == 'goto'):
                        self.__add_edge(i, self.vdata[i]['goto_label_line'], False)
                        self.__add_try_catch_edge(i, self.vdata[i]['try_dsts'])
                    elif (kind == 'throw' and len(self.vdata[i]['try_dsts']) > 0):
                        for try_dst in self.vdata[i]['try_dsts']:
                            self.__add_edge(i, try_dst, False)
                    else:
                        self.__add_edge(i, self.mend, False)

    def __get_switch_targets(self, slabel):
        labels = self.__get_switch_labels(slabel)
        result = []
        for i, idata in self.vdata.items():
            if (idata['kind'] == 'switch_label' and idata['label'] in labels):
                result.append(i)
        assert result != []
        return result

    def __get_switch_labels(self, slabel):
        result = None
        for i, idata in self.vdata.items():
            if (idata['kind'] == 'switch_data' and idata['label'] == slabel):
                result = idata['labels']
                break
        assert result is not None
        return result

    def __calculate_succs_and_preds(self):
        for e in self.edges:
            src_node = self.get_node(e.src)
            dst_node = self.get_node(e.dst)
            if (not e.try_catch):
                src_node.succs.add(dst_node)
                dst_node.preds.add(src_node)
            else:
                src_node.exception_succs.add(dst_node)
                dst_node.exception_preds.add(src_node)

    def get_node(self, line):
        result = None
        for n in self.nodes:
            if (n.line_is_the_edge(line)):
                result = n
                break
        assert result is not None, ('Line:', line)
        return result

    def get_node_containing_line(self, line):
        result = None
        for n in self.nodes:
            if (n.line_in_node(line)):
                result = n
                break
        assert result is not None
        return result

    def get_node_label(self, line):
        result = None
        for n in self.nodes:
            if (n.line_is_the_edge(line)):
                result = n.label
                break
        assert result is not None
        return result

    '''
    def show_cfg(self):
        g = Digraph('CFG')
        for e in self.edges:
            color = 'black'
            if (e.try_catch):
                color = 'blue'
            g.edge(
                self.get_node_label(e.src),
                self.get_node_label(e.dst),
                color=color
            )
        for n in self.nodes:
            if (n.loop_header):
                g.node(
                    n.label,
                    style='filled',
                    color='red',
                    xlabel=','.join(n.control_dependent_branch)
                )
            else:
                g.node(
                    n.label,
                    xlabel=','.join(n.control_dependent_branch)
                )

        g.attr(overlap='false')
        g.view()
    '''

    def find_exceptional_paths(self, start_line, end_line, setter_lines):
        found = False
        start_node = self.get_node_containing_line(start_line)
        end_node = self.get_node_containing_line(end_line)
        sline_exists = self.__setter_line_exists(
            end_node,
            end_line,
            setter_lines
        )
        if (sline_exists): return found
        for e_succ in start_node.exception_succs:
            if (e_succ != start_node):
                if (e_succ == end_node):
                    sline_exists = self.__setter_line_exists(
                        e_succ,
                        end_line,
                        setter_lines
                    )
                    if (sline_exists): break
                else:
                    sline_exists = self.__setter_line_exists(
                        e_succ,
                        None,
                        setter_lines
                    )
                    if (sline_exists): break
                if (end_node in e_succ.post_dominators):
                    found = True
                    break
        return found

    def __setter_line_exists(self, n, end_line, setter_lines):
        for sline in setter_lines:
            if (n.line_in_node(sline)):
                if (end_line is None or sline < end_line):
                    return True
        return False
