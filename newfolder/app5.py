from flask import Flask, render_template, Response, redirect, url_for, request
from gpiozero import MotionSensor, Buzzer
from time import sleep
from datetime import datetime
import cv2

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key for sessions

# Initialize Raspberry Pi components
pir = MotionSensor(17)  # PIR sensor connected to GPIO 17
buzzer = Buzzer(18)     # Buzzer connected to GPIO 18

# Initialize variables for alerts
alerts = []

@app.route('/')
def index():
    """Route to the homepage."""
    return render_template('index.html', alerts=alerts)

@app.route('/video_feed')
def video_feed():
    """Route to handle video streaming."""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start')
def start_security():
    """Start security monitoring."""
    pir.when_motion = motion_detected
    return "Security monitoring started"

@app.route('/stop')
def stop_security():
    """Stop security monitoring."""
    pir.when_motion = None
    return "Security monitoring stopped"

def gen_frames():
    """Capture and yield frames from the camera using OpenCV."""
    cap = cv2.VideoCapture(0)  # Use 0 for the default camera
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Encode frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield frame as a byte stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def store_alert(alert_message):
    """Store an alert locally."""
    alerts.append(alert_message)

def motion_detected():
    """Handle motion detection."""
    print("Motion detected!")
    buzzer.on()
    alert_message = f"Motion detected at {datetime.now()}"
    store_alert(alert_message)  # Store the alert locally
    sleep(5)
    buzzer.off()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
