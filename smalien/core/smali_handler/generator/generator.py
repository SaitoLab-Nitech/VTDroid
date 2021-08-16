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
from pprint import pprint

from .bytecode import bytecode


class Generator():
    def generate(self):
        instruction_counter = {
            'api': 0,
            'non-api': 0,
            'control': 0,
            'array': 0,
            'source': 0,
            'sink': 0,
        }
        for path, data in self.smalis['data'].items():
            self.meth_refs['cntr'] = 0
            # Generate for logging
            for method, mdata in data['methods'].items():
                if (mdata['attr'] in ['native', 'abstract']):
                    continue
                # Params at a head
                if ('thread' not in mdata.keys()):
                    self.__generate_for_head(
                        data['auxiliary'],
                        data['id'],
                        mdata['params'],
                        mdata['start']
                    )
                # Body
                for i, idata in mdata['vars'].items():
                    kind = idata['kind']
                    if (kind in ['sput', 'iput', 'aput']):
                        self.__generate_for_put(
                            data['auxiliary'],
                            data['id'],
                            i,
                            idata
                        )
                        if (kind == 'aput'): instruction_counter['array'] += 1
                    elif (kind in ['aget', 'sget', 'iget']):
                        self.__generate_for_get(
                            data['auxiliary'],
                            data['id'],
                            i,
                            idata
                        )
                        if (kind == 'aget'): instruction_counter['array'] += 1
                    elif (kind in ['if', 'switch']):
                        idata['log'] = True
                        self.__generate_for_brnch(data['auxiliary'], data['id'], i)
                        instruction_counter['control'] += 1
                    elif (kind == 'switch_label'):
                        idata['log'] = True
                        self.__generate_tagging(data['auxiliary'], data['id'], i, i + 1)
                    #elif (kind == 'catch_label'):
                    #  idata['log'] = True
                    #  self.__generate_tagging(
                    #      data['auxiliary'],
                    #      data['id'],
                    #      i,
                    #      i+idata['offset']
                    #  )
                    elif (kind == 'ivk'):
                        idata['log'] = True
                        self.__generate_for_ivk(data['auxiliary'], data['id'], i, idata)
                        if ('source' in idata.keys() and idata['source'] == 'IMEI1'):
                            instruction_counter['source'] += 1
                        if ('sink' in idata.keys()):
                            instruction_counter['sink'] += 1
                        if (idata['site'] == 'api'):
                            instruction_counter['api'] += 1
                        else:
                            instruction_counter['non-api'] += 1
                    elif (kind == 'exp_v2v'):
                        idata['log'] = True
                        self.__generate_for_exp_v2v(data['auxiliary'], data['id'], i, idata)
                    elif (kind == 'cmp'):
                        idata['log'] = True
                        self.__generate_for_cmp(data['auxiliary'], data['id'], i, idata)
            data['meth_refs'] += self.meth_refs['cntr']
            self.meth_refs['aux'] += self.meth_refs['cntr']

        print('Instruction counter')
        pprint(instruction_counter)

    def __generate_for_head(self, aux, cid, prms, s):
        i = 0
        logged = False
        while i < len(prms['types']):
            if (prms['types'][i] in self.trgt_typs):
                self.__define_logging_for_var(
                    prms['vars'][i],
                    prms['types'][i],
                    aux,
                    cid,
                    s,
                    s + 1
                )
                logged = True
            i += 2 if (prms['types'][i] in ['J', 'D']) else 1
        if (not logged):
            self.__generate_tagging(aux, cid, s, s + 1)

    def __generate_for_brnch(self, aux, cid, i):
        tag = str(cid) + '_' + str(i)
        method = 'Log_' + tag + '()V'
        clss = self.__get_logging_clss(1)
        self.meth_refs['cntr'] += 1
        for spot in [i, i + 1]:
            if (spot not in aux.keys()):
                aux[spot] = []
            aux[spot].append('invoke-static {}, ' + clss + ';->' + method + '\n')
        self.aux_clss['code'][clss].extend([
            '.method public static ' + method + '\n',
            '  .locals 1\n',
            '  const-string v0, "' + tag + '"\n',
        ])
        self.aux_clss['code'][clss].extend(bytecode['footer_tag'])

    def __generate_tagging(self, aux, cid, i, spot):
        tag = str(cid) + '_' + str(i)
        method = 'Log_' + tag + '()V'
        clss = self.__get_logging_clss(1)
        if (spot not in aux.keys()):
            aux[spot] = []
        aux[spot].append('invoke-static {}, ' + clss + ';->' + method + '\n')
        self.aux_clss['code'][clss].extend([
            '.method public static ' + method + '\n',
            '  .locals 1\n',
            '  const-string v0, "' + tag + '"\n',
        ])
        self.aux_clss['code'][clss].extend(bytecode['footer_tag'])

    def __generate_for_put(self, aux, cid, i, idata):
        if (idata['type'] in self.trgt_typs):
            #src = idata['dst'] if idata['kind'] == 'aput' else idata['src']
            src = idata['src']
            pos = i
            #pos = i + 1 if idata['kind'] == 'aput' else i
            if idata['kind'] == 'aput':
                data_type = idata['type'][1:]
            else:
                data_type = idata['type']
            self.__define_logging_for_var(src, data_type, aux, cid, i, pos)
            idata['log'] = True
            if (idata['kind'] == 'aput'):
                self.__define_logging_for_var(idata['pos'], 'I', aux, cid, i, i)

    def __generate_for_get(self, aux, cid, i, idata):
        typ = idata['dst_type'] if idata['kind'] == 'aget' else idata['type']
        #typ = idata['type'][1:] if idata['kind'] == 'aget' else idata['type']
        if (typ in self.trgt_typs):
            if (idata['kind'] == 'aget'):
                self.__define_logging_for_var(idata['pos'], 'I', aux, cid, i, i)
                self.__define_logging_for_var(idata['dst'], typ, aux, cid, i, i + 1)
            else:
                self.__define_logging_for_var(
                    idata['dst'],
                    typ,
                    aux,
                    cid,
                    i,
                    i + idata['inj_offset']
                )
            idata['log'] = True

    def __generate_for_ivk(self, aux, cid, i, idata):
        # Check if thread create
        if (idata['site'] == 'thread' and 'path' in idata['thread'].keys()):
            self.__generate_for_thread_ivk(aux, cid, i, idata)
            return
        types = idata['prm_types'].copy()
        if (idata['init']):
            if (len(idata['prms']) > 1):
                prms = idata['prms'][1:]
                types = idata['prm_types'][1:]
            else:
                prms = []
                types = []
        else:
            prms = idata['prms']
        # Params
        j = 0
        logged = False
        log_params_after_ivk = []
        while j < len(types):
            if (types[j] in self.trgt_typs):
                self.__define_logging_for_var(prms[j], types[j], aux, cid, i, i)
                logged = True
                if (idata['site'] == 'api' and types[j][0] == '['):
                    log_params_after_ivk.append([prms[j], types[j]])
            elif (types[j] == 'Ljava/lang/Object;'):
                chk, trgt_type = self.__chk_method_for_obj_logging(idata)
                if (chk):
                    self.__define_logging_for_var(prms[j], trgt_type, aux, cid, i, i)
                    logged = True
            j += 2 if (types[j] in ['J', 'D']) else 1
        if (not logged):
            self.__generate_tagging(aux, cid, i, i)
        # System Command
        if (
            idata['class'] == 'Ljava/lang/Runtime;' and
            idata['method'] == 'exec([Ljava/lang/String;)Ljava/lang/Process;'
        ):
            self.__define_system_command_logging(
                prms[1],
                '[Ljava/lang/String;',
                aux,
                cid,
                i,
                i
            )
        # Params after api ivk
        ret = idata['ret']
        for param in log_params_after_ivk:
            result = self.__check_equals_to_ret_var(param[0], ret)
            if (not result):
                if (ret['line'] is not None):
                    self.__define_param_ret_logging(
                        param[0],
                        param[1],
                        aux,
                        cid,
                        i,
                        ret['line'] + ret['offset']
                    )
                else:
                    self.__define_param_ret_logging(
                        param[0],
                        param[1],
                        aux,
                        cid,
                        i,
                        i + 1
                    )
        # Ret
        if (ret['var'] is not None):
            if (ret['type'] in self.trgt_typs):
                self.__define_logging_for_var(
                    ret['var'],
                    ret['convert'],
                    aux,
                    cid,
                    ret['line'],
                    ret['line'] + ret['offset']
                )
            elif ('source' in idata.keys() and idata['source'] == 'user_input'):
                print('Generating for USER_INPUT_SOURCE')
                self.__define_logging_for_var(
                    ret['var'],
                    ret['convert'],
                    aux,
                    cid,
                    ret['line'],
                    ret['line'] + ret['offset']
                )
            else:
                self.__generate_tagging(
                    aux,
                    cid,
                    ret['line'],
                    ret['line'] + ret['offset']
                )

    def __check_equals_to_ret_var(self, target_var, ret_data):
        if (ret_data['var'] is not None):
            if (target_var == ret_data['var']):
                return True
            elif (ret_data['convert'] in ['J', 'D']):
                high_half_var = ret_data['var'][0] + str(int(ret_data['var'][1:]) + 1)
                if (target_var == high_half_var):
                    return True
        return False

    def __generate_for_thread_ivk(self, aux, cid, i, idata):
        callee_data = self.smalis['data'][idata['thread']['path']]
        if (callee_data['methods'][idata['thread']['callee']]['attr'] == 'abstract'):
            return
        # Bytecode for the caller
        self.__generate_for_thread_ivk_caller(aux, cid, i, idata)
        # Bytecode for the callee
        self.__generate_for_thread_ivk_callee(
            callee_data['auxiliary'],
            callee_data['id'],
            idata['thread']['start'],
            idata
        )

    def __generate_for_thread_ivk_caller(self, aux, cid, i, idata):
        tag = str(cid) + '_' + str(i)
        method = 'Log_' + tag + '(' + idata['class'] + ')V'
        clss = self.__get_logging_clss(3)
        if (i not in aux.keys()):
            aux[i] = []
        aux[i].append(
            'invoke-static/range {' + idata['prms'][0] + ' .. ' +
            idata['prms'][0] + '}, ' + clss + ';->' + method + '\n'
        )
        self.aux_clss['code'][clss].extend([
            '.method public static ' + method + '\n',
            '  .locals 1\n',
            '  invoke-static {}, Landroid/os/Process;->myTid()I\n',
            '  move-result v0\n',
            '  iput v0, p0, ' + idata['class'] + '->SmalienTID:I\n',
            '  const-string v0, "' + tag + '"\n',
        ])
        self.aux_clss['code'][clss].extend(bytecode['footer_tag'])

    def __generate_for_thread_ivk_callee(self, aux, cid, i, idata):
        spot = i + 1
        tag = str(cid) + '_' + str(i) + '_tid'
        method = 'Log_' + tag + '(' + idata['class'] + ')V'
        clss = self.__get_logging_clss(2)
        if (spot not in aux.keys()):
            aux[spot] = []
        aux[spot].append(
            'invoke-static/range {p0 .. p0}, ' + clss + ';->' +
            method + '\n'
        )
        self.aux_clss['code'][clss].extend([
            '.method public static ' + method + '\n',
            '  .locals 2\n',
            '  const-string v1, "' + tag + '"\n',
            '  :try_start_0\n',
            '  iget v0, p0, ' + idata['class'] + '->SmalienTID:I\n',
            '  invoke-static {v0}, Ljava/lang/String;->valueOf(I)Ljava/lang/String;\n',
            '  move-result-object v0\n',
        ])
        self.aux_clss['code'][clss].extend(bytecode['footer_val'])
        # Define the instance field SmalienTID
        field_msg = \
            self.smalis['data'][idata['thread']['path']]['methods'][idata['thread']['callee']]['thread']
        if (field_msg == 'field_undefined'):
            self.smalis['data'][idata['thread']['path']]['methods'][idata['thread']['callee']]['thread'] = \
                'field_defined'
            if (4 not in aux.keys()):
                aux[4] = []
            aux[4].extend(bytecode['tid_field_define'])
            # Make the class public
            original = self.smalis['data'][idata['thread']['path']]['code'][0]
            self.smalis['data'][idata['thread']['path']]['code'][0] = re.sub(
                '^\.class.* L',
                '.class public L',
                original
            )

    def __chk_method_for_obj_logging(self, idata):
        if (idata['class'] + '->' + idata['method'] in self.trgt_obj_clss_ivks.keys()):
            return True, self.trgt_obj_clss_ivks[idata['class'] + '->' + idata['method']]
        return False, None

    def __generate_for_exp_v2v(self, aux, cid, i, idata):
        typ = idata['type']
        if (typ in self.trgt_typs):
            self.__define_logging_for_var(
                idata['dst'],
                typ,
                aux,
                cid,
                i,
                i + idata['inj_offset']
            )
            idata['log'] = True

    def __generate_for_cmp(self, aux, cid, i, idata):
        typ = idata['type']
        if (typ in self.trgt_typs):
            for obj in idata['objs']:
                self.__define_logging_for_var(obj, typ, aux, cid, i, i)
            idata['log'] = True

    def __define_logging_for_var(self, prm, typ, aux, cid, i, spot):
        tag = str(cid) + '_' + str(i) + '_' + prm
        if (typ in ['serialization', 'String.valueOf(Object)', 'Landroid/text/Editable;']):
            method = 'Log_' + tag + '(Ljava/lang/Object;)V'
            num = 8 if (typ == 'serialization') else 2
        else:
            method = 'Log_' + tag + '(' + typ + ')V'
            if (typ[0] == '['):
                num = 6 if (typ == '[B') else 4
            else:
                num = 1 if (typ == 'Ljava/lang/String;') else 2
        clss = self.__get_logging_clss(num)
        if (spot not in aux.keys()):
            aux[spot] = []
        if (typ in ['J', 'D']):
            prm2 = prm[0] + str(int(prm[1:]) + 1)
            aux[spot].append(
                'invoke-static/range {' + prm + ' .. ' + prm2 + '}, ' +
                clss + ';->' + method + '\n'
            )
        else:
            aux[spot].append(
                'invoke-static/range {' + prm + ' .. ' + prm + '}, ' +
                clss + ';->' + method + '\n'
            )

        self.aux_clss['code'][clss].extend([
            '.method public static ' + method + '\n',
            '  .locals 7\n',
            '  const-string v1, "' + tag + '"\n',
        ])
        if (typ != 'serialization'):
            self.aux_clss['code'][clss].append('  :try_start_0\n')

        self.aux_clss['code'][clss].extend(bytecode[typ])
        if (typ != 'serialization'):
            self.aux_clss['code'][clss].extend(bytecode['footer_val'])

    def __define_param_ret_logging(self, prm, typ, aux, cid, i, spot):
        tag = str(cid) + '_' + str(i) + '_' + prm + 'Ret'
        method = 'Log_' + tag + '(' + typ + ')V'
        num = 6
        clss = self.__get_logging_clss(num)
        if (spot not in aux.keys()):
            aux[spot] = []
        aux[spot].append(
            'invoke-static/range {' + prm + ' .. ' + prm + '}, ' +
            clss + ';->' + method + '\n'
        )

        self.aux_clss['code'][clss].extend([
            '.method public static ' + method + '\n',
            '  .locals 7\n',
            '  const-string v1, "' + tag + '"\n',
        ])
        self.aux_clss['code'][clss].append('  :try_start_0\n')

        self.aux_clss['code'][clss].extend(bytecode[typ])
        self.aux_clss['code'][clss].extend(bytecode['footer_val'])

    def __define_system_command_logging(self, prm, typ, aux, cid, i, spot):
        tag = str(cid) + '_' + str(i) + '_' + 'SystemCommandResult'
        method = 'Log_' + tag + '(' + typ + ')V'
        num = 2
        clss = self.__get_logging_clss(num)
        if (spot not in aux.keys()):
            aux[spot] = []
        aux[spot].append(
            'invoke-static/range {' + prm + ' .. ' + prm + '}, ' +
            clss + ';->' + method + '\n'
        )

        self.aux_clss['code'][clss].extend([
            '.method public static ' + method + '\n',
            '  .locals 1\n',
            '  const-string v0, "' + tag + '"\n',
        ])
        self.aux_clss['code'][clss].extend(bytecode['system_command_logging'])

    def __get_logging_clss(self, num):
        self.meth_refs['cntr'] += 1
        self.aux_clss['cntr'] += num
        if (self.aux_clss['cntr'] > self.aux_clss['lmt']):
            new = self.aux_clss['crnt'].split('_')[0] + '_'
            new += str(int(self.aux_clss['crnt'].split('_')[-1]) + 1)
            self.aux_clss['code'][new] = []
            self.aux_clss['crnt'] = new
            self.aux_clss['cntr'] = num
        return self.aux_clss['crnt']
