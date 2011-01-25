"""
	Database Interface
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
			log(Log.Notice,"db-auth", "Card id is not an integer.")
			return "Failed to read card."
		self.user_database.query("SELECT * FROM `%s` WHERE uin=%d" % (getConfig("db_mysql_user_table"), card_id))
		t_result = self.user_database.store_result()
		t_user = t_result.fetch_row(how=1)
		if len(t_user) < 1:
			log(Log.Notice,"db-auth", "User not found in database: %d" % card_id)
			return "You are not an ACM member."
		user_sql = t_user[0]
		user_dict = {}
		self.user_database.query("SELECT * FROM `%s` WHERE uid=%d" % (getConfig("db_mysql_user_table_alt"), user_sql['uid']))
		t_result = self.user_database.store_result()
		t_vending = t_result.fetch_row(how=1)
		if len(t_vending) < 1:
			log(Log.Warn,"db-auth", "User was not found in vending db, this is bad.")
			return "You are not in the vending database. Please contact a Vending admin."
		vending_sql = t_vending[0]
		user_dict = vending_sql
		for i, v in user_sql.iteritems():
			user_dict[i] = v
		Environment.user = VendingUser(user_sql['uid'],user_sql['uin'],user_dict)
		Environment.state = State.Authenticated
		Environment.tool.gui.updateUser()
		return None
	def getItems(self):
		"""
		Update and return the list of available items in each tray.
		"""
		Environment.trays = []
		self.vend_database.query("SELECT * FROM `%s`" % getConfig("db_mysql_vend_trays"))
		t_result = self.vend_database.store_result()
		for i in xrange(getConfig("tray_count")):
			tray = t_result.fetch_row(how=1)[0]
			self.vend_database.query("SELECT * FROM `%s` WHERE sid=%d" % (getConfig("db_mysql_vend_items"), int(tray['sid'])))
			s_result = self.vend_database.store_result()
			soda = s_result.fetch_row(how=1)[0]
			Environment.trays.append(VendingItem(soda['name'], i, tray['qty'], tray['price'], soda))
		return Environment.trays
	def purchaseItem(self, item):
		self.chargeUser(item.price, item.extra['sid'])
		u = Environment.user
		if u.isAdmin:
			return True
		self.user_database.query("UPDATE `%s` SET `calories`=%d, `caffeine`=%f, `spent`=%f, `sodas`=%d WHERE `uid`=%d" % \
				(getConfig("db_mysql_user_table_alt"), u.extra['calories'] + item.extra['calories'], u.extra['caffeine'] + item.extra['caffeine'], u.extra['spent'] + item.price, \
				u.extra['sodas'] + 1, u.uid))
		self.user_database.commit()
		self.vend_database.query("UPDATE `%s` SET `dispensed`=%d WHERE `sid`=%d" % (getConfig("db_mysql_vend_items"),item.extra['dispensed'], item.extra['sid']))
		self.vend_database.commit()
	def chargeUser(self, amount, item_id):
		"""
		Charge the current user some amount of money.
		"""
		if Environment.user.isAdmin:
			return True
		log(Log.Info,"db-charge", "uid: %d, amount: %.2f" % (int(Environment.user.uid), amount))
		self.user_database.query("INSERT INTO `%s` VALUES (NULL, NULL, %d, %d, %.2f)" % (getConfig("db_mysql_user_table_transactions"), int(Environment.user.uid), item_id, amount))
		self.user_database.query("UPDATE `%s` SET `balance`=`balance`-%.2f WHERE `uid`=%d" % (getConfig("db_mysql_user_table_alt"), amount, int(Environment.user.uid)))
		self.user_database.commit()
		return True
	def vend(self, tray):
		"""
		Update the databases' knowledge of the number of items in a tray.
		"""
		if Environment.user.isAdmin:
			return True
		self.vend_database.query("select * from `%s` where `tid`=%d" % (getConfig("db_mysql_vend_trays"),tray))
		dbtray = self.vend_database.store_result().fetch_row(how=1)[0]
		self.vend_database.query("update `%s` set `qty`=%d where `tid`=%d" % (getConfig("db_mysql_vend_trays"), dbtray['qty'] - 1, tray))
		self.vend_database.commit()
		self.getItems()
		return True

# Written by schober1 -- may be f***ing broken!
	def lastNPurchases(self, user, n):
		"""
		Retrieves the last n purchases for a user.
		"""
		try:
			num_purchases = int(n)
		except:
			log(Log.Notice,"db-auth", "n is not an integer.")
			return None
		self.user_database.query("SELECT * FROM `%s` WHERE `uid`=%d ORDER BY `tid` DESC LIMIT %d" % (getConfig("db_mysql_user_table_transactions"), user.uid, num_purchases))
		purchases = self.user_database.store_result().fetch_row(how=1,maxrows=num_purchases)
		return purchases
