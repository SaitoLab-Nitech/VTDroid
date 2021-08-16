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
import re
import glob
import shutil
import subprocess
import xml.etree.ElementTree as ElementTree


class ApkHandler():
    def __init__(self, app_info, ks, params_sbi):
        self.params = app_info
        self.ks = ks
        self.params_sbi = params_sbi

    def prologue(self):
        self.cp_target()
        self.unpack()
        self.__reloc_dex()

    def cp_target(self):
        # Move new target to workspace
        subprocess.call(
            'cp ' + self.params['tpath'] + ' ' +
            self.params['workspace'],
            shell=True
        )

    def unpack(self):
        try:
            subprocess.check_output(
                self.params_sbi['apktool']['name'] + ' d --only-main-classes ' +
                self.params['workspace'] + self.params['tapk'] + ' -o ' +
                self.params['tdir'] + ' > /dev/null 2>&1',
                stderr=subprocess.STDOUT,
                shell=True
            )
        except subprocess.CalledProcessError as e:
            print('[!] Failed to unpack')
            print(e.output.decode('utf-8'))
            raise e

    def __reloc_dex(self):
        dirs = glob.glob(self.params['tdir'] + 'smali*')
        num = len(dirs) + 1
        # Doubling the original smali directories
        for i in range(len(dirs)):
            newdir = self.params['tdir'] + 'smali_classes' + str(num + i) + '/'
            os.mkdir(newdir)
            target = next(os.walk(dirs[i]))[1]
            for j in range(int(len(target) / 2)):
                self.__move(dirs[i] + '/' + target[j], newdir)

    def __get_file_path(self, trgt, smali_num):
        rslt = []
        if (os.path.exists(self.params['tdir'] + 'smali' + trgt)):
            rslt.append(self.params['tdir'] + 'smali' + trgt)
        for i in range(2, smali_num):
            if (os.path.exists(self.params['tdir'] + 'smali_classes' + str(i) + trgt)):
                rslt.append(self.params['tdir'] + 'smali_classes' + str(i) + trgt)
        return rslt

    def __move(self, src, dst):
        subprocess.call('mv ' + src + ' ' + dst, shell=True)

    def get_pkg_name(self):
        try:
            output = subprocess.check_output(
                self.params_sbi['aapt'] + ' dump badging ' +
                self.params['workspace'] + self.params['tapk'] +
                ' | grep package',
                stderr=subprocess.STDOUT,
                shell=True
            )
            pkg_name = output.decode('utf-8').split("'")[1]
            self.params['package'] = pkg_name
        except subprocess.CalledProcessError as e:
            print('[!] Failed to get package name')
            print(e.output.decode('utf-8'))
            raise e

    def get_activity_name(self):
        self.params['activity'] = ''
        with io.open(
            self.params['tdir'] + 'AndroidManifest.xml',
            'r',
            encoding='utf-8'
        ) as f:
            AndMan = ElementTree.fromstring(f.read())
            for activity in AndMan.iter('activity'):
                for action in activity.iter('action'):
                    if (
                        action.attrib['{http://schemas.android.com/apk/res/android}name']
                        == 'android.intent.action.MAIN'
                    ):
                        self.params['activity'] = activity.attrib[
                            '{http://schemas.android.com/apk/res/android}name']
                        return
            for activity in AndMan.iter('activity-alias'):
                for action in activity.iter('action'):
                    if (
                        action.attrib['{http://schemas.android.com/apk/res/android}name']
                            == 'android.intent.action.MAIN'
                    ):
                        self.params['activity'] = activity.attrib[
                            '{http://schemas.android.com/apk/res/android}name']
                        return

    def epilogue(self):
        self.__pack()
        self.__sign()
        self.__move_implanted()

    def __pack(self):
        try:
            subprocess.check_output(
                self.params_sbi['apktool']['name'] + ' b ' +
                self.params_sbi['apktool']['p_opt'] + ' ' +
                self.params['tdir'],
                stderr=subprocess.STDOUT,
                shell=True
            )
        except subprocess.CalledProcessError as e:
            print('[!] Failed to pack')
            print(e.output.decode('utf-8'))
            raise e

    def __sign(self):
        try:
            subprocess.check_output(
                self.params_sbi['jarsigner'] + ' -verbose -keystore ' +
                self.ks['key'] + ' -storepass ' + self.ks['kspass'] +
                ' -keypass ' + self.ks['kpass'] + ' ' + self.params['tdir'] +
                'dist/*.apk ' + self.ks['alias'] + ' > /dev/null 2>&1',
                stderr=subprocess.STDOUT,
                shell=True
            )
        except subprocess.CalledProcessError as e:
            print('[!] Failed to sign')
            print(e.output.decode('utf-8'))
            raise e

    def __move_implanted(self):
        subprocess.call(
            'mv ' + self.params['tdir'] + 'dist/*.apk ' +
            self.params['implanted'],
            shell=True
        )
