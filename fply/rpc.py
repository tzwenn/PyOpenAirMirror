import config

conn = None

def rpc(command, data):
	conn.sendall("%s:%s" % (command, data))
	return conn.recv(1024)

if config.fplyServer is None:
	import sys
	sys.stderr.write("!! Cannot find binary fairplay module, fallback to dummy\n")
	sys.stderr.write("!! Most clients will refuse to connect\n")
else:
	import socket
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn.connect((config.fplyServer, config.fplyServerPort))
	phase1 = lambda data: rpc("phase1", data)
	phase2 = lambda data: rpc("phase2", data)
	decrypt = lambda data: rpc("decrypt", data)

