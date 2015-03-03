#!/usr/bin/env python

import config
import common.register
import common.server
import mirror.service
import tunes.service

def main():
	tunes_port = 49152
	common.register.registerAirPlay()
	common.register.registerAirTunes(tunes_port)

	try:
		t = common.async(lambda: common.server.run(tunes_port, tunes.service.TunesService))
		common.server.run(7100, mirror.service.MirrorService)
	except KeyboardInterrupt:
		pass

if __name__ == "__main__":
	config.parseArguments()
	main()
