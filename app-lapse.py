from flask import Flask, render_template, send_from_directory
from flask import flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import datetime
import os
from glob import glob

app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b617bb'
appdir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(appdir)

from picamera import PiCamera
import time
import datetime
import argparse
import os
import arrow

class TimeLapse:
    interval_s = None

    def run_timelapse(output, number, time_s):
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


class ExternalProc:
    running_recording = False
    stop = False
    def start_recording(self):
        self.runthread = threading.Thread(target=timelapse.run)
        self.runthread.daemon = True
        self.runthread.start()


@app.route("/")
def hello():
   now = datetime.datetime.now()
   timeString = now.strftime("%Y-%m-%d %H:%M")
   templateData = {
      'title' : 'HELLO!',
      'time': timeString
      }
   return render_template('main.html', **templateData)

@app.route("/videos")
def videos_page():
   videos = [os.path.basename(vid) for vid in glob(os.path.join(appdir, "videos", "*.avi"))]
   templateData = {
      'videos' : videos
      }
   print videos
   return render_template('videos.html', **templateData)

@app.route("/pictures")
def pictures_top_page():
   pictures = os.listdir("pictures")
   pictures.sort()
   templateData = {
      'pictures' : pictures
      }
   print pictures
   return render_template('pictures_top.html', **templateData)

#@app.route("/start")
#def startapp():
#   return render_template('pictures_top.html', **templateData)
# App config.

class StartForm(Form):
    name = TextField('Name:', validators=[validators.required()])

@app.route("/start", methods=['GET', 'POST'])
def start_entrypoint():
    form = StartForm(request.form)

    print form.errors
    if request.method == 'POST':
        name=request.form['name']
        print name

        if form.validate():
            # Save the comment here.
            flash('Hello ' + name)
        else:
            flash('All the form fields are required. ')

    return render_template('start.html', form=form)

@app.route("/start/<interval>/<time>")
def start_app():
    

@app.route('/videos/<filename>', methods=['GET', 'POST'])
def download_video(filename):
    return send_from_directory(directory=os.path.join(appdir,"videos"), filename=filename)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=False)

