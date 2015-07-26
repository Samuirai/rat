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

while True:
    print 17, GPIO.input(17)
    print 24, GPIO.input(24)
    sleep(0.1)