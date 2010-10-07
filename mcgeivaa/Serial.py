import serial, time, threading, datetime
from McGeivaa import *

class Serial:
    def __init__(self):
        attempts = 0
        devices = ["ttyUSB0", "ttyUSB1", "ttyS0", "ttyS1"]
        while attempts < 5:
            for device in devices:
                try:
                    self._serial = serial.Serial("/dev/%s" % device,getConfig("serial_baudrate"), getConfig("serial_line_timeout"))
                    log(Log.Info, "serial", "Using /dev/%s for serial communication." % device)
                    log(Log.Info, "serial", "Running at %d without a line timeout of %d." % (self._serial.baudrate, self._serial.timeout))
                    return
                except:
                    attempts += 1
        log(Log.Error, "serial", "Failed to initialize a serial device after 5 attempts, we're going nowhere.")
        fatalError("No serial device")
        self._handler = _SerialHandler(self)
    def read(self):
        try:
            start_time = datetime.datetime.now()
            data_in = _serial.read()
            end_time = datetime.datetime.now()
            read_time = end_time - start_time
            if len(data_in) < 1:
                if read_time.microseconds < 100:
                    sys.exit(2)
            return data_in
        except SystemExit:
            log(Log.Error, "serial", "Read blanck data way too fast - serial device is gone.")
            fatalError("Serial device went missing")
        except:
            fatalError("Error on serial read")

class _SerialHandler(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.isRunning = False
        self.parent = parent
    def start(self):
        self.isRunning = True
        threading.Thread.start(self)
    def run(self):
        while self.isRunning:
           
