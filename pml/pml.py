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


__copyright__ = "Copyright (C) 2009 by Hamid Alipour"
__license__ = "GPL"
__version__ = "0.7.8 Beta"
__author__ = "Hamid Alipour"
__url__ = "http://blog.code-head.com/???"


import Cookie
import cStringIO
import cgi
import datetime
import glob
import gzip
import imp
import inspect
import marshal
import os
import py_compile
import random
import re
import string
import sys
import thread
import time

from mcgeivaa.McGeivaa import *

class PML(object):
    
    __instance = None
    
    def __new__(classtype, *args, **kwargs):
        if classtype != type(classtype.__instance):
            classtype.__instance = object.__new__(classtype, *args, **kwargs)
        return classtype.__instance
    
    def __init__(self, config=False):
        self.version = __version__
        self.start_time = 0
        self.output_sent = False
        self.headers_sent = False
        self.ds = os.sep
        self.pml_folder = os.path.dirname(__file__)
        self.timenow = time.time()
        
        self._pre_filters = {}
        self._post_filters = {}
        self._output_filters = {}
        self._var_filters = {}
        self._data = {}
        self._user_headers = []
        self._template_cache = {}
        self._var_cache = {}
        
        self.config = {}
        self.config["templates_folder"] = self.pml_folder + self.ds + "templates"
        self.config["tmp_folder"] = self.pml_folder + self.ds + "tmp"
        self.config["force_compile"] = False
        self.config["pack_output"] = False
        self.config["output_compression"] = False
        self.config["output_compress_level"] = 5
        self.config["encoding"] = 'UTF-8'
        self.config["print_errors"] = True
        self.config["auto_escape_html"] = True
        self.config["cache_templates"] = True
        self.config["cache_template_vars"] = True
        self.config["cleanup_smart_quotes"] = False
        self.config["cleanup_xhtml"] = False
        
        if config:
            self.config.update(config)
        
        self.executer = PMLExecuter(self)
        self.cache = PMLCache(self)
        self.output_capture = PMLOutputCapture(self)
        self.helper = PMLHelper(self)
        
        if self.config["auto_escape_html"]:
            self.add_var_filter(self.escape)
            
        if self.config["cleanup_smart_quotes"]:
            self.add_output_filter(self.helper.fix_smart_quotes)
        
        if self.config["cleanup_xhtml"]:
            self.add_output_filter(self.helper.fix_xhtml_single_tags)
            self.add_output_filter(self.helper.fix_xhtml_entities)
        
        if self.config["pack_output"]:
            self.add_output_filter(self.helper.strip_white_spaces)
        
        if self.config["output_compression"]:
            self.add_output_filter(self.gzip_output)
        
    def set_config(self, key, value):
        self.config[key] = value
        self.refresh_internal_cache()
    
    def get_config(self, key):
        return self.config[key]
    
    def add_pre_filter(self, func):
        self._pre_filters[func] = func
    
    def del_pre_filter(self, func):
        if self._pre_filters.has_key(func):
            del self._pre_filters[func]
    
    def add_post_filter(self, func):
        self._post_filters[func] = func
    
    def del_post_filter(self, func):
        if self._post_filters.has_key(func):
            del self._post_filters[func]
    
    def add_output_filter(self, func):
        self._output_filters[func] = func
    
    def del_output_filter(self, func):
        if self._output_filters.has_key(func):
            del self._output_filters[func]
    
    def add_var_filter(self, func):
        self._var_filters[func] = func
    
    def del_var_filter(self, func):
        if self._var_filters.has_key(func):
            del self._var_filters[func]
    
    def set(self, key, value=None):
        if isinstance(key, dict) and value == None:
            for k, v in key.iteritems():
                self._set(k, v)
        else:
            self._set(key, value)
    
    def _set(self, key, value):
        if self.config["cache_template_vars"] and self._var_cache.has_key(key):
            del self._var_cache[key]
        self._data[key] = value
    
    def get(self, key):
        if self._data.has_key(key):
            if self.config["cache_template_vars"]:
                if not self._var_cache.has_key(key):
                    self._var_cache[key] = self.apply_var_filters(self._data[key])
                return self._var_cache[key]
            else:
                return self.apply_var_filters(self._data[key])
        else:
            return "" # Everything is a string
    
    def delkey(self, key):
        if self._data.has_key(key):
            del self._data[key]
        if self.config["cache_template_vars"] and self._var_cache.has_key(key):
            del self._var_cache[key]
    
    def get_raw(self, key):
        if self._data.has_key(key):
            return self._data[key]
        else:
            return "" # Everything is a string
    
    def apply_var_filters(self, value):
        if len(self._var_filters) > 0:
            for k, v in self._var_filters.iteritems():
                value = self.deep_apply_func(value, v) 
        return value
    
    def deep_apply_func(self, value, func):
        if isinstance(value, dict):
            for k, v in value.iteritems():
                value[k] = self.deep_apply_func(v, func)
        elif isinstance(value, list):
            value = map(lambda v: self.deep_apply_func(v, func), value)
        elif isinstance(value, tuple):
            value = map(lambda v: self.deep_apply_func(v, func), value)
        elif isinstance(value, str):
            # TODO: Var filters only apply to strings
            value = func(value)
        return value
    
    def escape(self, value):
        return cgi.escape(value, True)
    
    def get_output(self, template):
        return self.template_instance(template).get_output()
    
    def print_template_error(self, template, line, error, compiled_template):
        self.raise_error("There was an error in your template:\n\n \tTemplate: " + template + "\n \tLine: " + line + " (In compiled template, see bellow)\n\tError Message: " + error + "\n\nHere is the compiled version of your template:\n\n" + compiled_template)
    
    def raise_error(self, error):
        if self.output_capture.capturing:
            self.output_capture.end()
        if self.config["print_errors"]:
            log(Log.Warn, "web-pml", "Template engine error: %s" % error)
            raise
        else:
            # TODO: Create a PMLException class with line numbers etc.
            raise
    
    def is_cached(self, template):
        return self.cache.is_cached(template)
    
    def refresh_cache(self, template):
        if self.config["cache_templates"] and self.template_cache.has_key(template):
            del self.template_cache[template]
        return self.cache.refresh(self.template_instance(template))
    
    def refresh_internal_cache(self):
        self.var_get_cache = {}
        self.template_cache = {}
    
    def template_instance(self, template):
        if self.config["cache_templates"]:
            if not self._template_cache.has_key(template) or self.config["force_compile"]:
                self._template_cache[template] = PMLTemplate(self, template)
            return self._template_cache[template]
        else:
            return PMLTemplate(self, template)
            
    def write_to_file(self, path, contents):
        open(path, "w").write(contents)
    
    def get_random_string(self):
        random.seed()
        chars = list("abcdefghijklmnopqrstuvwxyz")
        random.shuffle(chars)
        return "".join(chars)
    
    def clean_up_tmpfolder(self):
        for file in os.listdir(self.config["tmp_folder"]):
            path = self.config["tmp_folder"] + self.ds + file
            if os.path.getmtime(path) < self.config["tmp_clean_up_time"]:
                os.remove(path)
    
    def benchmark(self, stage, template):
        if self.start_time is 0:
            self.start_time = time.time()
        print "<!-- " + stage + ": " + template + " --> " + str(time.time() - self.start_time)
    
    def gzip_output(self, buffer):
        zbuf = cStringIO.StringIO()
        zfile = gzip.GzipFile(mode = "wb",  fileobj = zbuf, compresslevel = self.config["output_compress_level"])
        zfile.write(buffer)
        zfile.close()
        return zbuf.getvalue()  

