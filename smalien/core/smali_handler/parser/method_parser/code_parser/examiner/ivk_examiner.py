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

from .api_detector import api_detector as ad
from ..dalvik_bytecode import ivk


class IvkExmnr(ad.ApiDetector):
    def examine_ivk(self, i, inst, c, vdata, code, path):
        if (ivk[inst]['class'] == 2):
            raise ValueError('Rare instruction found')
        name = c.split(', ')[-1]
        vdata[i] = {
            'kind': 'ivk',
            'class': name.split('->')[0],
            'method': name.split('->')[1],
            'prms': [],
            'prm_types': [name.split('->')[0]] if (ivk[inst]['class'] != 1) else [],
            'attr': 'static' if (ivk[inst]['class'] == 1) else 'normal',
            'init': True if (c.find(';-><init>(') > -1) else False,
            'site': 'api',
            'ret': {
                'type': name.split(')')[-1],
                'var': None,
                'line': None,
            },
        }
        self.__get_prms(c, vdata[i])
        self.__get_prm_types(name, vdata[i])
        self.__is_not_api(name, vdata[i])
        if (vdata[i]['ret']['type'] != 'V'):
            self.__find_ret(i, code, vdata[i], vdata, vdata[i]['ret']['type'])
        # Find sources, sinks, modifier, and changer
        self.detect_api(vdata, i, path)
        if (vdata[i]['site'] == 'thread'):
            self.__rslv_thread(vdata[i])

    def __get_prms(self, c, idata):
        prms = c[c.find('{') + 1:c.find('}')]
        if (prms.find(' .. ') > -1):
            attr = prms.split(' ')[0][0]
            s = int(prms.split(' ')[0][1:])
            e = int(prms.split(' ')[-1][1:]) + 1
            idata['prms'] = [attr + str(i) for i in range(s, e)]
        elif (len(prms) > 0):
            idata['prms'] = prms.split(', ')

    def __get_prm_types(self, c, idata):
        s = c.find('(') + 1
        e = c.find(')')
        prms = c[s:e]
        itr = re.finditer(r'\[*[VZBSCIJFD](?![a-z])|\[*L[a-zA-Z]', prms)
        offst = 0
        for i in itr:
            prm_type = i.group()
            if (len(prm_type) > 1 and re.match(r'^\[*L', prm_type)):
                prm_type = prms[i.start():i.start() + prms[i.start():].find(';') + 1]
            if (offst <= i.start()):
                idata['prm_types'].append(prm_type)
                if (prm_type in ['J', 'D']):
                    idata['prm_types'].append(prm_type)
                offst += len(prm_type)

    def __find_ret(self, i, code, idata, vdata, typ):
        l = i
        while True:
            i += 1
            c = code[i].strip(' ')
            if (c != '' and not c.startswith(':') and not c.startswith('.')):
                break
        if (c.startswith('move-result')):
            v = c.split(' ')[-1]
            offset, convert = self.__adjust_mv_rslt_offset(i, v, typ, code)
            idata['ret']['var'] = v
            idata['ret']['line'] = i
            idata['ret']['offset'] = offset
            idata['ret']['convert'] = convert
            vdata[i] = {
                'kind': 'move-result',
                'ivk': l,
                'dst': c.split(' ')[-1],
                'type': typ,
            }

    def __adjust_mv_rslt_offset(self, i, v, typ, code):
        if (
            code[i + 1].find(':try_end_') > -1 and
            code[i + 2].find('.catch ') > -1
        ):
            return 3, typ
        if (
            code[i + 2].endswith(v + ', ' + v) and
            code[i + 2].find('-to-') > -1
        ):
            new_type = code[i + 2].split('-to-')[1].split(' ')[0]
            if (new_type == 'byte'): new_type = 'B'
            elif (new_type == 'short'): new_type = 'S'
            elif (new_type == 'char'): new_type = 'C'
            elif (new_type == 'int'): new_type = 'I'
            elif (new_type == 'long'): new_type = 'J'
            elif (new_type == 'float'): new_type = 'F'
            elif (new_type == 'double'): new_type = 'D'
            return 3, new_type
        return 1, typ

    def __is_not_api(self, name, idata):
        clss = (name[1:].split('->')[0][:-1] + '.smali').split('/')
        for dex, dirs in self.smalis['index'].items():
            path = self.__search_clss_in_index(clss, dirs)
            if (path is not None):
                path = self.__search_method(path, name.split('->')[-1])
                if (path is not None):
                    idata['site'] = path
                    break

    def __search_clss_in_index(self, clss, dirs):
        target = clss[0]
        if (target in dirs.keys()):
            if (len(clss) > 1):
                return self.__search_clss_in_index(clss[1:], dirs[target])
            else:
                return dirs[target]['path']
        return None

    def __search_method(self, path, method):
        if (method in self.smalis['data'][path]['methods'].keys()):
            return path
        else:
            clss = (self.smalis['data'][path]['super'][1:-1] + '.smali').split('/')
            for dirs in self.smalis['index'].values():
                path = self.__search_clss_in_index(clss, dirs)
                if (path is not None):
                    return self.__search_method(path, method)
        return None

    def __get_path(self, name):
        clss = (name[1:].split('->')[0][:-1] + '.smali').split('/')
        for dex, dirs in self.smalis['index'].items():
            path = self.__search_clss_in_index(clss, dirs)
            if (path is not None):
                return path
        return None

    def __rslv_thread(self, idata):
        path = self.__get_path(idata['class'] + '->')
        if (path is None):
            return
        if (idata['thread']['callee'] in self.smalis['data'][path]['methods'].keys()):
            idata['thread']['path'] = path
            idata['thread']['start'] = \
                self.smalis['data'][path]['methods'][idata['thread']['callee']]['start']
            self.smalis['data'][path]['methods'][idata['thread']['callee']]['thread'] = \
                'field_undefined'
