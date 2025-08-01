#!/bin/bash

tar cvzf /home/admin/log.tar.gz -C /home/admin/logs .

timestamp=$(date +%s)

curl -X 'POST' \
  "https://filebin.net/sorax_log_bin/log_\"$timestamp\".tar.gz" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/octet-stream' \
  --data-binary '@/home/admin/log.tar.gz'


tar cvzf /home/admin/runlog.tar.gz -C /run/log/ .

curl -X 'POST' \
  "https://filebin.net/sorax_log_bin/runlog_\"$timestamp\".tar.gz" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/octet-stream' \
  --data-binary '@/home/admin/runlog.tar.gz'