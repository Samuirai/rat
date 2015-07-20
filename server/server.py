from flask import Flask, render_template, request, Response
import json
from datetime import datetime
from os import path, makedirs, listdir, remove
from functools import wraps

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid."""
    return username == 'sami' and password == 'w3l0ver4ts'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response('', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
#print(path.isdir("/home/el"))
#print(path.exists("/home/el/myfile.txt"))

app = Flask(__name__)

LOG_DEBUG = "?"
LOG_INFO = "*"
LOG_ERROR = "!"

FOLDER_MEDIA = path.abspath(path.join("static", "media"))
FOLDER_VIDEO = path.abspath(path.join(FOLDER_MEDIA, "videos"))
FOLDER_PIC = path.abspath(path.join(FOLDER_MEDIA, "pics"))
FILE_SETTINGS = path.abspath("settings")
FD_SETTINGS = None
SETTINGS = {}

######### HELPER #########

def log(severity, msg):
    print "[{0}] {1}".format(severity, msg)

def get_thumbnails(video_name, pic_files=listdir(FOLDER_PIC)):
    
    thumbnails = ['na.png']*4
    for pic_filename in pic_files:
        if pic_filename.startswith(video_name):
            thumbnails.append(pic_filename)
    return thumbnails[-4:]

def get_all_videos():
    videos = {}
    video_files = listdir(FOLDER_VIDEO)
    pic_files = listdir(FOLDER_PIC)
    for video_filename in video_files:
        video_name, extension = video_filename.split(".")
        if extension == 'mp4':
            log(LOG_DEBUG, "found video: {0}".format(video_filename))
            timestamp = 0
            try:
                timestamp = float(video_name)
            except ValueError:
                timestamp = 0
            videos[video_filename] = {
                'thumbnails': get_thumbnails(video_name, pic_files),
                'datetime': datetime.fromtimestamp(timestamp),
                }
    return videos

def load_settings():
    FD_SETTINGS = open(FILE_SETTINGS, "r")
    SETTINGS = json.loads(FD_SETTINGS.read())
    FD_SETTINGS.close()
    return SETTINGS

def dump_settings(SETTINGS=SETTINGS):
    FD_SETTINGS = open(FILE_SETTINGS, "w")
    FD_SETTINGS.write(json.dumps(SETTINGS))
    FD_SETTINGS.close()
    return SETTINGS

def save_settings(form):
    SETTINGS = {}
    for key in form.keys():
        SETTINGS[key] = form[key]
        dump_settings(SETTINGS)
    SETTINGS = load_settings()
    return SETTINGS

######### NORMAL #########

@app.route("/")
@requires_auth
def index():
    return render_template('index.html', videos=get_all_videos())

@app.route("/settings", methods=['GET', 'POST'])
@requires_auth
def setings():
    if request.method == 'POST':
        save_settings(request.form)
    SETTINGS = load_settings()
    return render_template('settings.html', settings=SETTINGS)

# ffmpeg -loglevel quiet -nostats -y -f h264 -r 5 -i /tmp/reh{0}.h264 -c:v copy -an -map 0:0 -f mp4 /home/stephan/reh/media/reh{0}.mp4 && rm /tmp/reh{0}.h264
# ffmpeg -i input.flv -vf fps=1 out%d.png
# ffmpeg -i input.flv -ss 00:00:00 -vframes 1 out.png

######### API #########

@app.route("/api/settings/save", methods=['POST'])
def api_setings_save():
    save_settings(request.form)
    return Response(json.dumps(SETTINGS), 200, mimetype="application/json")


@app.route("/api/delete/<video>")
def api_delete_video(video):
    if video:
        remove(path.join(FOLDER_VIDEO, video))
    return Response(json.dumps({'status': 'OK'}), 200, mimetype="application/json") 

@app.route("/api/settings")
@app.route("/api/ping")
@requires_auth
def api_settings():
    return Response(json.dumps(SETTINGS), 200, mimetype="application/json")

######### SETUP #########

def check_setup():
    if not path.exists(FOLDER_MEDIA):
        log(LOG_DEBUG, "make dirs: {0}".format(FOLDER_MEDIA))
        makedirs(FOLDER_MEDIA)
    if not path.exists(FOLDER_VIDEO):
        log(LOG_DEBUG, "make dirs: {0}".format(FOLDER_VIDEO))
        makedirs(FOLDER_VIDEO)
    if not path.exists(FOLDER_PIC):
        log(LOG_DEBUG, "make dirs: {0}".format(FOLDER_PIC))
        makedirs(FOLDER_PIC)
    if not path.exists(FILE_SETTINGS):
        log(LOG_DEBUG, "make config file: {0}".format(FILE_SETTINGS))
        FD_SETTINGS = open(FILE_SETTINGS, "w")
        FD_SETTINGS.close()

    load_settings()
    log(LOG_INFO, "settings loaded: {0}".format(SETTINGS))
    return True


if __name__ == "__main__":
    if check_setup():
        app.debug = True
        app.run()
    else:
        exit()