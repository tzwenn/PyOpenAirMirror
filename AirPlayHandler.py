import BaseHTTPServer
import biplist
import re, hashlib
import time, base64, random

import config

class DigestAuthHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	realm = "AirPlay"

	def md5Join(self, *args):
		return hashlib.md5(":".join(args)).hexdigest()

	def requestAuth(self):
		now = str(int(time.time()))
		randStr = "".join(chr(int(256 * random.random())) for i in xrange(16))
		self.nonce =  base64.b64encode(("%s %s" % (now, randStr)))
		self.send_response(401)
		self.send_header("WWW-Authenticate",
				         'Digest realm="%s", nonce="%s"' % (self.realm, self.nonce))
		self.send_header("Content-Length", 0)
		self.end_headers()

	def checkAuth(self):
		if config.password is None:
			return True

		auth = dict(re.findall(r'(\b[^ ,=]+)="?([^",]+)"?',
				          self.headers.getheader("Authorization") or ""))
		try:
			if self.nonce != auth["nonce"]:
				raise Exception("No nonce created, or wrong one")	
			hash_a1 = self.md5Join(auth["username"], self.realm, config.password)
			hash_a2 = self.md5Join(self.command, auth["uri"])
			response = self.md5Join(hash_a1, self.nonce, hash_a2)
			if response != auth["response"]:
				raise Exception("Wrong password")
			return True
		except:
			self.requestAuth()
			return False

	def setForAllRequests(self):
		self.parse_request = parse_request_and_check

	def parse_request_and_check(self):
		if not BaseHTTPServer.BaseHTTPRequestHandler.parse_request(self):
			return False
		return self.checkAuth()

class AirPlayHandler(DigestAuthHandler):
	sys_version = ""

	def sendPList(self, content, binary=False):
		mime = "application/x-plist" if binary else "text/x-apple-plist+xml"
		self.sendContent(biplist.writePlistToString(content, binary), mime)

	def sendContent(self, content, contentType, X_Apple_ET=None):
		self.send_response(200)
		self.send_header("Content-Type", contentType)
		if X_Apple_ET is not None:
			self.send_header("X-Apple-ET", X_Apple_ET)
		self.send_header("Content-Length", len(content))
		self.end_headers()
		self.wfile.write(content)

	def readBody(self):
		length = int(self.headers.getheader("Content-Length"))
		return self.rfile.read(length)

	def readPlist(self):
		return biplist.readPlistFromString(self.readBody())

