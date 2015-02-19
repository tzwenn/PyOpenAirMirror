import subprocess

class FPLY(object):
	"""Calls fairplay functions using cli"""

	def __init__(self, filename="fply/cli"):
		self.proc = subprocess.Popen(filename, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

	def __del__(self):
		self.proc.wait()

	def phase1(self, data, stype=0):
		assert len(data) == 16
		self.proc.stdin.write(data)
		self.proc.stdout.flush()
		return self.proc.stdout.read(0x8e)

	def phase2(self, data, stype=0):
		assert len(data) == 164
		self.proc.stdin.write(data)
		self.proc.stdout.flush()
		return self.proc.stdout.read(0x20)

	def decrypt(self, data):
		self.proc.stdin.write(data)
		self.proc.stdin.close()
		self.proc.stdout.flush()
		return self.proc.stdout.read(0x10)



