from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import mimetypes

from McGeivaa import *
from CaffeineTemplate import caffeine_template

from SocketServer import ThreadingMixIn

mimetypes.init()

class _GetHandler(BaseHTTPRequestHandler):
	def __init__(self, a, b, c):
		log(Log.Warn, "web-handler", "Received a request...")
		BaseHTTPRequestHandler.__init__(self, a, b, c)
	def parse_request(self):
		self.command = None  # set in case of error on the first line
		self.request_version = version = "HTTP/0.9" # Default
		self.close_connection = 1
		requestline = self.raw_requestline
		if requestline[-2:] == '\r\n':
			requestline = requestline[:-2]
		elif requestline[-1:] == '\n':
			requestline = requestline[:-1]
		self.requestline = requestline
		words = requestline.split()
		if len(words) < 3:
			self.do_term()
			return False
		if len(words) == 3:
			[command, path, version] = words
			if version[:5] != 'HTTP/':
				self.send_error(400, "Bad request version (%r)" % version)
				return False
			try:
				base_version_number = version.split('/', 1)[1]
				version_number = base_version_number.split(".")
				if len(version_number) != 2:
					raise ValueError
				version_number = int(version_number[0]), int(version_number[1])
			except (ValueError, IndexError):
				self.send_error(400, "Bad request version (%r)" % version)
				return False
			if version_number >= (1, 1) and self.protocol_version >= "HTTP/1.1":
				self.close_connection = 0
			if version_number >= (2, 0):
				self.send_error(505, "Invalid HTTP Version (%s)" % base_version_number)
				return False
		elif len(words) == 2:
			[command, path] = words
			self.close_connection = 1
			if command != 'GET':
				self.send_error(400, "Bad HTTP/0.9 request type (%r)" % command)
				return False
		elif not words:
			return False
		else:
			self.send_error(400, "Bad request syntax (%r)" % requestline)
			return False
		self.command, self.path, self.request_version = command, path, version
		self.headers = self.MessageClass(self.rfile, 0)
		conntype = self.headers.get('Connection', "")
		if conntype.lower() == 'close':
			self.close_connection = 1
		elif (conntype.lower() == 'keep-alive' and self.protocol_version >= "HTTP/1.1"):
			self.close_connection = 0
		return True
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
	def do_term(self):
		self.wfile.write("\033[1mACM Vending - Telnet Interface\033[0m\n")
		self.wfile.flush()
		command = ""
		exit = False
		while not exit:
			self.wfile.write("\033[33m>\033[0m ")
			command = self.rfile.readline().strip()
			if command == "quit":
				exit = True
		self.wfile.write("\033[1mThank you for using ACM Vending.\033[0m")
		self.wfile.flush()
	def do_STOP(self):
		self.send_response(200)
		self.end_headers()
		self.wfile.write("Shutting down...")
		self.server.serving = False
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

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	pass

class Server:
	def __init__(self):
		self.server = ThreadedHTTPServer((getConfig("web_server"),getConfig("web_port")), _GetHandler)
		log(Log.Info,"web","Web server is ready.")
	def start(self):
		global isRunning
		isRunning = True
		mythread = _WebThread(self)
		mythread.start()
		log(Log.Notice,"web","Web server is running.")
