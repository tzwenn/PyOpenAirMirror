import fply.dylib
import fply.rpc

if fply.rpc.available():
	FPLY = fply.rpc.FPLY
elif fply.dylib.available():
	FPLY = fply.dylib.FPLY
else:
	import sys
	sys.stderr.write("!! Cannot find binary fairplay module, fallback to dummy\n")
	sys.stderr.write("!! Most clients will refuse to connect\n")
	from fply.dummy import FPLY

