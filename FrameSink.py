import config
import datetime
import cPickle as pickle
import pygame

class FrameSink(object):
	"""
	Base class of different sinks for a received mirroring frame.
	Subclasses can reimplement handle to add functionality.
	"""

	"""The shortcut to select this subclass in the command line arguments"""
	cmdLineKey = None

	def __init__(self, streamInfo=None, clientName=None):
		self.streamInfo = streamInfo if streamInfo is not None else {}
		self.clientName = clientName if clientName is not None else str(self.streamInfo.get('deviceID', 'UnknownClient'))
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

class YUVFileStorage(FrameSink):
	"""
	Stores the received frames in a huge YUV420p file.
	The file name will be automatically generated from the current time
	and the connected client's device-id.

	Use yuv2mp4.sh to reencode as playable MP4-H.264 video (using ffmpeg).
	"""

	fileExtension = "yuv"
	cmdLineKey = "yuv"

	def start(self):
		filename = datetime.datetime.now().strftime("%y%m%d_%H%M%S_%%s.%%s") \
			% (self.clientName, self.fileExtension)
		self.outfile = open(filename, "wb")

	def handle(self, frame, timestamp):
		self.outfile.write(frame.y)
		self.outfile.write(frame.u)
		self.outfile.write(frame.v)

	def finish(self):
		self.outfile.close()

class PickleStorage(YUVFileStorage):
	# How big can files get?!?!?! m-(

	fileExtension = "pkl"
	cmdLineKey = "pickle"

	def handle(self, frame, timestamp):
		data = (frame.width, frame.height, frame.y, frame.u, frame.v, timestamp)
		pickle.dump(data, self.outfile, -1)

	@classmethod
	def framesInFile(cls, filename):
		import h264decode
		infile = open(filename, "rb")
		while True:
			frame = h264decode.YUVFrame()
			try:
				frame.width, frame.height, frame.y, frame.u, frame.v, \
					timestamp = pickle.load(infile)
			except EOFError:
				return

			yield frame, timestamp

class SDLRenderer(FrameSink):

	cmdLineKey = "sdl"

	def start(self):
		pygame.init()
		pygame.display.set_caption("%s: %s" % (config.sdl_window_caption, self.clientName))
		self.clock = pygame.time.Clock()
		self.window = None

	def handle(self, frame, timestamp):
		if self.window is None:
			self.setupWindow(frame)

		# No idea why I need to keep that, but otherwise overlay.display crashes
		dummyBufBecauseItSucks = "%s%s%s" % (frame.y, frame.u, frame.v)
		self.overlay.display((frame.y, frame.u, frame.v))
		dummyBufBecauseItSucks = ""
		pygame.event.get()
		#self.clock.tick(10)

	def finish(self):
		pygame.display.quit()

	def setupWindow(self, frame):
		self.window = pygame.display.set_mode((frame.width, frame.height))
		self.overlay = pygame.Overlay(pygame.YV12_OVERLAY, (frame.width, frame.height))

import sdl2, ctypes

class SDL2Renderer(FrameSink):

	cmdLineKey = "sdl2"

	def start(self):
		sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
		self.window = None

	def handle(self, frame, timestamp):
		if self.window is None:
			self.setupWindow(frame.width, frame.height)

		sdl2.SDL_UpdateTexture(self.texture, None, "%s%s%s" % (frame.y, frame.v, frame.u), frame.width) 
		sdl2.render.SDL_RenderClear(self.renderer)
		sdl2.render.SDL_RenderCopy(self.renderer, self.texture, None, None)
		sdl2.render.SDL_RenderPresent(self.renderer)
		sdl2.SDL_PollEvent(None)

	def finish(self):
		if self.window:
			sdl2.SDL_DestroyTexture(self.texture)
			sdl2.SDL_DestroyRenderer(self.renderer)
			sdl2.SDL_DestroyWindow(self.window)
		sdl2.SDL_Quit()

	def setupWindow(self, width, height):
		self.window = sdl2.SDL_CreateWindow("%s: %s" % (config.sdl_window_caption, self.clientName), sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, width, height, sdl2.SDL_WINDOW_SHOWN)

		self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_ACCELERATED)
		self.texture = sdl2.SDL_CreateTexture(self.renderer, sdl2.SDL_PIXELFORMAT_YV12, sdl2.SDL_TEXTUREACCESS_STREAMING, width, height)
		



##############################################################################

availableSinks = {}

def __findSubclasses(cls):
	global availableSinks
	for c in cls.__subclasses__():
		if c.cmdLineKey is not None:
			availableSinks[c.cmdLineKey] = c
		__findSubclasses(c)

__findSubclasses(FrameSink)
