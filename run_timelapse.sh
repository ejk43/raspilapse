#!/usr/bin/env bash

# 1) Run the timelapse script
# 2) Convert to avi

set -x
sleep 60s # Wait before starting so the raspberry pi can query internet time
/home/pi/raspilapse/timelapse.py -s -o /home/pi/raspilapse/pictures -t 10 -d 480
/home/pi/raspilapse/convert_to_avi.sh $(ls -td /home/pi/raspilapse/pictures/*/ | head -n 1) 10
