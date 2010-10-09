"""
	Machine-Controlled, Generic, Expandable Interface for Vending and Amusement Appliances
	(McGeivaa)

	An API for creating unified systems for managing and using vending machines and arcade games
	and attaching them to the Internet.
"""

import sys, datetime

"""
	Logging Routines and Types
"""

def log(log_type, module_name, log_message):
	"""
		Log a message from an internal module
	"""
	if log_type > Log.Verbose:
		log(Log.Notice, "log", "Invalid log message type. Assuming `Info`.")
		log_type = Log.Info
	log_level = getConfig("log_print_level")
	if log_level is None:
		log_level = Log.Warn
	if log_type <= log_level:
		if getConfig("color_log"):
			sys.stdout.write("[%s%s\033[0m] \033[1m%s\033[0m: %s\n" % (_logColors[log_type], _logNames[log_type], module_name, log_message))
		else:
			sys.stdout.write("[%s] %s: %s\n" % (_logNames[log_type], module_name, log_message))
	if not Environment.log_file:
		Environment.log_file = open("debug.log", "a")
	Environment.log_file.write("%s [%s] %s: %s\n" % (datetime.datetime.now().isoformat(' '), _logNames[log_type], module_name, log_message))
	Environment.log_file.flush()

	pass # TODO: Write to log file regardless

_logNames	= ["Error",		"Warn",			"Notice",		"Info",			"Verbose"]
_logColors	= ["\033[1;31m","\033[1;33m",	"\033[1;34m",	"\033[1;30m",	""]

class Log:
	Error	= 0
	Warn	= 1
	Notice	= 2
	Info	= 3
	Verbose	= 4
	# TODO: Add any other log levels and ensure INFO is the most trivial. Adjust values to match.

def fatalError(message):
	"""
		Raise a fatal, internal error.
		Kill everything, log sufficiently, and inform the main class to restart.
	"""
	log(Log.Error, "api-main", "FATAL ERROR: %s -- Shutting down and restarting!" % message)
	sys.exit(0)
	# TODO: Shutdown, restart

"""
	State
"""

class State:
	Initializing	= 0
	Ready			= 1
	Authenticated	= 2
	Confirm			= 3
	Acknowledge		= 4
	Vending			= 5
	Idaho			= 6
	New_York		= 7
	OfMind			= 8


"""
	Configuration
"""

config_options = {}

def getConfig(config_option):
	if config_options.has_key(config_option):
		return config_options[config_option]
	else:
		return None

def _readConfig():
	"""
		Read the configuration
	"""
	try:
		conf_file = open("vend.conf")
		conf = conf_file.readlines()
		for i in conf:
			if (i.startswith("#")):
				continue
			i = i.replace("\n","")
			arr = i.split(": ")
			if len(arr) < 2:
				log(Log.Warn, "api-main", "Invalid configuration line: %s." % i)
				continue
			config_options[arr[0]] = eval(arr[1],globals(),locals())
			log(Log.Info, "api-main", "Setting config value `%s` to `%s`." % (arr[0], arr[1]))
		log(Log.Notice, "api-main", "Finished reading config file.")
	except:
		log(Log.Warn, "api-main", "Could not read config file (vend.conf), this may be bad.")

class Environment:
	tool = 0
	state = State.Initializing
	user = None
	trays = []
	waiting_for = -1
	last_button = -1
	log_file = None

class AckEvents:
	Vend = 0

class VendingUser:
	def __init__(self, uid, uin, extra):
		self.uin = uin
		self.uid = uid
		self.extra = extra
		log(Log.Info,"api-user","Authenticated user %s %s with balance $%.2f" % (self.extra['first_name'], self.extra['last_name'], self.extra['balance']))
	def canAfford(self, item):
		return self.extra['balance'] >= item.price

class VendingItem:
	def __init__(self, title, tray, quantity, price, extra):
		self.title = title
		self.tray = tray
		self.quantity = quantity
		self.price = price
		self.extra = extra

"""
	Main Object
"""

