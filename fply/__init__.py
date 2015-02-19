import fply.dylib
import fply.dummy

if fply.dylib.available():
	FPLY = fply.dylib.FPLY
else:
	import sys
	sys.stderr.write("!! Cannot find binary fairplay module, fallback to dummy\n")
	sys.stderr.write("!! Most clients will refuse to connect\n")
	from fply.dummy import FPLY

