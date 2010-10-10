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
		Vending.Vending.start(self)
	def telnetCommand(self, command, wfile, rfile):
		if Vending.Vending.telnetCommand(self, command, wfile, rfile):
			return True
		else:
			args = command.split(" ")
			if args[0] == "user":
				wfile.write("Authenticating user with UIN %s\n" % args[1])
				self.db.authenticateUser(args[1])
				return True
			elif args[0] == "setpage":
				wfile.write("Setting GUI page to `%s.html`\n" % args[1])
				self.gui.setPage(args[1])
				return True
			else:
				return False
Caffeine().start()
