import subprocess
import os

import fply.base

defaultExectuableName = fply.base.path("cli")

class FPLY(fply.base.BaseFPLY):
	"""Calls fairplay functions by communicating with another
	   process via pipes.
	   Directly writes the passed bytes onto the subprocess' stdin
	   and reads the expected answer length from its stdout.

	   The process is required to keep track of the current state
	   it is in, and flush the open streams.
	"""

	def __init__(self, filename=defaultExecutableName):
		self.proc = subprocess.Popen(filename, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

	def __del__(self):
		self.proc.wait()

	def phase1(self, data, stype=0):
		fply.base.BaseFPLY.phase1(self, data, stype)
		self.proc.stdin.write(data)
		self.proc.stdout.flush()
		return self.proc.stdout.read(self.phase1_out_len)

	def phase2(self, data, stype=0):
		fply.base.BaseFPLY.phase2(self, data, stype)
		self.proc.stdin.write(data)
		self.proc.stdout.flush()
		return self.proc.stdout.read(self.phase2_out_len)

	def decrypt(self, data):
		fply.base.BaseFPLY.decrypt(self, data)
		self.proc.stdin.write(data)
		self.proc.stdout.flush()
		return self.proc.stdout.read(self.decrypt_out_len)


