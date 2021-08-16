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

exp_v2v = {
    # inst dst, src
    'move': {
        'class': 0
    },
    'move/16': {
        'class': 0
    },
    'move/from16': {
        'class': 0
    },
    'move-wide': {
        'class': 0
    },
    'move-wide/16': {
        'class': 0
    },
    'move-wide/from16': {
        'class': 0
    },
    'move-object': {
        'class': 0
    },
    'move-object/16': {
        'class': 0
    },
    'move-object/from16': {
        'class': 0
    },
    'add-int/lit16': {
        'class': 0,
        'type': 'I'
    },
    'rsub-int/lit16': {
        'class': 0,
        'type': 'I'
    },
    'mul-int/lit16': {
        'class': 0,
        'type': 'I'
    },
    'div-int/lit16': {
        'class': 0,
        'type': 'I'
    },
    'rem-int/lit16': {
        'class': 0,
        'type': 'I'
    },
    'and-int/lit16': {
        'class': 0,
        'type': 'I'
    },
    'or-int/lit16': {
        'class': 0,
        'type': 'I'
    },
    'xor-int/lit16': {
        'class': 0,
        'type': 'I'
    },
    'add-int/lit8': {
        'class': 0,
        'type': 'I'
    },
    'rsub-int/lit8': {
        'class': 0,
        'type': 'I'
    },
    'mul-int/lit8': {
        'class': 0,
        'type': 'I'
    },
    'div-int/lit8': {
        'class': 0,
        'type': 'I'
    },
    'rem-int/lit8': {
        'class': 0,
        'type': 'I'
    },
    'and-int/lit8': {
        'class': 0,
        'type': 'I'
    },
    'or-int/lit8': {
        'class': 0,
        'type': 'I'
    },
    'xor-int/lit8': {
        'class': 0,
        'type': 'I'
    },
    'shl-int/lit8': {
        'class': 0,
        'type': 'I'
    },
    'shr-int/lit8': {
        'class': 0,
        'type': 'I'
    },
    'ushr-int/lit8': {
        'class': 0,
        'type': 'I'
    },
    'neg-int': {
        'class': 0,
        'type': 'I'
    },
    'not-int': {
        'class': 0,
        'type': 'I'
    },
    'neg-long': {
        'class': 0,
        'type': 'J'
    },
    'not-long': {
        'class': 0,
        'type': 'J'
    },
    'neg-float': {
        'class': 0,
        'type': 'F'
    },
    'neg-double': {
        'class': 0,
        'type': 'D'
    },
    'int-to-byte': {
        'class': 0,
        'type': 'B'
    },
    'int-to-short': {
        'class': 0,
        'type': 'S'
    },
    'int-to-char': {
        'class': 0,
        'type': 'C'
    },
    'int-to-long': {
        'class': 0,
        'type': 'J'
    },
    'int-to-float': {
        'class': 0,
        'type': 'F'
    },
    'int-to-double': {
        'class': 0,
        'type': 'D'
    },
    'long-to-int': {
        'class': 0,
        'type': 'I'
    },
    'long-to-float': {
        'class': 0,
        'type': 'F'
    },
    'long-to-double': {
        'class': 0,
        'type': 'D'
    },
    'float-to-int': {
        'class': 0,
        'type': 'I'
    },
    'float-to-long': {
        'class': 0,
        'type': 'J'
    },
    'float-to-double': {
        'class': 0,
        'type': 'D'
    },
    'double-to-int': {
        'class': 0,
        'type': 'I'
    },
    'double-to-long': {
        'class': 0,
        'type': 'J'
    },
    'double-to-float': {
        'class': 0,
        'type': 'F'
    },

    # inst dst_src, src
    'add-int/2addr': {
        'class': 1,
        'type': 'I'
    },
    'sub-int/2addr': {
        'class': 1,
        'type': 'I'
    },
    'mul-int/2addr': {
        'class': 1,
        'type': 'I'
    },
    'div-int/2addr': {
        'class': 1,
        'type': 'I'
    },
    'rem-int/2addr': {
        'class': 1,
        'type': 'I'
    },
    'and-int/2addr': {
        'class': 1,
        'type': 'I'
    },
    'or-int/2addr': {
        'class': 1,
        'type': 'I'
    },
    'xor-int/2addr': {
        'class': 1,
        'type': 'I'
    },
    'shl-int/2addr': {
        'class': 1,
        'type': 'I'
    },
    'shr-int/2addr': {
        'class': 1,
        'type': 'I'
    },
    'ushr-int/2addr': {
        'class': 1,
        'type': 'I'
    },
    'add-long/2addr': {
        'class': 1,
        'type': 'J'
    },
    'sub-long/2addr': {
        'class': 1,
        'type': 'J'
    },
    'mul-long/2addr': {
        'class': 1,
        'type': 'J'
    },
    'div-long/2addr': {
        'class': 1,
        'type': 'J'
    },
    'rem-long/2addr': {
        'class': 1,
        'type': 'J'
    },
    'and-long/2addr': {
        'class': 1,
        'type': 'J'
    },
    'or-long/2addr': {
        'class': 1,
        'type': 'J'
    },
    'xor-long/2addr': {
        'class': 1,
        'type': 'J'
    },
    'shl-long/2addr': {
        'class': 1,
        'type': 'J'
    },
    'shr-long/2addr': {
        'class': 1,
        'type': 'J'
    },
    'ushr-long/2addr': {
        'class': 1,
        'type': 'J'
    },
    'add-float/2addr': {
        'class': 1,
        'type': 'F'
    },
    'sub-float/2addr': {
        'class': 1,
        'type': 'F'
    },
    'mul-float/2addr': {
        'class': 1,
        'type': 'F'
    },
    'div-float/2addr': {
        'class': 1,
        'type': 'F'
    },
    'rem-float/2addr': {
        'class': 1,
        'type': 'F'
    },
    'add-double/2addr': {
        'class': 1,
        'type': 'D'
    },
    'sub-double/2addr': {
        'class': 1,
        'type': 'D'
    },
    'mul-double/2addr': {
        'class': 1,
        'type': 'D'
    },
    'div-double/2addr': {
        'class': 1,
        'type': 'D'
    },
    'rem-double/2addr': {
        'class': 1,
        'type': 'D'
    },

    # inst dest, src, src
    'add-int': {
        'class': 2,
        'type': 'I'
    },
    'sub-int': {
        'class': 2,
        'type': 'I'
    },
    'mul-int': {
        'class': 2,
        'type': 'I'
    },
    'div-int': {
        'class': 2,
        'type': 'I'
    },
    'rem-int': {
        'class': 2,
        'type': 'I'
    },
    'and-int': {
        'class': 2,
        'type': 'I'
    },
    'or-int': {
        'class': 2,
        'type': 'I'
    },
    'xor-int': {
        'class': 2,
        'type': 'I'
    },
    'shl-int': {
        'class': 2,
        'type': 'I'
    },
    'shr-int': {
        'class': 2,
        'type': 'I'
    },
    'ushr-int': {
        'class': 2,
        'type': 'I'
    },
    'add-long': {
        'class': 2,
        'type': 'J'
    },
    'sub-long': {
        'class': 2,
        'type': 'J'
    },
    'mul-long': {
        'class': 2,
        'type': 'J'
    },
    'div-long': {
        'class': 2,
        'type': 'J'
    },
    'rem-long': {
        'class': 2,
        'type': 'J'
    },
    'and-long': {
        'class': 2,
        'type': 'J'
    },
    'or-long': {
        'class': 2,
        'type': 'J'
    },
    'xor-long': {
        'class': 2,
        'type': 'J'
    },
    'shl-long': {
        'class': 2,
        'type': 'J'
    },
    'shr-long': {
        'class': 2,
        'type': 'J'
    },
    'ushr-long': {
        'class': 2,
        'type': 'J'
    },
    'add-float': {
        'class': 2,
        'type': 'F'
    },
    'sub-float': {
        'class': 2,
        'type': 'F'
    },
    'mul-float': {
        'class': 2,
        'type': 'F'
    },
    'div-float': {
        'class': 2,
        'type': 'F'
    },
    'rem-float': {
        'class': 2,
        'type': 'F'
    },
    'add-double': {
        'class': 2,
        'type': 'D'
    },
    'sub-double': {
        'class': 2,
        'type': 'D'
    },
    'mul-double': {
        'class': 2,
        'type': 'D'
    },
    'div-double': {
        'class': 2,
        'type': 'D'
    },
    'rem-double': {
        'class': 2,
        'type': 'D'
    },
}

