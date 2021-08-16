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

from ..dalvik_bytecode import exp_v2v


class ExpV2VExmnr():
    def examine_exp_v2v(self, i, inst, c, vdata, code, mdata):
        clss = exp_v2v[inst]['class']
        prms = [p.replace(',', '') for p in c.split(' ')[1:]]
        if (clss == 0):
            src = [prms[1]]
        elif (clss == 1):
            src = prms
        elif (clss == 2):
            src = prms[1:]
        if ('type' in exp_v2v[inst].keys()):
            data_type = exp_v2v[inst]['type']
        else:
            data_type = 'unknown'
        vdata[i] = {
            'kind': 'exp_v2v',
            'inst': inst,
            'srcs': src,
            'dst': prms[0],
            'type': data_type,
        }
        vdata[i]['inj_offset'] = self.__calculate_injection_offset(
            i,
            prms[0],
            vdata[i],
            code,
            mdata,
            vdata
        )

    def __calculate_injection_offset(self, i, i_dst, idata, code, mdata, vdata):
        offset = 1
        if (code[i + 2].find('    move ') > -1):
            second_move_dst = code[i + 2].split('move ')[-1].split(', ')[0]
            second_move_src = code[i + 2].split('move ')[-1].split(', ')[1]
            if (second_move_dst != i_dst and second_move_src == i_dst):
                if (
                    code[i + 4].find('    move ') > -1 and
                    code[i + 4].split('move ')[-1].split(', ')[0] != i_dst
                ):
                    offset = 5
                elif (
                    code[i + 4].find('    move-object ') > -1 and
                    code[i + 4].split('move-object ')[-1].split(', ')[0] == i_dst
                ):
                    code[i] = code[i].replace(i_dst + ', ', second_move_dst + ', ', 1)
                    idata['dst'] = second_move_dst
                    code[ i + 2] = '    move ' + second_move_dst + ', ' + second_move_dst
                elif (
                    code[i + 4].find('    move-wide ') > -1 and
                    code[i + 4].split('move-wide ')[-1].split(', ')[0] == i_dst
                ):
                    code[i] = code[i].replace(i_dst + ', ', second_move_dst + ', ', 1)
                    idata['dst'] = second_move_dst
                    code[ i + 2] = '    move ' + second_move_dst + ', ' + second_move_dst
        elif (code[i + 1].find('    :try_end_') > -1):
            num_catches = self.__count_catches(i + 2, code)
            offset = 2 + num_catches
        elif (
            code[i + 2].find('int-to-long') > -1 or
            code[i + 2].find('long-to-int') > -1 or
            code[i + 2].find('float-to-int') > -1
        ):
            result, conv_dst, conv_src, prev_move_result = self.__detect_type_conversion_code(
                i,
                i_dst,
                idata,
                code
            )
            if (result):
                local_available_regs = 16 - len(mdata['params']['types']) - 1
                if (mdata['vnum'] < local_available_regs):
                    tmp_reg = 'v' + str(mdata['vnum'])
                    # Rewrite code
                    if (result == 'mr_cal_tc'):
                        idata['srcs'].remove(prev_move_result)
                        idata['srcs'].append(tmp_reg)
                        code[i] = code[i][::-1].replace(
                            prev_move_result[::-1],
                            tmp_reg[::-1],
                            1
                        )
                        code[i] = code[i][::-1]
                        code[i - 2] = '    move-result ' + tmp_reg
                        vdata[i - 2]['dst'] = tmp_reg
                        vdata[vdata[i - 2]['ivk']]['ret']['var'] = tmp_reg

                    additional = 1
                    if (code[i].find('long') > -1 or code[i].find('double') > -1):
                        additional = 2
                    code[mdata['start'] + 1] = '    .locals ' + str(mdata['vnum'] + additional)
                    if (code[i].find('/2addr ') < 0):
                        code[i] = code[i].replace(i_dst, tmp_reg, 1)
                    else:
                        split_code = code[i].split('/2addr ')
                        code[i] = split_code[0] + ' ' + tmp_reg + ', ' + split_code[1]
                    idata['dst'] = tmp_reg
                    code[i + 2] = code[i + 2].replace(
                        ', ' + conv_src,
                        ', ' + tmp_reg
                    )
        return offset

    def __detect_type_conversion_code(self, i, i_dst, idata, code):
        conv_dst = code[i + 2].split(', ')[0].split(' ')[-1]
        conv_src = code[i + 2].split(', ')[-1]
        prev_move_result = None
        if (
            code[i - 2].find('    move-result ') > -1 and
            code[i - 2].split(' ')[-1] in idata['srcs']
        ):
            prev_move_result = code[i - 2].split(' ')[-1]
        if (prev_move_result is not None):
            if (conv_src == i_dst and conv_dst == prev_move_result):
                return 'mr_cal_tc', conv_dst, conv_src, prev_move_result
        else:
            if (conv_dst == conv_src and conv_dst == i_dst):
                return 'cal_tc', conv_dst, conv_src, prev_move_result
        return False, None, None, None

    def __count_catches(self, i, code):
        j = 0
        while True:
            if (code[i + j].find('    .catch ') < 0):
                return j
            j += 1
