import RPi.GPIO as GPIO
import time
import wiringpi2 as wiringpi
import subprocess
import sys

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)


RED_LED = True

pressed = False

while True:
    if not pressed and GPIO.input(17)==0:
        pressed = time.time()
    elif pressed and GPIO.input(17)==0:
        print "pressed for {0}".format(time.time()-pressed)
        counter = int((time.time()-pressed)*10)
        inv_counter = 50-counter
        if inv_counter>=10:
            if counter%(inv_counter/10) == 0:
                RED_LED = not RED_LED
        elif inv_counter<10:
            RED_LED = True
        if counter>60:
            GPIO.output(22,True)
            subprocess.Popen("shutdown -P -h now", shell=True)
            exit(0)
    else:
        pressed = False
        RED_LED = False
    GPIO.output(23,RED_LED)
    time.sleep(0.1)
