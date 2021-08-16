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

from .source import source
from .sink import sink
from .changer import name_changer, thread_changer


class ApiDetector():
    def detect_api(self, vdata, i, path):
        self.__detect_source(vdata, i, path)
        self.__detect_sink(vdata[i], path)
        self.__detect_changer(vdata[i])

    def __detect_source(self, vdata, i, path):
        idata = vdata[i]
        target = idata['class'] + '->' + idata['method']
        for s, val in source.items():
            if (s == target):
                if (val == 'AndroidId'):
                    rslt = self.__chk_android_id(vdata, i, idata)
                    if (not rslt):
                        return
                idata['source'] = val
                self.src_detected = True
        for c, ms in self.user_input_sources.items():
            for m in ms:
                if (c + '->' + m == target):
                    print('User input source found', target)
                    print('  source_calling_path:', path)
                    idata['source'] = 'user_input'

    def __chk_android_id(self, vdata, i, idata):
        for j in range(1, 6):
            if (i - j in vdata.keys() and vdata[i - j]['kind'] == 'const'):
                if (
                    idata['prms'][1] == vdata[i - j]['dst'] and
                    vdata[i - j]['value'] == '"android_id"'
                ):
                    return True
                break
        return False

    def __detect_sink(self, idata, path):
        target = idata['class'] + '->' + idata['method']
        for s in sink:
            if (target.find(s) > -1):
                idata['sink'] = 'privacy_leak'
        for c, ms in self.user_input_sinks.items():
            for m in ms:
                if (c + '->' + m == target):
                    print('User input sink found', target)
                    print('  sink_calling_path:', path)
                    idata['sink'] = 'user_input'

    def __detect_changer(self, idata):
        for clss, method in name_changer.items():
            if (idata['class'] == clss and idata['method'] == method):
                idata['site'] = 'unknown'
                return
        for method, val in thread_changer.items():
            if (idata['method'] == method):
                idata['site'] = 'thread'
                idata['thread'] = val.copy()
