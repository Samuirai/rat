import requests
import json
from server import config
import sys
import time
import RPi.GPIO as GPIO
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

def get_wrapper(url, auth={}):
    for attempt range(0,10):
        try:
            return requests.get(url, auth=auth).json()
        except requests.exception.ConnectionError:
            time.sleep(attempt**3+2)
    return None


def post_wrapper(url, data={}, auth={}):
    for attempt range(0,10):
        try:
            return requests.post(url, data=data, auth=__AUTH)
        except requests.exception.ConnectionError:
            time.sleep(attempt**3+2)
    return None

def set_red_led(state):
    GPIO.output(23,state)

def set_green_led(state):
    GPIO.output(22,state)

def get_settings():
    return get_wrapper(__URL+__SETTINGS, auth=__AUTH).json()


def post_yt_auth_url(url):
    return post_wrapper(__URL+__YT_AUTH_URL, data=json.dumps({'url': url}), auth=__AUTH)

def get_yt_auth_url():
    return get_wrapper(__URL+__YT_AUTH_URL, auth=__AUTH).json()['url']

def clear_yt_auth_url():
    return get_wrapper(__URL+__YT_AUTH_URL+__CLEAR, auth=__AUTH).json()['status']


def post_yt_auth_code(code):
    return post_wrapper(__URL+__YT_AUTH_CODE, data=json.dumps({'code': code}), auth=__AUTH)

def get_yt_auth_code():
    return get_wrapper(__URL+__YT_AUTH_CODE, auth=__AUTH).json()['code']

def clear_yt_auth_code():
    return get_wrapper(__URL+__YT_AUTH_CODE+__CLEAR, auth=__AUTH).json()['status']


def post_log(log):
    return post_wrapper(__URL+__LOG, data=json.dumps({'log': log, 'src': sys.argv[0]}), auth=__AUTH)

def get_log():
    return get_wrapper(__URL+__LOG, auth=__AUTH).json()['logs']

def upload_photo():
    files = {'file': open('/tmp/photo.jpg', 'rb')}
    return post_wrapper(__URL+__UPLOAD_PHOTO, auth=__AUTH, files=files).json()['status']

