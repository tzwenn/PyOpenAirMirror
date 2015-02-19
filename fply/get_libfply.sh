#!/bin/bash

if [ $# -eq 1 ]; then
	OUTFILE=$1
else
	OUTFILE=fply.dylib
fi

echo "Downloading DMG"
curl http://d17kmd0va0f0mp.cloudfront.net/m360/mac/mirroring360_mac.dmg > m.dmg
echo "Mounting"
mkdir mirroring360
hdiutil attach m.dmg -mountpoint mirroring360
echo "Copy fply.dylib to \"$OUTFILE\""
cp -a mirroring360/Mirroring360.app/Contents/Frameworks/fply.dylib "$OUTFILE"
echo "Clean up"
hdiutil detach mirroring360
rmdir mirroring360
rm m.dmg
echo "Retrieved binary fairplay module"
