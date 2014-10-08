#!/usr/bin/env python

import select
import pybonjour

def splitTxtRecord(s):
	d = {}
	while s:
		length = ord(s[0]) + 1
		line = s[1:length]
		s = s[length:]
		if "=" not in line:
			continue
		key, _dummy, val = line.partition("=")
		d[key] = val
	return d

def buildTxtRecord(dic):
   return "".join([chr(len(s)) + s for s in ("%s=%s" % e for e in dic.iteritems())])

def getHWAddress(interface="wlan0"):
	import uuid
	macAddr = hex(uuid.getnode())[2:]
	return ':'.join(a+b for a,b in zip(macAddr[::2], macAddr[1::2]))

def register_callback(sdRef, flags, errorCode, name, regtype, domain):
	if errorCode == pybonjour.kDNSServiceErr_NoError:
		print "Registered service:"
		print "  name	=", name
		print "  regtype =", regtype
		print "  domain  =", domain

def registerAirPlay(name, targetPort=7000, verbose=True):
	airPlayParams = {
		"deviceid": getHWAddress(),
		"features": "0xf7",
		"model": "OpenAirMirror0,1",
		"srcvers": "130.14"
	}
	sdRef = pybonjour.DNSServiceRegister(name = name, 
										 regtype = "_airplay._tcp",
										 port = targetPort,
										 txtRecord = buildTxtRecord(airPlayParams),
										 callBack = register_callback if verbose else (lambda *args: None))
	try:
		while True:
			ready = select.select([sdRef], [], [])
			if sdRef in ready[0]:
				pybonjour.DNSServiceProcessResult(sdRef)
	finally:
		sdRef.close()

if __name__ == "__main__":
	import sys
	try:
		registerAirPlay(sys.argv[1] if len(sys.argv) > 1 else 'OpenAirMirror')
	except KeyboardInterrupt:
		pass