class PMLTemplate(object):
    
    def __init__(self, pml, filename):
        self.pml = pml
        self.path = self.pml.config["templates_folder"] + self.pml.ds + filename
        if not os.path.exists(self.path):
            self.pml.raise_error("Couldn't find template \"%s\"." % self.path)
        
        nameclean = filename.replace(".", "_d_").replace("/", "_ds_")
        self.compiled_path = self.pml.config["tmp_folder"] + self.pml.ds + "PML_" + nameclean + ".pml"
        self.bytecode_path = self.pml.config["tmp_folder"] + self.pml.ds + "PML_" + nameclean + ".cpml"
        self.cache_path = self.pml.config["tmp_folder"] + self.pml.ds + "PML_" + nameclean + ".pml_cache"
        self.cache_info_path = self.pml.config["tmp_folder"] + self.pml.ds + "PML_" + nameclean + ".pml_cache_info"
        
        self._is_cached = None
        self._content = ""
        self._bytecode_content = ""
        self._cached_content = ""
        
        self.compile()
    
    def compile(self):
        if not os.path.exists(self.bytecode_path) or os.path.getmtime(self.bytecode_path) < os.path.getmtime(self.path) or self.pml.config["force_compile"]:
            compiler = PMLCompiler(self.pml)
            compiler.template = self
            compiler._pre_filters = self.pml._pre_filters
            compiler._post_filters = self.pml._post_filters
            compiler.compile() 
    
    def get_content(self):
        if self._content == "":
            self._content = open(self.path).read()
        return self._content
    
    def get_bytecode_content(self):
        if self._bytecode_content == "":
            bytecode = open(self.bytecode_path, "rb").read()
            if bytecode[:4] != imp.get_magic():
                # Recompile, different Python version?!
                force_compile = self.pml.get_config("force_compile")
                self.pml.set_config("force_compile", True)
                self.compile()
                self.pml.set_config("force_compile", force_compile) 
                return self.get_bytecode_content()
            bytecode = bytecode[8:]
            self._bytecode_content = marshal.loads(bytecode)
        return self._bytecode_content
    
    def is_cached(self):
        if self._is_cached == None:
            self._is_cached = self.pml.cache.is_cached(self) 
        return self._is_cached
    
    def get_cached_content(self):
        if self._cached_content == "":
            self._cached_content = self.pml.cache.get(self)
        return self._cached_content
    
    def get_output(self):
        if self.is_cached() and not self.pml.config["force_compile"]:
            return self.get_cached_content()
        return self.pml.executer.exec_pml(self)
        

