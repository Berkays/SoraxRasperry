#!/bin/bash

/bin/bash /home/admin/usb-to-eth-route.sh
python3 /home/admin/modemCycle.py

sleep 10 # Wait Modem Manager

rfkill block 0
while true; do
    # Run mmcli -L and store output
    output=$(mmcli -L)
    # Check if output contains "Quectel"
    if echo "$output" | grep -q "Quectel"; then
        echo "Modem Found"
	echo "Configuring Modem..."
	modem_index=$(mmcli -L | grep -oP '/org/freedesktop/ModemManager1/Modem/\K\d+' | head -n 1)
	echo "$modem_index"
	sleep 3
	#mmcli -m any --command="AT+QCFG=\"usbnet\",1"
	#sleep 15
	mmcli -m any --command="AT+CSMS=1" # Enable SMS
	sleep 0.5
	mmcli -m any --command="AT+CPMS=\"MT\",\"MT\",\"MT\"" # Configure SMS Storage
	sleep 0.5
	mmcli -m any --command="AT+CNMI=2,0,0,0,0" # Disable SMS notifications
	sleep 0.5
	mmcli -m any --command="AT+CGDCONT=1,\"IP\",\"internet\""
	sleep 0.5
	mmcli -m any --command="AT+QICSGP=1,1,\"internet\",\"vodafone\",\"vodafone\",3"
	sleep 3
	echo "Modem configuration completed."
	systemctl start modemConnectScript.service
	/home/admin/listener_env/bin/python3 /home/admin/listener.py
	#while true; do
	#	echo "Press [CTRL+C] to stop.."
	#	sleep 1
	#done
    sleep 45
    reboot
    fi

    # Delay to avoid excessive CPU usage
    sleep 2
done
