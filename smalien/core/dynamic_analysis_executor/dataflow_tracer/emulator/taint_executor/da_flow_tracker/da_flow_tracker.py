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

import copy

from .transmitter import transmitter

class DAFlowTracker():
    da_data = {}

    def detect_da_flow(self, r, tracked):
        if (r['idata'] is not None and r['var'] is not None):
            idata = r['idata']
            if (idata['kind'] == 'ivk' and idata['site'] == 'api'):
                if (r['var'].find('SystemCommandResult') > -1):
                    self.__detect_system_command_flow(r, tracked)
                elif (r['var'].find('Ret') > -1):
                    self.__detect_receptor(r, r['var'].replace('Ret', ''), tracked)
                else:
                    self.__detect_transmitter(r, tracked)
            elif (idata['kind'] == 'move-result' and idata['api']['site'] == 'api'):
                if (idata['api']['method'].find('length') > -1):
                    return
                self.__detect_receptor(r, r['var'], tracked)

    def __detect_system_command_flow(self, r, tracked):
        cmd_var = r['idata']['prms'][-1]
        cmd_tracked = self.chk_tracked(tracked, cmd_var)
        if (cmd_tracked[0]):
            self.__save_value_as_transmitter(r, copy.deepcopy(cmd_tracked))
        else:
            self.__detect_receptor(r, cmd_var, tracked)

    def __detect_transmitter(self, r, tracked):
        prm = r['var']
        if (prm in tracked.keys() and tracked[prm][0]):
            self.__save_value_as_transmitter(
                r,
                copy.deepcopy(tracked[prm])
            )

    def __save_value_as_transmitter(self, r, prm_tracked):
        da_key = r['path'] + r['method']
        if (da_key not in DAFlowTracker.da_data.keys()):
            DAFlowTracker.da_data[da_key] = {}
        prm_key = r['tag']
        if (prm_key not in DAFlowTracker.da_data[da_key].keys()):
            DAFlowTracker.da_data[da_key][prm_key] = transmitter.Transmitter(
                r,
                prm_tracked,
                self.ocr_info
            )
        DAFlowTracker.da_data[da_key][prm_key].add_value(r['val'])
        self.printer.print(f'DA transmitter value memorized {prm_key = }, {r["val"] = }')

    def __detect_receptor(self, r, receptor_var, tracked):
        receptor_tracked = self.chk_tracked(tracked, receptor_var)
        if (receptor_tracked[0] == False):
            detected_flows = self.__match_values_with_transmitters(r, receptor_var)
            if (detected_flows != []):
                self.printer.print(f'Detected DA flows {detected_flows}')
                self.taint_prop_info['da']['num_uses']['cntr'] += 1
                self.taint_prop_info['da']['num_uses']['ids'].append(
                    detected_flows
                )
                for df in detected_flows:
                    self.propagate_append(
                        DAFlowTracker.da_data[df[0]][df[1]].get_var_tracked(),
                        receptor_var,
                        tracked,
                        False
                    )
                    self.set_ata_flow_to_tracked(
                        tracked,
                        receptor_var,
                        f'DA: {df[1]} -> {r["tag"]} {df[2]}'
                    )

    def __match_values_with_transmitters(self, r, receptor_var):
        receptor_value = r['val']
        detected = []
        for da_key, da_val in DAFlowTracker.da_data.items():
            for prm_key, prm_data in da_val.items():
                matched = prm_data.match_values(receptor_value)
                if (matched):
                    detected.append([
                        da_key,
                        prm_key,
                        [ r['tag'], r['line'], receptor_var ],
                    ])
        return detected
