import socket
import sys, subprocess
import time
import socket

def check_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        return False
    
def reset_pi(logger):
    try:
        logger.info(f"Running PI Reset")
        cmd = f'reboot'
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            universal_newlines=True, 
            shell=True
        )
    except Exception as exc:
        logger.error(f"Process error: {exc}")
        return ""
    
def simple_connect(logger):
    logger.info(f"Running connect command...")
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
    
def simple_disconnect(logger):
    try:
        logger.info(f"Running disconnect command...")
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
        logger.error(f"Process error: {exc}")
        return ""
    
def dhcp_release(logger):
    try:
        logger.info(f"Running dhclient...")
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
        logger.error(f"Process error: {exc}")
        return ""
    
def dhcp_lease(logger):
    try:
        logger.info(f"Running dhclient...")
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
        logger.error(f"Process error: {exc}")
        return ""
    
def git_fetch(logger):
    try:
        logger.info(f"Running GIT Fetch")
        cmd = f'/home/admin/fetch_source.sh'
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
        logger.error(f"Process error: {exc}")
        return ""
    
def git_copy_schedule(logger):
    try:
        logger.info(f"Running GIT Fetch")
        cmd = f'/home/admin/schedule_copy_source.sh'
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
        logger.error(f"Process error: {exc}")
        return ""
    
def create_logs(logger):
    try:
        logger.info(f"Running Create Logs")
        cmd = f'/home/admin/create_log.sh'
        subprocess.run(cmd, universal_newlines=True, shell=True)
    except Exception as exc:
        logger.error(f"Process error: {exc}")
        return ""

def upload_logs(logger):
    try:
        logger.info(f"Running Log Send")
        cmd = f'/home/admin/upload_log.sh'
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
        logger.error(f"Process error: {exc}")
        return ""

def parse_external_command(logger, msg, send_sms, delete_msg_store):
    try:
        number = msg['number']
        msgContent = msg['text'].upper()
        if("SORAX_FONK_RESET" in msgContent):
            delete_msg_store()
            send_sms(number , 'OK')
            time.sleep(3)
            reset_pi(logger)
            return True
        
        if("SORAX_FONK_LOG" in msgContent):
            if(check_internet() is False):
                send_sms(number, 'NET:0')
                return True

            create_logs(logger)
            time.sleep(1)
            upload_logs(logger)
            time.sleep(2)

            send_sms(number, 'OK')
            return True
        
        if("SORAX_FONK_FETCH" in msgContent):
            git_fetch(logger)
            send_sms(number , 'OK')
            return True
        
        if("SORAX_FONK_UPDATE" in msgContent):
            git_copy_schedule(logger)
            send_sms(number , 'OK')
            return True
        
        if("SORAX_FONK_DHCP" in msgContent):
            dhcp_release(logger)
            time.sleep(20)
            dhcp_lease(logger)
            send_sms(number , 'OK')
            return True
        
        if("SORAX_FONK_CONNECT" in msgContent):
            simple_connect(logger)
            send_sms(number , 'OK')
            return True
        
        if("SORAX_FONK_DISCONNECT" in msgContent):
            simple_disconnect(logger)
            send_sms(number , 'OK')
            return True
        return False
    
    except Exception as exc:
        logger.error("EXTRA_FUNC_ERROR")
        logger.error(exc)
        send_sms(number , 'FAIL')
        return False