import RPi.GPIO as GPIO
from time import sleep
import wiringpi2 as wiringpi

Pi_rev = wiringpi.piBoardRev()
wiringpi.wiringPiSetupGpio() 
wiringpi.pinMode(18,2)
wiringpi.pwmWrite(18, 1024/2)
sleep(5)
wiringpi.pwmWrite(18, 0)

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.OUT, pull_up_down=GPIO.PUD_UP)

while True:
    print 17, GPIO.input(17)
    print 24, GPIO.input(24)
    sleep(0.1)

import RPi.GPIO as GPIO ## Import GPIO library
GPIO.setmode(GPIO.BCM) ## Use board pin numbering
GPIO.setup(22, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN) ## Setup GPIO Pin 22 to OUT
GPIO.output(22,True) ## Turn on GPIO pin 7