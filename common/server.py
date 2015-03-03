import SocketServer
import BaseHTTPServer

class AirPlayServer(BaseHTTPServer.HTTPServer):
	pass

def run(port, handler):
	httpd = AirPlayServer(('', port), handler)
	httpd.serve_forever()

