# PyOpenAirMirror
An open-source (BSD 2) Python implementation of an AirPlay Mirroring Server.
What's not open is the drm handshake (fairplay sap), on starting a connection. It turns out that many third party closed-source AirPlay Mirrors use the very same code under the hood, and some even in the form of a shared library, ready to use.

[espes](https://github.com/espes) follows [another awesome approach](https://github.com/espes/Slave-in-the-Magic-Mirror), running Apple's airtunesd ARM binary, which is cross-platform and worth checking out.

## What you need
- Python 2.7
- OS X 10.8+ running on an x86_64 processor (this does not need to be the system you are mirroring too).
- ffmpeg or libav development files installed

## Installling
After cloning the repository, you need to load and compile the [pyh264decode submodule](https://github.com/tzwenn/pyh264decode) and install all dependencies.

```
$ git submodule init
$ git submodule update
$ (cd h264decode; ./setup.py build)
$ ln -s h264decode/build/lib.*/h264decode.so .
$ pip install -r requirements.txt
```

## Running

Just run ```main.py```. If you are on 64bit OS X for the first time it will automatically offer you to download some binary fairplay library (check out ```fply/get_libfply.sh``` if you want to do it manually). Your computer will show up as "OpenAirMirror" on your iDevice's mirroring list.

![sdl-sink](http://i.imgur.com/UX7jm5v.png)

For a complete list of options see:

```
$ ./main.py --help
usage: main.py [-h] [--sink {sdl,pickle,yuv} [{sdl,pickle,yuv} ...]]
               [--password PASSWORD] [--fply-server FPLY_SERVER]
               [name]
```

By default the transmitted video will be displayed with pygame. You can select alternative sinks, like pickling all received frames or storing them without time info as raw YUV frames (which can be converted back to MP4 using the ```yuv2mp4.sh``` script).

## Known issues

See [Issues](https://github.com/tzwenn/PyOpenAirMirror/issues).

## If you don't have an OS X at hand

If you want to mirror on another system or architecture, run the ```fplyServer.py``` on OS X and than define this host has a key server. (**ATTENTION**: Your session AES key will be transcripted unencryptedly over the network. This might be an issue for sensitive screen contents).

Alternatively you can communicate with epes's ARM-emulation via pipes.
