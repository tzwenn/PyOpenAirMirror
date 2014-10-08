#!/usr/bin/env python

import server
import fply
import plistlib

class MirrorHandler(server.AirPlayHandler):
	server_version = "AirTunes/150.33"
	sys_version = ""
	protocol_version = "HTTP/1.1"

	def do_GET(self):
		if self.path == "/stream.xml":
			print "Sending capabilities"
			self.sendCapabilities()
 
	def do_POST(self):
		if self.path == "/stream":
			self.receiveStream()
		elif self.path == "/fp-setup":
			self.fpSetup()

	def fpSetup(self):
		data = self.readBody()
		if len(data) == 0x10:
			answer = fply.phase1(data)
		else:
			answer = fply.phase2(data)
		print "Sending FPLY answer of %d bytes" % len(answer)
		self.sendContent(answer, "application/octet-stream", 32)

	def receiveStream(self):
		streamInfo = self.readBody()
		print "Receiving stream: ", streamInfo

	def sendCapabilities(self):
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
