import os
import subprocess
import rat
import time


while True:
    time.sleep(60)
    watch = {
        'light_control.py': False,
        'shutdown_button.py': False,
        'uploader.py': False,
        'camera.py': False,
    }
    # http://stackoverflow.com/questions/2703640/process-list-on-linux-via-python
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            process = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
            for w in watch.keys():
                if w in process:
                    watch[w] = True
        except IOError: # proc has already terminated
            continue
    for w in watch.keys():
        if not watch[w]:
            try:
                m = "Process {0} not running. REBOOT!".format(w)
                print m
                rat.post_log(m)
            except:
                pass
            p = subprocess.Popen("reboot", shell=True)

