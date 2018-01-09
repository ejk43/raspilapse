#!/bin/bash
gst-launch-1.0 multifilesrc location=$1/image%04d.jpg index=1 caps="image/jpeg,framerate=$2/1" ! jpegdec ! omxh264enc ! avimux ! filesink location=videos/`date -Iminutes`.avi

