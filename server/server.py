from flask import Flask, render_template, request, Response, redirect, url_for
from werkzeug import secure_filename
import json
from datetime import datetime
from os import path, makedirs, listdir, remove
from functools import wraps
from lockfile import locked
import config
import sun

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid."""
    return username == config.HTTP_AUTH[0] and password == config.HTTP_AUTH[1]

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

FD_SETTINGS = None
SETTINGS = {}

FILE_MESSAGE = path.abspath("messages")
LOCK_MESSAGE = path.join("/tmp", "lock_message")

FILE_SETTINGS = path.abspath("settings")
LOCK_SETTINGS = path.join("/tmp", "lock_settings")

FILE_YT_AUTH_URL = path.abspath("yt_auth_url")
LOCK_YT_AUTH_URL = path.join("/tmp", "lock_yt_auth_url")

LOCK_YT_AUTH_CODE = path.join("/tmp", "lock_yt_auth_code")
FILE_YT_AUTH_CODE = path.abspath("yt_auth_code")

LOCK_LOG = path.join("/tmp", "lock_log")
FILE_LOG = path.abspath("log")


######### HELPER #########

def log(severity, msg):
    _log = "[{0}] {1}".format(severity, msg)
    print _log
    write_log(_log)


@locked(LOCK_SETTINGS)
def load_settings():
    _FD = open(FILE_SETTINGS, "r")
    SETTINGS = json.loads(_FD.read())
    _FD.close()
    return SETTINGS

@locked(LOCK_SETTINGS)
def dump_settings(SETTINGS=SETTINGS):
    _FD = open(FILE_SETTINGS, "w")
    _FD.write(json.dumps(SETTINGS))
    _FD.close()
    return SETTINGS

def save_settings(form):
    SETTINGS = {}
    for key in form.keys():
        SETTINGS[key] = form[key]
        dump_settings(SETTINGS)
    SETTINGS = load_settings()
    return SETTINGS


@locked(LOCK_YT_AUTH_URL)
def write_yt_auth_url(_JSON):
    _FD = open(FILE_YT_AUTH_URL, "w")
    _FD.write(_JSON['url'])
    _FD.close()

@locked(LOCK_YT_AUTH_URL)
def clear_yt_auth_url():
    _FD = open(FILE_YT_AUTH_URL, "w")
    _FD.write("")
    _FD.close()

@locked(LOCK_YT_AUTH_URL)
def get_yt_auth_url():
    _FD = open(FILE_YT_AUTH_URL, "r")
    auth_url = _FD.read()
    _FD.close()
    return auth_url



@locked(LOCK_YT_AUTH_CODE)
def write_yt_auth_code(_JSON):
    _FD = open(FILE_YT_AUTH_CODE, "w")
    _FD.write(_JSON['code'])
    _FD.close()

@locked(LOCK_YT_AUTH_CODE)
def clear_yt_auth_code():
    _FD = open(FILE_YT_AUTH_CODE, "w")
    _FD.write("")
    _FD.close()

@locked(LOCK_YT_AUTH_CODE)
def get_yt_auth_code():
    _FD = open(FILE_YT_AUTH_CODE, "r")
    auth_url = _FD.read()
    _FD.close()
    return auth_url


@locked(LOCK_LOG)
def get_log():
    _FD = open(FILE_LOG, "r")
    logs = []
    for j in _FD.read().split("\n"):
        if j:
            try:
                logs.append(json.loads(j))
            except ValueError:
                pass
                #logs.append(j)
    _FD.close()
    return logs

@locked(LOCK_LOG)
def write_log(_MSG):
    _FD = open(FILE_LOG, "a")
    _FD.write(_MSG+"\n")
    _FD.close()


def convert_json(s):
    try:
        return json.loads(s)
    except ValueError:
        return {}


######### NORMAL #########

@app.route("/")
@requires_auth
def index():
    return render_template('index.html')

@app.route("/log")
@requires_auth
def log_get():
    logs = get_log()
    return render_template('log.html', logs=logs)

@app.route("/photo")
@requires_auth
def photo_get():
    return render_template('photo.html')

@app.route("/settings", methods=['GET', 'POST'])
@requires_auth
def setings():
    if request.method == 'POST':
        save_settings(request.form)
    SETTINGS = load_settings()

    sunrise, sunset = sun.get_times()
    is_it_dark = sun.is_it_dark()
    YT_AUTH_URL = get_yt_auth_url()
    YT_AUTH_CODE = get_yt_auth_code()
    return render_template('settings.html', 
        settings=SETTINGS,
        yt_auth_url=YT_AUTH_URL,
        yt_auth_code=YT_AUTH_CODE,
        sunrise=sunrise,
        sunset=sunset,
        is_it_dark=is_it_dark)

# ffmpeg -loglevel quiet -nostats -y -f h264 -r 5 -i /tmp/reh{0}.h264 -c:v copy -an -map 0:0 -f mp4 /home/stephan/reh/media/reh{0}.mp4 && rm /tmp/reh{0}.h264
# ffmpeg -i input.flv -vf fps=1 out%d.png
# ffmpeg -i input.flv -ss 00:00:00 -vframes 1 out.png

######### API #########

@app.route("/api/settings/save", methods=['POST'])
@requires_auth
def api_setings_save():
    save_settings(request.form)
    return Response(json.dumps(SETTINGS), 200, mimetype="application/json")


@app.route("/api/delete/<video>")
@requires_auth
def api_delete_video(video):
    if video:
        remove(path.join(FOLDER_VIDEO, video))
    return Response(json.dumps({'status': 'OK'}), 200, mimetype="application/json") 


@app.route("/api/yt_auth_url", methods=['POST'])
@requires_auth
def api_post_yt_auth_url():
    write_yt_auth_url(request.get_json(force=True))
    return Response(json.dumps({'status': 'OK'}), 200, mimetype="application/json") 

@app.route("/api/yt_auth_url", methods=['GET'])
@requires_auth
def api_get_yt_auth_url():
    _JSON = json.dumps({'status': 'OK', 'url': get_yt_auth_url()})
    return Response(_JSON, 200, mimetype="application/json") 

@app.route("/api/yt_auth_url/clear", methods=['GET'])
@requires_auth
def api_clear_yt_auth_url():
    clear_yt_auth_url()
    _JSON = json.dumps({'status': 'OK'})
    return Response(_JSON, 200, mimetype="application/json") 

@app.route("/api/yt_auth_code", methods=['POST'])
@requires_auth
def api_post_yt_auth_code():
    write_yt_auth_code(request.get_json(force=True))
    return Response(json.dumps({'status': 'OK'}), 200, mimetype="application/json") 

@app.route("/api/yt_auth_code", methods=['GET'])
@requires_auth
def api_get_yt_auth_code():
    _JSON = json.dumps({'status': 'OK', 'code': get_yt_auth_code()})
    return Response(_JSON, 200, mimetype="application/json") 

@app.route("/api/yt_auth_code/clear", methods=['GET'])
@requires_auth
def api_clear_yt_auth_code():
    clear_yt_auth_code()
    _JSON = json.dumps({'status': 'OK'})
    return Response(_JSON, 200, mimetype="application/json") 


@app.route("/api/log", methods=['POST'])
@requires_auth
def api_post_log():
    _JSON = request.get_json(force=True)
    write_log(json.dumps(_JSON))
    return Response(json.dumps({'status': 'OK'}), 200, mimetype="application/json") 

@app.route("/api/yt_auth_code", methods=['GET'])
@requires_auth
def api_get_log():
    _JSON = json.dumps({'status': 'OK', 'logs': get_log()})
    return Response(_JSON, 200, mimetype="application/json") 

@app.route("/api/upload_photo", methods=['POST'])
@requires_auth
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(path.join(FOLDER_PIC, filename))
    _JSON = json.dumps({'status': 'OK'})
    return Response(_JSON, 200, mimetype="application/json") 


@app.route("/api/settings")
@app.route("/api/ping")
@requires_auth
def api_settings():
    SETTINGS = load_settings()
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
    if not path.exists(FILE_MESSAGE):
        log(LOG_DEBUG, "make messages file: {0}".format(FILE_MESSAGE))
        _FD = open(FILE_MESSAGE, "w")
        _FD.close()
    if not path.exists(FILE_YT_AUTH_CODE):
        log(LOG_DEBUG, "make FILE_YT_AUTH_CODE file: {0}".format(FILE_YT_AUTH_CODE))
        _FD = open(FILE_YT_AUTH_CODE, "w")
        _FD.close()
    if not path.exists(FILE_YT_AUTH_URL):
        log(LOG_DEBUG, "make FILE_YT_AUTH_URL file: {0}".format(FILE_YT_AUTH_URL))
        _FD = open(FILE_YT_AUTH_URL, "w")
        _FD.close()

    load_settings()
    log(LOG_INFO, "settings loaded: {0}".format(SETTINGS))
    return True


if __name__ == "__main__":
    if check_setup():
        app.debug = True
        app.run(host=config.SERVER_IP, port=config.SERVER_PORT, threaded=True)
    else:
        exit()