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

import os
import io
import glob
from pprint import pprint

from .white_list import white_list
from .method_parser import method_parser as mprsr


class Parser(mprsr.MethodParser):
    use_whitelist = True

    def parse(self):
        print('  Start parsing')

        self.white_list = white_list

        self.__load()
        self.__get_class_info()
        self.parse_methods()

    def __load(self):
        dirs = glob.glob(self.params['tdir'] + 'smali*')
        for d in dirs:
            self.smalis['index'][d] = {}
            if (Parser.use_whitelist):
                self.white_list_paths = [d + i for i in self.white_list]
            self.__find_smalis(d, self.smalis['index'][d])

    def __add_dirs_to_index(self, index_d, dirs):
        index_d[dirs[0]] = {}
        prev = index_d[dirs[0]]
        if (len(dirs) > 1):
            return self.__add_dirs_to_index(prev, dirs[1:])
        else:
            return prev

    def __find_smalis(self, d, prev):
        if (Parser.use_whitelist):
            for white_list_path in self.white_list_paths:
                if (d.startswith(white_list_path)):
                    self.exclusion.append(d)
                    return
        files = os.listdir(d)
        for f in files:
            if (f.startswith('.')):
                continue
            elif (f.endswith('.smali')):
                path = d + '/' + f
                prev[f] = {'path': path}
                self.__read_smali(path)
            else:
                prev[f] = {}
                self.__find_smalis(d + '/' + f, prev[f])

    def __read_smali(self, path):
        with io.open(path, 'r', encoding='utf-8') as f:
            code = f.read().split('\n')[:-1]
            self.smalis['data'][path] = {
                'id': self.id,
                'code': code,
                'linage': len(code),
                'class': None,
                'super': None,
                'statics': {},
                'instances': {},
                'methods': {},
                'auxiliary': {},
                'meth_refs': 0,
            }
            self.smalis['ids'][self.id] = path
            self.id += 1

    def __get_class_info(self):
        for path in self.smalis['data'].keys():
            self.__get_self(path)
            self.__get_super(path)
            self.__get_statics(path)
            self.__get_instances(path)

    def __get_self(self, path):
        c = self.smalis['data'][path]['code'][0]
        if (c.startswith('.class ')):
            self.smalis['data'][path]['class'] = c.split(' ')[-1]

    def __get_super(self, path):
        c = self.smalis['data'][path]['code'][1]
        if (c.startswith('.super ')):
            self.smalis['data'][path]['super'] = c.split(' ')[-1]

    def __get_statics(self, path):
        clss = self.smalis['data'][path]['class']
        s, e = self.__get_fields(path, '# static fields')
        for c in self.smalis['data'][path]['code'][s:e]:
            if (c.startswith('.field ') and c.find(' static ') > -1):
                v = [i for i in c.split(' ') if i.find(':') > -1]
                if (v != []):
                    v = v[0]
                    self.smalis['data'][path]['statics'][clss + '->' + v] = {
                        'name': v.split(':')[0],
                        'type': v.split(':')[1],
                        'class': clss,
                        'put': {},
                        'get': {},
                    }

    def __get_instances(self, path):
        clss = self.smalis['data'][path]['class']
        s, e = self.__get_fields(path, '# instance fields')
        for c in self.smalis['data'][path]['code'][s:e]:
            if (c.startswith('.field ')):
                v = [i for i in c.split(' ') if i.find(':') > -1]
                if (v != []):
                    v = v[0]
                    self.smalis['data'][path]['instances'][clss + '->' + v] = {
                        'name': v.split(':')[0],
                        'type': v.split(':')[1],
                        'class': clss,
                        'put': {},
                        'get': {},
                    }

    def __get_fields(self, path, name):
        e = self.smalis['data'][path]['linage']
        for i in range(e):
            c = self.smalis['data'][path]['code'][i]
            if (c.startswith(name)):
                s = i + 1
                for j in range(s, e):
                    c = self.smalis['data'][path]['code'][j]
                    if (c.startswith('# ')):
                        return s, j
                return s, e
        return 0, 0
