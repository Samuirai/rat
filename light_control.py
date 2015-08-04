#!/usr/bin/python
import time
import wiringpi2 as wiringpi
import RPi.GPIO as GPIO
import subprocess
from server import sun
import rat
import time

time.sleep(10)


GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
Pi_rev = wiringpi.piBoardRev()
wiringpi.wiringPiSetupGpio() 
wiringpi.pinMode(18,2)

rat.post_log("Light Control Started")

while True:
    settings = rat.get_settings()
    # only turn LEDs on if its getting dark, and recording enabled
    if settings:
        if sun.is_it_dark() and GPIO.input(24)==0 and int(settings['disable_recording'])==0:
            ir_led = float(settings['ir_led'])/100.0
            rat.post_log("It's night. Set LEDs to: {0}%%".format(ir_led))
            wiringpi.pwmWrite(18, int(1024*ir_led))
        elif GPIO.input(24)==0 and int(settings['disable_recording'])==0:
            ir_led = float(settings['ir_led_day'])/100.0
            rat.post_log("It's day. Set LEDs to: {0}%%".format(ir_led))
            wiringpi.pwmWrite(18, int(1024*ir_led))
        else:
            rat.post_log("LEDs disabled")
            wiringpi.pwmWrite(18, 0)

    time.sleep(30.0)