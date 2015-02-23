#!/usr/bin/env python

import config
import common.register
import common.server
import mirror.service

def main():
	common.register.registerAirPlay()
	common.register.registerAirTunes(49153)

	common.server.run(7100, mirror.service.MirrorService)

if __name__ == "__main__":
	config.parseArguments()
	main()
