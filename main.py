#!/usr/bin/env python

import config
import common.register
import common.server
import mirror.service
import tunes.service

def main():
	tunes_s, tunes_t = common.server.runAsync(tunes.service.TunesService)

	common.register.registerAirTunes(tunes_s.server_address[1])
	common.register.registerAirPlay()
	try:
		common.server.run(mirror.service.MirrorService, 7100)
	except KeyboardInterrupt:
		pass

if __name__ == "__main__":
	config.parseArguments()
	main()
