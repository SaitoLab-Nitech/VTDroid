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


class ExecutedPart():
    def __init__(self, records, smalis):
        self.records = records
        self.smalis = smalis
        self.method_invocations = []

    def set_method_invocation_flag(self, data, rec):
        prvs = data[-1] if (len(data) > 0) else None
        if (
            rec['idata'] is not None and
            rec['idata']['kind'] == 'ivk' and
            rec['idata']['site'] != 'api'
        ):
            if (prvs is None or prvs['line'] != rec['line']):
                # Check prvs to avoid duplication
                rec['called'] = False
                self.method_invocations.append(rec)

    def detect(self, rec):
        prev_rec = None
        if (rec['is_method_start']):
            prev_rec = self.__detect_for_ivk(rec)
        elif (
            rec['idata'] is not None and
            rec['idata']['kind'] == 'move-result' and
            rec['idata']['api']['site'] != 'api'
        ):
            prev_rec = self.__detect_for_mvrslt(rec)
        else:
            data = self.records.get_a_field(rec, 'data')
            if (len(data) > 0):
                prev_rec = data[-1]
        return prev_rec, rec

    def __detect_for_ivk(self, rec):
        callee_tid = rec['val'] if (rec['var'] == 'tid') else rec['tid']
        for i in range(len(self.method_invocations)):
            caller_rec = self.method_invocations[i]
            if (
                caller_rec['called'] == False and
                caller_rec['pid'] == rec['pid'] and
                caller_rec['tid'] == callee_tid
            ):
                rslt = self.__chk_methods_rel(caller_rec['idata'], rec)
                if (rslt):
                    if (caller_rec['idata']['ret']['line'] is None):
                        # if the invoked method has no return, remove a record
                        self.method_invocations.pop(i)
                    caller_rec['called'] = {  # Used to detect mv-rslt
                      'path': rec['path'],
                      'method': rec['method'],
                      'pid': rec['pid'],
                      'tid': rec['tid'],
                    }
                    return caller_rec
        return None

    def __detect_for_mvrslt(self, rec):
        for i in range(len(self.method_invocations)):
            caller_rec = self.method_invocations[i]
            if (
                caller_rec['called'] and
                caller_rec['pid'] == rec['pid'] and
                caller_rec['tid'] == rec['tid']
            ):
                if (caller_rec['line'] == rec['idata']['ivk']):
                    self.method_invocations.pop(i)
                    return self.records.get_a_field(caller_rec['called'], 'data')[-1]
        return None

    def __chk_methods_rel(self, ivk_src, ivk_dst):
        if (ivk_src['site'] == 'unknown'):
            return True
        if ('thread' in ivk_src.keys()):
            if (
                ivk_src['class'] == ivk_dst['class'] and
                ivk_src['thread']['callee'] == ivk_dst['method']
            ):
                return True
        return self.__cmp_methods(ivk_src, ivk_dst)

    def __cmp_methods(self, ivk_src, ivk_dst):
        # Check whether the methods are same
        if (ivk_src['method'] == ivk_dst['method']):
            # Check whether the classes are same
            if (ivk_src['site'] == ivk_dst['path']):
                return True
            # Search Src's super classes
            rslt = self.__cmp_classes(ivk_src['site'], ivk_dst['path'])
            if (rslt): return rslt
            # Search Dst's super classes
            return self.__cmp_classes(ivk_dst['path'], ivk_src['site'])
        return False

    def __cmp_classes(self, p_src, p_dst):
        if (p_src == p_dst):
            return True
        super = self.smalis['data'][p_src]['super']
        if (super not in ['Ljava/lang/Object;', 'Ljava/lang/Enum;']):
            super_path = (super[1:-1] + '.smali').split('/')
            for dirs in self.smalis['index'].values():
                path = self.__search_clss_in_index(super_path, dirs)
                if (path is not None):
                    return self.__cmp_classes(path, p_dst)
        return False

    def __search_clss_in_index(self, clss, dirs):
        target = clss[0]
        if (target in dirs.keys()):
            if (len(clss) > 1):
                return self.__search_clss_in_index(clss[1:], dirs[target])
            else:
                return dirs[target]['path']
        return None

