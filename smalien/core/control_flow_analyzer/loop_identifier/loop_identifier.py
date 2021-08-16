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


class LoopIdentifier():
    LOGGING = False

    def identify_loops(self, cfg):
        if (LoopIdentifier.LOGGING): print('Identifying loops')
        self.__trav_loops_dfs(cfg.head, 1, cfg)
        if (LoopIdentifier.LOGGING): self.__print_loops(cfg)

        self.__identify_loop_body(cfg)

    def __trav_loops_dfs(self, b0, dfsp_pos, cfg):
        b0.traversed = True
        b0.dfsp_pos = dfsp_pos  # Mark b0's position in DFSP
        for b in b0.succs:
            if (not b.traversed):
                # Case (A), new
                if (LoopIdentifier.LOGGING):
                    print('Case (A)', b0.label, b.label)
                nh = self.__trav_loops_dfs(b, dfsp_pos + 1, cfg)
                self.__tag_lhead(b0, nh)
            else:
                if (b.dfsp_pos > 0):  # b in DFSP(b0)
                    # Case (B)
                    if (LoopIdentifier.LOGGING):
                        print('Case (B)', b0.label, b.label)
                    b.loop_header = True
                    self.__tag_lhead(b0, b)
                elif (b.iloop_header is None):
                    # Case (C), do nothing
                    if (LoopIdentifier.LOGGING):
                        print('Case (C)', b0.label, b.label)
                    pass
                else:
                    h = b.iloop_header
                    if (h.dfsp_pos > 0):  # h in DFSP(b0)
                        # Case (D)
                        if (LoopIdentifier.LOGGING):
                            print('Case (D)', b0.label, b.label, h.label)
                        self.__tag_lhead(b0, h)
                    else:  # h not in DFSP(b0)
                        # Case (E), reentry
                        if (LoopIdentifier.LOGGING):
                            print('Case (E)', b0.label, b.label, h.label)
                        b.reentry_to = b0
                        b0.reentry_from = b
                        h.loop_irreducible = True
                        while (h.iloop_header is not None):
                            h = h.iloop_header
                            if (h.dfsp_pos > 0):
                                self.__tag_lhead(b0, h)  # h in DFSP(b0)
                                break
                            h.loop_irreducible = True
        b0.dfsp_pos = 0
        return b0.iloop_header

    def __tag_lhead(self, b, h):
        if (b == h or h is None): return
        cur1 = b
        cur2 = h
        while (cur1.iloop_header is not None):
            ih = cur1.iloop_header
            if (ih == cur2): return
            if (ih.dfsp_pos < cur2.dfsp_pos):
                cur1.iloop_header = cur2
                cur1 = cur2
                cur2 = ih
            else:
                cur1 = ih
        cur1.iloop_header = cur2

    def __print_loops(self, cfg):
        for n in cfg.nodes:
            print(n.label, end='')
            if (n.iloop_header is not None):
                print('  ILH:', n.iloop_header.label, end='')
            if (n.loop_header):
                print('  (LOOP HEADER)', end='')
            print('')

    def __get_loop_body_and_exit_nodes(self, lh, cfg):
        loop_body = set()
        exit_nodes = copy.copy(lh.succs)
        target_lh_labels = {lh.label}
        changed = True
        while changed:
            changed = False
            for n in cfg.nodes:
                if (
                    n.iloop_header is not None and
                    n.iloop_header.label in target_lh_labels
                ):
                    loop_body.add(n)
                    exit_nodes = exit_nodes | n.succs
                    if (n.loop_header and n.label not in target_lh_labels):
                        # n is a nested-loop's header
                        target_lh_labels.add(n.label)
                        changed = True
        exit_nodes = exit_nodes - loop_body - {lh}
        assert loop_body is not set() and exit_nodes is not set()
        return loop_body, exit_nodes

    def __identify_loop_body(self, cfg):
        for n in cfg.nodes:
            if (n.loop_header):
                #print('loop header:', n.label)
                loop_body, exit_nodes = self.__get_loop_body_and_exit_nodes(
                    n,
                    cfg
                )
                #for lb in loop_body:
                #  print('  ', lb.label)
                #for en in exit_nodes:
                #  print('  exit node:', en.label)
                n.loop_body = loop_body
                n.exit_nodes = exit_nodes
