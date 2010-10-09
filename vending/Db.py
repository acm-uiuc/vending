"""
	 McGeivaa Database Interface
"""

import MySQLdb
from Vending import *

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
		Environment.tool.gui.updateUser()
		return True
	def getItems(self):
		Environment.trays = []
		self.vend_database.query("SELECT * FROM `trays`")
		t_result = self.vend_database.store_result()
		for i in xrange(getConfig("tray_count")):
			tray = t_result.fetch_row(how=1)[0]
			self.vend_database.query("SELECT * FROM `sodas` WHERE sid=%d" % int(tray['sid']))
			s_result = self.vend_database.store_result()
			soda = s_result.fetch_row(how=1)[0]
			Environment.trays.append(VendingItem(soda['name'], i, tray['qty'], tray['price'], soda))
		return Environment.trays
	def chargeUser(self, amount):
		log(Log.Info,"db-charge", "uid: %d, amount: %.2f" % (int(Environment.user.uid), amount))
		self.user_database.query("INSERT INTO `vending_transactions` VALUES (NULL, NULL, %d, %.2f, -1)" % (int(Environment.user.uid), amount))
		self.user_database.query("UPDATE `vending` SET `balance`=%.2f WHERE `uid`=%d" % (Environment.user.extra['balance'] - amount, int(Environment.user.uid)))
		self.user_database.commit()
		return True
	def vend(self, tray):
		# update tray amounts.
		self.vend_database.query("select * from `trays` where `tid`=%d" % tray)
		dbtray = self.vend_database.store_result().fetch_row(how=1)[0]
		self.vend_database.query("update `trays` set `qty`=%d where `tid`=%d" % (dbtray['qty'] - 1, tray))
		self.vend_database.commit()
		self.getItems()
		return True

