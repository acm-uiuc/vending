# -*- coding: UTF-8 -*-

#
#
# +-----------------------------------------------------------------+
# | Copyright (c) 2008 Hamid Alipour                                |
# | http://blog.code-head.com/pml-a-python-template-engine          |
# | November 9, 2008                                                |
# | Fast, compact and extendible Python template engine             |
# +-----------------------------------------------------------------+
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  
# To ask questions or discuss see the comment section here:
# http://blog.code-head.com/pml-a-python-template-engine
# 
#


import re
from pml import PMLHelper


_cycle_tmp = {"current_index": 0, "values": []}
def cycle(self, values, sep="|"):
    if len(_cycle_tmp["values"]) == 0:
        _cycle_tmp["values"] = values.split(sep)
    next_value = _cycle_tmp["values"][_cycle_tmp["current_index"]] 
    if _cycle_tmp["current_index"] < len(_cycle_tmp["values"]) - 1:
        _cycle_tmp["current_index"] += 1
    else:
        _cycle_tmp["current_index"] = 0
    return next_value.strip()
PMLHelper.cycle = cycle

def strip_white_spaces(self, buffer):
    return re.sub("\s+", " ", buffer)
PMLHelper.strip_white_spaces = strip_white_spaces

def fix_smart_quotes(self, buffer):
    search = [chr(145), chr(146), chr(147), chr(148), chr(151)]
    replace = ["'", "'", '"', '"', "-"]
    for i, v in enumerate(search):
        buffer = buffer.replace(v, replace[i])
    return buffer
PMLHelper.fix_smart_quotes = fix_smart_quotes

def fix_xhtml_single_tags(self, buffer):
    """ Very simple for now. """
    search = ["<br>", "<hr>"]
    replace = ["<br />", "<hr />"]
    for i, v in enumerate(search):
        buffer = re.sub(re.compile(v, re.IGNORECASE), replace[i], buffer)
    return buffer
PMLHelper.fix_xhtml_single_tags = fix_xhtml_single_tags

def fix_xhtml_entities(self, buffer):
    return re.sub('(?<!&)&(?![^ ]+;|&)', '&amp;', buffer)
PMLHelper.fix_xhtml_entities = fix_xhtml_entities
    