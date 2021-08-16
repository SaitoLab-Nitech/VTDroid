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
import copy
from pprint import pprint

from .dalvik_bytecode import *
from .examiner import exp_v2v_examiner as ee
from .examiner import ivk_examiner as ie
from .examiner import obscr_examiner as oe
from .examiner import brnch_examiner as be


class CodeParser(ee.ExpV2VExmnr, ie.IvkExmnr, oe.ObscrExmnr, be.BrnchExmnr):
    def parse_code(self, path, mdata, data, code):
        current_try_ids = []
        for i in range(mdata['start'], mdata['end']):
            c = code[i][4:]
            if (c not in ['', '}']):
                self.__examine_inst(
                    i,
                    c,
                    mdata,
                    mdata['vars'],
                    data,
                    code,
                    current_try_ids,
                    path
                )
        self.pairing_if_cond_goto_and_try(mdata['vars'])

    def __examine_inst(self, i, c, mdata, vdata, data, code, current_try_ids, path):
        inst = c.split(' ')[0]
        if (inst in exp_v2v.keys()):
            self.examine_exp_v2v(i, inst, c, vdata, code, mdata)
        elif (inst in ivk.keys()):
            data['meth_refs'] += 1
            self.examine_ivk(i, inst, c, vdata, code, path)
        elif (inst in obscr.keys()):
            count_meth_ref = self.examine_obscr(i, inst, c, mdata, vdata, code)
            if (count_meth_ref):
                data['meth_refs'] += 1
        elif (inst in brnch.keys()):
            self.examine_brnch(i, inst, c, mdata, vdata)
        elif (any([inst.startswith(l) for l in label])):
            self.examine_label(i, inst, c, mdata, vdata, code, current_try_ids)

        if (i in vdata.keys()):
            vdata[i]['try_ids'] = copy.copy(current_try_ids)
            vdata[i]['try_dsts'] = set()
