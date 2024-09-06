from flask import Flask, render_template, Response, redirect, url_for
from gpiozero import MotionSensor, Buzzer
import cv2
import serial
from time import sleep
from datetime import datetime
import os
import subprocess


# Initialize Flask app
app = Flask(__name__)

# Initialize Raspberry Pi components
pir = MotionSensor(17)   # PIR sensor connected to GPIO 17
buzzer = Buzzer(18)      # Buzzer connected to GPIO 18
gsm = serial.Serial('/dev/serial0', 9600, timeout=1)  # GSM module on serial port

# Initialize variables
monitoring = False
alerts = []
latest_image_path = None  # To keep track of the latest captured image

def send_sms(phone_number, message):
    """Send SMS using the GSM module."""
    gsm.write(b'AT+CMGF=1\r')  # Set SMS mode to text
    sleep(1)
    gsm.write(f'AT+CMGS="{phone_number}"\r'.encode())
    sleep(1)
    gsm.write(f'{message}\x1A'.encode())  # CTRL+Z to send
    sleep(1)

def capture_image():
    global latest_image_path

    # Wait for 2 seconds before capturing the image (if needed)
    sleep(2)

    # Define the image name and path
    image_name = f'intruder_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
    image_path = os.path.join('static', image_name)

    # Capture image using libcamera-still command
    command = f"libcamera-still -o {image_path}"
    process = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Check if the command was successful
    if process.returncode == 0:
        latest_image_path = image_name  # Update the latest image path
        return image_path
    else:
        print("Error capturing image:", process.stderr)
        return None

# Example usage
image_path = capture_image()
if image_path:
    print(f"Image saved at: {image_path}")
else:
    print("Failed to capture image.")

def motion_detected():
    """Handle motion detection."""
    print("Motion detected!")
    buzzer.on()
    sleep(0.5)
    buzzer.off()
    sleep(0.5)
    buzzer.on()
    sleep(1)
    buzzer.off()
    
    image_path = capture_image()
    if image_path:
        alert_message = f"Motion detected at {datetime.now()}! Picture saved at {image_path}"
        alerts.append(alert_message)
        send_sms('+233242013172', f"Intruder detected! Check: http://10.10.80.154:5000/{image_path}")
        print(alert_message)

@app.route('/')
def index():
    """Homepage with controls."""
    return render_template('index.html', alerts=alerts, latest_image=latest_image_path)

@app.route('/start')
def start_monitoring():
    """Start monitoring."""
    global monitoring
    monitoring = True
    pir.when_motion = motion_detected
    return redirect(url_for('index'))

@app.route('/stop')
def stop_monitoring():
    """Stop monitoring."""
    global monitoring
    monitoring = False
    pir.when_motion = None
    return redirect(url_for('index'))

@app.route('/alert_police')
def alert_police():
    """Simulate alerting the police."""
    # Add logic to alert police (e.g., send an SMS or email)
    alerts.append("Police alerted!")
    send_sms('+233508756598', "Intruder detected! Immediate assistance required!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
