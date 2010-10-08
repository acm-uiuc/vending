from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import httplib

from McGeivaa import *


htmlfile = """<html><head><title>McGeivaa</title></head>
<body>
Welcome to the McGeivaa Web Interface!<br/>
It doesn't do anything right now, but it will eventually.
</body>
</html>"""

class _GetHandler(BaseHTTPRequestHandler):
	def do_GET(self):
			self.send_response(200)
			self.send_header("Content-type","text/html")
			self.end_headers()
			self.wfile.write(htmlfile)
			return
	def do_STOP(self):
		self.send_response(200)
		self.end_headers()
		self.server.serving = False

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
		global isRunning
		self.server = HTTPServer(('localhost',6969), _GetHandler)
		isRunning = True

	def start(self):
		mythread = _WebThread(self)
		mythread.start()


"""
if __name__ == '__main__':
	myserver = HTTPServer(('localhost',6969), GetHandler)
	print 'Running Server...'
	isRunning = True
	def RunServer(server):
		while isRunning:
			server.handle_request()
	mythread = Thread(target = RunServer, args = (myserver,))
	mythread.start()
	while True:
		command = raw_input("> ")
		if command == "stop" or command == "quit" or command == "q":
			isRunning = False
			mythread.join()
			break
"""
