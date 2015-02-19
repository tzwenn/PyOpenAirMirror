class FPLY(object):

	def phase1(data, stype=0):
		res = "FPLY\x03\x01\x02"
		return res + '\x00' * (0x8e - len(res))

	def phase2(data, stype=0):
		res = "FPLY\x03\x01\x04"
		return res + '\x00' * (0x20 - len(res))

	def decrypt(data):
		return '\x00' * 0x10

