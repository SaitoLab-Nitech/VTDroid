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

# 13 APIs used for the detection of user-input validation [Zhao2020S&P]

user_input_sinks = {
    # Object
    'Ljava/lang/Object;': [
        'equals(Ljava/lang/Object;)Z',
    ],
    # String
    'Ljava/lang/String;': [
        'equals(Ljava/lang/Object;)Z',
        'indexOf(Ljava/lang/String;)I',
        'lastIndexOf(Ljava/lang/String;)I',
        'equalsIgnoreCase(Ljava/lang/String;)Z',
        'contentEquals(Ljava/lang/StringBuffer;)Z',
        'contentEquals(Ljava/lang/CharSequence;)Z',
        'contains(Ljava/lang/CharSequence;)Z',
    ],
    # StringBuffer
    'Ljava/lang/StringBuffer;': [
        'indexOf(Ljava/lang/String;)I',
        'lastIndexOf(Ljava/lang/String;)I',
    ],
    # TextUtils
    'Landroid/text/TextUtils;': [
        'equals(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Z',
    ],
    # HashMap
    'Ljava/util/HashMap;': [
        'containsKey(Ljava/lang/Object;)Z',
    ],
    # Map
    'Ljava/util/Map;': [
        'get(Ljava/lang/Object;)Ljava/lang/Object;',
    ],
}
