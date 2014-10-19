import BaseHTTPServer

def runServer(port, handler):
	try:
		httpd = BaseHTTPServer.HTTPServer(('', port), handler)
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
