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

class Colors:
    KEY = '\033[94m'
    LINE = '\033[96m'
    ENDC = '\033[0m'

class Printer:
    def __init__(self, workspace, redirect_to):
        if (redirect_to == ''):
            self.f = sys.stdout
        else:
            self.f = open(workspace + redirect_to, 'w')

    def print(self, line):
        print(line, file=self.f, flush=True)

    def print_dict(self, info):
        for key, val in info.items():
            if (self.f == sys.stdout):
                print(f'{Colors.KEY}{key}{Colors.ENDC}: {val}, ', flush=True)
            else:
                self.print(f'{key}: {val}, ')

    def print_dict_summary(self, info):
        if (type(info) is dict):
            for key, val in info.items():
                self.print(f'{key = }')
                if (type(val) is dict):
                    self.print_dict_summary(val)
                elif (type(val) is list):
                    self.print(f'{" "*20}{len(val) = }')
                    if (len(val) > 0):
                        self.print(f'{" "*20}e.g. {val[0] = }')
                else:
                    self.print(f'{" "*20}{val = }')

    def print_line(self, line):
        if (self.f == sys.stdout):
            print(f'\n{Colors.LINE}{line}{Colors.ENDC}', flush=True)
        else: # Print to file
            self.print(line)

