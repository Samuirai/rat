import requests
import json

__URL = "http://88.198.162.251"
__URL = "http://127.0.0.1:5000"
__SETTINGS = "/api/setings"
__MESSAGE = "/api/messages"
__YT_AUTH_URL = "/api/yt_auth_url"
__YT_AUTH_CODE = "/api/yt_auth_code"
__LOG = "/api/log"
__CLEAR = "/clear"
__AUTH = ('test', 'test')
YT_AUTH = '/YT_AUTH'

def get_settings():
    return requests.get(__URL+__SETTINGS, auth=__AUTH).json()


def post_yt_auth_url(url):
    return requests.post(__URL+__YT_AUTH_URL, data=json.dumps({'url': url}), auth=__AUTH)

def get_yt_auth_url():
    return requests.get(__URL+__YT_AUTH_URL, auth=__AUTH).json()['url']

def clear_yt_auth_url():
    return requests.get(__URL+__YT_AUTH_URL+__CLEAR, auth=__AUTH).json()['status']


def post_yt_auth_code(code):
    return requests.post(__URL+__YT_AUTH_CODE, data=json.dumps({'code': code}), auth=__AUTH)

def get_yt_auth_code():
    return requests.get(__URL+__YT_AUTH_CODE, auth=__AUTH).json()['code']

def clear_yt_auth_code():
    return requests.get(__URL+__YT_AUTH_CODE+__CLEAR, auth=__AUTH).json()['status']


def post_log(log):
    return requests.post(__URL+__LOG, data=json.dumps({'log': log}), auth=__AUTH)

def get_log():
    return requests.get(__URL+__LOG, auth=__AUTH).json()['logs']