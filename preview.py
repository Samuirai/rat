import picamera
import time
with picamera.PiCamera() as camera:
    try:
        camera.resolution = (1296, 730)
        camera.exposure_mode = 'night'
        camera.framerate = 20
        camera.start_preview()
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print "stopping"
    finally:
        print "finally"
        camera.stop_preview()

