#!/usr/bin/env python

import MirrorHandler
import register
import threading
import server

def main():
	register_thread = threading.Thread(target=register.registerAirPlay)
	register_thread.setDaemon(True)
	register_thread.start()

	server.runServer(7100, MirrorHandler.MirrorHandler)

if __name__ == "__main__":
	import config
	config.parseArguments()
	main()
