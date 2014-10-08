#!/usr/bin/env python

import BaseHTTPServer

def __fallbackAction__(request):
	request.send_error(404, "File not found")

class AirPlayHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def sendPList(self, content):
		self.sendContent(content, "text/x-apple-plist+xml")

	def sendContent(self, content, contentType, X_Apple_ET=None):
		self.send_response(200)
		self.send_header("Content-Type", contentType)
		if X_Apple_ET is not None:
			self.send_header("X-Apple-ET", X_Apple_ET)
		self.send_header("Content-Length", len(content))
		self.end_headers()
		self.wfile.write(content)

	def readBody(self):
		length = int(self.headers['Content-Length'])
		return self.rfile.read(length)

def runServer(port, handler):
	httpd = BaseHTTPServer.HTTPServer(('', port), handler)
	httpd.serve_forever()

def main(defaultPort=7000, handler=AirPlayHandler):
	import sys
	try:
		runServer(int(sys.argv[1]) if len(sys.argv) > 1 else defaultPort, handler)
	except KeyboardInterrupt:
		pass

if __name__ == "__main__":
	main()
