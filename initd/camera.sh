#! /bin/sh
### BEGIN INIT INFO
# Provides:          Pi Camera
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
        echo "Starte Pi Camera service"
        /home/pi/rat/camera.py
        ;;
 
    stop)
 #Aktion wenn stop uebergeben wird
        echo "Stoppe Pi Camera service"
        killall camera.py
        ;;
 
    restart)
 #Aktion wenn restart uebergeben wird
        echo "Restarte Pi Camera service"
        killall camera.py
        /home/pi/rat/camera.py
        ;;
 *)
 #Standard Aktion wenn start|stop|restart nicht passen
 echo "(start|stop|restart)"
 ;;
esac
 
exit 0