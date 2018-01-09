#!/usr/bin/env python

from picamera import PiCamera
import time
import datetime
import argparse
import os
import arrow

def run(output, number, time_s):
    camera = PiCamera()
    #camera.resolution = (640, 480) # Use a 4:3 ratio to get full FOV
    camera.resolution = (1280, 960) # Use a 4:3 ratio to get full FOV
    camera.rotation = 180

    #camera.start_preview()
    for ii in range(number):
      time.sleep(time_s)
      print("Recording image %04i" % ii)
      utc = arrow.utcnow()
      timestr = utc.to('US/Eastern').format('YYYY-MM-DD hh:mm:ss a')
      camera.annotate_text = timestr

      # Capture it!
      camera.capture(os.path.join(output, "image%04i.jpg" % ii))

    #camera.stop_preview()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #parser.add_argument("-n", "--number", type=int, help="Number of pictures")
    parser.add_argument("-d", "--duration", type=float, default=30, help="Collection duration (minutes)")
    parser.add_argument("-t", "--time", type=float, default=10, help="Sleep time (seconds)")
    parser.add_argument("-o", "--output", type=str, help="Output folder", default="")
    parser.add_argument("-s", "--stamp", action="store_true", default=False, help="Create a based on current timestamp")
    args = parser.parse_args()

    output = os.path.abspath(args.output)
    if args.stamp:
        utc = arrow.utcnow()
        timestr = utc.to('US/Eastern').format('YYYY-MM-DD_HH-mm-ss')
        output = os.path.join(output, timestr)		
    if not os.path.isdir(output):
        os.makedirs(output)
    print("Saving timelapse to folder: %s" % (output))

    sleeptime = args.time
    print("Sleeping for %0.1f seconds between captures" % (sleeptime))

    total_pics = int(args.duration * 60.0 / args.time)
    run(output, total_pics, sleeptime)
