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


class ControlDependenceAnalyzer():
    def analyze_control_dependencies(self, branch, cfg):
        self.printer.print(f'Analyzing control dependencies at {branch.line}')

        self_node = self.__get_self_node(branch.line, cfg)
        if (self_node.loop_header):  # Node is a loop header
            #control_dependent_nodes, exit_node = self.__get_loop_body(
            #   self_node.succs,
            #   self_node.label,
            #   cfg
            #)
            #self_node.exit_node = exit_node
            control_dependent_nodes = self_node.loop_body
            self.__print_nodes(control_dependent_nodes)
        else:
            control_dependent_nodes = self.__trav_succs(
                self_node,
                self_node.post_dominators,
                cfg
            )
            self.__print_nodes(control_dependent_nodes)

        self.__set_control_dependent_relation_to_nodes(
            control_dependent_nodes,
            self_node.label
        )
        #cfg.show_cfg()

        branch.set_self_node(self_node)
        branch.set_control_dependent_nodes(control_dependent_nodes)

    def check_control_dependence(self, line, branch):
        for cdn in branch.control_dependent_nodes:
            if (cdn.line_in_node(line)):
                return True
        if (branch.node.line_in_node(line)):
            return True
        return False

    def __print_nodes(self, nodes):
        i = 0
        for n in nodes:
            i += 1
            self.printer.print(f'  #{str(i)}: {n.label}')

    def __get_self_node(self, line, cfg):
        result = None
        for n in cfg.nodes:
            if (n.line_in_node(line)):
                self.printer.print(f'{n.label = }, {n.loop_header = }')
                result = n
                break
        assert result is not None
        return result

    def __set_control_dependent_relation_to_nodes(
        self,
        control_dependent_nodes,
        branch_label
    ):
        for n in control_dependent_nodes:
            n.control_dependent_branch.add(branch_label)

    def __get_loop_body(self, lh_succs, lh_label, cfg):
        result = set()
        exit_node = None
        target_lh_labels = {lh_label}
        changed = True
        while changed:
            changed = False
            for n in cfg.nodes:
                if (n.iloop_header is not None and n.iloop_header.label in target_lh_labels):
                    result.add(n)
                    if (n.loop_header and n.label not in target_lh_labels):
                        # n is a nested-loop's header
                        target_lh_labels.add(n.label)
                        changed = True
                elif (n in lh_succs):
                    exit_node = n
        assert result is not set() and exit_node is not None
        return result, exit_node

    def __trav_succs(self, n, goals, cfg):
        result = set()
        succs = n.succs
        if (n.loop_header):
            #loop_body, exit_node = self.__get_loop_body(n.succs, n.label, cfg)
            result = result | n.loop_body
            succs = n.exit_nodes
        for succ in succs:
            if (succ not in goals):  # Succ is not an n's post dominator
                result.add(succ)
                result = result | self.__trav_succs(succ, goals, cfg)
        return result

    def __trav_succs_old(self, n, goals, cfg):
        result = set()
        for succ in n.succs:
            if (succ not in goals):  # Succ is not an n's post dominator
                result.add(succ)
                next_nodes = succ.succs
                if (succ.loop_header):
                    loop_body, exit_node = self.__get_loop_body(succ.succs, succ.label, cfg)
                    result = result | loop_body
                    next_nodes = {exit_node}
                for next_node in next_nodes:
                    result = result | self.__trav_succs(next_node, goals, cfg)
        assert result is not set()
        return result
