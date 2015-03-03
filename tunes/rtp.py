import SocketServer

import common

class RTPService(SocketServer.BaseRequestHandler):
	pass

class RTPControl(SocketServer.BaseRequestHandler):
	pass

class RTPTiming(SocketServer.BaseRequestHandler):
	pass

class RTP(object):

	def __init__(self):
		self.servers = []
		self.threads = []

	def startServer(self, handler):
		return SocketServer.UDPServer(('', 0), handler)

	def start(self):
		self.server = self.startServer(RTPService)
		self.control = self.startServer(RTPControl)
		self.timing = self.startServer(RTPTiming)

		self.servers = (self.server, self.control, self.timing)
		self.threads = [common.async(s.serve_forever) for s in self.servers]

		return tuple(s.server_address[1] for s in self.servers)

	def __del__(self):
		[s.shutdown() for s in self.servers]
		[t.join() for t in self.threads]

