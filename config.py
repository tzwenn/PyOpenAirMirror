model = "OpenAirMirror0,1"

server_name = "AirTunes"
server_version = "150.33"
service_name = "OpenAirMirror"
sdl_window_caption = service_name

selectedSinks = []
password = None

default_capabilities = {
		"width": 1280,
		"height": 720,
		"overscanned": True,
		"version": server_version,
		"refreshRate": 1.0/60,
}

#####################################################################

import argparse
import FrameSink

args = None

def parseArguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("name", type=str, nargs='?',
			            help="the name under which the service gets announced",
						default=service_name)
	parser.add_argument("--sink", "-s", nargs='+',
						choices=FrameSink.availableSinks.keys(),
						default=["sdl"],
						help="What to do with received frames")
	parser.add_argument("--password", "-p",
						help="server's password (none if not provided)")

	global args
	args = parser.parse_args()
	applyArguments()

def applyArguments():
	global service_name
	global password
	global selectedSinks
	service_name = args.name
	password = args.password
	selectedSinks = [FrameSink.availableSinks[key] for key in args.sink]
	
	
