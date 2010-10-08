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
	pass

class Log:
	Error	= 0
	Info	= 1
	Warn	= 2
	Notice	= 3

def fatalError(message):
	"""
		Raise a fatal, internal error.
		Kill everything, log sufficiently, and inform the main class to restart.
	"""
	log(Log.Error, "api-main", "FATAL ERROR: %s -- Shutting down and restarting!" % message)
	# TODO: Shutdown, restart

config_options = {}

def getConfig(config_option):
	if config_options.has_key(config_option):
		return config_options[config_option]
	else:
		return 0

"""
	Main Object
"""

def Vending:
	"""
		Vending API super class
	"""
	def __init__(self):
