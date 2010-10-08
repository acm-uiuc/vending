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
			self.setPage(self.page_queue.pop())
	def setPage(self, page):
		self.web.load(QUrl("http://localhost:6969/gui/%s" % page))
		log(Log.Info, "gui", "Loaded page %s." % page)
	def showMain(self):
		self.page_queue.append("main")
	def showConfirmation(self):
		self.page_queue.append("confirm")
	def updateUser(self):
		self.page_queue.append("user")
	def showCanNotAfford(self):
		self.page_queue.append("cantafford")
	def showVended(self):
		self.page_queue.append("vended")
	def showCancel(self):
		self.page_queue.append("cancel")
	def showEmpty(self):
		self.page_queue.append("empty")
