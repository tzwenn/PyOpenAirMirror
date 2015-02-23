import SocketServer
import BaseHTTPServer

class AirPlayServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
	pass

def run(port, handler):
	try:
		httpd = AirPlayServer(('', port), handler)
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
