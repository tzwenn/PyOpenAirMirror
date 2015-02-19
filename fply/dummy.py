import fply.base

class FPLY(fply.base.BaseFPLY):

	def phase1(self, data, stype=0):
		res = "FPLY\x03\x01\x02"
		return res + '\x00' * (self.phase1_out_len - len(res))

	def phase2(self, data, stype=0):
		res = "FPLY\x03\x01\x04"
		return res + '\x00' * (self.phase2_out_len - len(res))

	def decrypt(self, data):
		return '\x00' * self.decrypt_out_len

