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

from .branch import branch
from smalien.core.control_flow_analyzer import control_flow_analyzer as cfa
from .control_dependence_analyzer import control_dependence_analyzer as cda
from .information_preservation_inspector import information_preservation_inspector as ipi


class CDFlowTracker(
    cfa.ControlFlowAnalyzer,
    cda.ControlDependenceAnalyzer,
    ipi.InformationPreservationInspector
):

    cd_data = {}
    transmitter_inst_kinds = {
        'if',
    }
    receptor_inst_visible = {
        'const',
        'exp_v2v',
        'move-result',
        #'instance',
    }
    receptor_inst_invisible = {
        'ivk',
    }

    def detect_cd_transmitters_and_receptors(self, line, idata, r, tracked):
        if (idata['kind'] in CDFlowTracker.transmitter_inst_kinds):
            #print('[ CDFlowTracker ] Branch:', r['tag'], idata)
            for i in range(len(idata['vars'])):
                var = idata['vars'][i]
                if (var in tracked.keys() and tracked[var][0]):
                    # Operand variable v is tracked
                    self.printer.print(
                        f'[ CDFlowTracker ] {r["tag"]}, {var}, is tracked {tracked[var][:3]}'
                    )
                    compared_value = self.__get_compared_value(i, idata['vars'], tracked)
                    self.__analyze_a_branch(
                        var,
                        copy.deepcopy(tracked[var]),
                        r,
                        compared_value,
                        tracked
                    )
        elif (idata['kind'] in CDFlowTracker.receptor_inst_visible):
            dst = idata['dst']
            self.__detect_receptor(
                line,
                'visible',
                dst,
                tracked[dst][5],
                tracked[dst][0],
                r
            )
        elif (idata['kind'] in CDFlowTracker.receptor_inst_invisible):
            if (idata['site'] == 'api'):
                for prm in idata['prms']:
                    prm_tracked = self.chk_tracked(tracked, prm)
                    self.__detect_receptor(
                        line,
                        'invisible',
                        prm,
                        prm_tracked[5],
                        prm_tracked[0],
                        r
                    )

    def __get_compared_value(self, i, vars, tracked):
        if (len(vars) > 1):
            compared_var_index = (i + 1) % len(vars)
            compared_var = vars[compared_var_index]
            compared_var_tracked = self.chk_tracked(tracked, compared_var)
            return compared_var_tracked[5]

    def save_branch_values_with_false_condition(self, idata, tracked, r):
        cd_key = r['path'] + r['method']
        if (cd_key in CDFlowTracker.cd_data.keys()):
            for var in idata['vars']:
                b_key = r['tag'] + '_' + var
                if (b_key in CDFlowTracker.cd_data[cd_key]['branches'].keys()):
                    if (var in tracked.keys() and tracked[var][5] is not None):
                        CDFlowTracker.cd_data[cd_key]['branches'][b_key].set_value_with_false_condition(
                            tracked[var][5]
                        )

    def verify_cd_flows(self, line, idata, r, tracked):
        self.__detect_sinks_within_branches(idata, r)
        self.__verify_cd_flows_with_exited_branches(line, idata, r, tracked)

    def __detect_sinks_within_branches(self, idata, r):
        if ('sink' in idata.keys() and idata['sink'] == 'privacy_leak'):
            for cd_key, cd_val in CDFlowTracker.cd_data.items():
                for branch_key, b in CDFlowTracker.cd_data[cd_key]['branches'].items():
                    if (b.get_body_running()):
                        self.taint_prop_info['cd']['num_uses']['sink']['cntr'] += 1
                        self.taint_prop_info['cd']['num_uses']['sink']['ids'].append([
                            branch_key,
                            r['tag'],
                        ])

    def __verify_cd_flows_with_exited_branches(self, line, idata, r, tracked):
        detected_flows = self.__verify_visible_cd_flow(line, r)
        if (detected_flows != []):
            #print('Detected visible CD-flows at', r['tag'], line)
            #print(detected_flows)
            # Visible CD flow is detected
            self.taint_prop_info['cd']['num_uses']['visible']['cntr'] += 1
            self.taint_prop_info['cd']['num_uses']['visible']['ids'].append(
                detected_flows
            )
            for df in detected_flows:
                self.propagate_append(
                    CDFlowTracker.cd_data[df[0]]['branches'][df[1]].get_var_tracked(),
                    df[2][1],
                    tracked,
                    False
                )
                self.set_ata_flow_to_tracked(
                    tracked,
                    df[2][1],
                    f'CD: {df[1]} -> {df[2]}'
                )

        if (idata['kind'] == 'move-result'):
            dst_tracked = self.chk_tracked(tracked, idata['dst'])
            if (dst_tracked[0] == False and dst_tracked[5] is not None):
                detected_flows = self.__verify_invisible_cd_flow(
                    line,
                    idata['dst'],
                    dst_tracked[5],
                    r
                )
                if (detected_flows != []):
                    #print('Detected invisible CD-flows', r['tag'], line, detected_flows)
                    # Invisible CD flow is detected
                    self.taint_prop_info['cd']['num_uses']['invisible']['cntr'] += 1
                    self.taint_prop_info['cd']['num_uses']['invisible']['ids'].append(
                        detected_flows
                    )
                    for df in detected_flows:
                        self.propagate_append(
                            CDFlowTracker.cd_data[df[0]]['branches'][df[1]].get_var_tracked(),
                            df[3][1],
                            tracked,
                            False
                        )
                        self.set_ata_flow_to_tracked(
                            tracked,
                            df[3][1],
                            f'CD: {df[1]} -> {df[2]} -> {df[3]}'
                        )

    def __analyze_a_branch(self, var, var_tracked, r, compared_value, tracked):
        value = var_tracked[5]
        cd_key = r['path'] + r['method']
        if (cd_key not in CDFlowTracker.cd_data.keys()):
            # Create CFG, DOMT, and PDOMT, and Identify loops
            method_code = self.smalis['data'][r['path']]['methods'][r['method']]
            CDFlowTracker.cd_data[cd_key] = {
                'cfg': self.analyze_control_flows(
                    r['path'],
                    r['method'],
                    method_code,
                    r['tag']
                ),
                'branches': {},
            }
        branch_key = r['tag'] + '_' + var
        if (branch_key not in CDFlowTracker.cd_data[cd_key]['branches'].keys()):
            new_branch = branch.Branch(r, var_tracked)
            self.analyze_control_dependencies(
                new_branch,
                CDFlowTracker.cd_data[cd_key]['cfg']
            )
            CDFlowTracker.cd_data[cd_key]['branches'][branch_key] = new_branch
        current_branch = CDFlowTracker.cd_data[cd_key]['branches'][branch_key]
        # Get receptors' values at the branch
        receptor_values = {}
        for receptor in current_branch.get_receptors().values():
            receptor_tracked = self.chk_tracked(tracked, receptor.get_var())
            receptor_values[receptor.get_var()] = receptor_tracked[5]
        # Add value
        CDFlowTracker.cd_data[cd_key]['branches'][branch_key].update_branch_round_with_true_condition(
            value,
            compared_value,
            receptor_values,
            copy.deepcopy(tracked)
        )

    def __detect_receptor(self, line, kind, dst, value, taint, r):
        cd_key = r['path'] + r['method']
        if (cd_key in CDFlowTracker.cd_data.keys()):
            for branch_key, b in CDFlowTracker.cd_data[cd_key]['branches'].items():
                control_dependent = self.check_control_dependence(line, b)
                if (control_dependent):
                    b.update_receptor(line, kind, dst, value, taint)

    def __verify_visible_cd_flow(self, line, r):
        detected = []
        cd_key = r['path'] + r['method']
        if (cd_key in CDFlowTracker.cd_data.keys()):
            for branch_key, b in CDFlowTracker.cd_data[cd_key]['branches'].items():
                if (b.get_body_running()):
                    control_dependent = self.check_control_dependence(line, b)
                    if (not control_dependent): # Exited the branch
                        b.set_body_running(False)
                        for receptor in b.get_receptors().values():
                            if (receptor.get_kind() == 'visible' and receptor.get_taint() == False):
                                preserve_information = self.check_information_preservation_vis(
                                    receptor,
                                    b
                                )
                                if (preserve_information):
                                    #print(line, r['tag'])
                                    #print(b.get_values())
                                    #print(receptor.get_values())
                                    detected.append([
                                        cd_key,
                                        branch_key,
                                        [ receptor.get_line(), receptor.get_var() ],
                                    ])
        return detected

    def __verify_invisible_cd_flow(self, line, da_dst, value, r):
        detected = []
        da_receptor_id = r['path'] + '_' + str(line)
        for cd_key, cd_val in CDFlowTracker.cd_data.items():
            for branch_key, branch_data in cd_val['branches'].items():
                if (not branch_data.get_body_running()):
                    for receptor in branch_data.get_receptors().values():
                        if (receptor.get_kind() == 'invisible'):
                            da_receptor = receptor.test_and_add_da_receptor(
                                da_receptor_id,
                                value,
                            )
                            if (da_receptor is not None):
                                preserve_information = self.check_information_preservation_inv(
                                    da_receptor,
                                    receptor,
                                    branch_data
                                )
                                if (preserve_information):
                                    #print(line, r['tag'])
                            	    #print(b.get_values())
                            	    #print(receptor.get_values())
                            	    detected.append([
                                        cd_key,
                                        branch_key,
                                        [ receptor.get_line(), receptor.get_var() ],
                                        [ line, da_dst ],
                                    ])
        return detected
