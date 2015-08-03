sudo ln -s /home/pi/rat/initd/shutdown_button.sh /etc/init.d/shutdown_button.sh
sudo ln -s /home/pi/rat/initd/light_control.sh /etc/init.d/light_control.sh
sudo ln -s /home/pi/rat/initd/uploader.sh /etc/init.d/uploader.sh
sudo ln -s /home/pi/rat/initd/camera.sh /etc/init.d/camera.sh
sudo ln -s /home/pi/rat/initd/watchdog.sh /etc/init.d/watchdog.sh
sudo update-rc.d camera.sh defaults
sudo update-rc.d light_control.sh defaults
sudo update-rc.d uploader.sh defaults
sudo update-rc.d watchdog.sh defaults
sudo update-rc.d shutdown_button.sh defaults