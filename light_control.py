import RPi.GPIO as GPIO
from time import sleep
import wiringpi2 as wiringpi
import subprocess

Pi_rev = wiringpi.piBoardRev()
wiringpi.wiringPiSetupGpio() 
wiringpi.pinMode(18,2)

def set_leds(pwm):
    wiringpi.pwmWrite(18, pwm) # duty cycle between 0 and 1024. 0 = off, 1024 = fully on  

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    sleep(1.0)
    if not GPIO.input(24):
        set_leds(1024/2) # 50%
    else:
        set_leds(0) # disable leds
    if not GPIO.input(17):
        subprocess.Popen("shutdown -P -h now \"shutdown by button\"", shell=True)
        exit("shutting down")