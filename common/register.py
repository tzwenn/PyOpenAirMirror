import config

import uuid
import atexit
import pybonjour

def buildTxtRecord(dic):
   return "".join([chr(len(s)) + s for s in
	   ("%s=%s" % (k, str(v)) for k, v in dic.iteritems())])

def getHWAddress():
	macAddr = hex(uuid.getnode())[2:].upper()
	return [a + b for a, b in zip(macAddr[::2], macAddr[1::2])]

def registerAirPlay(targetPort=7000):
	params = {
		"deviceid": ":".join(getHWAddress()),
		"features": "0x100029ff",
		"model": config.model,
		"rhd": config.rhd,
		"srcvers": config.server_version,
		"rmodel": config.rmodel,
		"pw": str(int(config.password is not None)),
		"vv": "1"
	}

	sdRef = pybonjour.DNSServiceRegister(
			name = config.service_name,
			regtype = "_airplay._tcp",
			port = targetPort,
			txtRecord = buildTxtRecord(params))
	atexit.register(sdRef.close)

def registerAirTunes(targetPort):
	params = {
		"txtvers": "1",
		"am": config.model,
		"ch": "2",
		"cn": "0,1,2,3",
		"da": "true",
		"et": "0,1,3",
		"md": "0,1,2",
		"pw": "false" if config.password is None else "true",
		"rhd": config.rhd,
		"rmodel": config.rmodel,
		"sf": "0x4",
		"sr": "44100",
		"ss": "16",
		"sv": "false",
		"tp": "UDP",
		"vn": "65537",
		"vs": config.server_version,
		"vv": "1"
	}

	sdRef = pybonjour.DNSServiceRegister(
			name = "%s@%s" % ("".join(getHWAddress()), config.service_name),
			regtype = "_raop._tcp",
			port = targetPort,
			txtRecord = buildTxtRecord(params))
	atexit.register(sdRef.close)

if __name__ == "__main__":
	import sys
	if len(sys.argv) > 1:
		config.service_name = sys.argv[1]
	registerAirPlay()

