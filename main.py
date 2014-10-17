#!/usr/bin/env python

import config
import MirrorHandler
import register
import threading

def main():
	register_thread = threading.Thread(target=register.registerAirPlay, args=[config.service_name])
	register_thread.setDaemon(True)
	register_thread.start()

	MirrorHandler.runServer()

if __name__ == "__main__":
	config.parseArguments()
	main()
