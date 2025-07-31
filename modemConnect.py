import sys, subprocess, signal
import time
import logging
import re

logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger()

def simple_connect():
    logging.info(f"Running connect command...")
    cmd = f'mmcli -m any --timeout=15 --simple-connect="apn=internet,user=vodafone,password=vodafone"'
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
        universal_newlines=True, 
        shell=True
    )
    return result.stdout
    
def simple_disconnect():
    try:
        logging.info(f"Running disconnect command...")
        cmd = f'mmcli -m any --simple-disconnect'
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            universal_newlines=True, 
            shell=True
        )
        return result.stdout
    except Exception as exc:
        logging.error(f"Process error: {exc}")
        return ""
    
def dhcp_release():
    try:
        logging.info(f"Running dhclient...")
        cmd = f'dhclient -v -r'
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            universal_newlines=True, 
            shell=True
        )
        return result.stdout
    except Exception as exc:
        logging.error(f"Process error: {exc}")
        return ""
    
def dhcp_lease():
    try:
        logging.info(f"Running dhclient...")
        cmd = f'dhclient usb0 -v'
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            universal_newlines=True, 
            shell=True
        )
        return result.stdout
    except Exception as exc:
        logging.error(f"Process error: {exc}")
        return ""
    
while True:
    try:
        response = simple_connect()

        if('error' in response or 'timeout' in response or 'couldn\'t' in response):
            simple_disconnect()
            time.sleep(5)
            continue
    except:
        simple_disconnect()
        time.sleep(5)
        continue
    logging.info("Connected to station...")
    # Run dhclient and exit
    time.sleep(20)
    logging.info(dhcp_release())
    time.sleep(10)
    logging.info(dhcp_lease())
    sys.exit(0)
    break
    