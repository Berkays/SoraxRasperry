#!/bin/bash

#systemctl stop dnsmasq
#systemctl disable NetworkManager ModemManager
#systemctl stop NetworkManager ModemManager
sleep 5
systemctl stop ModemManager
/usr/sbin/ModemManager --debug
