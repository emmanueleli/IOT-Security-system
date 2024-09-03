import RPi.GPIO as GPIO
import time

# Setup
PIR_PIN = 17  # GPIO pin for PIR sensor
BUZZER_PIN = 18  # GPIO pin for Buzzer

GPIO.setmode(GPIO.BCM)  # Use Broadcom pin-numbering scheme
GPIO.setup(PIR_PIN, GPIO.IN)  # Set PIR_PIN as input
GPIO.setup(BUZZER_PIN, GPIO.OUT)  # Set BUZZER_PIN as output

try:
    print("PIR Motion Sensor Test (CTRL+C to exit)")
    time.sleep(2)  # Allow PIR sensor to settle
    print("Ready")

    while True:
        if GPIO.input(PIR_PIN):
            print("Motion Detected!")
            GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn on the buzzer
            time.sleep(1)  # Keep the buzzer on for 1 second
        else:
            GPIO.output(BUZZER_PIN, GPIO.LOW)  # Turn off the buzzer
        time.sleep(0.1)  # Small delay to prevent excessive CPU usage

except KeyboardInterrupt:
    print("Quit")
finally:
    GPIO.cleanup()  # Clean up GPIO settings
