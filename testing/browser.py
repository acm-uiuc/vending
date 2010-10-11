#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

class browser:
	def __init__(self):
		self.app = QApplication(sys.argv)
		self.web = QWebView()
		self.web.load(QUrl("http://google.com"))
		self.web.show()
		self.app.exec_()
browser()


