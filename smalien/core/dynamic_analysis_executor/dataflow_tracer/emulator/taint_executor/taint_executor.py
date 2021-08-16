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
import copy
from pprint import pprint

from .source_detector import source_detector
from .sink_detector import sink_detector
from .da_flow_tracker import da_flow_tracker as daft
from .cd_flow_tracker import cd_flow_tracker as cdft
from .tc_flow_tracker import tc_flow_tracker as tcft


class TaintExecutor(
    source_detector.SourceDetector,
    sink_detector.SinkDetector,
    daft.DAFlowTracker,
    cdft.CDFlowTracker,
    tcft.TCFlowTracker
):
    field_tracked = {}
    sources_detected = {}

    def taint_params(self, caller, callee):
        params = caller['idata']['prms']
        caller_snapshot = self.records.get_a_field(caller, 'snapshot')
        if (caller['line'] not in caller_snapshot):
            return
        callee_tracked = self.records.get_a_field(callee, 'tracked')
        self.__clear_tracked(callee_tracked)

        if (len(caller['tag'].split('_')) > 2):
            caller_base_smali_tag = caller['tag'].split('_')[:-1]
        else:
            caller_base_smali_tag = caller['tag'].split('_')
        caller_base_smali_tag = '_'.join(caller_base_smali_tag) + '_'
        # If reflection
        if (caller['idata']['site'] == 'unknown'):
            p2_tracked = caller_snapshot[caller['line']][params[2]]
            p2_smali_tag = caller_base_smali_tag + params[2]
            if (callee[ 'attr'] == 'static'):
                targets = callee['params']['vars']
            else:
                targets = callee['params']['vars'][1:]
            for t in targets:
                # For reflection, propagating tag to all params except the base object
                self.__set_tracked(
                    callee_tracked,
                    t,
                    p2_tracked[0],
                    p2_tracked[1],
                    p2_smali_tag,
                    p2_tracked[3]
                )
        # If not reflection
        else:
            for p, p_tracked in caller_snapshot[caller['line']].items():
                if (p_tracked[0]):
                    p_smali_tag = caller_base_smali_tag + p
                    self.__set_tracked(
                        callee_tracked,
                        'p' + str(params.index(p)),
                        p_tracked[0],
                        p_tracked[1],
                        p_smali_tag,
                        p_tracked[3]
                    )

    def taint_vars(self, i, idata, r, tracked, rec_end):
        self.verify_cd_flows(i, idata, r, tracked)

        if (idata['kind'] == 'ivk'):
            if (idata['site'] == 'api'):
                # [params] -> [params and move-result]
                self.__taint_api(idata, r, tracked, rec_end)
            else:
                # Found an invocation of an apps' method without move-result
                self.__taint_pointer_params(r, idata, tracked)
        elif (
            'dst' in idata.keys() and
            idata['dst'] is not None and
            idata['kind'] != 'move-result'
        ):
            if ('src' in idata.keys()):
                if (idata['kind'] in ['iget', 'sget']):
                    self.__unset_tracked(tracked, idata['dst'])
                    instance = idata['instance']
                    if (
                        instance in TaintExecutor.field_tracked.keys() and
                        r['pid'] in TaintExecutor.field_tracked[instance].keys() and
                        r['tid'] in TaintExecutor. field_tracked[instance][r['pid']].keys()
                    ):
                        src_instance_tracked = \
                            TaintExecutor.field_tracked[instance][r['pid']][r['tid']]
                        if (idata['obj']):
                            src_tracked = copy.copy(src_instance_tracked[0])
                            self.__propagate_by_copy(src_tracked, idata['dst'], tracked)
                        elif (
                            r['line'] == i and
                            r['var'] is not None and
                            r['val'] == src_instance_tracked[1]
                        ):
                            src_tracked = copy.copy(src_instance_tracked[0])
                            self.__propagate_by_copy(src_tracked, r['var'], tracked)
                    if (idata['obj']):
                        tracked[idata['dst']][4].add(instance)
                elif (idata['kind'] in ['iput', 'sput']):
                    pass
                elif (idata['kind'] in ['aget']):
                    rslt = self.chk_tracked(tracked, idata['pos'])
                    if (rslt[0]): # [Rule 3] dst <- index U array
                        self.taint_prop_info['mo']['num_uses']['R3']['cntr'] += 1
                        self.taint_prop_info['mo']['num_uses']['R3']['ids'].append([ r['tag'], i ])
                        # Rule dst <- index
                        tracked_before_taint = copy.copy(tracked)
                        self.__propagate(idata['pos'], idata['dst'], tracked, r['tag'])
                        # Rule dst <- array
                        rslt = self.chk_tracked(tracked_before_taint, idata['src'])
                        if (rslt[0]):
                            self.propagate_append(
                                tracked_before_taint[idata['src']],
                                idata['dst'],
                                tracked,
                                True
                            )
                        self.set_ata_flow_to_tracked(tracked, idata['dst'], 'R3')
                        del tracked_before_taint
                    else: # [Rule 3, 4]  dst, index <- array
                        self.__unset_tracked(tracked, idata['dst'])
                        rslt = self.chk_tracked(tracked, idata['src'])
                        if (rslt[0]):
                            # dst <- array
                            self.taint_prop_info['mo']['num_uses']['R3']['cntr'] += 1
                            self.taint_prop_info['mo']['num_uses']['R3']['ids'].append([
                                r['tag'],
                                i,
                            ])
                            self.__propagate(idata['src'], idata['dst'], tracked, r['tag'])
                            self.set_ata_flow_to_tracked(tracked, idata['dst'], 'R3')
                            # index <- array
                            self.taint_prop_info['mo']['num_uses']['R4']['cntr'] += 1
                            self.taint_prop_info['mo']['num_uses']['R4']['ids'].append([
                                r['tag'],
                                i,
                            ])
                            self.__propagate(idata['src'], idata['pos'], tracked, r['tag'])
                            self.set_ata_flow_to_tracked(tracked, idata['pos'], 'R4')
                elif (idata['kind'] in ['aput']):
                    # [Rule 2] array <- index U array
                    rslt = self.chk_tracked(tracked, idata['pos'])
                    if (rslt[0]):
                        self.taint_prop_info['mo']['num_uses']['R2']['cntr'] += 1
                        self.taint_prop_info['mo']['num_uses']['R2']['ids'].append([r['tag'], i])
                        self.propagate_append(rslt, idata['dst'], tracked, True)
                        self.set_ata_flow_to_tracked(tracked, idata['dst'], 'R2')
                    # [Rule 1] array <- src U array
                    rslt = self.chk_tracked(tracked, idata['src'])
                    if (rslt[0]):
                        self.taint_prop_info['mo']['num_uses']['R1']['cntr'] += 1
                        self.taint_prop_info['mo']['num_uses']['R1']['ids'].append([r['tag'], i])
                        self.propagate_append(tracked[idata['src']], idata['dst'], tracked, True)
                        self.set_ata_flow_to_tracked(tracked, idata['dst'], 'R1')
                        for instance in tracked[idata['dst']][4]:
                            self.__set_instance_tracked_at_aput(instance, tracked[idata['src']], r)
                else:
                    self.__propagate(idata['src'], idata['dst'], tracked, r['tag'])
            elif ('srcs' in idata.keys()):
                tracked_before_taint = copy.copy(tracked)
                self.__unset_tracked(tracked, idata['dst'])
                for src in idata['srcs']:
                    rslt = self.chk_tracked(tracked_before_taint, src)
                    if (rslt[0]):
                        self.propagate_append(
                            tracked_before_taint[src],
                            idata['dst'],
                            tracked,
                            True
                        )
                del tracked_before_taint
            elif ('objs' in idata.keys()):  # objs for cmp-kind
                tracked_before_taint = copy.copy(tracked)
                self.__unset_tracked(tracked, idata['dst'])
                operand_values = []
                for src in idata['objs']:
                    rslt = self.chk_tracked(tracked_before_taint, src)
                    operand_values.append(rslt[5])
                    if (rslt[0]):
                        self.propagate_append(
                            tracked_before_taint[src],
                            idata['dst'],
                            tracked,
                            True
                        )
                cmp_result_value = self.__emulate_cmp(operand_values)
                if (cmp_result_value is not None):
                    self.set_value_to_tracked(tracked, idata['dst'], cmp_result_value)
                del tracked_before_taint
            elif (
                'array' == idata['kind'] and
                self.smalis['data'][r['path']]['code'][i].find('array-length') > -1
            ):
                # [Rule 5] length <- array
                self.__taint_propagate_for_array_length(i, idata, r, tracked)
            else:
                self.__unset_tracked(tracked, idata['dst'])

            # Set a regsiter's value
            if (idata['kind'] == 'const'):
                self.set_value_to_tracked(tracked, idata['dst'], idata['value'])
            elif (r['line'] == i and r['var'] == idata['dst']):
                self.set_value_to_tracked(tracked, r['var'], r['val'])

        self.detect_cd_transmitters_and_receptors(i, idata, r, tracked)

    def __emulate_cmp(self, values):
        if (None not in values):
            value1 = float(values[0])
            value2 = float(values[1])
            if (value1 > value2): result = '1'
            elif (value1 < value2): result = '-1'
            else: result = '0'
            return result

    def __taint_propagate_for_array_length(self, i, idata, r, tracked):
        src = self.smalis['data'][r['path']]['code'][i].split(', ')[-1]
        rslt = self.chk_tracked(tracked, src)
        if (rslt[0]):
            self.taint_prop_info['mo']['num_uses']['R5']['cntr'] += 1
            if (rslt[5] is not None and rslt[5] in self.target_source_values):
                self.taint_prop_info['mo']['num_uses']['R5']['ids_skipped'].append([
                    r['tag'],
                    i,
                ])
                self.__unset_tracked(tracked, idata['dst'])
            else:
                self.taint_prop_info['mo']['num_uses']['R5']['ids_propagated'].append([
                    r['tag'],
                    i,
                ])
                self.__set_tracked(tracked, idata['dst'], rslt[0], rslt[1], r['tag'], rslt[3])
                self.set_ata_flow_to_tracked(tracked, idata['dst'], 'R5')

    def __set_instance_tracked(self, instance, src_tracked, value, pid, tid):
        if (instance not in TaintExecutor.field_tracked.keys()):
            TaintExecutor.field_tracked[instance] = {}
        if (pid not in TaintExecutor.field_tracked[instance].keys()):
            TaintExecutor.field_tracked[instance][pid] = {}
        TaintExecutor.field_tracked[instance][pid][tid] = [copy.copy(src_tracked), value]

    def __set_instance_tracked_at_aput(self, target_instance, src_tracked, r):
        target_class = target_instance.split('->')[0]
        target_field = target_instance.split('->')[1]
        target_classes = set()
        self.__search_super_classes(target_class, target_classes)
        for target_class in target_classes:
            instance = target_class + '->' + target_field
            self.__set_instance_tracked(instance, src_tracked, None, r['pid'], r['tid'])

    def __search_super_classes(self, target_class, target_classes):
        target_smali_path = (target_class[1:-1] + '.smali').split('/')
        for dirs in self.smalis['index'].values():
            path = self.__search_clss_in_index(target_smali_path, dirs)
            if (path is not None):
                target_classes.add(target_class)
                super_class = self.smalis['data'][path]['super']
                if (super_class not in ['Ljava/lang/Object;']):
                    return self.__search_super_classes(super_class, target_classes)

    def __search_clss_in_index(self, clss, dirs):
        target = clss[0]
        if (target in dirs.keys()):
            if (len(clss) > 1):
                return self.__search_clss_in_index(clss[1:], dirs[target])
            else:
                return dirs[target]['path']
        return None

    def __taint_pointer_params(self, caller_rec, caller_idata, caller_tracked):
        start_offset = 0 if (caller_idata['attr'] == 'static') else 1

        # Obtain callee's tracked data
        callee_rec = {
            'path': caller_idata['site'],
            'method': caller_idata['method'],
            'pid': caller_rec['pid'],
            'tid': caller_rec['tid'],
        }
        callee_tracked = self.records.get_a_field(callee_rec, 'tracked')
        for i in range(start_offset, len(caller_idata['prms'])):
            prm = caller_idata['prms'][i]
            prm_type = caller_idata['prm_types'][i]
            if (prm_type[0] == '['):
                callee_prm = 'p' + str(i)
                rslt = self.chk_tracked(callee_tracked, callee_prm)
                if (rslt[0]):
                    self.propagate_append(
                        callee_tracked[callee_prm],
                        prm,
                        caller_tracked,
                        True
                    )

    def taint_mvrslt(self, idata, callee, caller):
        if (idata['src'] is None):
            return
        if (caller['idata'] is not None and caller['idata']['kind'] == 'move-result'):
            dst = caller['idata']['dst']
            caller_tracked = self.records.get_a_field(caller, 'tracked')
            callee_tracked = self.records.get_a_field(callee, 'tracked')
            rslt = self.chk_tracked(callee_tracked, idata['src'])
            if (rslt[0]):
                self.__set_tracked(
                    caller_tracked,
                    dst,
                    rslt[0],
                    rslt[1],
                    callee['tag'],
                    rslt[3]
                )
                caller_tracked[dst][3] = callee_tracked[idata['src']][3]
            else:
                self.__unset_tracked(caller_tracked, dst)

    def take_a_snapshot(self, r):
        if (
            r['idata'] is not None and
            r['idata']['kind'] == 'ivk' and
            r['idata']['site'] != 'api'
        ):
            tracked = self.records.get_a_field(r, 'tracked')
            snapshot = self.records.get_a_field(r, 'snapshot')
            snapshot[r['line']] = {}
            for p in r['idata']['prms']:
                rslt = self.chk_tracked(tracked, p)
                snapshot[r['line']][p] = rslt

    def taint_next_flow(self, r_previous, r):  # r_previous can be None
        idata = r['idata']
        tracked = self.records.get_a_field(r, 'tracked')

        self.detect_da_flow(r, tracked)

        if (idata is not None and idata['kind'] in ['iput', 'sput']):
            # Taint for iput and sput
            if (r['var'] is not None):
                rslt = self.chk_tracked(tracked, idata['src'])
                if (rslt[0]):
                    self.__set_instance_tracked(
                        idata['instance'],
                        rslt,
                        r['val'],
                        r['pid'],
                        r['tid']
                    )

    def __taint_api(self, idata, r, tracked, rec_end):
        # Detect source
        rslt, skey = self.detect_source_api(
            idata,
            r,
            rec_end,
            TaintExecutor.sources_detected
        )
        if (rslt):
            self.__set_tracked(
                tracked,
                idata['ret']['var'],
                self.tag['strong'],
                {skey},
                r['tag']
            )
            return

        # Detect sink
        is_sink = self.detect_sink(idata, r, tracked, TaintExecutor.sources_detected)
        if (is_sink):
            return

        # [Rule 9] length <- base object
        if (idata['method'].find('length()') > -1): # Check an object is tracked
            rslt = self.chk_tracked(tracked, idata['prms'][0])
            if (rslt[0]): # Object is tracked and apply our Rule 9
                self.taint_prop_info['mo']['num_uses']['R9-length']['cntr'] += 1
                if (r['var'] is not None and r['val'] in self.target_source_values):
                    self.taint_prop_info['mo']['num_uses']['R9-length']['ids_skipped'].append([
                        r['tag'],
                        r['line'],
                    ])
                    self.__unset_tracked(tracked, idata['ret']['var'])
                else:
                    self.taint_prop_info['mo']['num_uses']['R9-length']['ids_propagated'].append([
                        r['tag'],
                        r['line'],
                    ])
                    self.__set_tracked(
                        tracked,
                        idata['ret']['var'],
                        rslt[0],
                        rslt[1],
                        r['tag'],
                        rslt[3]
                    )
                    self.set_ata_flow_to_tracked(tracked, idata['ret']['var'], 'R9-length')
            else: # Object is not tracked and ret_var's taint is removed
                self.__unset_tracked(tracked, idata['ret']['var'])
            return

        # Taint API
        # [ taint_tag, {source_kind}, {direc_parent_smali_tag}, {indirect_parent_smali_tag} ]
        if (len(r['tag'].split('_')) > 2):
            base_tag = r['tag'].split('_')[:-1]
        else:
            base_tag = r['tag'].split('_')
        base_tag = '_'.join(base_tag) + '_'
        ref_type_args = self.__get_ref_type_args(idata)
        tracked_before_taint = copy.copy(tracked)
        if (idata['ret']['var'] is not None):  # Clear ret var
            self.__unset_tracked(tracked, idata['ret']['var'])
        for p in idata['prms']:
            rslt = self.chk_tracked(tracked_before_taint, p)
            if (rslt[0]):
                # [Rule 6, 7] all args <- any arg
                for dst in idata['prms']:
                    if (dst != p):
                        self.propagate_append(rslt, dst, tracked, True)
                        if (dst in tracked_before_taint.keys()):
                            for instance in tracked_before_taint[dst][4]:
                                self.__set_instance_tracked_at_aput( instance, rslt, r)
                        if (dst in ref_type_args):
                            self.taint_prop_info['mo']['num_uses']['R6']['cntr'] += 1
                            self.taint_prop_info['mo']['num_uses']['R6']['ids'].append([
                                r['tag'],
                                r['line'],
                            ])
                            self.set_ata_flow_to_tracked(tracked, dst, 'R6')
                        else:
                            self.taint_prop_info['mo']['num_uses']['R7']['cntr'] += 1
                            self.taint_prop_info['mo']['num_uses']['R7']['ids'].append([
                                r['tag'],
                                r['line'],
                            ])
                            self.set_ata_flow_to_tracked(tracked, dst, 'R7')
                # [Rule 8, 9] ret <- any args
                if (idata['ret']['var'] is not None):
                    self.taint_prop_info['mo']['num_uses']['R8-9']['cntr'] += 1
                    self.taint_prop_info['mo']['num_uses']['R8-9']['ids'].append([
                        r['tag'],
                        r['line'],
                    ])
                    self.propagate_append(rslt, idata['ret']['var'], tracked, True)
                    self.set_ata_flow_to_tracked(tracked, idata['ret']['var'], 'R8-9')
        del tracked_before_taint

    def __get_ref_type_args(self, idata):
        ref_type_args = []
        for i in range(len(idata['prms'])):
            prm = idata['prms'][i]
            prm_type = idata['prm_types'][i]
            if (prm_type[0] == '[' or prm_type == 'Ljava/lang/Object;'):
                ref_type_args.append(prm)
            elif (i == 0 and idata['attr'] != 'static'):
                ref_type_args.append(prm)
        return ref_type_args

    def set_value_to_tracked(self, tracked, var, value):
        rslt = self.chk_tracked(tracked, var)
        rslt[5] = value

    def set_ata_flow_to_tracked(self, tracked, var, ata_flow):
        if (ata_flow not in tracked[var][3]):
            tracked[var][3].append(ata_flow)

    def propagate_append(self, src_tracked, dst, tracked, clear_value):
        dst_tracked = self.chk_tracked(tracked, dst)
        if ((dst_tracked[0] == False) or dst_tracked[0] < src_tracked[0]):
            dst_tracked[0] = src_tracked[0]
        dst_tracked[1] = dst_tracked[1] | src_tracked[1]
        dst_tracked[2] = dst_tracked[2] | src_tracked[2]
        for ata_flow in src_tracked[3]:
            if (ata_flow not in dst_tracked[3]):
                dst_tracked[3].append(ata_flow)
        dst_tracked[4] = dst_tracked[4] | src_tracked[4]
        if (clear_value):
            dst_tracked[5] = None

    def __propagate_by_copy(self, src_tracked, dst, tracked):
        tracked[dst] = src_tracked

    def __propagate(self, src, dst, tracked, direct_smali_tag):
        rslt = self.chk_tracked(tracked, src)
        if (rslt[0]):
            self.__set_tracked(tracked, dst, rslt[0], rslt[1], direct_smali_tag, rslt[3])
            return True
        self.__set_tracked(tracked, dst, False, set(), direct_smali_tag, rslt[3])
        return False

    def __set_tracked(self, tracked, v, tag, skey, direct_smali_tag, ata_flows = None):
        if (v.find('->') > -1):  # Ignore globals
            return
        else:
            if (v not in tracked.keys()):
                tracked[v] = [ False, set(), set(), [], set(), None ]
                # [
                #   taint_tag,
                #   {source_kind},
                #   {direct_parent_smali_tag},
                #   [ ata_flows ],
                #   field ref,
                #   value
                # ]
            tracked[v][0] = tag
            tracked[v][1] = tracked[v][1] | skey
            if (direct_smali_tag):
                tracked[v][2].add(direct_smali_tag)
            else:
                tracked[v][2] = set()
            if (ata_flows is not None):
                tracked[v][3] = ata_flows
            tracked[v][4] = set()
            tracked[v][5] = None
            return tracked[v]

    def __unset_tracked(self, tracked, v):
        if (v.find('->') > -1):  # Ignore globals
            return
        else:
            tracked[v] = [False, set(), set(), [], set(), None]

    def chk_tracked(self, tracked, v):
        if (v.find('->') > -1):  # Ignore globals
            return [False, set(), set(), [], set(), None]
        if (v in tracked.keys()):
            return tracked[v]
        tracked[v] = [False, set(), set(), [], set(), None]
        return tracked[v]

    def __clear_tracked(self, tracked):
        for v in tracked.keys():
            self.__unset_tracked(tracked, v)
