#!/usr/bin/env python

import config
import MirrorHandler
import register
import threading
import server

def main():
	register_thread = threading.Thread(target=register.registerAirPlay, args=[config.service_name])
	register_thread.setDaemon(True)
	register_thread.start()

	server.runServer(7100, MirrorHandler)

if __name__ == "__main__":
	config.parseArguments()
	main()
