#!/usr/bin/python
import subprocess
import rat
from os import path, makedirs, listdir, remove, killpg
import signal
import time
import traceback
from datetime import datetime
import RPi.GPIO as GPIO
import sys
authenticated = True

if len(sys.argv)<2:
    time.sleep(10)

GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def log(msg):
    print msg
    rat.post_log(msg)

def is_not_authenticated():
    p = subprocess.Popen("python /home/pi/rat/youtube.py", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, bufsize=1)
    out = p.communicate()[0]
    if not out:
        return False
    else:
        return out.split()[8]

def authenticate(code):
    p = subprocess.Popen("/home/pi/rat/youtube.py", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, bufsize=1)
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
    files = [file_name for file_name in listdir(FOLDER_VIDEO) if file_name.split(".")[-1] == 'mp4' and file_name.startswith('done')]
    if len(files)>0:
        file_name = files[-1]
        try:
            timestamp = float(file_name.split(".")[0].split("_")[1])
            video_file = path.join(FOLDER_VIDEO, file_name)
            log("found video {0} with backlog: {1}".format(video_file, len(files)))
            if timestamp+5<time.time():
                if path.getsize(video_file)>64:
                    rat.set_green_led(True)
                    log("attempt to upload {0} with size: {1}mb".format(video_file, int(path.getsize(video_file)/1024.0/1024.0)))
                    upload_process = subprocess.Popen("python /home/pi/rat/youtube.py \"{0}\" \"{1}\" >> /tmp/log".format(
                        path.abspath(video_file), 
                        str(datetime.fromtimestamp(timestamp))), shell=True)
                    #upload_process.communicate()
                    for _ in xrange(0,10):
                        if upload_process.poll() == None:
                            log("still not done uploading. sleep")
                            time.sleep(30)

                    log("kill process: {0} and remove: {1}".format(upload_process.pid, video_file))
                    try:
                        killpg(upload_process.pid, signal.SIGTERM)
                    except OSError:
                        pass
                    try:
                        remove(video_file)
                    except OSError:
                        pass
                    rat.set_green_led(False)
                    
                else:
                    log("remove {0}".format(video_file))
                    remove(video_file)
        except:
            rat.post_log(str(traceback.format_exc()))
    time.sleep(10)

