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
import json
from .arg_parser import arg_parser
from .core.controller import Controller

ksc_path = './key/keystore_conf.txt'


def load_keystore(ksc_path):
    with open(ksc_path, 'r') as f:
        data = f.read().split('\n')
        ks = {
            'key': data[0],
            'kspass': data[1],
            'kpass': data[2],
            'alias': data[3],
        }
        return ks

def load_parameters(path):
    with open(path, 'r') as f:
        return json.load(f)

def activate_snb(app_info):
    parameters = load_parameters(app_info['parameters_path'])
    if ('pack' in app_info.keys()):
        ks = load_keystore(ksc_path)
    else:
        ks = None
    controller = Controller(app_info, parameters, ks)
    controller.run()

if __name__ == '__main__':
    app_info = {}
    arg_parser(sys.argv, app_info)
    print('[ TAPK ]', app_info['tapk'])
    start = time.time()
    activate_snb(app_info)
    print(f'[ PROCESSING TIME ] {time.time() - start}')

