#!/usr/bin/env python
"""
	The Caffeine Interface (Alpha)

	Powered by McGeivaa
	Uses:
	- MySQL for Database Backend
	- A theme based on the original PHP web interface
	- GUI is designed for a large screen
	
"""

from mcgeivaa import Db, Gui, Serial, Web
from mcgeivaa.McGeivaa import *

class Caffeine(Vending):
	def start(self):
		self.serial = Serial.Serial()
		self.db = Db.MySQLBackend()
		self.web = Web.Server()
		self.gui = Gui.GraphicalInterface()
		Vending.start(self)

Caffeine().start()
