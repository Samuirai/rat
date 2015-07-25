#!/usr/bin/python
# based on script from Stephan Wypler
import numpy as np
import picamera
import picamera.array
import time
import subprocess
import rat
import sys

videoIDlist = []

# {"min_len": "2", "max_len": "30", "nr_vectors": "7", "video_height": "1080", "magnitude": "21", "video_width": "1920"}

settings = rat.get_settings()
for atr in ['min_len', 'max_len', 'nr_vectors', 'magnitude', 'video_height', 'video_width', 'motions', 'fps']:
    if atr not in settings:
        exit("{0} is missing in settings".format(atr))

__VIDEO_HEIGHT = int(settings['video_height'])
__VIDEO_WIDTH = int(settings['video_width'])
__FPS = int(settings['fps'])

print "__MIN_LEN: {0}".format(__MIN_LEN)
print "__MAX_LEN: {0}".format(__MAX_LEN)
print "__NR_VECTORS: {0}".format(__NR_VECTORS)
print "__MAGNITUDE: {0}".format(__MAGNITUDE)
print "__VIDEO_HEIGHT: {0}".format(__VIDEO_HEIGHT)
print "__VIDEO_WIDTH: {0}".format(__VIDEO_WIDTH)
print "__MOTIONS: {0}".format(__MOTIONS)
print "__FPS: {0}".format(__FPS)

class DetectMotion(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, size = None, settings={}):
        super(DetectMotion, self).__init__(camera, size)
        self.__MIN_LEN = int(settings['min_len'])
        self.__MAX_LEN = int(settings['max_len'])
        self.__NR_VECTORS = int(settings['nr_vectors'])
        self.__MAGNITUDE = int(settings['magnitude'])
        self.__MOTIONS = int(settings['motions'])
        self.__camera = camera
        self.__lastMotion = time.time()
        self.__recordingStarted = time.time()
        self.__motionsInLastClip = 0
        self.__recording = False
        self.__filename = "ERROR"

    def analyse(self, a):
        a = np.sqrt(np.square(a['x'].astype(np.float)) + np.square(a['y'].astype(np.float))).clip(0, 255).astype(np.uint8) # compute vector from both directions
        if (a > self.__MAGNITUDE).sum() > self.__NR_VECTORS:  # If there're more than 7 vectors with a magnitude greater than 21, then say we've detected motion
            #print "motion detected! {0} motions: {1}".format((a > 21).sum(), self.__motionsInLastClip)
            self.__lastMotion = time.time()
            self.__motionsInLastClip += 1
            if not self.__recording:
                self.__filename = str(int(time.time()))
                self.__camera.split_recording("/tmp/{0}.h264".format(self.__filename), splitter_port=1)
                self.__recording = True
                self.__recordingStarted = time.time()
                self.__motionsInLastClip = 0
                print "start recording clip {0}".format(self.__filename)
                #self.__camera.logger.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "start recording clip {0}\n".format(self.__filename))

        if self.__recording:
            _t = time.time()
            if (_t - self.__lastMotion > self.__MIN_LEN or _t - self.__recordingStarted>self.__MAX_LEN):
                self.__camera.split_recording('/dev/null', splitter_port=1)
                self.__recording = False
                print "stop recording clip {0} motions: {1}".format(self.__filename, self.__motionsInLastClip)
                #self.__camera.logger.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "stop recording clip {0}\n".format(self.__filename))
                if self.__motionsInLastClip > self.__MOTIONS:
                    videoIDlist.append(self.__filename)
                else:
                    executionString = "rm /tmp/{0}.h264".format(self.__filename)
                    subprocess.Popen(executionString, shell=True)
                    print "no motion during the clip! false positive?!"
                    #self.__camera.logger.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "no motion during the clip! false positive?!\n")

print "startup"
with picamera.PiCamera() as camera:
    print "got camera"
    with DetectMotion(camera, (640, 480), settings) as motionDetection, open("/tmp/log.txt", 'a') as log:
        try:
            camera.logger = log
            camera.resolution = (__VIDEO_WIDTH, __VIDEO_HEIGHT)
            camera.exposure_mode = 'night'
            camera.framerate = __FPS
            camera.start_preview()
            camera.start_recording('/dev/null',
                                   format='h264',
                                   splitter_port=1,
                                   resize=None,
                                   profile='high',
                                   inline_headers=True,
                                   bitrate=17000000,
                                   intra_period = 1,
                                   quality=20)
            camera.start_recording('/dev/null',
                                   format='h264',
                                   motion_output=motionDetection,
                                   splitter_port=2,
                                   intra_period = 0,
                                   resize=(640, 480))
            log.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "running\n")
            while True:
                while len(videoIDlist):
                    executionString = "avconv -loglevel quiet -y -r {0} -i /tmp/{1}.h264 -vcodec copy /tmp/{1}.mp4 && rm /tmp/{1}.h264".format(__FPS, videoIDlist.pop(0))
                    print executionString
                    log.write(time.strftime("%Y-%m-%d %H:%M:%S ") + executionString + "\n")
                    subprocess.Popen(executionString, shell=True)

                time.sleep(5)

        except KeyboardInterrupt:
            print "stopping"
            log.write(time.strftime("%Y-%m-%d %H:%M:%S ") + "stopping\n")
        finally:
            print "finally"
            camera.stop_preview()
            camera.stop_recording(splitter_port=2)
            camera.stop_recording(splitter_port=1)