import subprocess
import os

import fply.base

defaultExecutableName = fply.base.path("cli")

class FPLY_repl(fply.base.BaseFPLY):
	"""Calls fairplay functions by communicating with another process.
	   Subclasses reimplement send and read to directly write the passed
	   data to the communication line and read the expected answer length

	   The other side is required to keep track of the current state
	   it is in and flush the open streams.
	"""

	def send(self, data):
		""" Reimplement in subclass to send data """
		pass

	def read(self, length):
		""" Reimplement in subclass to read length bytes """
		pass

	def repl(self, data, out_len):
		self.send(data)
		return self.read(out_len)

	def phase1(self, data, stype=0):
		fply.base.BaseFPLY.phase1(self, data, stype)
		return self.repl(data, self.phase1_out_len)

	def phase2(self, data, stype=0):
		fply.base.BaseFPLY.phase2(self, data, stype)
		return self.repl(data, self.phase2_out_len)

	def decrypt(self, data):
		fply.base.BaseFPLY.decrypt(self, data)
		return self.repl(data, self.decrypt_out_len)

class FPLY(FPLY_repl):
	"""Communicates with a subprocess using pipes
	   (i.e. its stdin and stdout)"""

	def __init__(self, filename=defaultExecutableName):
		self.proc = subprocess.Popen(filename, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

	def __del__(self):
		self.proc.wait()

	def send(self, data):
		self.proc.stdin.write(data)
		self.proc.stdin.flush()

	def read(self, length):
		self.proc.stdout.flush()
		return self.proc.stdout.read(length)
