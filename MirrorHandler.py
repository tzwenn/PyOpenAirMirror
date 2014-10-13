#!/usr/bin/env python

import biplist
import socket
import sys

try:
	import fply
except ImportError:
	sys.stderr.write("!! Cannot find binary fairplay module, fallback to dummy\n")
	sys.stderr.write("!! Most clients will refuse to connect\n")
	import dummyFPLY as fply

import h264decode
import register
import server
import Cryptor
import MirroringPacket
import FrameHandler

import config

SelectedHandlers = (FrameHandler.SDLRenderer)

class MirrorHandler(server.AirPlayHandler):
	server_version = config.server_version
	sys_version = ""
	protocol_version = "HTTP/1.1"

	def do_GET(self):
		if self.path == "/stream.xml":
			self.sendCapabilities()
 
	def do_POST(self):
		if self.path == "/fp-setup":
			self.fpSetup()
		elif self.path == "/stream":
			self.receiveStream()

	def fpSetup(self):
		data = self.readBody()
		if len(data) == 0x10:
			answer = fply.phase1(data)
		else:
			answer = fply.phase2(data)
		self.log_message("Sending FPLY answer of %d bytes" % len(answer))
		self.sendContent(answer, "application/octet-stream", 32)

	def receiveStream(self):
		self.streamInfo = biplist.readPlistFromString(self.readBody())
		if 'param1' in self.streamInfo and 'param2' in self.streamInfo:
			aesKey = fply.decrypt(self.streamInfo['param1'])
			aesIV = self.streamInfo['param2']
			self.cryptor = Cryptor.Cryptor(aesKey, aesIV)
		else:
			self.log_message("Client doesn't want to encrypt stream. Skipping AES")
			self.cryptor = Cryptor.EchoCryptor()

		self.frameHandlers = []
		self.log_message("Get Stream info: %r", self.streamInfo)
		self.log_message("Switching to stream packet mode")
		self.handle_one_request = self.parseStreamPacket

	def closeConnection(self):
		self.log_message("Closing connection")
		self.close_connection = 1
		self.frameHandlers = []

	def parseStreamPacket(self):
		try:
			packet = MirroringPacket.Packet(self.rfile)
		except IOError:
			return self.closeConnection() # TODO: Really?
		except EOFError:
			return self.closeConnection()
		except socket.timeout, e:
			self.log_error("Request timed out: %r", e)
			return self.closeConnection()
		self.handlePacket(packet)

	def handlePacket(self, packet):
		if packet.payloadType == MirroringPacket.TYPE_VIDEO:
			decryptedH264Packet = self.cryptor.decrypt(packet.data)
			frame = self.decoder.decodeFrame(decryptedH264Packet)
			if frame:
				for handler in self.frameHandlers:
					handler.handle(frame, packet.timestamp)

		elif packet.payloadType == MirroringPacket.TYPE_CODECDATA:
			self.decoder = h264decode.Decoder(packet.data)
			self.frameHandlers = [cls(self.streamInfo) for cls in SelectedHandlers]

	def sendCapabilities(self):
		self.log_message("Sending capabilities")
		self.sendPList(config.default_capabilities)

def runServer():
	try:
		server.runServer(7100, MirrorHandler)
	except KeyboardInterrupt:
		pass

if __name__ == "__main__":
	runServer()
