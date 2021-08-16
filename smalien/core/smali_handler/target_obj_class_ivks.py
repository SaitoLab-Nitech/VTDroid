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

trgt_obj_clss_ivks = {
    'Ljava/io/ObjectOutput;->writeObject(Ljava/lang/Object;)V': 'serialization',
    'Ljava/io/ObjectOutputStream;->writeObject(Ljava/lang/Object;)V': 'serialization',
    'Ljava/io/ObjectOutputStream;->writeUnshared(Ljava/lang/Object;)V': 'serialization',
    'Ljava/io/PrintStream;->print(Ljava/lang/Object;)V': 'String.valueOf(Object)',
    'Ljava/io/PrintStream;->println(Ljava/lang/Object;)V': 'String.valueOf(Object)',
    'Ljava/io/PrintWriter;->print(Ljava/lang/Object;)V': 'String.valueOf(Object)',
    'Ljava/io/PrintWriter;->println(Ljava/lang/Object;)V': 'String.valueOf(Object)',
}
