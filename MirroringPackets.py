""" Based on the awesome unofficial AirPlay doc

	http://nto.github.io/AirPlay.html#screenmirroring-streampackets
"""

import struct

TYPE_VIDEO     = 0
TYPE_CODECDATA = 1
TYPE_HEARTBEAT = 2

class Header(object):

	nBytes = 128
	infoFrmt = "<IHHQ"
	infoSize = struct.calcsize(infoFrmt)

	def __init__(self, rawdata):
		#self.data = rawdata[self.infoSize:]
		self.payloadSize, self.payloadType, self.third, self.timestamp = \
				struct.unpack(self.infoFrmt, rawdata[:self.infoSize])

	def __str__(self):
		return "MirroringPackets.Header(size=%d, type=%d, third=%d, timestamp=%d)" \
				% (self.payloadSize, self.payloadType, self.third, self.timestamp)

class Packet(object):

	def __init__(self, rawdata, header):
		self.header = header

	def __str__(self):
		return "<%s.%s packet of %d bytes>" % (__name__, self.__class__.__name__, self.header.payloadSize)

class Video(Packet):

	def __init__(self, rawdata, header):
		super(Video, self).__init__(rawdata, header)
		self.bitstream = rawdata

class CodecData(Packet):
	""" H.264 extra data in avcC (ISO/IEC 14496:15) format:
		http://www.iso.org/iso/iso_catalogue/catalogue_tc/catalogue_detail.htm?csnumber=55980 
	Send on start/stop and if video properties changed
	"""

	codecFmt = "<BBBBBBH16sBH4s"
	codecSize = struct.calcsize(codecFmt)

	def __init__(self, rawdata, header):
		super(CodecData, self).__init__(rawdata, header)
		self.version, self.profile, self.compatibility, self.level, \
				pack1, pack2, self.SPSLength, self.sequenceParamSet, \
				self.PPSNum, self.PPSLength, self.pictureParamSet = \
							struct.unpack(self.codecFmt, rawdata[:self.codecSize])
		self.reservedBits1 = pack1 >> 2
		self.NALunits = pack1 & 0x3
		self.reservedBits2 = pack2 >> 5
		self.SPSNum = pack2 & 0x1f

		# TODO: In Portrait orientation I received 32 bytes
		# Check what changed and put note in doc
		self.portraitMode = len(rawdata) == 32

class HeartBeat(Packet):
	""" Usually no payload """

	def __init__(self, rawdata, header):
		super(HeartBeat, self).__init__(rawdata, header)

############################################################

_classByType = {
	TYPE_VIDEO: Video,
	TYPE_CODECDATA: CodecData,
	TYPE_HEARTBEAT: HeartBeat
}

def readNext(fd):
	header = Header(fd.read(Header.nBytes))
	cls = _classByType.get(header.payloadType, Packet)
	return cls(fd.read(header.payloadSize), header)

