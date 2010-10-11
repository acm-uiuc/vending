import serial, time, threading, datetime
from Vending import *

class Serial:
	"""
	Serial interface.
	"""
	def __init__(self):
		self._internal = Environment.tool
		attempts = 0
		devices = ["ttyUSB0", "ttyUSB1"] #, "ttyS0", "ttyS1"]
		while attempts < 5 * len(devices):
			for device in devices:
				try:
					log(Log.Info, "serial", "Trying /dev/%s" % device)
					self._serial = serial.Serial("/dev/%s" % device,getConfig("serial_baudrate"), timeout=getConfig("serial_line_timeout"))
					log(Log.Info, "serial", "Using /dev/%s for serial communication." % device)
					log(Log.Info, "serial", "Running at %d with a line timeout of %f." % (self._serial.baudrate, self._serial.timeout))
					self._handler = _SerialHandler(self)
					return
				except:
					attempts += 1
		log(Log.Error, "serial", "FATAL: Failed to initialize a serial device after 5 attempts, we're going nowhere.")
		fatalError("No serial device")
	def start(self):
		"""
		Start the serial handler.
		"""
		self._handler.start()
		log(Log.Info, "serial", "Device started, serial interface running.")
	def read(self):
		"""
		Read a command from the serial device.
		"""
		try:
			start_time = datetime.datetime.now()
			data_in = self._serial.read(255)
			end_time = datetime.datetime.now()
			read_time = end_time - start_time
			if (len(data_in) < 1) and (read_time.microseconds < 100):
				sys.exit(2)
			if (len(data_in) < 1):
				return None
			log(Log.Info, "serial", "Read %s from serial device." % data_in)
			return data_in
		except SystemExit:
			log(Log.Error, "serial", "FATAL: Read blank data way too fast - serial device is gone.")
			fatalError("Serial device went missing")
		except:
			log(Log.Error, "serial", "FATAL: Unknown error occured on serial read.")
			fatalError("Error on serial read")
	def write(self, data):
		"""
		Send a command to the serial device.
		"""
		try:
			bytesWritten = self._serial.write(data)
			log(Log.Info, "serial", "Successfully wrote %s to serial interface." % data.replace("\xa0","\\xa0"))
			log(Log.Verbose, "serial", "Wrote %s out to serial." % bytesWritten)
		except:
			log(Log.Error, "serial", "FATAL: Unknown error writing %s")
			fatalError("Error on serial write")
	def vend(self, tray):
		"""
		Request that the machine vend the specified tray.
		"""
		self.write("%s%d" % (getConfig("serial_command_vend"), tray))

class _SerialReset(threading.Thread):
	def __init__(self, parent):
		threading.Thread.__init__(self)
		self.parent = parent
	def run(self):
		while self.parent.isRunning:
			time.sleep(60)
			if Environment.state == State.Ready:
				log(Log.Notice,"serial","Sending reset.")
				self.parent.parent.write("\xa0")

class _SerialHandler(threading.Thread):
	"""
	Serial device handling thread.
	"""
	def __init__(self, parent):
		threading.Thread.__init__(self)
		self.isRunning = False
		self.parent = parent
	def start(self):
		self.isRunning = True
		self.reset = _SerialReset(self)
		self.reset.start()
		threading.Thread.start(self)
	def run(self):
		while self.isRunning:
			incoming = self.parent.read()
			if not incoming is None:
				self.parent._internal.handleSerialData(incoming)
