"""
	Machine-Controlled, Generic, Expandable Interface for Vending and Amusement Appliances
	(McGeivaa)

	An API for creating unified systems for managing and using vending machines and arcade games
	and attaching them to the Internet.
"""

import sys

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
		sys.stdout.write("[%s] %s: %s\n" % (_logNames[log_type], module_name, log_message))
	pass # TODO: Write to log file regardless

_logNames = ["Error", "Warn", "Notice", "Info"]

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

class VendingUser:
	def __init__(self, uin, uid, extra):
		self.uin = uin
		self.uid = uid
		self.extra = extra
		log(Log.Info,"api-user","Authenticated user %s %s with balance $%.2f" % (self.extra['first_name'], self.extra['last_name'], self.extra['balance']))

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
		self.gui.start() # GUI should take over from here.
	def handleSerialData(self, data):
		if data.startswith(getConfig("serial_data_card_prefix")):
			log(Log.Verbose, "api-serial", "^ Card swipe.")
			self.handleCardSwipe(data.replace(getConfig("serial_data_card_prefix"),""))
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



"""
	Transaction Classes
"""

class User:
	def __init__(self, uid):
		self.uid = uid
	def chargeMoney(self, amount):
		pass
