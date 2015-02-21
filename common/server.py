import BaseHTTPServer

def run(port, handler):
	try:
		httpd = BaseHTTPServer.HTTPServer(('', port), handler)
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
