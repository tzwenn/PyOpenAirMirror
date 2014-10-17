#!/usr/bin/env python

import BaseHTTPServer
import biplist

def __fallbackAction__(request):
	request.send_error(404, "File not found")

class AirPlayHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def sendPList(self, content, binary=False):
		mime = "application/x-plist" if binary else "text/x-apple-plist+xml"
		self.sendContent(biplist.writePlistToString(content, binary), mime)

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

	def readPlist(self):
		return biplist.readPlistFromString(self.readBody())

def runServer(port, handler):
	httpd = BaseHTTPServer.HTTPServer(('', port), handler)
	httpd.serve_forever()

