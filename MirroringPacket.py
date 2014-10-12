""" Based on the awesome unofficial AirPlay doc

	http://nto.github.io/AirPlay.html#screenmirroring-streampackets
"""

import struct

TYPE_VIDEO     = 0
TYPE_CODECDATA = 1
TYPE_HEARTBEAT = 2

class Packet(object):

	headerSize = 128
	headerFrmt = "<IHHQ"
	headerParseSize = struct.calcsize(headerFrmt)

	def __init__(self, fd):
		self.header = fd.read(self.headerSize)
		if len(self.header) == 0:
			raise EOFError("Socket delivered no more data for header")

		self.payloadSize, self.payloadType, self.thirdHdrField, self.timestamp = \
				struct.unpack(self.headerFrmt, self.header[:self.headerParseSize])
		self.data = fd.read(self.payloadSize)

		if len(self.data) < self.payloadSize:
			raise IOError("Packet was smaller than excpected")

	def __str__(self):
		return "%s.Packet(size=%d, type=%d, thirdHdrField=%d, timestamp=%d)" \
				% (__name__, self.payloadSize, self.payloadType, self.thirdHdrField, self.timestamp)

