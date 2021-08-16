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

import io
import re

from ..printer import Printer

class CodeCoverageCalculator():
    def __init__(self, smalis, path_smalienlog, workspace, parameters):
        self.smalis = smalis
        self.data = self.__load_runtime_data(path_smalienlog)
        self.explored = set()
        self.printer = Printer(workspace, parameters['redirect_to'])

    def __load_runtime_data(self, path):
        with io.open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                yield line.rstrip('\n')

    def calculate(self):
        code_whole = self.__calculate_code_whole()
        #print('    code whole:', code_whole)
        code_explored = self.__calculate_code_explored()
        #print('    code explored:', code_explored)
        print(
            '    coverage:', code_explored, '/', code_whole, '* 100 =',
            code_explored / code_whole * 100
        )

    def __calculate_code_whole(self):
        result = 0
        for path, data in self.smalis['data'].items():
            result += data['linage']
        return result

    def __calculate_code_explored(self):
        result = 0
        tags = set()
        for line in self.data:
            matched_objs = re.finditer(r'\d{13}:\d+:\d+:\d+_\d+', line)
            for obj in matched_objs:
                tag = line[obj.start():obj.end()].split(':')[-1]
                tags.add(tag)
        print('    tags:', len(tags))
        for tag in tags:
            amount = self.__get_method_code_size(tag)
            result += amount
        print('    classes:', len(self.explored), '/',
              len(self.smalis['data'].keys()), '* 100 = ',
              len(self.explored) / len(self.smalis['data'].keys()) * 100)
        return result

    def __get_method_code_size(self, tag):
        cid = int(tag.split('_')[0])
        if (cid not in self.smalis['ids'].keys()):
            return None
        path = self.smalis['ids'][cid]
        line = int(tag.split('_')[1])
        for method, mdata in self.smalis['data'][path]['methods'].items():
            if (mdata['start'] <= line <= mdata['end']):
                if (path + method not in self.explored):
                    self.explored.add(path + method)
                    return mdata['end'] - mdata['start'] + 1
                else:
                    return 0
        return 0

    # Calculate method coverage
    def calculate_method_coverage(self):
        method_whole = self.__calculate_method_whole()
        method_explored = self.__calculate_method_explored(method_whole)
        self.printer.print(
            f'    method coverage: {method_explored} / {method_whole} * 100 = '
            f'{method_explored / method_whole * 100}'
        )

    def __calculate_method_whole(self):
        result = 0
        for path, data in self.smalis['data'].items():
            result += len(data['methods'].keys())
        return result

    def __calculate_method_explored(self, method_whole):
        for line in self.data:
            matched_objs = re.finditer(r'\d{13}:\d+:\d+:\d+_\d+', line)
            for obj in matched_objs:
                tag = line[obj.start():obj.end()].split(':')[-1]
                class_method = self.__get_class_method(tag)
                if (class_method is not None):
                    self.explored.add(class_method)
                    #print('    current_coverage:', len(self.explored), '/',
                    #      method_whole, '* 100 =',
                    #      len(self.explored) / method_whole * 100)
        return len(self.explored)

    def __get_class_method(self, tag):
        cid = int(tag.split('_')[0])
        if (cid not in self.smalis['ids'].keys()):
            return None
        path = self.smalis['ids'][cid]
        line = int(tag.split('_')[1])
        for method, mdata in self.smalis['data'][path]['methods'].items():
            if (mdata['start'] <= line <= mdata['end']):
                return path + method
        return None
