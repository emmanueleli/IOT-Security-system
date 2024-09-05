import RPi.GPIO as GPIO
import time
import serial

# Pin configuration
PIR_PIN = 17          # GPIO pin for PIR sensor
BUZZER_PIN = 18       # GPIO pin for buzzer
SERIAL_PORT = '/dev/serial0'  # Serial port for GSM module
BAUD_RATE = 9600      # Baud rate for GSM module communication

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Initialize Serial for GSM
gsm = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

def send_sms(phone_number, message):
    """Send SMS using the GSM module."""
    try:
        # Set SMS mode to text mode
        gsm.write(b'AT+CMGF=1\r')
        time.sleep(1)
        # Set the recipient phone number
        gsm.write(('AT+CMGS="{}"\r'.format(phone_number)).encode())
        time.sleep(1)
        # Write the message
        gsm.write((message + "\r").encode())
        time.sleep(1)
        # Send the message
        gsm.write(bytes([26]))  # ASCII code of CTRL+Z
        time.sleep(3)
        print("SMS sent successfully")
    except Exception as e:
        print("Failed to send SMS:", e)

def main():
    print("PIR Motion Sensor and GSM Test (CTRL+C to exit)")
    time.sleep(2)  # Allow PIR sensor to settle
    print("Ready")

    phone_number = +233242013172  # Replace with your phone number
    sms_message = "Motion detected at your location!"

    try:
        while True:
            if GPIO.input(PIR_PIN):
                print("Motion Detected!")
                GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn on the buzzer
                send_sms(phone_number, sms_message)  # Send SMS notification
                time.sleep(1)  # Keep the buzzer on for 1 second
                GPIO.output(BUZZER_PIN, GPIO.LOW)   # Turn off the buzzer
            else:
                GPIO.output(BUZZER_PIN, GPIO.LOW)  # Ensure buzzer is off
            time.sleep(0.1)  # Small delay to prevent excessive CPU usage

    except KeyboardInterrupt:
        print("Program interrupted")

    finally:
        GPIO.cleanup()  # Clean up GPIO settings
        gsm.close()  # Close serial connection

if __name__ == "__main__":
    main()
