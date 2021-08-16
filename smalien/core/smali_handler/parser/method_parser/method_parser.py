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

import re
from pprint import pprint

from .code_parser import code_parser as cprsr


class MethodParser(cprsr.CodeParser):
    def parse_methods(self):
        self.__find_methods()

        for path, data in self.smalis['data'].items():
            for method, mdata in data['methods'].items():
                self.parse_code(path, mdata, data, data['code'])
                # Count this method
                data['meth_refs'] += 1
                self.meth_refs['original'] += data['meth_refs']

    def __find_methods(self):
        for path, data in self.smalis['data'].items():
            i = 0
            while i < data['linage']:
                c = data['code'][i]
                if (c.startswith('.method ')):
                    name = c.split(' ')[-1]
                    j = i
                    while j < data['linage']:
                        c = data['code'][j]
                        if (c.startswith('.end method')):
                            data['methods'][name] = {
                                'start': i,
                                'end': j,
                                'attr': 'normal',
                                'params': {
                                    'vars': [],
                                    'types': [],
                                },
                                'vnum': None,
                                'vars': {},
                                'ret': {
                                    'type': None,
                                    'vars': [],
                                },
                            }
                            self.__get_method_info(
                                data['class'],
                                data['methods'][name],
                                data['code']
                            )
                            break
                        j += 1
                    i = j + 1
                else:
                    i += 1

    def __get_method_info(self, clss, mdata, code):
        c = code[mdata['start']]
        self.__get_attr(mdata, c)
        self.__get_prm_types(clss, mdata, c)
        self.__get_ret_type(mdata, c)
        c = code[mdata['start'] + 1]
        self.__get_vnum(mdata, c)

    def __get_attr(self, mdata, c):
        if (c.find(' native ') > -1):
            mdata['attr'] = 'native'
        elif (c.find(' abstract ') > -1):
            mdata['attr'] = 'abstract'
        elif (c.find(' static ') > -1):
            mdata['attr'] = 'static'

    def __get_prm_types(self, clss, mdata, c):
        if (mdata['attr'] != 'static'):
            self.__add_prm(mdata, clss)
        s = c.find('(') + 1
        e = c.find(')')
        prms = c[s:e]
        itr = re.finditer(r'\[*[VZBSCIJFD](?![a-z])|\[*L\w', prms)
        offst = 0
        for i in itr:
            prm_type = i.group()
            if (len(prm_type) > 1 and re.match(r'^\[*L', prm_type)):
                prm_type = prms[i.start():i.start() + prms[i.start():].find(';') + 1]
            if (offst <= i.start()):
                self.__add_prm(mdata, prm_type)
                if (prm_type in ['J', 'D']): self.__add_prm(mdata, prm_type)
                offst += len(prm_type)

    def __add_prm(self, mdata, prm_type):
        num = len(mdata['params']['vars'])
        #if (mdata['attr'] != 'static'):
        #  num += 1
        mdata['params']['vars'].append('p' + str(num))
        mdata['params']['types'].append(prm_type)

    def __get_ret_type(self, mdata, c):
        mdata['ret']['type'] = c.split(')')[-1]

    def __get_vnum(self, mdata, c):
        if (c.find(' .locals ') > -1):
            mdata['vnum'] = int(c.split(' ')[-1])
