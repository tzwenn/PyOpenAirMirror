#!/usr/bin/env python

import biplist
import socket
import itertools
import datetime

import fply
import h264decode
import server
import Cryptor
import MirroringPackets

splitEveryNChars = lambda s, n: (s[i:i+n] for i in xrange(0, len(s), n))

class MirrorHandler(server.AirPlayHandler):
	server_version = "AirTunes/150.33"
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

		self.decoder = None
		self.log_message("Get Stream info: %r", self.streamInfo)
		self.log_message("Switching to stream packet mode")
		self.handle_one_request = self.parseStreamPacket
		
		filename = datetime.datetime.now().strftime("%y%m%d_%H%M%S_%%s.yuv") \
				% str(self.streamInfo.get('deviceID', 'Unknown client'))
		self.outfile = open(filename, "w")


	def closeConnection(self):
		self.log_message("Closing connection")
		self.close_connection = 1
		self.outfile.close()

	def parseStreamPacket(self):
		try:
			packet = MirroringPackets.readNext(self.rfile)
			if packet is None:
				return self.closeConnection()

			if isinstance(packet, MirroringPackets.CodecData):
				self.decoder = h264decode.Decoder(packet.data)

			if isinstance(packet, MirroringPackets.Video):
				decrypted = self.cryptor.decrypt(packet.bitstream)
				if decrypted:
					self.decodeAndDisplayFrame(decrypted)

		except socket.timeout, e:
			self.log_error("Request timed out: %r", e)
			self.closeConnection()
	
	def decodeAndDisplayFrame(self, h264Packet):
		if self.decoder is None:
			return

		frame = self.decoder.decodeFrame(h264Packet)
		try:
			width, height, ((yLineSkip, yData), (uLineSkip, uData), (vLineSkip, vData)) = frame
		except TypeError:
			return

		for line in splitEveryNChars(yData, yLineSkip):
			self.outfile.write(line[:width])
		
		for line in itertools.chain(splitEveryNChars(uData, uLineSkip), \
		                            splitEveryNChars(vData, vLineSkip)):
			self.outfile.write(line[:width / 2])

	def sendCapabilities(self):
		self.log_message("Sending capabilities")
		self.sendPList("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
 <dict>
  <key>height</key>
  <integer>720</integer>
  <key>overscanned</key>
  <true/>
  <key>refreshRate</key>
  <real>0.016666666666666666</real>
  <key>version</key>
  <string>130.14</string>
  <key>width</key>
  <integer>1280</integer>
 </dict>
</plist>""")

if __name__ == "__main__":
	server.main(7100, MirrorHandler)
