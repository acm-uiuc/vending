from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import mimetypes

from McGeivaa import *
from CaffeineTemplate import caffeine_template

mimetypes.init()

class _GetHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		# Set default path to the main page
		path="caffeine.html"
		log(Log.Info,"web", "Request from %s for page %s" % (self.client_address[0], self.path))
		path = self.path[1:]
		if len(path) == 0:
			path = "main"
		if self.path.startswith("gui/"):
			if not self.client_address[0] == '127.0.0.1':
				self.send_response(403)
				return
		if not path.find("..") == -1:
			self.send_response(403)
			return
		if not path.find(".") == -1:
			try:
				fio = open("www/%s" % path,"r")
				htmlfile = fio.read()
				fio.close()
				self.send_response(200)
				self.send_header("Content-type", mimetypes.types_map[path[path.find("."):]])
				self.end_headers()
				log(Log.Info, "web", "Sent header %s" % mimetypes.types_map[path[path.find("."):]])
				self.wfile.write(htmlfile)
			except:
				fio = open("www/404_error.html","r")
				htmlfile = fio.read()
				fio.close()
				self.send_response(404)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				self.wfile.write(htmlfile)
		else:
			try:
				htmlfile = caffeine_template(path + ".html")
				self.send_response(200)
			except:
				fio = open("www/500_error.html","r")
				htmlfile = fio.read()
				fio.close()
				self.send_response(500)
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
		self.server = HTTPServer((getConfig("web_server"),getConfig("web_port")), _GetHandler)
		log(Log.Info,"web","Web server is ready.")
	def start(self):
		global isRunning
		isRunning = True
		mythread = _WebThread(self)
		mythread.start()
		log(Log.Notice,"web","Web server is running.")