ivk = {
    'invoke-virtual': {
        'class': 0
    },
    'invoke-super': {
        'class': 0
    },
    'invoke-direct': {
        'class': 0
    },
    'invoke-interface': {
        'class': 0
    },
    'invoke-virtual/range': {
        'class': 0
    },
    'invoke-super/range': {
        'class': 0
    },
    'invoke-direct/range': {
        'class': 0
    },
    'invoke-interface/range': {
        'class': 0
    },
    'invoke-static': {
        'class': 1
    },
    'invoke-static/range': {
        'class': 1
    },
    'invoke-polymorphic': {
        'class': 2
    },
    'invoke-polymorphic/range': {
        'class': 2
    },
    'invoke-custom': {
        'class': 2
    },
    'invoke-custom/range': {
        'class': 2
    },
}

obscr = {
    'const': {
        'class': 0,
        'type': 'numeric'
    },
    'const/4': {
        'class': 0,
        'type': 'numeric'
    },
    'const/16': {
        'class': 0,
        'type': 'numeric'
    },
    'const/high16': {
        'class': 0,
        'type': 'numeric'
    },
    'const-wide': {
        'class': 0,
        'type': 'numeric'
    },
    'const-wide/16': {
        'class': 0,
        'type': 'numeric'
    },
    'const-wide/32': {
        'class': 0,
        'type': 'numeric'
    },
    'const-wide/high16': {
        'class': 0,
        'type': 'numeric'
    },
    'const-string': {
        'class': 0,
        'type': 'string'
    },
    'const-string/jumbo': {
        'class': 0,
        'type': 'string'
    },
    'const-class': {
        'class': 0,
        'type': 'string'
    },  # old type: 'class'
    'const-method-handle': {
        'class': 0,
        'type': 'string'
    },  # old type: 'method_handler'
    'const-method-type': {
        'class': 0,
        'type': 'string'
    },  # old type: 'method_type'
    'cmpl-float': {
        'class': 1,
        'type': 'F'
    },
    'cmpg-float': {
        'class': 1,
        'type': 'F'
    },
    'cmpl-double': {
        'class': 1,
        'type': 'D'
    },
    'cmpg-double': {
        'class': 1,
        'type': 'D'
    },
    'cmp-long': {
        'class': 1,
        'type': 'J'
    },
    'return': {
        'class': 2
    },
    'return-void': {
        'class': 2
    },
    'return-wide': {
        'class': 2
    },
    'return-object': {
        'class': 2
    },
    'new-array': {
        'class': 3
    },
    'array-length': {
        'class': 3
    },
    'fill-array-data': {
        'class': 3
    },
    'filled-new-array': {
        'class': 3,
        'filled': True
    },  # with move-result
    'filled-new-array/range': {
        'class': 3,
        'filled': True
    },  # with move-result
    'move-exception': {
        'class': 4
    },
    'instance-of': {
        'class': 5
    },
    'new-instance': {
        'class': 5
    },
    'sget': {
        'class': 6
    },
    'sget-byte': {
        'class': 6
    },
    'sget-short': {
        'class': 6
    },
    'sget-char': {
        'class': 6
    },
    'sget-boolean': {
        'class': 6
    },
    'sget-wide': {
        'class': 6
    },
    'sget-object': {
        'class': 6
    },
    'iget': {
        'class': 6
    },
    'iget-byte': {
        'class': 6
    },
    'iget-short': {
        'class': 6
    },
    'iget-char': {
        'class': 6
    },
    'iget-boolean': {
        'class': 6
    },
    'iget-wide': {
        'class': 6
    },
    'iget-object': {
        'class': 6
    },
    'sput': {
        'class': 7
    },
    'sput-byte': {
        'class': 7
    },
    'sput-short': {
        'class': 7
    },
    'sput-char': {
        'class': 7
    },
    'sput-boolean': {
        'class': 7
    },
    'sput-wide': {
        'class': 7
    },
    'sput-object': {
        'class': 7
    },
    'iput': {
        'class': 7
    },
    'iput-byte': {
        'class': 7
    },
    'iput-short': {
        'class': 7
    },
    'iput-char': {
        'class': 7
    },
    'iput-boolean': {
        'class': 7
    },
    'iput-wide': {
        'class': 7
    },
    'iput-object': {
        'class': 7
    },
    'aget': {
        'class': 8
    },
    'aget-byte': {
        'class': 8
    },
    'aget-short': {
        'class': 8
    },
    'aget-char': {
        'class': 8
    },
    'aget-boolean': {
        'class': 8
    },
    'aget-wide': {
        'class': 8
    },
    'aget-object': {
        'class': 8
    },
    'aput': {
        'class': 9
    },
    'aput-byte': {
        'class': 9
    },
    'aput-short': {
        'class': 9
    },
    'aput-char': {
        'class': 9
    },
    'aput-boolean': {
        'class': 9
    },
    'aput-wide': {
        'class': 9
    },
    'aput-object': {
        'class': 9
    },
}