class Vending:
	"""
		Vending API super class
	"""
	def __init__(self):
		log(Log.Warn, "api-main", "Starting up...")
		_readConfig()
	def start(self):
		if self.serial is None:
			log(Log.Error, "api-main", "No Serial module loaded. This is fatal.")
			fatalError("No Serial module")
		if self.db is None:
			log(Log.Error, "api-main", "No DB module loaded. This is fatal.")
			fatalError("No DB module")
		if self.gui is None:
			log(Log.Error, "api-main", "No GUI module loaded. This is fatal.")
			fatalError("No GUI module")
		if self.web is None:
			log(Log.Error, "api-main", "No Web module loaded. This is fatal.")
			fatalError("No Web module")
		self.serial.start()
		self.db.start()
		self.web.start()
		Environment.state = State.Ready
		self.db.getItems()
		self.gui.start() # GUI should take over from here.
	def handleSerialData(self, data):
		if Environment.state == State.Ready:
			# Ready -> Card Reads
			if data.startswith(getConfig("serial_data_card_prefix")):
				log(Log.Verbose, "api-serial", "^ Card swipe.")
				self.handleCardSwipe(data.replace(getConfig("serial_data_card_prefix"),""))
		elif Environment.state == State.Authenticated or Environment.state == State.Confirm:
			# Authenticated -> Button Presses
			if data.startswith(getConfig("serial_data_button_prefix")):
				log(Log.Verbose, "api-serial", "^ Button press.")
				self.handleButtonPress(data.replace(getConfig("serial_data_button_prefix"),""))
		elif Environment.state == State.Acknowledge:
			if data.startswith(getConfig("serial_data_acknowledge_prefix")):
				log(Log.Info, "api-serial", "Acknowledged. Returning to Ready state.")
				Environment.state = State.Ready
				self.gui.showMain()
	def handleCardSwipe(self, card):
		if not card.startswith(";"):
			log(Log.Error,"card-swipe", "Bad card: Missing ;")
			return False
		if len(card) < 19:
			log(Log.Error,"card-swipe", "Bad card: Not really long enough.")
			return False
		if not card[17] == "=":
			log(Log.Error,"card-swipe", "Bad card: Missing =")
			return False
		card_uin = card[5:14] # UIN
		return self.db.authenticateUser(card_uin)
	def cancelTransaction(self):
		Environment.user = None
		Environment.tray = None
		Environment.state = State.Ready
		self.gui.showCancel()
	def handleButtonPress(self, data):
		if len(data) < 1:
			log(Log.Error, "button-press", "oh... crap (button press data is only one character")
			return False
		try:
			button_id = int(data[0])
		except:
			log(Log.Error, "button-press", "Button is not a number.")
			return False
		# XXX: REMOVE THIS! THIS WILL CANCEL THE SESSION ON ANY PRESS OF BUTTON 0
		if button_id == 0:
			self.cancelTransaction()
			return False
		# XXX: ^^^ REMOVE THIS
		if not data.find(getConfig("serial_data_button_up_prefix")) == "-1":
			log(Log.Verbose, "button-press", "fyi: Button was pressed quickly and up was received with down.")
		if Environment.state == State.Authenticated:
			# This is a button press from this user. Check the trays.
			log(Log.Info, "button-press", "Button %d pressed in Authenticated mode. Confirmation requested." % button_id)
			this_tray = Environment.trays[button_id]
			if Environment.trays[button_id].quantity < 1:
				self.gui.showEmpty()
				return False
			if Environment.user.canAfford(this_tray):
				self.gui.showConfirmation()
				Environment.state = State.Confirm
				Environment.last_button = button_id
				return True
			else:
				self.gui.showCanNotAfford()
				return False
		elif Environment.state == State.Confirm:
			if button_id == Environment.last_button:
				this_tray = Environment.trays[button_id]
				log(Log.Info, "button-press", "Confirming selection. Vending!")
				self.db.chargeUser(this_tray.price)
				self.db.vend(button_id)
				Environment.waiting_for = AckEvents.Vend
				Environment.state = State.Acknowledge
				self.serial.vend(button_id)
				return True
			else:
				log(Log.Info, "button-press", "User changed selection.")
				Environment.state = State.Authenticated
				return self.handleButtonPress(data)
	def telnetListCommands(self):
		return {"help": "Show this help text.", "status": "Display current system status."}
	def telnetCommand(self, command, wfile, rfile):
		log(Log.Info, "telnet", "Telnet command received: %s" % command)
		args = command.split(" ")
		if len(args) < 1:
			return
		if args[0] == "help":
			wfile.write("\033[1mWelcome to the ACM Vending telnet interface.\033[0m\n")
			wfile.write("You can use this interface to get information about this vending machine\n")
			wfile.write("and your ACM vending account.\n")
			wfile.write("\033[1mAvailable commands:\033[0m\n")
			for c, t in self.telnetListCommands().iteritems():
				wfile.write("%s %s\n" % (c.ljust(10),t))
		elif args[0] == "status":
			wfile.write("\033[1mTrays:\033[0m\n")
			for tray in Environment.trays:
				if tray.quantity == 0:
					color = "31"
				elif tray.quantity < 5:
					color = "1;33"
				elif tray.quantity < 25:
					color = "1;32"
				else:
					color = "1;34"
				wfile.write("%d: %s ($%.2f) \033[%sm%d remaining\033[0m\n" % (tray.tray, tray.title.ljust(20), tray.price, color, tray.quantity))
		# DEBUG COMMANDS XXX REMOVE THESE XXX
		elif args[0] == "user":
			wfile.write("Authenticating user with UIN %s\n" % args[1])
			self.db.authenticateUser(args[1])


"""
	Transaction Classes
"""

class User:
	def __init__(self, uid):
		self.uid = uid
	def chargeMoney(self, amount):
		pass
