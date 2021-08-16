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

from ..dalvik_bytecode import obscr


class ObscrExmnr():
    def examine_obscr(self, i, inst, c, mdata, vdata, code):
        clss = obscr[inst]['class']
        count_meth_ref = False
        if (clss == 0):
            self.__const_exmnr(i, c, inst, vdata)
        elif (clss == 1):
            self.__cmp_exmnr(i, c, inst, vdata)
        elif (clss == 2):
            self.__ret_exmnr(i, c, mdata, vdata)
        elif (clss == 3):
            if ('filled' in obscr[inst].keys()):
                self.__filled_new_array_exmnr(i, c, vdata, code)
            else:
                self.__array_exmnr(i, c, vdata)
        elif (clss == 4):
            self.__excp_exmnr(i, c, vdata)
        elif (clss == 5):
            self.__instnc_exmnr(i, c, vdata)
            count_meth_ref = True
        elif (clss == 6):
            self.__get_exmnr(i, c, inst, vdata, code)
            count_meth_ref = True
        elif (clss == 7):
            self.__put_exmnr(i, c, inst, vdata)
            count_meth_ref = True
        elif (clss == 8):
            self.__aget_exmnr(i, c, inst, vdata, mdata, code)
        elif (clss == 9):
            self.__aput_exmnr(i, c, inst, vdata, mdata, code)
        return count_meth_ref

    def __const_exmnr(self, i, c, inst, vdata):
        value = ' '.join(c.split(', ')[1:])
        data_type = obscr[inst]['type']
        if (data_type == 'numeric'):
            value = value.split('#')[0]
            value = value.rstrip(' ')
            value = value.rstrip('L')
            value = str(int(value, 16))
        elif (data_type == 'string'):
            value = value[1:-1]
        else:
            print('[CONST] Rare instruction found', c)
            value = None
        vdata[i] = {
            'kind': 'const',
            'dst': c.split(' ')[1].rstrip(','),
            'value': value,
            'inst': inst,
        }

    def __cmp_exmnr(self, i, c, inst, vdata):
        data_type = obscr[inst]['type']
        vdata[i] = {
            'kind': 'cmp',
            'objs': c.split(', ')[1:],
            'dst': c.split(' ')[1].rstrip(','),
            'inst': inst,
            'type': data_type,
        }

    def __ret_exmnr(self, i, c, mdata, vdata):
        if (len(c.split(' ')) > 1):
            src = c.split(' ')[-1]
            mdata['ret']['vars'].append(src)
        else:
            src = None
        vdata[i] = {
            'kind': 'ret',
            'src': src,
            'type': mdata['ret']['type'],
            'dst': None,
        }

    def __array_exmnr(self, i, c, vdata):
        prms = [p.rstrip(',') for p in c.split(' ')[1:]]
        vdata[i] = {
            'kind': 'array',
            'dst': prms[0],
        }
        if (len(prms) > 2):
            vdata[i]['type'] = prms[2]

    def __filled_new_array_exmnr(self, i, c, vdata, code):
        prms = self.__get_fna_prms(c)
        dst = self.__get_fna_dst(i, code)
        vdata[i] = {
            'kind': 'fn_array',
            'srcs': prms,
            'type': c.split(', ')[-1],
            'dst': dst,
        }

    def __get_fna_prms(self, c):
        prms = c[c.find('{') + 1:c.find('}')]
        if (prms.find(' .. ') > -1):
            attr = prms.split(' ')[0][0]
            s = int(prms.split(' ')[0][1:])
            e = int(prms.split(' ')[-1][1:]) + 1
            return [attr + str(i) for i in range(s, e)]
        elif (len(prms) > 0):
            return prms.split(', ')

    def __get_fna_dst(self, i, code):
        l = i
        while True:
            i += 1
            c = code[i].strip(' ')
            if (c != '' and not c.startswith(':') and not c.startswith('.')):
                break
        if (c.startswith('move-result')):
            return c.split(' ')[-1]
        return None

    def __excp_exmnr(self, i, c, vdata):
        vdata[i] = {
            'kind': 'exception',
            'dst': c.split(' ')[-1],
        }

    def __instnc_exmnr(self, i, c, vdata):
        vdata[i] = {
            'kind': 'instance',
            'dst': c.split(' ')[1].rstrip(','),
            'inst': c.split(' ')[0],
            'type': c.split(' ')[-1],
        }

    def __get_exmnr(self, i, c, inst, vdata, code):
        prms = [p.rstrip(',') for p in c.split(' ')[1:]]
        vdata[i] = {
            'kind': inst[0] + 'get',
            'src': prms[1],
            'dst': prms[0],
            'type': prms[-1].split(':')[-1],
            'obj': True if (inst.find('-object') > -1) else False,
            'instance': prms[-1],
            'inj_offset': self.__calculate_injection_offset_for_getter(i, code),
        }
        if (len(prms) > 2):
            vdata[i]['pos'] = prms[2]

    def __calculate_injection_offset_for_getter(self, i, code):
        offset = 1
        if (code[i + 1].find('    :try_end_') > -1):
            num_catches = self.__count_catches(i + 2, code)
            offset = 2 + num_catches
        return offset

    def __count_catches(self, i, code):
        j = 0
        while True:
            if (code[i + j].find('    .catch ') < 0):
                return j
            j += 1

    def __put_exmnr(self, i, c, inst, vdata):
        prms = [p.rstrip(',') for p in c.split(' ')[1:]]
        vdata[i] = {
            'kind': inst[0] + 'put',
            'src': prms[0],
            'dst': prms[1],
            'type': prms[-1].split(':')[-1],
            'instance': prms[-1],
        }
        if (len(prms) > 2):
            vdata[i]['pos'] = prms[2]

    def __aget_exmnr(self, i, c, inst, vdata, mdata, code):
        prms = [p.rstrip(',') for p in c.split(' ')[1:]]
        vdata[i] = {
            'kind': 'aget',
            'src': prms[1],
            'dst': prms[0],
            'pos': prms[2],
        }
        vdata[i]['type'] = self.__resolve_array_type(
            i,
            vdata[i]['src'],
            inst,
            vdata,
            mdata,
            code
        )
        vdata[i]['dst_type'] = vdata[i]['type'][1:]

    def __aput_exmnr(self, i, c, inst, vdata, mdata, code):
        prms = [p.rstrip(',') for p in c.split(' ')[1:]]
        vdata[i] = {
            'kind': 'aput',
            'src': prms[0],
            'dst': prms[1],
            'pos': prms[2],
        }
        vdata[i]['type'] = self.__resolve_array_type(
            i,
            vdata[i]['dst'],
            inst,
            vdata,
            mdata,
            code
        )

    def __resolve_array_type(self, i, v, inst, vdata, mdata, code):
        #if (v[0] == 'p'):
        #  return mdata['params']['types'][mdata['params']['vars'].index(v)]
        rslt = self.__search_prev_data(i, v, code, vdata, mdata)
        if (rslt == '[unknown'):
            if (inst.split('-')[-1] == 'byte'):
                rslt = '[B'
            if (inst.split('-')[-1] == 'short'):
                rslt = '[S'
            if (inst.split('-')[-1] == 'char'):
                rslt = '[C'
            if (inst.split('-')[-1] == 'boolean'):
                rslt = '[Z'
        return rslt

    def __search_prev_data(self, i, v, code, vdata, mdata):
        for j in range(i - 1, mdata['start'], -1):
            if (j in vdata.keys()):
                if ('dst' in vdata[j].keys() and vdata[j]['dst'] == v):
                    if ('dst_type' in vdata[j].keys()):
                        return vdata[j]['dst_type']
                    elif ('type' in vdata[j].keys() and vdata[j]['type'][0] == '['):
                        return vdata[j]['type']
                    else:
                        break
                elif (
                    vdata[j]['kind'] in ['cond', 'goto_label', 'switch_label', 'catch_label']
                ):
                    break
        return '[unknown'
