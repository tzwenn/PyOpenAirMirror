#!/bin/sh

if [ $# -lt 1 ]; then
	echo "Please provide a yuv file"
	exit 1
fi

ffmpeg -vcodec rawvideo -f rawvideo -pix_fmt yuv420p -s:v 1036x648 -r 25 -i $1 -c:v libx264 ${1%.yuv}.mp4
