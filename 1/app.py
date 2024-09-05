from flask import Flask, render_template, jsonify
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
latest_image = None
captured_images = []  # List to hold all captured images

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
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    if ret:
        global latest_image
        image_filename = f'intruder_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        image_path = f'static/{image_filename}'
        cv2.imwrite(image_path, frame)
        captured_images.append(image_filename)
        camera.release()
        latest_image = image_filename
        return image_filename
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
    
    image_filename = capture_image()
    if image_filename:
        alert_message = f"Motion detected at {datetime.now()}! Picture saved as {image_filename}"
        alerts.append(alert_message)
        send_sms('+233242013172', f"Intruder detected! Check: http://10.10.80.154:5000/static/{image_filename}")
        print(alert_message)

@app.route('/')
def index():
    """Homepage with controls and alerts."""
    return render_template('index.html', alerts=alerts, latest_image=latest_image, captured_images=captured_images)

@app.route('/start')
def start_monitoring():
    """Start monitoring."""
    global monitoring
    monitoring = True
    pir.when_motion = motion_detected
    return jsonify({"status": "Monitoring started"})

@app.route('/stop')
def stop_monitoring():
    """Stop monitoring."""
    global monitoring
    monitoring = False
    pir.when_motion = None
    return jsonify({"status": "Monitoring stopped"})

@app.route('/alert_police')
def alert_police():
    """Simulate alerting the police."""
    alerts.append("Police alerted!")
    send_sms('+233508756598', "Intruder detected! Immediate assistance required!")
    return jsonify({"status": "Police alerted"})

@app.route('/alerts')
def get_alerts():
    """Endpoint to fetch alerts dynamically."""
    return jsonify(alerts=alerts, latest_image=latest_image, captured_images=captured_images)

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(host='0.0.0.0', port=5000, debug=True)
