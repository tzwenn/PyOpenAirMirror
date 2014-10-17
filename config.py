import argparse

model = "OpenAirMirror0,1"

server_name = "AirTunes"
server_version = "150.33"
service_name = "OpenAirMirror"
sdl_window_caption = service_name

selectedSinks = []

default_capabilities = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
 <dict>
  <key>height</key>
  <integer>720</integer>
  <key>overscanned</key>
  <true/>
  <key>refreshRate</key>
  <real>0.016666666666666666</real>
  <key>version</key>
  <string>130.14</string>
  <key>width</key>
  <integer>1280</integer>
 </dict>
</plist>"""

#####################################################################

import FrameSink

args = None

def parseArguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("name", type=str, nargs='?',
			            help="the name under which the service gets announced",
						default=service_name)
	parser.add_argument("--sink", nargs='+',
						choices=FrameSink.availableSinks.keys(),
						default=["sdl"],
						help="What to do with received frames")

	global args
	args = parser.parse_args()
	applyArguments()

def applyArguments():
	global service_name
	global selectedSinks
	service_name = args.name
	selectedSinks = [FrameSink.availableSinks[key] for key in args.sink]
	
	
