"""
	The Caffeine Interface (Alpha)

	Powered by McGeivaa
	Uses:
	- MySQL for Database Backend
	- A theme based on the original PHP web interface
	- GUI is designed for a large screen
	
"""

from mcgeivaa import *

class Caffeine(Vending):
	def start(self):
		self.db = Db.MySQLBackend
		base.start(self)
