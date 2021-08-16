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
#from graphviz import Digraph


class DominatorAnalyzer():
    LOGGING = False

    def analyze_dominators(self, cfg):
        if (DominatorAnalyzer.LOGGING): print('Analyzing dominators')
        self.__init_dominators(cfg)
        self.__compute_dominators(cfg)
        #self.__show_dominators(cfg)

        if (DominatorAnalyzer.LOGGING): print('Analyzing post-dominators')
        self.__init_post_dominators(cfg)
        self.__compute_post_dominators(cfg)
        #self.__show_post_dominators(cfg)

        self.__init_exception_post_dominators(cfg)
        self.__compute_exception_post_dominators(cfg)
        #self.__show_exception_post_dominators(cfg)

    def __init_dominators(self, cfg):
        cfg.head.dominators.add(cfg.head)
        for n in cfg.nodes:
            if (n != cfg.head):
                for item in cfg.nodes:
                    n.dominators.add(item)

    def __init_post_dominators(self, cfg):
        cfg.tail.post_dominators.add(cfg.tail)
        for n in cfg.nodes:
            if (n != cfg.tail):
                for item in cfg.nodes:
                    n.post_dominators.add(item)

    def __init_exception_post_dominators(self, cfg):
        cfg.tail.exception_post_dominators.add(cfg.tail)
        for n in cfg.nodes:
            if (n != cfg.tail):
                for item in cfg.nodes:
                    n.exception_post_dominators.add(item)

    def __compute_dominators(self, cfg):
        change = True
        while change:
            change = False
            for n in cfg.nodes:
                if (n != cfg.head and len(n.preds) > 0):  # Skip catch's node
                    if (DominatorAnalyzer.LOGGING):
                        print('[ DOM ] Node:', n.label, len(n.dominators))
                    tmp_dominators = set()
                    for pred in n.preds:
                        if (DominatorAnalyzer.LOGGING):
                            print('  Pred:', pred.label)
                        if (tmp_dominators == set()):
                            tmp_dominators = copy.copy(pred.dominators)
                        else:
                            tmp_dominators = tmp_dominators & pred.dominators
                    tmp_dominators.add(n)
                    if (not (tmp_dominators == n.dominators)):
                        n.dominators = tmp_dominators
                        change = True

    def __compute_post_dominators(self, cfg):
        change = True
        while change:
            change = False
            for n in cfg.nodes:
                if (n != cfg.tail):
                    if (DominatorAnalyzer.LOGGING):
                        print('[ PDOM ] Node:', n.label)
                    tmp_post_dominators = set()
                    for succ in n.succs:
                        if (DominatorAnalyzer.LOGGING):
                            print('  Pred:', succ.label)
                        if (tmp_post_dominators == set()):
                            tmp_post_dominators = copy.copy(succ.post_dominators)
                        else:
                            tmp_post_dominators = tmp_post_dominators & succ.post_dominators
                    tmp_post_dominators.add(n)
                    if (not (tmp_post_dominators == n.post_dominators)):
                        n.post_dominators = tmp_post_dominators
                        change = True

    def __compute_exception_post_dominators(self, cfg):
        change = True
        while change:
            change = False
            for n in cfg.nodes:
                if (n != cfg.tail):
                    if (DominatorAnalyzer.LOGGING):
                        print('[ E-PDOM ] Node:', n.label)
                    tmp_exception_post_dominators = set()
                    for e_succ in n.exception_succs:
                        if (DominatorAnalyzer.LOGGING):
                            print('  Pred:', e_succ.label)
                        if (tmp_exception_post_dominators == set()):
                            tmp_exception_post_dominators = copy.copy(
                                e_succ.exception_post_dominators
                            )
                        else:
                            tmp_exception_post_dominators = \
                                tmp_exception_post_dominators & e_succ.exception_post_dominators
                    tmp_exception_post_dominators.add(n)
                    if (not (tmp_exception_post_dominators == n.exception_post_dominators)):
                        n.exception_post_dominators = tmp_exception_post_dominators
                        change = True

    '''
    def __show_dominators(self, cfg):
        g = Digraph('DOM')
        for n in cfg.nodes:
            g.node(n.label)
            for dom in n.dominators:
                g.edge(dom.label, n.label)
        g.view()

    def __show_post_dominators(self, cfg):
        g = Digraph('PDOM')
        for n in cfg.nodes:
            g.node(n.label)
            for pdom in n.post_dominators:
                g.edge(pdom.label, n.label)
        g.view()

    def __show_exception_post_dominators(self, cfg):
        g = Digraph('E-PDOM')
        for n in cfg.nodes:
            g.node(n.label)
            for pdom in n.exception_post_dominators:
                g.edge(pdom.label, n.label)
        g.view()
    '''
