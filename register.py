import select
import pybonjour
import config

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

def registerAirPlay(targetPort=7000):
	airPlayParams = {
		"deviceid": getHWAddress(),
		"features": "0xf7",
		"model": config.model,
		"srcvers": config.server_version
	}
	sdRef = pybonjour.DNSServiceRegister(name = config.service_name,
										 regtype = "_airplay._tcp",
										 port = targetPort,
										 txtRecord = buildTxtRecord(airPlayParams))
	try:
		while True:
			ready = select.select([sdRef], [], [])
			if sdRef in ready[0]:
				pybonjour.DNSServiceProcessResult(sdRef)
	finally:
		sdRef.close()

