#! /bin/sh
### BEGIN INIT INFO
# Provides:          LED Light Control
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
        echo "Starte LED Light Control"
        /home/pi/rat/light_control.py
        ;;
 
    stop)
 #Aktion wenn stop uebergeben wird
        echo "Stoppe LED Light Control"
        killall light_control.py
        ;;
 
    restart)
 #Aktion wenn restart uebergeben wird
        echo "Restarte LED Light Control"
        killall light_control.py
        /home/pi/rat/light_control.py
        ;;
 *)
 #Standard Aktion wenn start|stop|restart nicht passen
 echo "(start|stop|restart)"
 ;;
esac
 
exit 0