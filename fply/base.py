import os

class BaseFPLY(object):

	phase1_in_len   = 16
	phase2_in_len   = 164
	decrypt_in_len  = 72

	phase1_out_len  = 0x8e
	phase2_out_len  = 0x20
	decrypt_out_len = 0x10

	def phase1(self, data, stype=0):
		assert len(data) == self.phase1_in_len		

	def phase2(self, data, stype=0):
		assert len(data) == self.phase2_in_len

	def decrypt(self, data):
		pass

def path(name):
	return os.path.join(os.path.dirname(__file__), name)
