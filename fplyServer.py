#!/usr/bin/env python
import fply
import socket
import sys
from config import fplyServerPort as defaultPort

methods = {
	"phase1": fply.phase1,
	"phase2": fply.phase2,
	"decrypt": fply.decrypt
}

def handle(msg):
	command, _, data = msg.partition(':')
	return methods.get(command, lambda s: "Unknown")(data)

def start(port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', port))
	s.listen(1)
	print "Listening on %d" % port
	while True:
		conn, addr = s.accept()
		while True:
			msg = conn.recv(1024)
			if not msg:
				break
			conn.sendall(handle(msg))	
		conn.close()

if __name__ == "__main__":
	port = defaultPort if len(sys.argv) < 2 else int(sys.argv[1])
	start(port)
