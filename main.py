#!/usr/bin/env python

import config
import MirrorHandler
import register
import threading
import sys

def main():
	serviceName = sys.argv[1] if len(sys.argv) > 1 else config.service_name
	register_thread = threading.Thread(target=register.registerAirPlay, args=[serviceName])
	register_thread.setDaemon(True)
	register_thread.start()

	MirrorHandler.runServer()

if __name__ == "__main__":
	main()
