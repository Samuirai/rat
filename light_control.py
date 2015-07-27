import time
import wiringpi2 as wiringpi
import RPi.GPIO as GPIO
import subprocess
import sun
import rat
import time

GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
Pi_rev = wiringpi.piBoardRev()
wiringpi.wiringPiSetupGpio() 
wiringpi.pinMode(18,2)

def is_it_dark():
    sunrise, sunset = sun.get_times()
    now = time.time()
    if now > sunset or now < sunrise:
        return True
    return False

while True:
    # only turn LEDs on if its getting dark, and recording enabled
    if is_it_dark() and GPIO.input(24)==1:
        ir_led = float(rat.get_settings()['ir_led'])/100.0
        rat.post_log("IT'S NIGHT! set LEDs to: {0}%%".format(ir_led))
        wiringpi.pwmWrite(18, int(1024*ir_led))
    else:
        wiringpi.pwmWrite(18, 0)
    time.sleep(30.0)