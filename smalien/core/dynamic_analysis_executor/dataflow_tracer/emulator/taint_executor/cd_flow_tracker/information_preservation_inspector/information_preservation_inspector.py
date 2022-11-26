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


class InformationPreservationInspector():
    def check_information_preservation_vis(self, receptor, b):
        # if (len(b.get_values_with_both_conditions()) < 2):
        #     return False

        # Check 1
        result = self.__check_unique_decodability(
            receptor.get_branch_values(),
            receptor.get_values()
        )
        if (result):
            return True
        elif (len(set(receptor.get_values_before_branch()) - set(receptor.get_values())) > 0):
            # Check 2
            result = self.__check_unique_decodability(
                b.get_values(),
                b.get_compared_values()
            )
            if (result):
                return True
        return False

    def check_information_preservation_inv(self, da_receptor, receptor, b):
        # if (len(b.get_values_with_both_conditions()) < 2):
        #     return False

        # Check 1
        result = self.__check_unique_decodability(
            receptor.get_branch_values(),
            receptor.get_values()
        )
        if (result):
            return True
        elif (len(set(da_receptor['values']) - set(receptor.get_values())) > 0):
            # Check 2
            result = self.__check_unique_decodability(
                b.get_values(),
                b.get_compared_values()
            )
            if (result):
                return True
        return False

    def __check_unique_decodability(self, words, codewords):
        assert len(words) == len(codewords)
        mapping = {}
        result = True
        for i in range(len(codewords)):
            w = words[i]
            cw = codewords[i]
            if (cw not in mapping.keys()):
                mapping[cw] = w
            elif (mapping[cw] != w):
                result = False
                break
        return result
