import BaseHTTPServer

def runServer(port, handler):
	httpd = BaseHTTPServer.HTTPServer(('', port), handler)
	httpd.serve_forever()
