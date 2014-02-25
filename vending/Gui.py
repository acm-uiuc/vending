#!/usr/bin/env python

import sys, threading, urllib
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from Vending import *

class GraphicalInterface:
	"""
	Qt/Webkit GUI module
	"""
	def __init__(self):
		self.app = QApplication(sys.argv)
		self.web = QWebView()
		self.web.load(QUrl("http://%s:%d/gui/main" % (getConfig("web_server"), getConfig("web_port"))))
		log(Log.Info, "gui", "Qt/WebKit GUI is initialized.")
		self.page_queue = []
	def start(self):
		"""
		Start the interface and load the main page.
		"""
		log(Log.Notice, "gui", "Interface is ready.")
		self.web.show()
		self.timer = QTimer()
		QObject.connect(self.timer, SIGNAL("timeout()"), self.processUpdates)
		self.timer.start(100)
		self.app.exec_()
	def processUpdates(self):
		"""
		Internally process updates (Qt threading handling)
		"""
		if len(self.page_queue) > 0:
			self.setPage_(self.page_queue.pop())
	def setPage_(self, page):
		"""
		Actually set the page.
		"""
		self.web.load(QUrl("http://%s:%d/gui/%s" % (getConfig("web_server"), getConfig("web_port"), page)))
		log(Log.Info, "gui", "Loaded page %s." % page)
	def setPage(self, page):
		"""
		Request the GUI page to be set.
		"""
		self.page_queue.append(page)
	def showMain(self):
		"""
		Show the main window.
		"""
		self.setPage("main")
	def showConfirmation(self):
		"""
		Show a vending confirmation screen.
		"""
		self.setPage("confirm")
	def updateUser(self):
		"""
		Show the user page.
		"""
		self.setPage("user")
	def showCanNotAfford(self):
		"""
		Inform they user they can not afford an item.
		"""
		self.setPage("cantafford")
	def showCancel(self):
		"""
		Acknowledge that the user has cancelled their session.
		"""
		self.setPage("cancel")
	def showEmpty(self):
		"""
		Inform the user that this tray is empty.
		"""
		self.setPage("empty")
	def showCardError(self, error_msg):
		"""
		There was an error reading the card.
		"""
		self.setPage("card_error?%s" % urllib.quote(error_msg))
	def showAdminCard(self):
		self.setPage("admin_card")
