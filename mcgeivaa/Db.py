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
		self.user_database.select_db(getConfig("db_mysql_user_db"))
		self.vend_database.select_db(getConfig("db_mysql_vend_db"))
		log(Log.Info, "db-mysql", "Disabling TRANSACTION mode for reads.")
		self.user_database.query("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
		self.vend_database.query("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
		log(Log.Notice, "db-mysql", "MySQL is ready.")
	def authenticateUser(self, card_id):
		"""
			Get a user by their Card's ID number
		"""
		# Pull user from `user` database
		try:
			card_id = int(card_id)
		except:
			log(Log.Error,"db-auth", "Card id is not an integer.")
			return False
		self.user_database.query("SELECT * FROM `users` WHERE uin=%d" % card_id)
		t_result = self.user_database.store_result()
		t_user = t_result.fetch_row(how=1)
		if len(t_user) < 1:
			log(Log.Error,"db-auth", "User not found in database: %d" % card_id)
			return False
		user_sql = t_user[0]
		user_dict = {}
		self.user_database.query("SELECT * FROM `vending` WHERE uid=%d" % user_sql['uid'])
		t_result = self.user_database.store_result()
		t_vending = t_result.fetch_row(how=1)
		if len(t_vending) < 1:
			log(Log.Error,"db-auth", "User was not found in vending db, this is bad.")
			return False
		vending_sql = t_vending[0]
		user_dict = vending_sql
		for i, v in user_sql.iteritems():
			user_dict[i] = v
		Environment.user = VendingUser(user_sql['uid'],user_sql['uin'],user_dict)
		Environment.state = State.Authenticated
		return True


