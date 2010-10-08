"""
	 McGeivaa Database Interface
"""

import MySQLdb
from McGeivaa import *

class MySQLBackend:
	"""
		MySQL backend
		There are no other backends at the moment.
	"""
	def __init__(self):
		"""
			Instantiate a new MySQL backend, but do not connect yet.
		"""
		log(Log.Info, "db", "Using MySQL backend.")
		self.user_database	= None #: Server connection set to a database for user data
		self.vend_database	= None #: Server connection set to a database for vending data, like sodas
	def start(self):
		"""
			Connect to the MySQL databases.
		"""
		log(Log.Info, "db-mysql", "Connecting to MySQL 'user' server (%s)." % getConfig("db_mysql_user_server"))
		self.user_database	= MySQLdb.connect(getConfig("db_mysql_user_server"), getConfig("db_mysql_user_user"), getConfig("db_mysql_user_password"))
		log(Log.Info, "db-mysql", "Connecting to MySQL 'vend' server (%s)." % getConfig("db_mysql_vend_server"))
		self.vend_database	= MySQLdb.connect(getConfig("db_mysql_vend_server"), getConfig("db_mysql_vend_user"), getConfig("db_mysql_vend_password"))
		log(Log.Info, "db-mysql", "Attaching to databases - user: %s, vend: %s." % (getConfig("db_mysql_user_db"), getConfig("db_mysql_vend_db")))
		self.user_database.select(getConfig("db_mysql_user_db"))
		self.vend_database.select(getConfig("db_mysql_vend_db"))
		log(Log.Info. "db-mysql", "Disabling TRANSACTION mode for reads.")
		self.user_database.query("SET TRANSACTION ISOLATION LEAVE READ COMMITTED")
		self.vend_database.query("SET TRANSACTION ISOLATION LEAVE READ COMMITTED")
		log(Log.Info, "db-mysql", "MySQL is ready.")
	def authenticateUser(self, card_id):
		"""
			Get a user by their Card's ID number
		"""
		pass

