import itertools
import datetime

class FrameHandler(object):
	"""
	Base class of different handlers for a received mirroring frame.
	Subclasses can reimplement handleFrameData to add functionality.
	"""

	def __init__(self, streamInfo):
		self.streamInfo = streamInfo
		self.start()

	def __del__(self):
		self.finish()

	def handle(self, frame):
		try:
			width, height, ((yLineSkip, yData), (uLineSkip, uData), (vLineSkip, vData)) = frame
		except TypeError:
			return
		self.handleFrameData(width, height, yLineSkip, yData, uLineSkip, uData, vLineSkip, vData)

	def start(self):
		""" Called on initialization. Reimplement in subclass if needed """
		pass

	def finish(self):
		""" Called when the session was finished """
		pass

	def handleFrameData(self, width, height, yLineSkip, yData, uLineSkip, uData, vLineSkip, vData):
		""" What should I do with this frame. Please reimplement """
		pass

class YUVFileStorage(FrameHandler):
	"""
	Stores the received frames in a huge YUV420p file.
	The file name will be automatically generated from the current time
	and the connected client's device-id.

	Use yuv2mp4.sh to reencode as playable MP4-H.264 video (using ffmpeg).
	"""

	splitEveryNChars = lambda self, s, n: (s[i:i+n] for i in xrange(0, len(s), n))
	
	def start(self):
		filename = datetime.datetime.now().strftime("%y%m%d_%H%M%S_%%s.yuv") \
			% str(self.streamInfo.get('deviceID', 'Unknown client'))
		self.outfile = open(filename, "w")

	def finish(self):
		self.outfile.close()

	def handleFrameData(self, width, height, yLineSkip, yData, uLineSkip, uData, vLineSkip, vData):
		for line in self.splitEveryNChars(yData, yLineSkip):
			self.outfile.write(line[:width])
		
		for line in itertools.chain(self.splitEveryNChars(uData, uLineSkip), \
		                            self.splitEveryNChars(vData, vLineSkip)):
			self.outfile.write(line[:width / 2])
				
