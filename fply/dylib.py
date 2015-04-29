import ctypes
import fply.base

defaultLibName = fply.base.path("fply.dylib")

class FPLY(fply.base.BaseFPLY):
	"""Calls fairplay functions directly from a dylib"""

	def __init__(self, filename=defaultLibName):
		self.lib = ctypes.cdll.LoadLibrary(filename)
		self.lib.init_fply.restype = ctypes.c_void_p
		self._setCharArrayResT(self.lib.phase1, self.phase1_out_len)
		self._setCharArrayResT(self.lib.phase2, self.phase2_out_len)
		self._setCharArrayResT(self.lib.decrypt, self.decrypt_out_len)

		self.handle = ctypes.c_void_p(self.lib.init_fply(None))

	def __del__(self):
		self.lib.uninit_fply(self.handle)

	def _cbuf(self, data):
		return ctypes.create_string_buffer(data, len(data))

	def _join(self, char_array):
		return "".join(char_array.contents)

	def _setCharArrayResT(self, funcObj, nbytes):
		funcObj.restype = ctypes.POINTER(ctypes.c_char * nbytes)

	def phase1(self, data, stype=0):
		fply.base.BaseFPLY.phase1(self, data, stype)
		return self._join(self.lib.phase1(self.handle, self._cbuf(data), len(data), stype))

	def phase2(self, data, stype=0):
		fply.base.BaseFPLY.phase2(self, data, stype)
		return self._join(self.lib.phase2(self.handle, self._cbuf(data), len(data), stype))

	def decrypt(self, data):
		fply.base.BaseFPLY.decrypt(self, data)
		return self._join(self.lib.decrypt(self.handle, self._cbuf(data), len(data)))

def available(filename=defaultLibName):
	import platform, sys, os, hashlib
	if not (platform.system() == 'Darwin' and platform.machine() == 'x86_64'):
		return False

	if not os.path.exists(filename):
		answer = raw_input("\033[33mBinary fply library missing.\033[m\nShall I try to download it [Y/n]? ")
		if answer.lower() in ["", "y", "yes"]:
			os.system(fply.base.path("get_libfply.sh") + " " + filename)
		else:
			return False

	return True
