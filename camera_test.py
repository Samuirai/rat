#!/usr/bin/python
# based on script from Stephan Wypler
import numpy as np
import picamera
import picamera.array
import time
import subprocess

videoIDlist = []

class DetectMotion(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, size = None):
        super(DetectMotion, self).__init__(camera, size)
        self.__camera = camera
        self.__lastMotion = time.time()
        self.__recordingStarted = time.time()
        self.__motionsInLastClip = 0
        self.__recording = False
        self.__filename = "ERROR"
        
    def analyse(self, a):
        a = np.sqrt(np.square(a['x'].astype(np.float)) + np.square(a['y'].astype(np.float))).clip(0, 255).astype(np.uint8) # compute vector from both directions
        if (a > 21).sum() > 7:  # If there're more than 7 vectors with a magnitude greater than 21, then say we've detected motion
            print "motion detected! {0} motions: {1}".format((a > 21).sum(), self.__motionsInLastClip)
            self.__lastMotion = time.time()
            self.__motionsInLastClip += 1
            if not self.__recording:
                self.__filename = str(int(time.time()))
                self.__camera.split_recording("/tmp/{0}.h264".format(self.__filename), splitter_port=1)
                self.__recording = True
                self.__recordingStarted = time.time()
                self.__motionsInLastClip = 0
                print "start recording clip {0}".format(self.__filename)
                self.__camera.logger.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "start recording clip {0}\n".format(self.__filename))
        if self.__recording and (time.time() - self.__lastMotion > 2.0 or time.time()-self.__recordingStarted>30):
            self.__camera.split_recording('/dev/null', splitter_port=1)
            self.__recording = False
            print "stop recording clip {0} motions: {1}".format(self.__filename, self.__motionsInLastClip)
            self.__camera.logger.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "stop recording clip {0}\n".format(self.__filename))
            if self.__motionsInLastClip != 0:
                videoIDlist.append(self.__filename)
            else:
                print "no motion during the clip! false positive?!"
                self.__camera.logger.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "no motion during the clip! false positive?!\n")

with picamera.PiCamera() as camera:
    with DetectMotion(camera, (640, 480)) as motionDetection, open("/tmp/log.txt", 'a') as log:
        try:
            camera.logger = log
            camera.resolution = (1920, 1080)
            camera.framerate = 5
            camera.exposure_mode = 'night'
            camera.start_recording('/dev/null', 
                                   format='h264',
                                   splitter_port=1, 
                                   resize=None, 
                                   profile='high',
                                   inline_headers=True,
                                   bitrate=6000000,
                                   intra_period = 1,
                                   quality=17)
            camera.start_recording('/dev/null', 
                                   format='h264',
                                   motion_output=motionDetection,
                                   splitter_port=2, 
                                   intra_period = 0,
                                   resize=(640, 480))
            print "running"
            log.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "running\n")
            while True:
                while len(videoIDlist):
                    executionString = "ffmpeg -loglevel quiet -nostats -y -f h264 -r 5 -i /tmp/{0}.h264 -c:v copy -an -map 0:0 -f mp4 /tmp/{0}.mp4 && rm /tmp/{0}.h264".format(videoIDlist.pop(0))
                    print executionString
                    log.write(time.strftime("%Y-%m-%d %H:%M:%S ") + executionString + "\n")
                    subprocess.Popen(executionString, shell=True)
                
                time.sleep(1)
            
        except KeyboardInterrupt:
            print "stopping"
            log.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "stopping\n")
        finally:
            camera.stop_recording(splitter_port=2)
            camera.stop_recording(splitter_port=1)
            