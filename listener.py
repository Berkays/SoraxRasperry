# AT COMMANDS
# Turn OFF
# AT+QPOWD

# Return IMEI
# AT+GSN

# Set SIM PIN
# AT+CPIN=1234

# Get SIM STATUS
# AT+COPS?
# +COPS: 0,0,"CHINA MOBILE",7

# Enable string errors
# AT+CMEE=2 

# Query the status of (U)SIM card.
# AT+CLCK="SC",2 
# +CLCK: 0 SIM card is unlocked (OFF).
# OK
# AT+CLCK="SC",1,"1234" //Lock (U)SIM card, and the password is 1234.
# OK
# Query the status of (U)SIM card
# AT+CLCK="SC",2 
# +CLCK: 1 //The (U)SIM card is locked (ON).
# OK
# AT+CLCK="SC",0,"1234" //Unlock (U)SIM card.
# OK

# AT+QSIMSTAT (U)SIM Card Insertion Status Report

# Status Commands
# AT+CEREG - EPS Network Registration Status
# AT+CSQ Signal Quality Report
# AT+CREG?
# AT+CGREG?

# Check Network Status:
# AT+CEREG?
# +CEREG: 0,1
# OK
# AT+CSQ
# +CSQ: 20,99
# OK
# AT+QENG="servingcell"
# +QENG: "servingcell","NOCONN","LTE",...
# OK

# Notes
# Replace "internet" with your network’s APN and "1234" with your SIM’s barring password.

import sys, subprocess, signal
import time
import logging
from datetime import datetime, timedelta
import pytz
import re
import RPi.GPIO as GPIO
from smspdudecoder.easy import read_incoming_sms
import socket

logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger()

DVR_RELAY_PIN = 17  # Relay
EXPIRATION_LENGTH = 15 # Minutes

modemIndex = -1
relayStatus = False

def sigint_handler(signal, frame):
    print('Interrupted')
    GPIO.setup(DVR_RELAY_PIN, GPIO.IN)
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def get_first_modem_index():
    global modemIndex
    try:
        # Run mmcli -m to list all modems
        logger.info("Finding modem instance...")
        result = subprocess.run(['mmcli', '-L'], capture_output=True, text=True, check=True)
        output = result.stdout

        logger.info(output)
        # Extract modem indices using regex
        modem_indices = re.findall(r'/org/freedesktop/ModemManager1/Modem/(\d+)', output)
        
        if not modem_indices:
            modemIndex = -1
            return

        # Return the first modem index
        modemIndex = modem_indices[0]

    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing mmcli: {e}")
        modemIndex = -1
        return

get_first_modem_index()

if(modemIndex == -1):
    logger.error("No Modem Found")
    time.sleep(1)

def run_at_command(command):
    try:
        logging.info(f"Running AT Command: {command}")
        cmd = f'mmcli -m any --command="{command}"'
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
    
def reset_pi():
    try:
        logging.info(f"Running PI Reset")
        cmd = f'reboot now'
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            universal_newlines=True, 
            shell=True
        )
    except Exception as exc:
        logging.error(f"Process error: {exc}")
        return ""
    
def send_sms(number, text):
    try:
        logging.info(f"Creating sms: {text}")
        cmd = f'mmcli -m any --messaging-create-sms="text=\'{text}\',number=\'{number}\'"'
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            universal_newlines=True, 
            shell=True
        )

        indexText = result.stdout
        # Use regex to extract the number after /SMS/
        pattern = r"/SMS/(\d+)"
        match = re.search(pattern, indexText)

        if match:
            sms_index = match.group(1)
            logging.info(f"SMS Index: {sms_index}")
            logging.info(f"Sending sms: {text}")
            cmd = f'mmcli -s {sms_index} --send'
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                universal_newlines=True, 
                shell=True
            )
            logging.info(result.stdout)
        else:
            logging.info("No SMS index found")
    except Exception as exc:
        logging.error(f"Process error: {exc}")

def internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        logging.info(ex)
        return False
    
def check_CPU_temp():
    temp = None
    err, msg = subprocess.getstatusoutput('vcgencmd measure_temp')
    if not err:
        m = re.search(r'-?\d\.?\d*', msg)
        try:
            temp = float(m.group())
        except ValueError:
            pass
    return temp, msg

def get_sms_cmd(index):
    try:
        logging.info(f"List SMS Command")
        cmd = f'mmcli -m any --sms {index}'
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
    
