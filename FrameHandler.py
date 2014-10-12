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

	def start(self):
		""" Called on initialization. Reimplement in subclass if needed """
		pass

	def handle(self, frame, timestamp):
		""" What should I do with this frame. Please reimplement """
		pass

	def finish(self):
		""" Called when the session was finished """
		pass

class YUVFileStorage(FrameHandler):
	"""
	Stores the received frames in a huge YUV420p file.
	The file name will be automatically generated from the current time
	and the connected client's device-id.

	Use yuv2mp4.sh to reencode as playable MP4-H.264 video (using ffmpeg).
	"""

	splitEveryNChars = lambda self, s, n: (s[i:i+n] for i in xrange(0, len(s), n))
	fileExtension = "yuv"
	
	def start(self):
		filename = datetime.datetime.now().strftime("%y%m%d_%H%M%S_%%s.%%s") \
			% (str(self.streamInfo.get('deviceID', 'Unknown client')), self.fileExtension)
		self.outfile = open(filename, "wb")

	def handle(self, frame, timestamp):
		for line in self.splitEveryNChars(frame.yData, frame.yLineSkip):
			self.outfile.write(line[:frame.width])
		
		for line in itertools.chain(self.splitEveryNChars(frame.uData, frame.uLineSkip), \
		                            self.splitEveryNChars(frame.vData, frame.vLineSkip)):
			self.outfile.write(line[:frame.width / 2])

	def finish(self):
		self.outfile.close()

import cPickle as pickle

class PickleStorage(YUVFileStorage):
	# How big can files get?!?!?! m-(

	fileExtension = "pkl"

	def handle(self, frame, timestamp):
		pickle.dump((frame.width, frame.height, frame.yData, frame.yLineSkip, \
		                    frame.uData, frame.uLineSkip, frame.vData, frame.vLineSkip, timestamp), self.outfile, -1)


