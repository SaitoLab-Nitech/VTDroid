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

import bz2
import json
import time
import pickle
import _pickle as cPickle
import subprocess
from pprint import pprint
from ..taint_sources import sources
from .apk_handler import apk_handler as apk_hndr
from .smali_handler import smali_handler as sml_hndr
from .dynamic_analysis_executor import dynamic_analysis_executor as DA
from .code_coverage_calculator import code_coverage_calculator as CCC

class Controller():
    def __init__(self, app_info, parameters, ks):
        self.app_info = app_info
        self.parameters = parameters
        self.ks = ks
        self.time = 0
        self.smalis = None

        self.app_info['target_source'] = sources[parameters['target_source']]['keys']
        self.app_info['target_source_values'] = sources[parameters['target_source']]['values']

    def run(self):
        self.apk_hndr = apk_hndr.ApkHandler(
            self.app_info,
            self.ks,
            self.parameters['static_bytecode_instrumentation']
        )
        self.sml_hndr = sml_hndr.SmaliHandler(
            self.app_info,
            self.parameters['static_bytecode_instrumentation']
        )

        if ('unpack' in self.app_info.keys()):
            print('  Copying and unpackaging')
            start = time.time()
            self.apk_hndr.prologue()
            self.time += time.time() - start
            print('    Copying and unpackaging done in', self.time)

        if ('analyze' in self.app_info.keys()):
            print('  Analyzing')
            # Get package name and activity name
            self.apk_hndr.get_pkg_name()
            self.apk_hndr.get_activity_name()
            print(
                '    Package:', self.app_info['package'],
                ', Activity:', self.app_info['activity']
            )

            start = time.time()
            self.smalis, aux_meths = self.sml_hndr.run()
            self.__store_static_rslts()
            duration = time.time() - start
            self.time += duration
            print('  Analysis done in', duration)
            if (aux_meths == 0):
                print('  No aux meth generated')
                return

        #input('Press enter to continue')

        if ('pack' in self.app_info.keys()):
            print('  Packing and signing')
            start = time.time()
            self.apk_hndr.epilogue()
            duration = time.time() - start
            self.time += duration
            print('  Packing and signing done in', duration)

        if (len(set(self.app_info.keys()) & { 'unpack', 'analyze', 'pack' }) == 3):
            print('Static bytecode instrumentation done in', self.time)

        if ('trace' in self.app_info.keys()):
            #print('  Tracing data flows')
            #start = time.time()
            self.__load_static_rslts()
            self.DA = DA.DynAnalysisExecutor(
                self.smalis,
                self.app_info['workspace'],
                self.app_info['smalien_log_path'],
                self.app_info['target_source'],
                self.app_info['target_source_values'],
                self.parameters
            )
            self.DA.run()

        if ('coverage' in self.app_info.keys()):
            start = time.time()
            self.__load_static_rslts()
            print('  Calculating code coverage', flush=True)
            ccc = CCC.CodeCoverageCalculator(
                self.smalis,
                self.app_info['smalien_log_path'],
                self.app_info['workspace'],
                self.parameters
            )
            ccc.calculate_method_coverage()
            print('  Calculation done in', time.time() - start, flush=True)
        # Free memory
        del self.smalis

    def __load_static_rslts(self):
        if (self.smalis is None):
            try:
                data = bz2.BZ2File(self.app_info['sbi_results'], 'rb')
                self.smalis = cPickle.load(data)
            except:
                with open(self.app_info['sbi_results'], 'rb') as f:
                    self.smalis = pickle.load(f)

    def __store_static_rslts(self):
        with bz2.BZ2File(self.app_info['sbi_results'], 'w') as f:
            cPickle.dump(self.smalis, f)
