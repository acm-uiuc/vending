#!/usr/bin/env python
"""
	The Caffeine Interface (Alpha)

	Powered by ACM Vending
	Uses:
	- MySQL for Database Backend
	- A theme based on the original PHP web interface
	- GUI is designed for a large screen
	
"""

from vending import Db, Gui, Serial, Web, Vending

class Caffeine(Vending.Vending):
	def start(self):
		Vending.Environment.tool = self
		self.serial = Serial.Serial()
		self.db = Db.MySQLBackend()
		self.web = Web.Server()
		self.gui = Gui.GraphicalInterface()
		Vending.Vending.start(self)

Caffeine().start()
