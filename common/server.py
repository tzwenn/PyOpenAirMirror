import SocketServer
import BaseHTTPServer

import common

class AirPlayServer(BaseHTTPServer.HTTPServer):
	pass

def run(handler, port=0):
	httpd = AirPlayServer(('', port), handler)
	httpd.serve_forever()

def runAsync(handler, port=0):
	httpd = AirPlayServer(('', port), handler)
	return httpd, common.async(httpd.serve_forever)

