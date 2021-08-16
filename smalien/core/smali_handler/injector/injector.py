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
import os
import shutil

from .smalien_writer import smalien_writer, storage_permission
from .command_handler import command_handler


class Injector():
    smalien_writer = ''

    def inject(self):
        self.aux_clss['dex_num'] = len(self.smalis['index'].keys()) + 1

        Injector.smalien_writer = smalien_writer.replace(
            'TARGET_FLASH_INTERVAL',
            self.flash_interval
        )
        Injector.smalien_writer += command_handler

        self.__add_storage_permission_to_AM()
        self.__mv_excl_smalis()
        self.__write_aux_clss()
        self.__inject_aux_calls()

    def __add_storage_permission_to_AM(self):
        with io.open(
            self.params['tdir'] + 'AndroidManifest.xml',
            'r',
            encoding='utf-8'
        ) as f:
            data = f.read()
            if (data.find(storage_permission) > -1):
                return
        with io.open(
            self.params['tdir'] + 'AndroidManifest.xml',
            'w',
            encoding='utf-8'
        ) as f:
            data = data.split('\n')
            output = data[0] + '\n' + storage_permission + '\n' + '\n'.join(data[1:])
            f.write(output)

    def __mv_excl_smalis(self):
        for es in self.exclusion:
            d = self.__create_aux_dir()
            dst = self.__create_dst(d, es)
            self.__mv_dir(es, dst)

    def __write_aux_clss(self):
        for clss, code in self.aux_clss['code'].items():
            d = self.__create_aux_dir()
            #d = self.params['tdir']+'smali/'
            if (clss.split('_')[-1] == '0'):
                self.__put_SmalienWriter(d)
            output = self.__write_header(clss)
            output += ''.join(code)
            with io.open(d + clss[1:] + '.smali', 'w', encoding='utf-8') as f:
                f.write(output)

    def __create_aux_dir(self):
        new = self.params['tdir'] + 'smali_classes' + str(self.aux_clss['dex_num']) + '/'
        self.__create_dir(new)
        self.aux_clss['dex_num'] += 1
        return new

    def __create_dir(self, path):
        os.mkdir(path)

    def __mv_dir(self, src, dst):
        shutil.move(src, dst)

    def __put_SmalienWriter(self, dst):
        with open(dst + 'SmalienWriter.smali', 'w') as f:
            f.write(Injector.smalien_writer)

    def __write_header(self, clss):
        code = '.class public ' + clss + ';\n'
        code += '.super Ljava/lang/Object;\n\n'
        return code

    def __inject_aux_calls(self):
        for path, data in self.smalis['data'].items():
            dst = self.__get_output_dst(path, data)
            data['dst_path'] = dst
            output = ''
            for i in range(0, data['linage']):
                if (i in data['auxiliary'].keys()):
                    for c in data['auxiliary'][i]:
                        output += c
                output += data['code'][i] + '\n'
            with io.open(dst, 'w', encoding='utf-8') as f:
                f.write(output)

    def __get_output_dst(self, path, data):
        dp = self.__get_dex_path(path)
        if (dp not in self.meth_refs['dex'].keys()):
            self.meth_refs['dex'][dp] = {
                'cntr': data['meth_refs'],
                'dst': 'original',
            }
            return path
        self.meth_refs['dex'][dp]['cntr'] += data['meth_refs']
        if (self.meth_refs['dex'][dp]['cntr'] > self.meth_refs['lmt']):
            self.meth_refs['dex'][dp]['cntr'] = data['meth_refs']
            self.meth_refs['dex'][dp]['dst'] = self.__create_aux_dir()
        if (self.meth_refs['dex'][dp]['dst'] == 'original'):
            return path
        else:
            self.__rm_path(path)
        return self.__create_dst(self.meth_refs['dex'][dp]['dst'], path)

    def __get_dex_path(self, path):
        for dex in self.smalis['index'].keys():
            if path.startswith(dex):
                return dex + '/'

    def __rm_path(self, path):
        os.remove(path)

    def __create_dst(self, dex, path):
        sub = '/'.join(path.split('/smali')[-1].split('/')[1:])
        for d in sub.split('/')[:-1]:
            dex += d + '/'
            if (not os.path.isdir(dex)):
                self.__create_dir(dex)
        return dex + path.split('/')[-1]
