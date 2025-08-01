#!/bin/bash

mkdir -p /home/admin/logs/

journalctl --no-pager --since "1 week ago" > /home/admin/logs/journal_full.log
journalctl --no-pager -u modemManagerDebug.service > /home/admin/logs/modemManagerDebug.log
journalctl --no-pager -u modemConnectScript.service > /home/admin/logs/modemConnectScript.log
systemctl status modemManagerDebug > /home/admin/logs/modemManagerDebugStatus.log
systemctl status modemConnectScript > /home/admin/logs/modemConnectScript.log
ifconfig > /home/admin/logs/ifconfig.log
dmesg > /home/admin/logs/dmesg.log

journalctl --vacuum-size=1G