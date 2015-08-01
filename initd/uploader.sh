#! /bin/sh
### BEGIN INIT INFO
# Provides:          Youtube Upload Service
# Required-Start:    
# Required-Stop:     
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Starts & Stops My Programm
# Description:       Starts & Stops My Programm
### END INIT INFO
 
#Switch case fuer den ersten Parameter
case "$1" in
    start)
 #Aktion wenn start uebergeben wird
        echo "Starte Youtube Upload Service"
        nohup /home/pi/rat/uploader.py >> /tmp/log &
        ;;
 
    stop)
 #Aktion wenn stop uebergeben wird
        echo "Stoppe Youtube Upload Service"
        killall uploader.py
        ;;
 
    restart)
 #Aktion wenn restart uebergeben wird
        echo "Restarte Youtube Upload Service"
        killall uploader.py
        nohup /home/pi/rat/uploader.py >> /tmp/log &
        ;;
 *)
 #Standard Aktion wenn start|stop|restart nicht passen
 echo "(start|stop|restart)"
 ;;
esac
 
exit 0