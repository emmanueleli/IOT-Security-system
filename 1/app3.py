from flask import Flask, render_template, Response, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from gpiozero import MotionSensor, Buzzer
from time import sleep
from datetime import datetime
import cv2

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "12345"  # Replace with a strong secret key for sessions

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Initialize Raspberry Pi components
pir = MotionSensor(17)  # PIR sensor connected to GPIO 17
buzzer = Buzzer(18)     # Buzzer connected to GPIO 18

# Initialize variables for alerts
alerts = []

# User class for authentication
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Sample user data
users = {'admin': User(1, 'admin', 'password')}  # Replace with your own users

@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Invalid credentials!")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():
    """Route to the homepage."""
    return render_template('index.html', alerts=alerts)

@app.route('/capture_image')
def capture_image():
    """Capture image from the camera."""
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    if ret:
        image_path = f'static/intruder_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        cv2.imwrite(image_path, frame)
        camera.release()
        return image_path
    else:
        camera.release()
        return None

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



def motion_detected():
    """Handle motion detection."""
    print("Motion detected!")
    buzzer.on()
    alert_message = f"Motion detected at {datetime.now()}"
    #store_alert(alert_message)  # Store the alert locally
    sleep(5)
    buzzer.off()

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
