from flask import Flask, render_template, Response, redirect, url_for
from gpiozero import MotionSensor, Buzzer
from picamera import PiCamera
import serial
from time import sleep
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Initialize Raspberry Pi components
pir = MotionSensor(17)   # PIR sensor connected to GPIO 17
buzzer = Buzzer(18)      # Buzzer connected to GPIO 18
gsm = serial.Serial('/dev/serial0', 9600, timeout=1)  # GSM module on serial port
camera = PiCamera()
camera.resolution = (640, 480)

# Initialize variables
monitoring = False
alerts = []
latest_image = None  # To store the path of the latest image captured

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
    global latest_image
    image_path = f'static/intruder_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
    camera.capture(image_path)
    latest_image = image_path
    return image_path

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
    alert_message = f"Motion detected at {datetime.now()}! Picture saved at {image_path}"
    alerts.append(alert_message)
    send_sms("+233242013172", f"Intruder detected! Check: http://10.10.80.154:5000/{image_path}")
    print(alert_message)

@app.route('/')
def index():
    """Homepage with controls."""
    return render_template('index2.html', alerts=alerts, latest_image=latest_image)

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
    alerts.append("Police alerted!")
    send_sms("+233508756598", "Intruder detected! Immediate assistance required!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
