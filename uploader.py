import youtube
from os import path, makedirs, listdir, remove
import time
from datetime import datetime

FOLDER_VIDEO = "/tmp"
LOG_FILE = open("/tmp/uploader_log", "a")

def log(msg):
    print msg
    LOG_FILE.write(msg+"\n")


while True:
    for file_name in listdir(FOLDER_VIDEO):
        if file_name.split(".")[-1] == 'mp4':
            try:
                timestamp = float(file_name.split(".")[0])
                video_file = path.join(FOLDER_VIDEO, file_name)
                if timestamp+5<time.time():
                    if path.getsize(video_file)>512:
                        print "try to upload {0} size: {1)".format(video_file, path.getsize(video_file))
                        yt_id = youtube.upload_video(
                            path.abspath(video_file),
                            str(datetime.fromtimestamp(timestamp)))
                        print yt_id
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