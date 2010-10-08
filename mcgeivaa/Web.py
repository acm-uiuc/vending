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

class Server:
    def __init__(self):
        self = HTTPServer(('localhost',6969), _GetHandler)
        isRunning = True

    def serve(server):
        while isRunning
            server.handle_request()

    def start(self):
        mythread = Thread(target = RunServer, args = (self,))
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
