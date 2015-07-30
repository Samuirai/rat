#!/usr/bin/python
import subprocess
import rat
from os import path, makedirs, listdir, remove
import time
from datetime import datetime

authenticated = True

def log(msg):
    print msg
    rat.post_log(msg)

def is_not_authenticated():
    p = subprocess.Popen("python youtube.py", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, bufsize=1)
    out = p.communicate()[0]
    if not out:
        return False
    else:
        return out.split()[8]

def authenticate(code):
    p = subprocess.Popen("./youtube.py", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, bufsize=1)
    out = p.communicate(code)[0]

auth_url = is_not_authenticated()
while auth_url:
    log("auth_url: {0}".format(auth_url))
    rat.post_yt_auth_url(auth_url)
    auth_code = None
    while not auth_code:
        time.sleep(15)
        auth_code = rat.get_yt_auth_code()
        log("got API auth code: {0}".format(auth_code))
        if auth_code:
            authenticate(auth_code)
    
    auth_url = is_not_authenticated()
    if auth_url:
        rat.clear_yt_auth_code()
        time.sleep(5)
log("Youtube API authenticated")
rat.clear_yt_auth_url()
rat.clear_yt_auth_code()

FOLDER_VIDEO = "/tmp"
rat.set_green_led(False)
while True:
    for file_name in listdir(FOLDER_VIDEO):
        if file_name.split(".")[-1] == 'mp4' and file_name.startswith('done'):
            try:
                timestamp = float(file_name.split(".")[0].split("_")[1])
                video_file = path.join(FOLDER_VIDEO, file_name)
                if timestamp+5<time.time():
                    if path.getsize(video_file)>512:
                        rat.set_green_led(True)
                        log("attempt to upload {0} with size: {1} MB".format(video_file, path.getsize(video_file)/1024.0/1024.0))
                        upload_process = subprocess.Popen("python youtube.py \"{0}\" \"{1}\"".format(
                            path.abspath(video_file), 
                            str(datetime.fromtimestamp(timestamp))), shell=True)
                        upload_process.communicate()
                        rat.set_green_led(False)

                    else:
                        remove(video_file)
            except ValueError:
                pass
            time.sleep(5)
    time.sleep(5)

