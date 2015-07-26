import picamera
with picamera.PiCamera() as camera:
    camera.resolution = (1920, 1080)
    camera.exposure_mode = 'night'
    camera.framerate = 30
    camera.start_preview()
    except KeyboardInterrupt:
        print "stopping"
    finally:
        print "finally"
        camera.stop_preview()