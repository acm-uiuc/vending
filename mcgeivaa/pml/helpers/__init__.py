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


import glob
import imp
import os


path = os.path.dirname(__file__)

def file_name(helper):
    return os.path.basename(helper).split(".")[0]

def load_helper(helper):
    # TODO: Document this, no "." in helpers file name
    imp.load_module(helper, *imp.find_module(helper, [path]))
    
for helper in glob.glob(os.path.join(path, '*.py')):
    helper = file_name(helper)
    if helper != '__init__':
        load_helper(helper)
