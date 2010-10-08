from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import httplib

htmlfile = """
<html><head><title>McGeivaa</title></head>
<body>
Welcome to the McGeivaa Web Interface!<br/>
It doesn't do anything right now, but it will eventually.
</body>
</html>"""

class NewServer(HTTPServer):
    def serve_forever(self):
        self.serving=True
        while self.serving:
            self.handle_request()

class GetHandler(BaseHTTPRequestHandler):

    def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(htmlfile)
            return

    def do_STOP(self):
        self.send_response(200)
        self.end_headers()
        self.server.serving = False

if __name__ == '__main__':
    myserver = NewServer(('localhost',6969), GetHandler)
    print 'Running Server...'
    def RunServer(server):
        server.serve_forever()
    mythread = Thread(target = RunServer, args = (myserver,))
    mythread.start()
    raw_input('Press Enter to Kill\n')
    conn = httplib.HTTPConnection("localhost:6969")
    conn.request("STOP","/")
    print 'Stopping Server...'
    mythread.join()
    print 'Stopped Server.'

