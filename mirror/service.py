import socket

import config
import h264decode

import common.AirPlayHandler
import mirror.Packet
import mirror.Cryptor

class MirrorService(common.AirPlayHandler.FPLYHandler):
	protocol_version = "HTTP/1.1"
	decoder_cls = h264decode.Decoder

	def do_GET(self):
		if self.path == "/stream.xml" and self.checkAuth():
			self.sendCapabilities()

	def do_POST(self):
		common.AirPlayHandler.FPLYHandler.do_POST(self)
		if self.path == "/stream":
			self.receiveStream()

	def receiveStream(self):
		self.streamInfo = self.readPlist()
		if 'param1' in self.streamInfo and 'param2' in self.streamInfo:
			aesKey = self.fply.decrypt(self.streamInfo['param1'])
			aesIV = self.streamInfo['param2']
			self.cryptor = mirror.Cryptor.Cryptor(aesKey, aesIV)
		else:
			self.log_message("Client doesn't want to encrypt stream. Skipping AES")
			self.cryptor = mirror.Cryptor.EchoCryptor()

		self.frameSinks = []
		self.log_message("Get Stream info: %r", self.streamInfo)
		self.log_message("Switching to stream packet mode")
		self.handle_one_request = self.parseStreamPacket

	def closeConnection(self):
		self.log_message("Closing connection")
		self.close_connection = 1
		self.frameSinks = []

	def parseStreamPacket(self):
		try:
			packet = mirror.Packet.Packet(self.rfile)
		except IOError:
			return self.closeConnection() # TODO: Really?
		except EOFError:
			return self.closeConnection()
		except socket.timeout, e:
			self.log_error("Request timed out: %r", e)
			return self.closeConnection()
		self.handlePacket(packet)

	def handlePacket(self, packet):
		if packet.payloadType == mirror.Packet.TYPE_VIDEO:
			decryptedH264Packet = self.cryptor.decrypt(packet.data)
			frame = self.decoder.decodeFrame(decryptedH264Packet)
			if frame:
				for sink in self.frameSinks:
					sink.handle(frame, packet.timestamp)

		elif packet.payloadType == mirror.Packet.TYPE_CODECDATA:
			self.decoder = self.decoder_cls(packet.data)
			self.frameSinks = [cls(self.streamInfo, self.clientName) \
									for cls in config.selectedSinks]

	def sendCapabilities(self):
		self.log_message("Sending capabilities")
		self.clientName = self.headers.getheader('X-Apple-Client-Name')
		self.clientProtocolVersion = self.headers.getheader('X-Apple-ProtocolVersion')
		self.sendPList(config.default_capabilities)

