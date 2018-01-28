from flask import Flask, render_template, send_from_directory
import datetime
import os
from glob import glob
app = Flask(__name__)
appdir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

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
   videos = [os.path.basename(vid) for vid in glob(os.path.join(appdir, "videos", "*"))]
   templateData = {
      'videos' : videos
      }
   print videos
   return render_template('videos.html', **templateData)

@app.route('/videos/<filename>', methods=['GET', 'POST'])
def download_video(filename):
    return send_from_directory(directory=os.path.join(appdir,"videos"), filename=filename)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=False)

