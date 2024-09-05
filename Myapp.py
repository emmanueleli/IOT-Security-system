from flask import Flask, render_template, Response, redirect, url_for
from gpiozero import MotionSensor, Buzzer
import cv2
import serial
from time import sleep
from datetime import datetime
import os

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
    """Capture image from the camera."""
    global latest_image_path
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    if ret:
        # Save image to the static directory
        image_name = f'intruder_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        image_path = os.path.join('static', image_name)
        cv2.imwrite(image_path, frame)
        latest_image_path = image_name  # Update the latest image path
        camera.release()
        return image_path
    else:
        camera.release()
        return None

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
