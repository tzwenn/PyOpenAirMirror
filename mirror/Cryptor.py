from Crypto.Cipher import AES
import Crypto.Util.Counter

class Cryptor(AES.AESCipher):

	def __init__(self, key, iv):
		self.counter = Crypto.Util.Counter.new(128, initial_value=long(iv.encode("hex"), 16))
		AES.AESCipher.__init__(self, key, mode=AES.MODE_CTR, counter=self.counter)

class EchoCryptor(object):

	def decrypt(self, data):
		return data
