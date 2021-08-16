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
import json
import time

class SinkDetector():
    excluded_apis = [
        'Ljava/io/FileOutputStream;',
        'Ljava/io/FileWriter;',
    ]
    excluded_types = [
        'I',
    ]

    def detect_sink(self, idata, r, tracked, sources_detected):
        if (
            idata['class'] in self.user_input_sinks.keys() and
            idata['method'] in self.user_input_sinks[idata['class']]
        ): # For compatibility with older versions
            idata['sink'] = 'user_input'
        if ('sink' not in idata.keys()):
            return False
        if (idata['sink'] == 'user_input' and 'user_input' not in self.target_source):
            return False
        for prm in idata['prms']:
            if (prm in tracked.keys() and tracked[prm][0]):
                self.printer.print(
                    f"\n[ SINK ] {r['tag']}, "\
                    f"{idata['class']} -> {idata['method']} "\
                    f"( param: {prm}) "\
                    f"in {r['path']}"
                )
                self.printer.print(
                    f"\n  [ TIME ] analysis: {time.time() - self.df_start} "\
                    f"app: {float(int(r['time']) - int(self.launch_time)) / 1000.0}"
                )
                self.printer.print(f"  [ TAINT_FOUND ] {tracked[prm][:-3]}")
                ata_flows = tracked[prm][3]
                if (len(ata_flows) > 10):
                    ata_flows = ata_flows[:10]
                self.printer.print(f"  [ ATA_FLOW ] {ata_flows}")
                if (tracked[prm][5] is not None):
                    value = tracked[prm][5]
                    if (len(value) > 1000):
                        value = value[:1000]
                        value += ' (and more data, total length:'
                        value += str(len(value)) + ')'
                    self.printer.print(f"  [ VALUE ] {value}\n")

                if (idata['sink'] == 'user_input'):
                    self.__print_validator_api_info(
                        prm,
                        tracked[prm],
                        idata,
                        r,
                        sources_detected
                    )
                self.printer.print('')
        return True

    def __print_validator_api_info(self, prm, prm_tracked, idata, r, sources_detected):
        result = {
            'tracked': {
                prm: [
                    prm_tracked[0],
                    list(prm_tracked[1]),
                    list(prm_tracked[2]),
                    prm_tracked[3],
                    list(prm_tracked[4]),
                    prm_tracked[5],
                ]
            }
        }
        source_tag = result['tracked'][prm][1][0].split('input-')[-1]
        result['source'] = sources_detected[source_tag]
        result['tag'] = r['tag']
        result['path'] = r['path']
        result['app_class'] = r['class']
        result['app_attr'] = r['attr']
        result['app_method'] = r['method']
        result['app_params'] = r['params']
        result['class'] = idata['class']
        result['attr'] = idata['attr']
        result['method'] = idata['method']
        result['prms'] = idata['prms']
        result['prm_types'] = idata['prm_types']
        self.printer.print(
            f"[ VALIDATOR_API ] {r['tag']}, "\
            f"{idata['class']}, {idata['method']}, "\
            f"{idata['prms']}"
        )
        self.printer.print(f'    JSON: {json.dumps(result)}')