def list_sms_cmd():
    try:
        logging.info(f"List SMS Command")
        cmd = f'mmcli -m any --messaging-list-sms'
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            universal_newlines=True, 
            shell=True
        )
        pattern = r'SMS/(\d+)'
        indices = re.findall(pattern, result.stdout)
        # Convert to integers
        indices = [int(index) for index in indices]
        patterns = {
            'number': r'number:\s*(\+\d+)',
            'text': r'text:\s*(\S+)',
            'timestamp': r'timestamp:\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2})'
        }

        sms_list = []
        for i in indices:
            sms_raw_data = get_sms_cmd(i)
            sms_data = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, sms_raw_data)
                if match:
                    sms_data[key] = match.group(1)
            if 'timestamp' in sms_data:
                sms_data['timestamp'] = datetime.fromisoformat(sms_data['timestamp'])
                sms_data['date'] = sms_data['timestamp']
            sms_list.append(sms_data)
            print(sms_data)
        return sms_list
    except Exception as exc:
        logging.error(f"Process error: {exc}")
        return []
    
def delete_sms_store():
    try:
        logging.info(f"Delete SMS Store")
        cmd = f'mmcli -m any --messaging-list-sms'
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            universal_newlines=True, 
            shell=True
        )
        pattern = r'SMS/(\d+)'
        indices = re.findall(pattern, result.stdout)

        for i in indices:
            cmd2 = f'mmcli -m any --messaging-delete-sms {i}'
            result = subprocess.run(
                cmd2,
                capture_output=True,
                text=True,
                check=True,
                universal_newlines=True, 
                shell=True
            )
            time.sleep(0.3)
        
    except Exception as exc:
        logging.error(f"Process error: {exc}")
        return []

# Configure GPIO
logger.info("Configuring GPIO...")
GPIO.setmode(GPIO.BCM)
GPIO.setup(DVR_RELAY_PIN, GPIO.OUT)
logger.info("GPIO Configured.")

# Test Trigger
time.sleep(0.5)
GPIO.output(DVR_RELAY_PIN, GPIO.HIGH)  # Turn on
time.sleep(1)
GPIO.output(DVR_RELAY_PIN, GPIO.LOW)  # Turn off
time.sleep(1)

def configure_module():
    # run_at_command("AT+CMGD=1,4") # Delete message store
    pass

def extract_pdu_messages(text):
    if(text is None or text == ""):
        return []
    pdu_messages = []
    for line in text.split('\n'):
        try:
            decoded_msg = read_incoming_sms(line)
            pdu_messages.append(decoded_msg)
        except:
            continue
    return pdu_messages

def has_minutes_passed(dt, minutes):
    current_time = datetime.now(dt.tzinfo)
    time_diff = current_time - dt
    return time_diff >= timedelta(minutes=minutes)

try:
    configure_module()
    logger.info("Waiting for SMS...")

    while True:
        # logger.info("Listing messages...")
        # response1 = run_at_command(f"AT+CMGL=0").strip() # Get unread messages
        # response2 = run_at_command(f"AT+CMGL=1").strip() # Get unread messages
        # messages1 = extract_pdu_messages(response1)
        # messages2 = extract_pdu_messages(response2)
        # logging.info(response1)
        messages = list_sms_cmd()
        if(messages is None or len(messages) == 0):
            messages = []
            # logger.info("No message.")
        else:
            logger.info(f"{len(messages)} messages.")
            relayToggled = False
            validCommand = False
            # messages.reverse()
            for msg in messages:
                logger.info(msg)
                if(has_minutes_passed(msg['date'], 10)):
                    logger.info("SMS Expired.")
                    continue 
                if("SORAX_STATUS" in msg['text'].upper()):
                    validCommand = True
                    number = msg['number']
                    drvStatus = 1 if relayStatus is True else 0
                    hasInternet = 1 if internet() is True else 0
                    temp, msg = check_CPU_temp()
                    text = f'DVR:{drvStatus},NET:{hasInternet}, CPU:{temp}C'
                    send_sms(number ,text)
                    time.sleep(2)
                    continue
                if("SORAX_RESET" in msg['text'].upper()):
                    delete_sms_store()
                    time.sleep(1)
                    reset_pi()
                    time.sleep(2)
                    continue
                if(relayToggled is True):
                    continue
                if("SORAX_ON" in msg['text'].upper()):
                    validCommand = True
                    GPIO.output(DVR_RELAY_PIN, GPIO.HIGH)  # Turn on
                    logger.info("Relay:ON")
                    relayToggled = True
                    relayStatus = True
                    continue
                elif("SORAX_OFF" in msg['text'].upper()):
                    validCommand = True
                    GPIO.output(DVR_RELAY_PIN, GPIO.LOW)  # Turn off
                    logger.info("Relay:OFF")
                    relayToggled = True
                    relayStatus = False
                    continue
            if(validCommand == True):
                # run_at_command("AT+CMGD=1,4") # Delete Read Messages
                delete_sms_store()
        time.sleep(5)
        # get_first_modem_index()

except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()