from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from McGeivaa import *
from CaffeineTemplate import caffeine_template



class _GetHandler(BaseHTTPRequestHandler):
	def do_GET(self):
			htmlfile = caffeine_template()
			log(Log.Info,"web", "Request from %s for page %s" % (self.client_address[0], self.path))
			self.send_response(200)
			self.send_header("Content-type","text/html")
			self.end_headers()
			self.wfile.write(htmlfile)
	def do_STOP(self):
		self.send_response(200)
		self.end_headers()
		self.server.serving = Falsei
	def log_message(self, format, *args):
		pass

isRunning = False

class _WebThread(Thread):
	def __init__(self, server):
		Thread.__init__(self)
		self.server = server
	def run(self):
		global isRunning
		while isRunning:
			self.server.server.handle_request()

class Server:
	def __init__(self):
		self.server = HTTPServer(('localhost',6969), _GetHandler)
		log(Log.Info,"web","Web server is ready.")
	def start(self):
		global isRunning
		isRunning = True
		mythread = _WebThread(self)
		mythread.start()
		log(Log.Notice,"web","Web server is running.")
