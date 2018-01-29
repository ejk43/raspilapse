from flask import Flask, render_template, send_from_directory
from flask import flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import datetime
import os
import sys
from glob import glob

app = Flask(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b617bb'
appdir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(appdir)

from picamera import PiCamera
import time
import arrow
import threading
import humanize
import subprocess

framerate = 10

convert_avi_tmpl = """gst-launch-1.0 multifilesrc location={infolder}/{name}/image%04d.jpg index=1 caps="image/jpeg,framerate={framerate}/1" ! jpegdec ! omxh264enc ! avimux ! filesink location={outfolder}/{name}.avi"""

def convert_to_timedelta(time_val):
    """
    http://code.activestate.com/recipes/577894-convert-strings-like-5d-and-60s-to-timedelta-objec/
    Given a *time_val* (string) such as '5d', returns a timedelta object
    representing the given value (e.g. timedelta(days=5)).  Accepts the
    following '<num><char>' formats:
    
    =========   ======= ===================
    Character   Meaning Example
    =========   ======= ===================
    s           Seconds '60s' -> 60 Seconds
    m           Minutes '5m'  -> 5 Minutes
    h           Hours   '24h' -> 24 Hours
    d           Days    '7d'  -> 7 Days
    =========   ======= ===================
    
    Examples::
    
        >>> convert_to_timedelta('7d')
        datetime.timedelta(7)
        >>> convert_to_timedelta('24h')
        datetime.timedelta(1)
        >>> convert_to_timedelta('60m')
        datetime.timedelta(0, 3600)
        >>> convert_to_timedelta('120s')
        datetime.timedelta(0, 120)
    """
    num = int(time_val[:-1])
    if time_val.endswith('s'):
        return datetime.timedelta(seconds=num)
    elif time_val.endswith('m'):
        return datetime.timedelta(minutes=num)
    elif time_val.endswith('h'):
        return datetime.timedelta(hours=num)
    elif time_val.endswith('d'):
        return datetime.timedelta(days=num)

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


class TimeLapse:
    running = False
    stopping = False
    interval_s = None
    stop_datetime = None
    destination = None
    runthread = None
    ii = None

    def __init__(self):
        self.camera = PiCamera()
        #camera.resolution = (640, 480) # Use a 4:3 ratio to get full FOV
        self.camera.resolution = (1280, 960) # Use a 4:3 ratio to get full FOV
        self.camera.rotation = 180

    def run_timelapse(self):
        self.running = True
        self.ii = 0
        while datetime.datetime.now() < self.stop_datetime and not self.stopping:
            time.sleep(self.interval_s)
            print("Recording image %04i" % self.ii)
            utc = arrow.utcnow()
            timestr = utc.to('US/Eastern').format('YYYY-MM-DD hh:mm:ss a')
            self.camera.annotate_text = timestr

            # Capture it!
            self.camera.capture(os.path.join(self.destination, "image%04i.jpg" % self.ii))
            self.ii = self.ii + 1
        self.running = False
        self.stopping = False

    def start_timelapse(self, interval_s, duration_timedelta):
        utc = arrow.utcnow()
        timestr = utc.to('US/Eastern').format('YYYY-MM-DD_HH-mm-ss')
        self.destination = os.path.join(appdir, "pictures", timestr)      
        if not os.path.isdir(self.destination):
            os.makedirs(self.destination)
        print("Saving timelapse to folder: %s" % (self.destination))

        self.stop_datetime = datetime.datetime.now() + duration_timedelta
        print("Scheduling end time for: %s" % (self.stop_datetime))

        self.interval_s = interval_s
        print("Setting interval to:  %s seconds" % self.interval_s)

        self.stopping = False
        self.runthread = threading.Thread(target=self.run_timelapse)
        self.runthread.daemon = True
        self.runthread.start()

    def stop_timelapse(self):
        self.stopping = True

    def get_status(self):
        if self.running:
            statusString = "Running... (Stop time = %s)" % (humanize.naturaltime(now - self.stop_datetime))
        else:
            statusString = "Idle"
        return statusString

class Conversion:
    proc = None
    target = None

    def __init__(self):
        pass

    def check_if_running(self):
        if not self.proc:
            return False
        poll = self.proc.poll()
        if poll is None:
            return True
        else:
            return False

    def start_conversion(self, name):
        convert_params = {
            "name" : name,
            "infolder" : os.path.join(appdir, "pictures"),
            "outfolder" : os.path.join(appdir, "videos"),
            "framerate" : framerate
        }
        mycall = convert_avi_tmpl.format(**convert_params)
        print("Running conversion: %s" % mycall)

        self.target = name
        self.proc = subprocess.Popen(mycall, shell=True)

    def get_status(self):
        if self.check_if_running():
            statusString = "Converting %s" % (self.target)
        else:
            statusString = "Idle"
        return statusString

lapseobj = TimeLapse()
convertobj = Conversion()

@app.route("/")
def hello():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    templateData = {
        'title' : 'HELLO!',
        'time': timeString,
        'app_status' : lapseobj.get_status(),
        'convert_status' : convertobj.get_status(),
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
    picdir = os.path.join(appdir, "pictures")
    pictures = os.listdir(picdir)
    pictures.sort()
    dict_pics = []
    for pic in pictures:
        currdir = os.path.join(picdir,pic)
        size = "%i MB" % (get_size(currdir)/2048)
        count = len(os.listdir(currdir))
        temp = {'name' : pic, 'count': count, 'size' : size}
        dict_pics.append(temp)
    templateData = {
        'pictures' : dict_pics
    }
    # print pictures
    return render_template('pictures_top.html', **templateData)

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
def start_app(interval, time):
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    if lapseobj.running:
        titleString = "Start Failed! Already running"
    else:
        titleString = "Start Succeeded!"
        duration_request = convert_to_timedelta(time)
        lapseobj.start_timelapse(float(interval), duration_request)

    templateData = {
        'title' : titleString,
        'time': timeString,
        'app_status' : lapseobj.get_status(),
        'convert_status' : convertobj.get_status(),
    }
    return render_template('main.html', **templateData)

@app.route("/convert/<name>")
def convert_app(name):
    pictures = os.listdir("pictures")
    if not name in pictures:
        titleString = "Conversion Failed! No pictures named %s" % (name) 
    else:
        if convertobj.check_if_running():
            titleString = "Conversion Failed! Already running"
        else:
            titleString = "Conversion Started!"
            convertobj.start_conversion(name)

    templateData = {
        'title' : titleString,
        'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        'app_status' : lapseobj.get_status(),
        'convert_status' : convertobj.get_status(),
    }
    return render_template('main.html', **templateData)

@app.route('/videos/<filename>', methods=['GET', 'POST'])
def download_video(filename):
    return send_from_directory(directory=os.path.join(appdir,"videos"), filename=filename)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=False)

