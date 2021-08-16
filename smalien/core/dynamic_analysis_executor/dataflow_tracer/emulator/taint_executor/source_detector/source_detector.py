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

import sys
import time
import binascii
from pprint import pprint


class SourceDetector():
    src_detected_smali_tags = []

    def detect_source_api(self, idata, rec_start, rec_end, sources_detected):
        if ('user_input_source' in idata.keys()): # For compatibility with older versions
            idata['source'] = 'user_input'
        if ('source' in idata.keys() and idata['source'] in self.target_source):
            if (idata['source'] != 'user_input'):
                self.printer.print(
                    f"[ SOURCE_API ] {rec_end['tag']}, {rec_end['path']}, "
                    f"{idata['source']}, {rec_end['idata']['kind']}, "
                    f"[ TIME ] analysis: {time.time() - self.df_start}, "
                    f"app: {float(int(rec_end['time']) - int(self.launch_time)) / 1000.0}"
                )
                if (rec_end['idata'] is not None and rec_end['idata']['kind'] == 'move-result'):
                    self.printer.print(f"  [ RET ] {rec_end['var']}, {rec_end['val']}")
                    if (rec_end['val'] not in self.target_source_values):
                        self.target_source_values.append(rec_end['val'])
                else:
                    self.printer.print(' (End rec not found) ')
                self.printer.print('')
                return True, idata['source']
            else:
                result = {
                    'tag': rec_start['tag'],
                    'path': rec_end['path'],
                    'app_class': rec_end['class'],
                    'app_attr': rec_end['attr'],
                    'app_method': rec_end['method'],
                    'app_params': rec_end['params'],
                    'class': idata['class'],
                    'attr': idata['attr'],
                    'method': idata['method'],
                    'prms': idata['prms'],
                    'prm_types': idata['prm_types'],
                    'line': rec_end['line'],
                    'ret_var': rec_end['var'],
                    'ret_val': rec_end['val'],
                }
                if (result['ret_val'] is not None):
                    self.target_source_values.append(result['ret_val'])
                sources_detected[result['tag']] = result
                self.printer.print(
                    f"[ USER_INPUT_SOURCE ] {rec_start['tag']}, "
                    f"{rec_end['tag']}, {idata['class']}, {idata['method']}"
                )
                self.printer.print(f'    JSON: {result}\n')
                return True, 'user_input-' + rec_start['tag']
        return False, None
