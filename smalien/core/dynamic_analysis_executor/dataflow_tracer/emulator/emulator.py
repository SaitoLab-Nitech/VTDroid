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

from .taint_executor import taint_executor


class Emulator(taint_executor.TaintExecutor):
    def emulate(self, rec_begin, rec_end):
        # Exit if an exception has thrown
        if (rec_end['idata'] is not None and rec_end['idata']['kind'] == 'catch_label'):
            return

        tracked = self.records.get_a_field(rec_begin, 'tracked')
        # Set a register's value
        if (rec_begin['var'] is not None and rec_begin['var'][0] in ['v', 'p']):
            self.set_value_to_tracked(tracked, rec_begin['var'], rec_begin['val'])

        # Check branches
        rslt = self.__adjust_beginning(rec_begin, rec_end, tracked)
        if (rslt is not None):  # Taking a jump to rslt['line']
            if (rec_begin['idata'] is not None and rec_begin['idata']['kind'] == 'switch'):
                self.detect_cd_transmitters_and_receptors(rec_begin['line'], rec_begin['idata'], rec_begin, tracked)
            rec_begin = rslt
        # In the same method
        if (rec_begin['path'] == rec_end['path']
                and rec_begin['method'] == rec_end['method']):
            if (rec_begin['line'] == rec_end['line']):  # No area to emulate
                return
            goto_max = 0
            self.__emulate_in_a_method(rec_begin, rec_end['line'], goto_max, rec_end)
            self.take_a_snapshot(rec_end)
        # Cross two methods
        else:
            if ('called' in rec_begin.keys()):  # Caller -> Callee
                self.taint_params(rec_begin, rec_end)
            else:  # Callee -> Caller
                end = self.smalis['data'][rec_begin['path']]['methods'][rec_begin['method']]['end']
                goto_max = 0
                rslt = self.__emulate_in_a_method(rec_begin, end, goto_max, rec_end)
                if (rslt is not None):  # Move result
                    self.taint_mvrslt(rslt, rec_begin, rec_end)

    def __adjust_beginning(self, r, nxt, tracked):
        if (r['idata'] is not None):
            prvs_num = self.__count_prvs(r)
            if (r['idata']['kind'] == 'if'):  # Detect if branch
                if (prvs_num % 2 == 0 and r['line'] != nxt['line']):
                    # Take a jump to cond
                    self.save_branch_values_with_false_condition(r['idata'], tracked, r)
                    return self.__get_branch_dst(r, r['idata']['cond_line'])
            elif (r['idata']['kind'] == 'switch'):
                if (nxt['idata']['kind'] == 'switch_label'):
                    return nxt
                if (prvs_num % 2 == 0 and r['line'] != nxt['line']):
                    return nxt
        return None

    def __count_prvs(self, r):
        data = self.records.get_a_field(r, 'data')
        cntr = 0
        for i in range(len(data) - 2, 0, -1):  # Skip data[-1] ( = rec_begin)
            if (data[i]['line'] == r['line']):
                cntr += 1
            else:
                break
        return cntr

    def __get_branch_dst(self, rec, dst_line):
        new_rec = {
            'tag': rec['tag'],
            'pid': rec['pid'],
            'tid': rec['tid'],
            'cid': rec['cid'],
            'time': rec['time'],
            'path': rec['path'],
            'class': rec['class'],
            'method': rec['method'],
            'idata': self.smalis['data'][rec['path']]['methods'][rec['method']]['vars'][dst_line],
            'line': dst_line,
            'var': None,
        }
        return new_rec

    def __emulate_in_a_method(self, r, end, goto_max, rec_end):
        vdata = self.smalis['data'][r['path']]['methods'][r['method']]['vars']
        tracked = self.records.get_a_field(r, 'tracked')

        # Before tainting
        self.detect_tc_flow(r, rec_end, tracked)

        i = r['line']
        while (i != end):
            if (i in vdata.keys()):
                idata = vdata[i]
                rslt = self.__chk_end(idata)
                if (rslt):
                    if (idata['kind'] == 'ret'):
                        return idata
                    return None
                rslt = self.__chk_branch(idata, r)
                if (rslt is not None):
                    goto_max += 1
                    if (goto_max < self.emulate_info['follow_goto_limit']):
                        return self.__emulate_in_a_method(rslt, end, goto_max, rec_end)
                    else:
                        self.emulate_info['fail_count'] += 1
                        return None
                self.taint_vars(i, idata, r, tracked, rec_end)
            i += 1
        return None

    def __chk_end(self, idata):
        if (idata['kind'] in ['throw', 'ret']):
            return True
        return False

    def __chk_branch(self, idata, rec):
        if (idata['kind'] == 'goto'):
            return self.__get_branch_dst(rec, idata['goto_label_line'])
        return None
