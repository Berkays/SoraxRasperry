1. Copy original service + script
2. Download logs
3. Install git
4. Copy create.log fetch_source.sh fonks.py listener.py runonce.sh schedule_copy_source.sh upload_log.sh runonce.service to raspberry
5. Copy runonce.service to /etc/systemd/
6. Chmod +x fetch_source.sh runonce.sh schedule_copy_source.sh upload_log.sh
7. Create git ssh keygen
   ssh-keygen -t ed25519 -C "your_email@example.com"
   cat id_ed25519.pub
8. echo "0" > update.txt
9. Test git credentials

OPTIONAL Install watchdog
https://xavier.arnaus.net/blog/watchdog-service-for-raspberry-pi-machines
