from Crypto.Cipher import AES

class Cryptor(object):

	def __init__(self, key, iv):
		self.aes = AES.new(key, mode=AES.MODE_CBC, IV=iv) # This resembles stuff from shairtunes
		#self.aes = AES.new(key, mode=AES.MODE_ECB) # I found this in airtunesd
		self.buf = ""

	def decrypt(self, data):
		self.buf += data
		blocksEnd = len(self.buf)
		blocksEnd -= blocksEnd % AES.block_size;
		result = self.aes.decrypt(self.buf[:blocksEnd])
		self.buf = self.buf[blocksEnd:]
		return data

class EchoCryptor(object):

	def decrypt(self, data):
		return data
