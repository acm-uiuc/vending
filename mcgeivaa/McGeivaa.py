"""
	Machine-Controlled, Generic, Expandable Interface for Vending and Amusement Appliances
	(McGeivaa)

	An API for creating unified systems for managing and using vending machines and arcade games
	and attaching them to the Internet.
"""

"""
	Logging Routines and Types
"""

def log(log_type, module_name, log_message):
	"""
		Log a message from an internal module
	"""
	if log_type > Log.Info:
		log(Log.Notice, "log", "Invalid log message type. Assuming `Info`.")
		log_type = Log.Info
	if log_type <= getConfig("log_print_level"):
		sys.stdout.write("[%s] %s: %s\n" % (logNames[log_type], module_name, log_message))
	pass # TODO: Write to log file regardless

_logNames = ["Error", "Warn", "Notice", "Info"]

class Log:
	Error	= 0
	Warn	= 1
	Notice	= 2
	Info	= 3
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
	Configuration
"""

config_options = {}

def getConfig(config_option):
	if config_options.has_key(config_option):
		return config_options[config_option]
	else:
		return 0

def _readConfig():
	"""
		Read the configuration
	"""
	try:
		conf_file = open("vend.conf")
	except:
		log(Log.Warn, "api-main", "Could not read config file (vend.conf), this may be bad.")

"""
	Main Object
"""

Tool = None

class Vending:
	"""
		Vending API super class
	"""
	def __init__(self):
		Tool = self
		_readConfig()

"""
	Transaction Classes
"""

class User:
	def __init__(self, uid):
		self.uid = uid
	def chargeMoney(self, amount):
		pass
