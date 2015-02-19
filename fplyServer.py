#!/usr/bin/env python
import sys
import SocketServer

import fply
from config import fplyServerPort as defaultPort

class FPLYService(SocketServer.BaseRequestHandler):

	def setup(self):
		self.fply = fply.FPLY()

	def handle(self):
		print "Connection from", self.client_address[0]
		data = self.request.recv(self.fply.phase1_in_len)
		self.request.send(self.fply.phase1(data))
		data = self.request.recv(self.fply.phase2_in_len)
		self.request.send(self.fply.phase2(data))
		data = self.request.recv(self.fply.decrypt_in_len)
		self.request.send(self.fply.decrypt(data))

class FPLYServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
	pass

if __name__ == "__main__":
	port = defaultPort if len(sys.argv) < 2 else int(sys.argv[1])
	server = FPLYServer(('', port), FPLYService)
	server.serve_forever()
