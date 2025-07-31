import logging
import RPi.GPIO as GPIO
import time

logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger()

MODEM_PWR_PIN = 26  # Relay

# Configure GPIO
logger.info("Configuring GPIO...")
GPIO.setmode(GPIO.BCM)
GPIO.setup(MODEM_PWR_PIN, GPIO.OUT)
logger.info("GPIO Configured.")

time.sleep(1)
GPIO.output(MODEM_PWR_PIN, GPIO.HIGH)  # Cut Power
time.sleep(1)
GPIO.output(MODEM_PWR_PIN, GPIO.LOW)  # Provide Power

GPIO.cleanup()
logger.info("MODEM POWER CYCLE")
