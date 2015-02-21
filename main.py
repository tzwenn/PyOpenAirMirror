#!/usr/bin/env python

import config
import common.register
import common.server
import mirror.service

def main():
	register_thread = common.async(common.register.registerAirPlay)
	common.server.run(7100, mirror.service.MirrorService)

if __name__ == "__main__":
	config.parseArguments()
	main()
