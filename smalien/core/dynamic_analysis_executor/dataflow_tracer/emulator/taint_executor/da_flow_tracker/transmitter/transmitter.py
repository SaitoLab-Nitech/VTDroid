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

import subprocess

class Transmitter():
    def __init__(self, r, var_tracked, ocr_info):
        self.tag = r['tag']
        self.var_tracked = var_tracked
        self.values = []
        self.ocr_info = ocr_info

    def get_var_tracked(self):
        return self.var_tracked

    def add_value(self, value):
        self.values.append(value)

    def match_values(self, value):
        newest_value = self.__preprocess_value(self.values[-1])
        value = self.__preprocess_value(value)
        if (newest_value == value):
            return True
        return False

    def __preprocess_value(self, value):
        if (value.startswith('89504e47')):
            value = self.__extract_text_from_image(value)
        try:
            processed = str(float(value))
        except:
            processed = value
        return processed

    def __extract_text_from_image(self, value):
        try:
            png_path = self.ocr_info['dst'] + 'secret_' + self.tag + '.png'
            text_path = self.ocr_info['dst'] + 'extracted_' + self.tag + '.txt'
            with open(png_path, 'bw') as f:
                f.write(bytes.fromhex(value))
            subprocess.call(
                self.ocr_info['cmd'] + ' ' + png_path + ' ' + text_path[:-4] + ' --psm 10',
                stderr=subprocess.DEVNULL,
                shell=True
            )
            with open(text_path, 'r') as f:
                data = f.read().split('\n')[0]
                if (len(data) > 0):
                    return data
        except:
            pass
        return value
