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

from pprint import pprint

from .target_obj_class_ivks import trgt_obj_clss_ivks
from .parser import parser as prsr
from .generator import generator as gnrtr
from .injector import injector as ijctr
from ..user_input_sources import user_input_sources
from ..user_input_sinks import user_input_sinks


class SmaliHandler(prsr.Parser, gnrtr.Generator, ijctr.Injector):
    def __init__(self, app_info, params_sbi):
        self.params = app_info
        self.flash_interval = hex(params_sbi['flash_interval'])
        self.src_detected = False
        self.white_list = None
        self.exclusion = []
        self.smalis = {
            'ids': {},
            'data': {},
            'index': {},
        }
        self.id = 0
        self.trgt_typs = [
            'Z',
            'B',
            'S',
            'C',
            'I',
            'J',
            'F',
            'D',
            '[Z',
            '[B',
            '[S',
            '[C',
            '[I',
            '[J',
            '[F',
            '[D',
            '[Ljava/lang/String;',
            'Ljava/lang/String;',
            #'Ljava/lang/CharSequence;',
        ]
        self.trgt_obj_clss_ivks = trgt_obj_clss_ivks
        self.aux_clss = {
            'cntr': 33,  # Num of Ivks in injector/SmalienWriter.smali
            'dex_num': 0,
            'code': {
                'LsmalienLog_0': [],
            },
            'crnt': 'LsmalienLog_0',
            'lmt': 65000,
        }
        self.meth_refs = {
            'cntr': 0,
            'original': 0,
            'aux': 0,
            'dex': {},
            'lmt': 65000,
        }
        self.user_input_sources = user_input_sources
        self.user_input_sinks = user_input_sinks

    def run(self):
        self.parse()
        print('    Method refs:', self.meth_refs['original'])
        print('    Class excluded:', self.exclusion)

        self.generate()
        print(
            '    Aux methods:', self.meth_refs['aux'],
            ', Total meth refs:', self.meth_refs['original'] + self.meth_refs['aux']
        )

        self.inject()

        self.smalis['package'] = self.params['package']
        self.smalis['activity'] = self.params['activity']
        return self.smalis, self.meth_refs['aux']
