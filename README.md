# Raspi-Lapse

A dumb timelapse implementation in python for raspberry pi.

A much easier solution is here: https://www.raspberrypi.org/documentation/usage/camera/raspicam/timelapse.md

But, I wanted to do a few more things:
  1. Add some annotation 
  2. Add some scripting to run on boot
  3. Make something that I can adapt to other things...

## Setup

Install into the home directory (for me, it's /home/pi)

`git clone git@github.com:ejk43/raspilapse.git`

Enter the raspilapse folder and install the python requirements:

`pip install requirements.txt`

To get the raspberry pi video converter to work, I followed instructions here: https://www.raspberrypi.org/forums/viewtopic.php?t=72435

Specifically: 

```
sudo sh -c 'echo deb http://vontaene.de/raspbian-updates/ . main >> /etc/apt/sources.list'

sudo apt-get update

sudo apt-get install libgstreamer1.0-0 liborc-0.4-0 gir1.2-gst-plugins-base-1.0 gir1.2-gstreamer-1.0 gstreamer1.0-alsa gstreamer1.0-omx gstreamer1.0-plugins-bad gstreamer1.0-plugins-base gstreamer1.0-plugins-base-apps gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-pulseaudio gstreamer1.0-tools gstreamer1.0-x libgstreamer-plugins-bad1.0-0 libgstreamer-plugins-base1.0-0
```

Then I wrapped the video conversion command into a small script, convert_to_avi.sh. For example, the following command will convert images (with the name imageXXXX.jpg) in the specified location to an AVI file with the specified framerate. Seems to work well.

`./convert_to_avi.sh <location> <framerate>`

## Running

To run the command line application:

`./timelapse.py -t <time between pictures, seconds> -d <duration, minutes> -o <output location>`

Also, the `run_timelapse.sh` script kicks stuff off and then runs the video converter afterwards.

To run on boot:

`crontab -e`

Then enter something like this:

`@reboot /home/pi/raspilapse/run_timelapse.sh &>> /home/pi/raspilapse/log.txt`

## Download Videos

There's a "host" folder that contains a few scripts to rsync some data from my raspberry pi to my host PC.

## Edits?

I currently just edit the timelapse.py file to change camera parameters and stuff.

What I'd like to do:

  - Add a web frontend to interact with the recording functionality (start, stop, convert to video, download video, clear images)
  - Add some image processing to do something cool. ie, detect when my dog gets on the couch. 
  - Turn it into a robot (a little out there, but hey it's possible)
  - I'm open to better ideas

