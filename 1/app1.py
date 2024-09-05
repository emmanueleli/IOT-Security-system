from flask import Flask, render_template, Response, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from gpiozero import MotionSensor, Buzzer
from picamera import PiCamera
from time import sleep
from datetime import datetime
#import cv2
import boto3
from botocore.exceptions import NoCredentialsError

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 12345678  # Replace with a strong secret key for sessions

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the login view

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
    """Load user for session management."""
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
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
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('login'))

# Initialize Raspberry Pi components
camera = PiCamera()
camera.resolution = (640, 480)
pir = MotionSensor(17)  # PIR sensor connected to GPIO 17
buzzer = Buzzer(18)     # Buzzer connected to GPIO 18

# Initialize variables for alerts
alerts = []

# Initialize AWS DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('IoTAlerts')

def store_alert(alert_message):
    """Store an alert in DynamoDB."""
    try:
        table.put_item(Item={'alert_id': str(datetime.now()), 'message': alert_message})
    except NoCredentialsError:
        print("Credentials not available")

def gen_frames():
    """Capture and yield frames for video streaming."""
    camera.start_preview()
    while True:
        frame = camera.capture(output='frame.jpg', format='jpeg')
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def motion_detected():
    """Handle motion detection."""
    print("Motion detected!")
    buzzer.on()
    alert_message = f"Motion detected at {datetime.now()}"
    alerts.append(alert_message)
    store_alert(alert_message)  # Store the alert in DynamoDB
    sleep(5)
    buzzer.off()

@app.route('/')
@login_required
def index():
    """Route to the homepage."""
    return render_template('index.html', alerts=alerts)

@app.route('/video_feed')
@login_required
def video_feed():
    """Route to handle video streaming."""
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start')
@login_required
def start_security():
    """Start security monitoring."""
    pir.when_motion = motion_detected
    return "Security monitoring started"

@app.route('/stop')
@login_required
def stop_security():
    """Stop security monitoring."""
    pir.when_motion = None
    return "Security monitoring stopped"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
