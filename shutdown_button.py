import RPi.GPIO as GPIO
import time
import subprocess
import sys
import rat

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

RED_LED = True

pressed = False

while True:
    if not pressed and GPIO.input(17)==0:
        pressed = time.time()
    elif pressed and GPIO.input(17)==0:
        #print "pressed for {0}".format(time.time()-pressed)
        counter = int((time.time()-pressed)*10)
        inv_counter = 50-counter
        if inv_counter>=10:
            if counter%(inv_counter/10) == 0:
                RED_LED = not RED_LED
                rat.set_red_led(RED_LED)
        elif inv_counter<10:
            RED_LED = True
            rat.set_red_led(RED_LED)
        if counter>60:
            rat.set_green_led(True)
            p = subprocess.Popen("shutdown -P -h now", shell=True)
            p.communicate()
            exit(0)
    elif pressed and GPIO.input(17)==1:
        RED_LED = False
        rat.set_red_led(RED_LED)
    else:
        pressed = False
        RED_LED = False
    time.sleep(0.1)
