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

class TCFlowTracker():

    threshold = 100
    tc_data  = {
        'decoders': [],
        'encoders': {},
    }
    executed_command = []

    def detect_tc_flow(self, r, r_end, tracked):
        if (r['idata'] is not None):
            idata = r['idata']
            is_decoder = self.__detect_decoder(idata)
            if (is_decoder):
                TCFlowTracker.tc_data['decoders'].append({
                    'id': r['tag'],
                    'timestamp': r['time'],
                    'following_encoders': {},
                })
                # Detect TC flow
                for encoder_id, encoder_info in TCFlowTracker.tc_data['encoders'].items():
                    is_tc_flow = self.__verify_tc_flow_between_encoders_and_previous_decoders(
                        encoder_id,
                        encoder_info
                    )
                    #print(f'Detecting tc flow {encoder_id = } at a new decoder {r["tag"] = }')
                    #print(f'{is_tc_flow = }, {encoder_info["intervals"] = }')
                    #print(f'{encoder_info["map"] = }')
                    #print(f'{encoder_info["minimum_diff"] = }')
                    #print('\n')
                    if (is_tc_flow):
                        if (encoder_info['type'] == 'command'):
                            self.taint_prop_info['tc']['num_uses']['invisible']['cntr'] += 1
                            self.taint_prop_info['tc']['num_uses']['invisible']['ids'].append([
                                encoder_id,
                                r['tag'],
                            ])
                        else:
                            self.taint_prop_info['tc']['num_uses']['visible']['cntr'] += 1
                            self.taint_prop_info['tc']['num_uses']['visible']['ids'].append([
                                encoder_id,
                                r['tag'],
                            ])
                        self.propagate_append(encoder_info['taint'], r['var'], tracked, False)
                        self.set_ata_flow_to_tracked(
                            tracked,
                            r['var'],
                            f'TC: {encoder_id} -> {r["tag"]}'
                        )
            else:
                encoder_type = self.__detect_encoder(idata, r['time'], r_end['time'])
                if (encoder_type):
                    taint = self.__check_tracked_and_get_value_and_taint(
                        encoder_type,
                        idata,
                        tracked,
                        r
                    )
                    if (taint is None):
                        return
                    value = taint[5]
                    # Save the taint of encoder
                    if (r['tag'] not in TCFlowTracker.tc_data['encoders'].keys()):
                        TCFlowTracker.tc_data['encoders'][r['tag']] = {
                            'taint': taint,
                            'type': encoder_type,
                            'intervals': [],
                            'map': {},
                            'minimum_diff': TCFlowTracker.threshold,
                        }
                    # Set encoder's value to decoder
                    if (TCFlowTracker.tc_data['decoders'] != []):
                        TCFlowTracker.tc_data['decoders'][-1]['following_encoders'][r['tag']] = value
                else:
                    self.__detect_and_record_executed_command(r, tracked)

    # Decoder detection
    def __detect_decoder(self, idata):
        if (idata['kind'] == 'move-result' and idata['api']['site'] == 'api'):
            return self.__detect_decoder_by_name(idata['api'])
        elif ('sink' in idata.keys() and idata['sink'] == 'privacy_leak'):
            return True
        return False

    def __detect_decoder_by_name(self, idata):
        if (idata['class'] == 'Ljava/lang/System;' and idata['method'] == 'currentTimeMillis()J'):
            return True
        return False

    # Encoder detection
    def __detect_encoder(self, idata, curr_time, next_time):
        if (idata['kind'] == 'ivk' and idata['site'] == 'api'):
            return self.__detect_encoder_of_system(idata, curr_time, next_time)
        elif (idata['kind'] in [ 'if', 'cond' ]):
            return self.__detect_encoder_of_loop()
        return False

    def __detect_encoder_of_loop(self):
        return 'loop'

    def __detect_encoder_of_system(self, idata, curr_time, next_time):
        return self.__detect_encoder_of_system_by_name(idata)

    def __detect_encoder_of_system_by_name(self, idata):
        if (idata['class'] == 'Ljava/lang/Thread;' and idata['method'] == 'sleep(J)V'):
            return 'api'
        elif (idata['class'] == 'Ljava/lang/Process;' and idata['method'] == 'waitFor()I'):
            return 'command'
        return False

    def __check_tracked_and_get_value_and_taint(self, encoder_type, idata, tracked, r):
        if (encoder_type == 'api'):
            param = idata['prms'][0]
            if (param in tracked.keys()):
                if (tracked[param][0] and tracked[param][5] is not None):
                    return copy.deepcopy(tracked[param])
        elif (encoder_type == 'command'):
            if (TCFlowTracker.executed_command != []):
                return TCFlowTracker.executed_command[-1]['taint']
        elif (encoder_type == 'loop'):
            vars = idata['vars'] if idata['kind'] == 'if' else idata['if_vars']
            for var in vars:
                if (var in tracked.keys()):
                    if (tracked[var][0] and tracked[var][5] is not None):
                        return copy.deepcopy(tracked[var])

    def __verify_tc_flow_between_encoders_and_previous_decoders(self, encoder_id, encoder_info):
        if (len(TCFlowTracker.tc_data['decoders']) < 2):
            return
        new_decoder = TCFlowTracker.tc_data['decoders'][-2]
        # Calculate intervals
        intervals = encoder_info['intervals'] # [ [ encoded_value, decoder_1, decoder_2, interval ] ]
        if (encoder_id in new_decoder['following_encoders'].keys()):
            encoder_value = new_decoder['following_encoders'][encoder_id]
            if (intervals != [] and intervals[-1][0] == encoder_value):
                pass
            else:
                if (intervals != []):
                    intervals[-1].append(int(new_decoder['timestamp']))
                    intervals[-1].append(intervals[-1][2] - intervals[-1][1])
                intervals.append([
                    encoder_value,
                    int(new_decoder['timestamp']),
                ])
        # Check one-to-one mapping
        map = encoder_info['map']
        minimum_diff = encoder_info['minimum_diff']
        if (len(intervals) > 1 and len(intervals[1]) == 4):
            new_interval = intervals[-2]
            if (new_interval[0] not in map.keys()):
                map[new_interval[0]] = set()
            if (new_interval[3] not in map[new_interval[0]]):
                map[new_interval[0]].add(new_interval[3])
                minimum_diff = self.__calculate_minimum_diff(
                    map,
                    new_interval[0],
                    new_interval[3],
                    minimum_diff
                )
        encoder_info['minimum_diff'] = minimum_diff
        if (map != {} and minimum_diff >= TCFlowTracker.threshold):
            return True
        return False

    def __calculate_minimum_diff(self, map, target_key, target_val, current_minimum_diff):
        for key, vals in map.items():
            if (key != target_key):
                for val in vals:
                    diff = abs(val - target_val)
                    if (diff < current_minimum_diff):
                        current_minimum_diff = diff
        return current_minimum_diff

    def __detect_and_record_executed_command(self, r, tracked):
        if (r['idata'] is not None):
            idata = r['idata']
            if (idata['kind'] == 'ivk' and
                idata['site'] == 'api' and
                idata['class'] == 'Ljava/lang/Runtime;' and
                idata['method'] == 'exec([Ljava/lang/String;)Ljava/lang/Process;'
            ):
                command_var = idata['prms'][1]
                if (command_var in tracked.keys()):
                    taint = tracked[command_var]
                    command = taint[5]
                    if (command.find('sleep') > -1 or command.find('for') > -1):
                        TCFlowTracker.executed_command.append({
                            'id': r['tag'],
                            'taint': copy.deepcopy(taint),
                            'command': command,
                        })
