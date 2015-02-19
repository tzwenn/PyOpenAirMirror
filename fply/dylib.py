import ctypes

class FPLY(object):
	"""Calls fairplay functions directly from a dylib"""

	def __init__(self, filename="fply/libfply.dylib"):
		self.lib = ctypes.cdll.LoadLibrary(filename)
		self.lib.init_fply.restype = ctypes.c_void_p
		self.lib.phase1.restype = ctypes.POINTER(ctypes.c_char * 0x8e)
		self.lib.phase2.restype = ctypes.POINTER(ctypes.c_char * 0x20)
		self.lib.decrypt.restype = ctypes.POINTER(ctypes.c_char * 0x10)

		self.handle = ctypes.c_void_p(self.lib.init_fply(None))

	def __del__(self):
		self.lib.uninit_fply(self.handle)

	def _cbuf(self, data):
		return ctypes.create_string_buffer(data, len(data))

	def _join(self, char_array):
		return "".join(char_array.contents)

	def phase1(self, data, stype=0):
		assert len(data) == 16
		return self._join(self.lib.phase1(self.handle, self._cbuf(data), len(data), stype))

	def phase2(self, data, stype=0):
		assert len(data) == 164
		return self._join(self.lib.phase2(self.handle, self._cbuf(data), len(data), stype))

	def decrypt(self, data):
		buf = ctypes.create_string_buffer(data, len(data))
		return self._join(self.lib.decrypt(self.handle, self._cbuf(data), len(data)))

