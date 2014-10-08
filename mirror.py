#!/usr/bin/env python

import server
import fply
import biplist
import socket
from Crypto.Cipher import AES

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
		aesKey = fply.decrypt(self.streamInfo['param1'])
		aesIV = self.streamInfo['param2']
		self.cryptor = AES.new(aesKey, mode=AES.MODE_CBC, IV=aesIV)

		self.log_message("Get Stream info: %r", self.streamInfo)
		self.log_message("Switching to stream packet mode")
		self.handle_one_request = self.parseStreamPacket

	def parseStreamPacket(self):
		try:
			header = self.rfile.read(128)
			print "Read header: ", repr(header)
			# Todo: Get payload size and parse
		except socket.timeout, e:
			self.log_error("Request timed out: %r", e)
			self.close_connection = 1
			return

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
