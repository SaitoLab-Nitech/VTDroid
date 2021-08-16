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

from .emulator import emulator as emu


class DataflowTracer(emu.Emulator):
    def trace(self, rec):
        self.__get_info(rec)
        rec_begin, rec_end = self.executed_part.detect(rec)
        if (rec_begin is not None):
            self.emulate(rec_begin.copy(), rec_end.copy())
        self.taint_next_flow(rec_begin, rec)
        data = self.records.get_a_field(rec, 'data')
        self.executed_part.set_method_invocation_flag(data, rec)
        self.records.insert_rec(rec)

    def __get_info(self, rec):
        rec['path'] = self.smalis['ids'][rec['cid']]
        rec['class'] = self.smalis['data'][rec['path']]['class']
        rec['method'], mdata = self.__get_method(rec['path'], rec['line'])
        rec['params'] = mdata['params']
        rec['attr'] = mdata['attr']
        rec['is_method_start'] = (rec['line'] == mdata['start'])
        rec['idata'] = self.__get_idata(rec['line'], mdata)

    def __get_method(self, path, line):
        for method, mdata in self.smalis['data'][path]['methods'].items():
            if (mdata['start'] <= line <= mdata['end']):
                return method, mdata
        return None, None

    def __get_idata(self, line, mdata):
        if (mdata is None):
            return None
        vdata = mdata['vars']
        if (line in vdata.keys()):
            idata = vdata[line].copy()
            if (idata['kind'] == 'move-result'):
                idata['api'] = vdata[idata['ivk']]
            return idata
        return None
