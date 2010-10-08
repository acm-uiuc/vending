#!/usr/bin/env python

import sys, threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from McGeivaa import *

class GraphicalInterface:
	def __init__(self):
		self.app = QApplication(sys.argv)
		self.web = QWebView()
		self.web.load(QUrl("http://localhost:6969/gui/main"))
		log(Log.Info, "gui", "Qt/WebKit GUI is initialized.")
	def start(self):
		self.web.show()
		log(Log.Notice, "gui", "Interface is ready.")
		self.app.exec_()
	def setPage(self, page):
		self.web.load(QUrl("http://localhost:6969/gui/%s" % page))
		log(Log.Info, "gui", "Loaded page %s." % page)