class PMLCompiler(object):
    
    def __init__(self, pml):
        self.pml = pml
        self.template = ""
        self.current_line = 0
        self.tab_depth = 0
        self.tab_keywords = ["class", "def", "if", "elif", "else", "for", "while", "try", "except", "finally"]
        self.untab_keywords = map(lambda e: "#" + e, self.tab_keywords)
        self._keyword_stack = []
        self._pre_filters = {}
        self._post_filters = {}
        self.cacheable = False
        self.cache_time = 0
        
        self.keyword_handler = PMLCompilerKeywordHandler(self.pml, self)
    
    def apply_pre_filters(self, template):
        if len(self._pre_filters) > 0:
            for k, v in self._pre_filters.iteritems():
                template = v(template, self.pml)
        return template
    
    def apply_post_filters(self, template):
        if len(self._post_filters) > 0:
            for k, v in self._post_filters.iteritems():
                template = v(template, self.pml)
        return template
    
    def format_line(self, line):
        # TODO: Fix this
        self.current_line += len(line.splitlines())
        if line is not "":
            if (line.startswith('"') and line.endswith('\'')) or (line.startswith('\'') and line.endswith('"')):
                return self.get_padding() + "sys.stdout.write(''' " + line + " ''')\n"
            elif line.startswith('"') or line.endswith('"'):
                return self.get_padding() + "sys.stdout.write('''" + line + "''')\n"
            else:
                return self.get_padding() + "sys.stdout.write(\"\"\"" + line + "\"\"\")\n"
        else:
            return ""
    
    def format_pyline(self, line):
        self.current_line += 1
        line = line.strip()
        if line is not "":
            return self.get_padding() + line + "\n"
        else:
            return ""
    
    def get_padding(self):
        if self.tab_depth > 0:
            return " ".center(self.tab_depth * 4)
        else:
            return ""
    
    def is_pyblock(self, block):
        return block.lstrip().startswith("<?")
    
    def compile(self):
        compiled_template = self._compile()
        compiled_template = "# Generated by: PML v" + self.pml.version + " Hamid Alipour blog.code-head.com\n# -*- coding: " + self.pml.config["encoding"] + " -*-\n\n" + compiled_template
        self.pml.write_to_file(self.template.compiled_path, compiled_template)
        self.compile_to_bytecode()
        
    def _compile(self):
        tokens = re.compile("(\<\?\s*.*?\s+?\?\>)", re.IGNORECASE | re.DOTALL).split(self.apply_pre_filters(self.template.get_content()))
        buffer = ""
        for token in tokens:
            if self.is_pyblock(token):
                buffer += self.compile_pyblock(token)
            else:
                buffer += self.format_line(token)
        if len(self._keyword_stack) > 0:
            last_tab_keyword = self._keyword_stack.pop()
            self.pml.raise_error("You forgot to close a \"" + last_tab_keyword[0] + "\" in " + self.template.path + " near line: " + str(last_tab_keyword[1]) + "\n")
        if self.cacheable and self.cache_time > 0:
                buffer += "\n\n__PML_Cache_Expire__ = " + str(self.cache_time)
        return self.apply_post_filters(buffer)
    
    def compile_pyblock(self, block):
        buffer = ""
        
        for line in re.compile("\<\?\s*(.*?)\s+?\?\>", re.IGNORECASE | re.DOTALL).split(block)[1].splitlines():
            
            keywords = line.strip().split(" ")
            keyword = keywords[0].split(":")[0].strip().lower()
            
            if hasattr(self.keyword_handler, "handle_" + keyword):
                buffer += getattr(self.keyword_handler, "handle_" + keyword)(line, keyword, keywords)
            
            elif keyword.startswith("="):
                buffer += self.format_pyline("sys.stdout.write(" + keyword.split("=")[1].strip() + ")")
            
            elif keyword in self.tab_keywords:
                stack_item = (keyword, self.current_line)
                self._keyword_stack.append(stack_item)
                buffer += self.format_pyline(line)
                self.tab_depth += 1
            
            elif keyword in self.untab_keywords:
                last_tab_keyword = self._keyword_stack.pop()
                if keyword != "#" + last_tab_keyword[0]:
                   self.pml.raise_error("You forgot to close a \"%s\" in %s near line: %s" % (last_tab_keyword[0], self.template, str(last_tab_keyword[1])))
                self.tab_depth -= 1
            
            else:
                buffer += self.format_pyline(line)
                
        return buffer
    
    def compile_to_bytecode(self):
        try:
            py_compile.compile(self.template.compiled_path, self.template.bytecode_path, None, True)
        except Exception:
            # TODO: Error handling
            raise


