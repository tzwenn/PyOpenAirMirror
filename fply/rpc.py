import config
import socket

import fply.cli

class FPLY(fply.cli.FPLY_repl):

	def __init__(self):
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.conn.connect((config.fplyServer, config.fplyServerPort))

	def __del__(self):
		self.conn.close()

	def send(self, data):
		self.conn.sendall(data)

	def read(self, length):
		return self.conn.recv(length)

def available():
	return config.fplyServer is not None
