import config
import common.AirPlayHandler
import tunes.rtp

class TunesService(common.AirPlayHandler.FPLYHandler):
	protocol_version = "RTSP/1.0"

	def setup(self):
		self.params = {"volume": "0"}
		self.options = [m.split("_")[1] for m in dir(self) if m.startswith("do_")]
		common.AirPlayHandler.FPLYHandler.setup(self)

	def parse_request(self):
		self.raw_requestline = self.raw_requestline.replace(self.protocol_version, "HTTP/1.1")
		return common.AirPlayHandler.AirPlayHandler.parse_request(self)

	def sendAnswerHeaders(self, headers=None):
		self.send_response(200)
		for k, v in (headers or {}).iteritems():
			self.send_header(k, str(v))

		self.send_header("Audio-Jack-Status", "connected; type=analog")
		self.send_header("CSeq", self.headers.getheader("CSeq"))
		self.end_headers()

	def sendParams(self, content):
		self.sendAnswerHeaders({
			"Content-Type": "text/parameters",
			"Content-Length": len(content)})
		self.wfile.write(content)

	def nonEmptyStrs(self, strs):
		return filter(bool, (s.strip() for s in strs))

	def do_OPTIONS(self):
		self.sendAnswerHeaders({"Public": ", ".join(self.options)})

	def do_ANNOUNCE(self):
		self.announced = self.readSDP()
		self.rtp = tunes.rtp.RTP()
		self.sendAnswerHeaders()

	def do_SETUP(self):
		self.transport = self.parseToDict(self.headers.getheader("Transport").split(";"))
		ports = self.rtp.start()

		self.sendAnswerHeaders({
			"Session": 1,
			"Transport": "RTP/AVP/UDP;unicast;mode=record;events;server_port=%d;control_port=%d;timing_port=%d" % ports
			})

	def do_RECORD(self):
		# self.rtpInfo = self.parseToDict(self.headers.getheader("RTP-Info").split(";"))
		self.sendAnswerHeaders()

	def do_GET_PARAMETER(self):
		req = self.nonEmptyStrs(self.readBody().split())
		answer = "\r\n".join("%s: %s" % it for it in self.params.iteritems() if it[0] in req)
		self.sendParams(answer)

	def do_SET_PARAMETER(self):
		data = self.nonEmptyStrs(self.readBody().split("\n"))
		validParams = []
		for k, v in self.parseToDict(data, ":").iteritems():
			if k in self.params:
				self.params[k] = v
				validParams.append(k)

		self.sendParams("\r\n".join(validParams))

	def do_FLUSH(self):
		self.sendAnswerHeaders()

	def do_TEARDOWN(self):
		# FIXME: Read session ID and close it
		self.rtp = None
		self.sendAnswerHeaders()

