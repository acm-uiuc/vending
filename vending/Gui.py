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
		self.web.load(QUrl("http://%s:%d/gui/main" % (getConfig("web_server"), getConfig("web_port"))))
		log(Log.Info, "gui", "Qt/WebKit GUI is initialized.")
		self.page_queue = []
	def start(self):
		log(Log.Notice, "gui", "Interface is ready.")
		self.web.show()
		self.timer = QTimer()
		QObject.connect(self.timer, SIGNAL("timeout()"), self.processUpdates)
		self.timer.start(100)
		self.app.exec_()
	def processUpdates(self):
		if len(self.page_queue) > 0:
			self.setPage_(self.page_queue.pop())
	def setPage_(self, page):
		self.web.load(QUrl("http://localhost:6969/gui/%s" % page))
		log(Log.Info, "gui", "Loaded page %s." % page)
	def setPage(self, page):
		self.page_queue.append(page)
	def showMain(self):
		self.setPage("main")
	def showConfirmation(self):
		self.setPage("confirm")
	def updateUser(self):
		self.setPage("user")
	def showCanNotAfford(self):
		self.setPage("cantafford")
	def showVended(self):
		self.setPage("vended")
	def showCancel(self):
		self.setPage("cancel")
	def showEmpty(self):
		self.setPage("empty")