brnch = {
    'if-eq': {
        'class': 0
    },
    'if-ne': {
        'class': 0
    },
    'if-lt': {
        'class': 0
    },
    'if-le': {
        'class': 0
    },
    'if-ge': {
        'class': 0
    },
    'if-gt': {
        'class': 0
    },
    'if-eqz': {
        'class': 0
    },
    'if-nez': {
        'class': 0
    },
    'if-ltz': {
        'class': 0
    },
    'if-lez': {
        'class': 0
    },
    'if-gtz': {
        'class': 0
    },
    'if-gez': {
        'class': 0
    },
    'packed-switch': {
        'class': 1
    },
    'sparse-switch': {
        'class': 1
    },
    'goto': {
        'class': 2
    },
    'goto/16': {
        'class': 2
    },
    'goto/32': {
        'class': 2
    },
    'throw': {
        'class': 3
    },
}

label = {
    ':cond': {
        'class': 0
    },
    ':goto': {
        'class': 1
    },
    ':pswitch': {
        'class': 2
    },
    ':pswitch_data': {
        'class': 2
    },
    ':sswitch': {
        'class': 2
    },
    ':sswitch_data': {
        'class': 2
    },
    ':try_start': {
        'class': 3
    },
    ':try_end': {
        'class': 4
    },
    '.catch': {
        'class': 5
    },
    '.catchall': {
        'class': 5
    },
    ':catch': {
        'class': 6
    },
    ':catchall': {
        'class': 6
    },
}
