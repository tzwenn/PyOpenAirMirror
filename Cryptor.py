from Crypto.Cipher import AES

class Cryptor(object):

	def __init__(self, key, iv):
		#self.aes = AES.new(key, mode=AES.MODE_CBC, IV=iv) # This resembles stuff from shairtunes
		self.aes = AES.new(key, mode=AES.MODE_ECB, IV=iv) # I found this in airtunesd
		self.inbuf = ""
		self.outbuf = ""
		self.lastLen = 0

	def decrypt(self, data):
		self.inbuf += data
		blocksEnd = len(self.inbuf)
		blocksEnd -= blocksEnd % AES.block_size
		self.outbuf += self.aes.decrypt(self.inbuf[:blocksEnd])
		self.inbuf = self.inbuf[blocksEnd:]
		
		res = self.outbuf[:self.lastLen]
		self.outbuf = self.outbuf[self.lastLen:]
		
		self.lastLen = len(data)
		return res
	

class EchoCryptor(object):

	def decrypt(self, data):
		return data
