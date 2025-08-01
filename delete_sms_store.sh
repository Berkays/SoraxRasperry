#!/bin/bash

for i in $(seq 1 255);
do
    mmcli -m any --messaging-delete-sms $i
    sleep 0.1
done