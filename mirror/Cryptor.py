from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class Cryptor(object):

	def __init__(self, key, iv):
		self.cipher = Cipher(
				algorithms.AES(key),
				modes.CTR(iv),
				backend=default_backend())
		self.cryptor = self.cipher.decryptor()

	def decrypt(self, data):
		return self.cryptor.update(data)

class EchoCryptor(object):

	def decrypt(self, data):
		return data

