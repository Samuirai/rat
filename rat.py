import requests
import json
from server import config
import sys
import time
import RPi.GPIO as GPIO
import subprocess
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)

__URL = "http://88.198.162.251"
__URL = config.SERVER_URL
__SETTINGS = "/api/settings"
__MESSAGE = "/api/messages"
__YT_AUTH_URL = "/api/yt_auth_url"
__YT_AUTH_CODE = "/api/yt_auth_code"
__LOG = "/api/log"
__UPLOAD_PHOTO = "/api/upload_photo"
__CLEAR = "/clear"
__AUTH = config.HTTP_AUTH

def log(msg):
    #print msg
    l = open("/tmp/log", "a")
    l.write("{2} - {0}: {1}\n".format(sys.argv[0], msg, time.time()))
    l.close()

def get_wrapper(url, auth={}):
    for attempt in xrange(0,4):
        try:
            return requests.get(url, auth=auth)
        except requests.exceptions.ConnectionError:
            log("GET error. sleep and try again. attempt: {0}".format(attempt))
            time.sleep(attempt**3+2)
    log("GOING FOR REBOOT")
    p = subprocess.Popen("reboot", shell=True)
    p.communicate()
    return None


def post_wrapper(url, data={}, auth={}, files=None):
    for attempt in xrange(0,4):
        try:
            if not files:
                return requests.post(url, data=data, auth=__AUTH)
            else:
                return requests.post(url, data=data, auth=__AUTH, files=files)
        except requests.exceptions.ConnectionError:
            time.sleep(attempt**3+2)
    return None

def set_red_led(state):
    GPIO.output(23,state)

def set_green_led(state):
    GPIO.output(22,state)

def get_settings():
    settings = get_wrapper(__URL+__SETTINGS, auth=__AUTH)
    if settings:
        return settings.json()
    else:
        return None


def post_yt_auth_url(url):
    return post_wrapper(__URL+__YT_AUTH_URL, data=json.dumps({'url': url}), auth=__AUTH)

def get_yt_auth_url():
    r = get_wrapper(__URL+__YT_AUTH_URL, auth=__AUTH)
    if r:
        return r.json()['url']
    else:
        return None

def clear_yt_auth_url():
    r = get_wrapper(__URL+__YT_AUTH_URL+__CLEAR, auth=__AUTH)
    if r:
        return r.json()['status']
    else:
        return None


def post_yt_auth_code(code):
    return post_wrapper(__URL+__YT_AUTH_CODE, data=json.dumps({'code': code}), auth=__AUTH)

def get_yt_auth_code():
    r = get_wrapper(__URL+__YT_AUTH_CODE, auth=__AUTH)
    if r:
        return r.json()['code']
    else:
        return None

def clear_yt_auth_code():
    r = get_wrapper(__URL+__YT_AUTH_CODE+__CLEAR, auth=__AUTH)
    if r:
        return r.json()['status']
    else:
        return None


def post_log(msg):
    log(msg)
    return post_wrapper(__URL+__LOG, data=json.dumps({'log': msg, 'src': sys.argv[0], 'time': int(time.time())}), auth=__AUTH)

def get_log():
    return get_wrapper(__URL+__LOG, auth=__AUTH).json()['logs']

def upload_photo():
    files = {'file': open('/tmp/photo.jpg', 'rb')}
    return post_wrapper(__URL+__UPLOAD_PHOTO, auth=__AUTH, files=files)
    if r:
        return r.json()['status']
    else:
        return None

