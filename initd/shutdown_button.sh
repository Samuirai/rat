#! /bin/sh
### BEGIN INIT INFO
# Provides:          Shutdown Button
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
        echo "Starte Shutdown Button"
        /home/pi/rat/shutdown_button.py >> /tmp/log
        ;;
 
    stop)
 #Aktion wenn stop uebergeben wird
        echo "Stoppe Shutdown Button"
        killall shutdown_button.py
        ;;
 
    restart)
 #Aktion wenn restart uebergeben wird
        echo "Restarte Shutdown Button"
        killall shutdown_button.py
        /home/pi/rat/shutdown_button.py
        ;;
 *)
 #Standard Aktion wenn start|stop|restart nicht passen
 echo "(start|stop|restart)"
 ;;
esac
 
exit 0