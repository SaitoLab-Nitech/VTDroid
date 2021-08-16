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

from ..dalvik_bytecode import brnch, label


class BrnchExmnr():
    def examine_brnch(self, i, inst, c, mdata, vdata):
        clss = brnch[inst]['class']
        if (clss == 0):
            self.__if_exmnr(i, c, vdata, inst)
        elif (clss == 1):
            self.__switch_exmnr(i, c, vdata)
        elif (clss == 2):
            self.__goto_exmnr(i, c, vdata)
        elif (clss == 3):
            self.__throw_exmnr(i, c, vdata)

    def __if_exmnr(self, i, c, vdata, inst):
        vdata[i] = {
            'kind': 'if',
            'vars': [v.replace(',', '') for v in c.split(' ')[1:-1]],
            'label': c.split(' ')[-1],
            'inst': inst,
        }

    def __switch_exmnr(self, i, c, vdata):
        vdata[i] = {
            'kind': 'switch',
            'vars': [c.split(' ')[-2].replace(',', '')],
            'label': c.split(' ')[-1],
        }

    def __goto_exmnr(self, i, c, vdata):
        vdata[i] = {
            'kind': 'goto',
            'label': c.split(' ')[-1],
        }

    def examine_label(self, i, inst, c, mdata, vdata, code, current_try_ids):
        l = inst
        inst = '_'.join(inst.split('_')[:-1]) if (inst.find('_') > -1) else inst
        clss = label[inst]['class']
        vdata[i] = {'label': l}
        if (clss == 0):
            vdata[i]['kind'] = 'cond'
            vdata[i]['cond_line'] = i
        elif (clss == 1):
            vdata[i]['kind'] = 'goto_label'
        elif (clss == 2):
            if (inst.find('_data') < 0):
                vdata[i]['kind'] = 'switch_label'
            else:
                vdata[i]['kind'] = 'switch_data'
                vdata[i]['labels'] = self.__extract_switch_labels(i, mdata, code)
        elif (clss == 3):
            vdata[i]['kind'] = 'try_start'
            try_id = l.split('_')[-1]
            current_try_ids.append(try_id)
        elif (clss == 4):
            vdata[i]['kind'] = 'try_end'
            try_id = l.split('_')[-1]
            current_try_ids.remove(try_id)
        elif (clss == 5):
            self.__catch_exmnr(i, c, vdata)
        elif (clss == 6):
            vdata[i]['kind'] = 'catch_label'
            vdata[i]['offset'] = self.__get_catch_offset(i, code)

    def pairing_if_cond_goto_and_try(self, vdata):
        for i, idata in vdata.items():
            if (idata['kind'] == 'if'):
                idata['cond_line'] = self.__get_cond_line(
                    vdata,
                    idata['label'],
                    idata['inst'],
                    i,
                    idata['vars']
                )
            elif (idata['kind'] == 'goto'):
                idata['goto_label_line'] = self.__get_goto_label_line(
                    vdata,
                    idata['label'],
                    i
                )
            elif (idata['kind'] == 'catch'):
                idata['catch_dst'] = self.__get_catch_dst(vdata, idata)
                self.__set_try_catch_path(vdata, idata)

    def __get_cond_line(self, vdata, if_label, if_inst, if_line, if_vars):
        for i, idata in vdata.items():
            if (idata['kind'] == 'cond' and idata['label'] == if_label):
                idata['if_inst'] = if_inst
                idata['if_line'] = if_line
                idata['if_vars'] = if_vars
                return i
        return None

    def __get_goto_label_line(self, vdata, goto_label, goto_line):
        for i, idata in vdata.items():
            if (idata['kind'] == 'goto_label' and idata['label'] == goto_label):
                idata['goto_line'] = goto_line
                return i
        return None

    def __get_catch_dst(self, vdata, catch_data):
        for i, idata in vdata.items():
            if (idata['kind'] == 'catch_label' and idata['label'] == catch_data['catch']):
                return i
        return None

    def __set_try_catch_path(self, vdata, catch_data):
        try_id = catch_data['try_id']
        for i, idata in vdata.items():
            if (try_id in idata['try_ids']):
                idata['try_dsts'].add(catch_data['catch_dst'])

    def __catch_exmnr(self, i, c, vdata):
        labels = c.split(' {')[-1].split('} ')[0].split(' .. ')
        vdata[i]['try_id'] = labels[0].split('_')[-1]
        vdata[i]['try_start'] = labels[0]
        vdata[i]['try_end'] = labels[1]
        vdata[i]['catch'] = c.split(' ')[-1]
        vdata[i]['kind'] = 'catch'

    def __throw_exmnr(self, i, c, vdata):
        vdata[i] = {
            'kind': 'throw',
        }

    def __get_catch_offset(self, i, code):
        if (len(code) > i + 3 and code[i + 3].find('monitor-exit') > -1):
            return 4
        if (code[i + 1].find('move-exception') > -1):
            return 2
        return 1

    def __extract_switch_labels(self, i, mdata, code):
        labels = []
        for i in range(i + 1, mdata['end']):
            if (code[i].find('.end ') > -1):
                break
            if (code[i].find(':') > -1):
                labels.append(code[i].split(' ')[-1])
        return labels
