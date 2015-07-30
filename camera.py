#!/usr/bin/python
# based on script from Stephan Wypler
import numpy as np
import picamera
import picamera.array
import time
import subprocess
import rat
import sys
import io
import Queue
import threading
import traceback
import RPi.GPIO as GPIO

skip = False

if len(sys.argv)>1:
    if sys.argv[1]=='skip':
        skip = True

if not skip:
    for _ in xrange(0,15):
        rat.set_red_led(True)
        rat.set_green_led(False)
        time.sleep(1)
        rat.set_red_led(False)
        rat.set_green_led(True)
        time.sleep(1)

def log(msg):
    sys.stdout.write("[camera] "+str(msg)+"\n")
    sys.stdout.flush()


rat.set_red_led(False)
rat.set_green_led(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

MOTIONS_FIFO = Queue.Queue()
RECORDED_VIDEOS_FIFO = Queue.Queue()

settings = rat.get_settings()
log("got settings")
for atr in ['min_len', 'max_len', 'nr_vectors', 'magnitude', 'video_height', 'video_width', 'motions', 'fps', 'rotation']:
    if atr not in settings:
        exit("{0} is missing in settings".format(atr))

FPS = int(settings['fps'])
VIDEO_WIDTH = int(settings['video_width'])
VIDEO_HEIGHT = int(settings['video_height'])
MAGNITUDE = int(settings['magnitude'])
PRE_MOTION = int(settings['pre_motion'])
POST_MOTION = int(settings['post_motion'])
ROTATION = int(settings['rotation'])
PREVIEW = int(settings['preview'])
DISABLE_RECORDING = int(settings['disable_recording'])


class ProcessingThread(threading.Thread):
    def __init__(self, camera, stream, MOTIONS_FIFO, RECORDED_VIDEOS_FIFO, log, settings={}):
        super(ProcessingThread, self).__init__()
        self.camera = camera
        self.stream = stream
        self.MOTIONS_FIFO = MOTIONS_FIFO
        self.RECORDED_VIDEOS_FIFO = RECORDED_VIDEOS_FIFO
        self.update_settings(settings)
        self.running = True
        self.lastMotion = time.time()
        self.motionsCounter = 0
        self.recording = False
        self.timestamp = time.time()
        self.log = log

    def update_settings(self, settings):
        self.MIN_LEN = int(settings['min_len'])
        self.MAX_LEN = int(settings['max_len'])
        self.NR_VECTORS = int(settings['nr_vectors'])
        self.MOTIONS = int(settings['motions'])
        self.POST_MOTION = int(settings['post_motion'])
        self.DISABLE_RECORDING = int(settings['disable_recording'])

    def write_stream(self, filename):
        # Write the entire content of the circular buffer to disk. No need to
        # lock the stream here as we're definitely not writing to it
        # simultaneously
        # http://picamera.readthedocs.org/en/latest/recipes2.html#splitting-to-from-a-circular-stream
        with io.open(filename, 'wb') as output:
            for frame in self.stream.frames:
                if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                    self.stream.seek(frame.position)
                    break
            while True:
                buf = self.stream.read1()
                if not buf:
                    break
                output.write(buf)
        # Wipe the circular self.stream once we're done
        self.stream.seek(0)
        self.stream.truncate()

    def run(self):
        self.log("processing thread started")
        while self.running:
            # get the nr of vectors that were over the threshold
            nr_of_vectors = None
            try:
                nr_of_vectors = self.MOTIONS_FIFO.get(False)
            except Queue.Empty:
                pass
            if nr_of_vectors:
                # if enough vectors were over the thershold | and if button is active
                if nr_of_vectors > self.NR_VECTORS and (GPIO.input(24)==0 and self.DISABLE_RECORDING==0):
                    # save the time of the last motion
                    self.lastMotion = time.time()
                    # increasse the motion counter
                    self.motionsCounter += 1
                    #self.log("+1 motions counter = {0}".format(self.motionsCounter))
                    # if it's not recording, check if there were enough motions
                    if not self.recording and self.motionsCounter > self.MOTIONS:
                        # save the recording started time
                        self.startedRecording = time.time()
                        # get current timestamp for filenames
                        self.timestamp = str(int(self.startedRecording))
                        # start recording to file, by switching from writing to stream to write to file
                        self.recording = True
                        rat.set_red_led(True)
                        self.camera.split_recording("/tmp/part1_{0}.h264".format(self.timestamp), splitter_port=1)
                        # and save the last 2 seconds from the stream
                        self.write_stream("/tmp/part0_{0}.h264".format(self.timestamp))
                self.MOTIONS_FIFO.task_done()
            now = time.time()
            # if there was no motion in the last 2 seconds, reset motion counter
            if (now-self.lastMotion) > self.MIN_LEN:
                #self.log("reset motions counter = {0}")
                self.motionsCounter = 0
            if self.recording:
                if (now-self.lastMotion) > self.POST_MOTION or (now-self.startedRecording) > self.MAX_LEN:
                    self.log("stop recording with {0}s since last motion, and length: {1}s".format((now-self.lastMotion), (now-self.startedRecording)))
                    self.recording = False
                    rat.set_red_led(False)
                    self.camera.split_recording(self.stream, splitter_port=1)
                    RECORDED_VIDEOS_FIFO.put(
                            ("part0_{0}.h264".format(self.timestamp), 
                            "part1_{0}.h264".format(self.timestamp), 
                            "done_{0}.mp4".format(self.timestamp)))



class DetectMotion(picamera.array.PiMotionAnalysis):
    def __init__(self, MOTIONS_FIFO, magnitude, camera, size):
        super(DetectMotion, self).__init__(camera, size)
        self.MOTIONS_FIFO = MOTIONS_FIFO
        self.MAGNITUDE = magnitude

    def analyse(self, a):
        _a = np.sqrt(np.square(a['x'].astype(np.float)) + np.square(a['y'].astype(np.float))).clip(0, 255).astype(np.uint8) # compute vector from both directions
        _motions = (_a > self.MAGNITUDE).sum()
        self.MOTIONS_FIFO.put(_motions, False) # non blocking


with picamera.PiCamera() as camera:
    log("got camera")
    stream = picamera.PiCameraCircularIO(camera, seconds=PRE_MOTION)

    md = DetectMotion(MOTIONS_FIFO, MAGNITUDE, camera, (640, 480))
    pt = ProcessingThread(camera, stream, MOTIONS_FIFO, RECORDED_VIDEOS_FIFO, log, settings)
    pt.daemon = True
    try:
        log("setting up cam")
        camera.resolution = (VIDEO_WIDTH, VIDEO_HEIGHT)
        camera.exposure_mode = 'night'
        camera.framerate = FPS
        camera.rotation = ROTATION
        if PREVIEW>0:
            camera.start_preview()
        log("start recording")
        camera.start_recording(stream,
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
                               motion_output=md,
                               splitter_port=2,
                               intra_period = 0,
                               resize=(640, 480))
        pt.start()
        rat.post_log("Camera Started")
        while True:
            try:
                (part1, part2, done) = RECORDED_VIDEOS_FIFO.get(False)
                if part1 and part2 and done:
                    #executionString = "avconv -loglevel quiet -y -r {0} -i /tmp/{1}.h264 -vcodec copy -r 30 /tmp/{1}.mp4 && rm /tmp/{1}.h264".format(__FPS, videoIDlist.pop(0))
                    executionString = "avconv -loglevel quiet -y -r {3} -i concat:/tmp/{0}\|/tmp/{1} -c copy -r {3} /tmp/_{2} && rm /tmp/{0} /tmp/{1} && mv /tmp/_{2} /tmp/{2}".format(part1, part2, done, FPS)
                    #executionString = "avconv -loglevel quiet -y -r {3} -i concat:/tmp/{0}\|/tmp/{1} -c copy -r {3} /tmp/_{2}".format(part1, part2, done, FPS)
                    log(executionString)
                    subprocess.Popen(executionString, shell=True)
            except Queue.Empty:
                pass
            
            if GPIO.input(17)==0 or int(time.time())%120==0:
                print "update camera"
                rat.set_green_led(True)
                rat.set_red_led(True)
                settings = rat.get_settings()
                FPS = int(settings['fps'])
                VIDEO_WIDTH = int(settings['video_width'])
                VIDEO_HEIGHT = int(settings['video_height'])
                MAGNITUDE = int(settings['magnitude'])
                PRE_MOTION = int(settings['pre_motion'])
                POST_MOTION = int(settings['post_motion'])
                ROTATION = int(settings['rotation'])
                PREVIEW = int(settings['preview'])
                DISABLE_RECORDING = int(settings['disable_recording'])
                pt.update_settings(settings)
                if PREVIEW>0:
                    try:
                        camera.start_preview()
                    except:
                        pass
                else:
                    try:
                        camera.stop_preview()
                    except:
                        pass
                camera.rotation = ROTATION
                camera.capture('/tmp/photo.jpg', 
                    use_video_port=True, 
                    splitter_port=0,
                    resize=(320, 180))
                rat.post_log("upload photo")
                rat.upload_photo()
                time.sleep(2)
                rat.set_green_led(False)
                rat.set_red_led(False)

            time.sleep(0.2)

    except KeyboardInterrupt:
        log("CTR+C Keyboard Interrupt")
    finally:
        rat.post_log(traceback.format_exc())
        pt.running=False

        camera.stop_preview()
        camera.stop_recording(splitter_port=2)
        camera.stop_recording(splitter_port=1)
        rat.set_red_led(False)
        rat.set_green_led(False)
        exit(0)
        #time.sleep(1)
        #exit(0)