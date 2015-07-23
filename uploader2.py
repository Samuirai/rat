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

log("check if not authenticated")
auth_url = is_not_authenticated()
while auth_url:
    log("auth_url: {0}".format(auth_url))
    log("send auth url")
    rat.post_yt_auth_url(auth_url)
    auth_code = None
    while not auth_code:
        time.sleep(15)
        log("get auth code")
        auth_code = rat.get_yt_auth_code()
        log("got: {0}".format(auth_code))
        if auth_code:
            authenticate(auth_code)
    
    auth_url = is_not_authenticated()
    if auth_url:
        rat.clear_yt_auth_code()
        time.sleep(5)
log("authenticated")
rat.clear_yt_auth_url()
rat.clear_yt_auth_code()

FOLDER_VIDEO = "/tmp"

while True:
    for file_name in listdir(FOLDER_VIDEO):
        if file_name.split(".")[-1] == 'mp4':
            try:
                timestamp = float(file_name.split(".")[0])
                video_file = path.join(FOLDER_VIDEO, file_name)
                log("wait a bit more fore {0} size: {1}".format(video_file, path.getsize(video_file)))
                if timestamp+5<time.time():
                    if path.getsize(video_file)>512:
                        log("try to upload {0} size: {1}".format(video_file, path.getsize(video_file)))

                        upload_process = Popen("python youtube.py \"{0}\" \"{1}\"".format(
                            path.abspath(video_file), 
                            str(datetime.fromtimestamp(timestamp))))
                        log(upload_process.communicate())
                        #yt_id = youtube.upload_video(
                        #    path.abspath(video_file),
                        #    str(datetime.fromtimestamp(timestamp)))
                        log(yt_id)
                        if yt_id:
                            log("YT Uploaded: {0}".format(yt_id))
                            remove(video_file)
                        else:
                            log("FAILED UPLOAD")
                    else:
                        remove(video_file)
            except ValueError:
                pass
            time.sleep(5)
    time.sleep(5)

