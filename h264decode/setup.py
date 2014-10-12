#!/usr/bin/env python

from distutils.core import setup, Extension

setup(
	name = "h264decode",
	version = "0.1",
	description = "Module for simple decoding of raw H264 streams with external avcC (ISO/IEC 14496:15)",
	ext_modules = [Extension(	"h264decode",
								sources=["yuvframe.c", "decoder.c", "h264decode.c"],
								libraries=["avcodec"],
								library_dirs=["/usr/local/lib", "/usr/lib"])]
)
