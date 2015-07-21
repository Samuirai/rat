import youtube
from os import path, makedirs, listdir, remove
import time

FOLDER_VIDEO = "/tmp"
LOG_FILE = open("/tmp/uploader_log", "a")

def log(msg):
    print msg
    LOG_FILE.write(msg+"\n")


while True:
    for file_name in listdir(FOLDER_VIDEO):
        if file_name.split(".")[-1] == 'mp4':
            try:
                timestmap = float(file_name.split(".")[0])
                if timestmap+5<time.time():
                    print ""
                    upload_video(
                        path.abspath(path.join(FOLDER_VIDEO, file_name)), 
                        str(datetime.fromtimestamp(timestamp)))
            except ValueError:
                pass
    time.sleep(5)