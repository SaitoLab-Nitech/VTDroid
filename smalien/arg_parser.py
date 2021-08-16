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

import os
import sys

def arg_parser(argv, app_info):
    target = argv[-1]
    if (target == '-h' or len(sys.argv) < 5):
        print_opts()
    elif (not os.path.isfile(target) and not os.path.isdir(target)):
        raise FileNotFoundError(f'{target} does not exist')
    else:
        workspace = sys.argv[-2] + '/'
        parameter_path = sys.argv[-3]
        app_info['workspace'] = workspace
        app_info['parameters_path'] = parameter_path
        app_info['tpath'] = target
        app_info['tapk'] = target.split('/')[-1]
        app_info['tdir'] = workspace + app_info['tapk'].replace('.apk', '') + '/'
        app_info['implanted'] = workspace + 'implanted_' + app_info['tapk']
        app_info['sbi_results'] = workspace + '/results_' + app_info['tapk'][:-4] + '.pickle'
        app_info['smalien_log_path'] = workspace + '/SmalienLog.txt'

    # Parse options
    i = 0
    opts = argv[1:-1]
    while i < len(opts):
        if (opts[i] == '-u'):
            app_info['unpack'] = True
        elif (opts[i] == '-a'):
            app_info['analyze'] = True
        elif (opts[i] == '-p'):
            app_info['pack'] = True
        elif (opts[i] == '-t'):
            app_info['trace'] = True
        elif (opts[i] == '-c'):
            app_info['coverage'] = True
        i += 1


def print_opts():
    print('usage: python3 -m smalien.main [-options] <path_to_parameter_file> <path_to_workspace> <path_to_apk>')
    print('options:')
    print('  -h: show help')
    print('  -u: unpack')
    print('  -a: static bytecode instrumentation')
    print('  -p: pack')
    print('  -t: trace information flows')
    print('  -c: calculate coverage')
    sys.exit()
