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
				if Vending.Environment.state == Vending.State.Ready:
					wfile.write("Authenticating user with UIN %s\n" % args[1])
					self.db.authenticateUser(args[1])
				else:
					wfile.write("Can not authorize now, wait until system is 'Ready'.\n")
				return True
			elif args[0] == "request":
				if len(args) < 2:
					wfile.write("No tray specified.\n")
				else:
					if Vending.Environment.state == Vending.State.Authenticated:
						self.handleButtonPress(args[1])
					else:
						wfile.write("No user authenticated, log in first.\n")
				return True
			elif args[0] == "confirm":
				if Vending.Environment.state == Vending.State.Confirm:
					self.handleButtonPress(str(Vending.Environment.last_button))
				else:
					wfile.write("Can not confirm, no request made.\n")
				return True
			elif args[0] == "setpage":
				wfile.write("Setting GUI page to `%s.html`\n" % args[1])
				self.gui.setPage(args[1])
				return True
			else:
				return False
Caffeine().start()