class PMLCompilerKeywordHandler(object):
    
    def __init__(self, pml, compiler):
        self.pml = pml
        self.compiler = compiler
    
    def handle_include(self, line, keyword, args):
        buffer = ""
        _args = line.split(',')
        include_template = re.match(".*(\"|')(.+?)\\1.*", line, re.DOTALL).group(2)
        for arg in _args[1:]:
            arg = arg.strip() 
            buffer += self.compiler.format_pyline("\n pml.set(\"" + arg + "\", " + arg + ")")
        buffer += self.compiler.format_pyline("\n print pml.get_output(\"" + include_template + "\")")
        return buffer
    
    def handle_cache(self, line, keyword, args):
        self.compiler.cache_time = eval("self.pml.cache." + re.match(".*(\"|')(.+?)\\1.*", line, re.DOTALL).group(2).lower())
        self.compiler.cacheable = True
        return "" # It has to return an empty string at least
    
    def handle_print(self, line, keyword, args):
        _print = " ".join(args[1:]).strip()
        if _print.endswith(","):
            _print = _print[0:-1]
        _print = re.sub("('|\"|\))\s*,\s*('|\"|\()", "\\1 + \" \" + \\2", _print)
        return self.compiler.format_pyline("sys.stdout.write(" + _print + ")")
        

class PMLExecuter(object):
    
    def __init__(self, pml):
        self.pml = pml
        self._exec_id = 0
    
    def exec_pml(self, template):
        pml = self.pml
        helper = self.pml.helper
        if self._exec_id == 0:
            self.pml.output_capture.start()
        self.pml.output_capture.start_new_session()
        self._exec_id += 1
        __PML_Cache_Expire__ = 0
        try:
            exec template.get_bytecode_content()
        except Exception:
            self.pml.output_capture.end()
            # TODO: Error handling
            raise
        else:
            self._exec_id -= 1
            buffer = self.pml.output_capture.get_buffer()
            if __PML_Cache_Expire__ > 0:
                self.pml.cache.cache(template, buffer, __PML_Cache_Expire__)
            if self._exec_id == 0:
                self.pml.output_capture.end()
            return buffer


class PMLOutputCapture(object):
    
    def __init__(self, pml):
        self.pml = pml
        self.buffers = []
        self.lock = thread.allocate_lock()
        self.capturing = False
    
    def start(self):
        self.lock.acquire()
        self.python_stdout = sys.stdout
        self.capturing = True
        sys.stdout = self
    
    def end(self):
        sys.stdout = self.python_stdout
        self.buffers = []
        self.capturing = False
        self.lock.release()
    
    def start_new_session(self):
        self.buffers.append(cStringIO.StringIO()) 
    
    def write(self, string):
        self.buffers[-1].write(str(string).encode(self.pml.config["encoding"]))
    
    def get_buffer(self):
        return self.buffers.pop().getvalue()
    

class PMLHelper(object):
    
    def __init__(self, pml):
        self.pml = pml
        import helpers
    

class PMLCache(object):
    
    def __init__(self, pml):
        self.pml = pml
        self.a_second = 1
        self.a_minute = self.a_second * 60
        self.an_hour = self.a_minute * 60
        self.a_day = self.an_hour * 24
    
    def cache(self, template, buffer, seconds):
        # It was just compiled so
        self.pml.write_to_file(template.cache_path, buffer)
        self.pml.write_to_file(template.cache_info_path, str(self.pml.timenow + seconds))
        
    def is_cached(self, template):
        return os.path.exists(template.cache_info_path) and os.path.exists(template.cache_path) and self.pml.timenow < float(open(template.cache_info_path).read().strip())
    
    def get(self, template):
        return open(template.cache_path).read().strip()
    
    def refresh(self, template):
        self.pml.write_to_file(template.cache_info_path, str(self.pml.timenow - self.an_hour))
        template._is_cached = None
