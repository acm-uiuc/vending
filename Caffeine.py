#!/usr/bin/env python
"""
	The Caffeine Interface (Alpha)
"""

from vending import Db, Gui, Serial, Web, Vending

class Caffeine(Vending.Vending):
	def start(self):
		Vending.Environment.tool = self
		self.serial = Serial.Serial()
		self.db = Db.MySQLBackend()
		self.web = Web.Server()
		self.gui = Gui.GraphicalInterface()
		self.serial.write("\xa0")
		Vending.Vending.start(self)

Caffeine().start()
