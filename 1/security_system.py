from gpiozero import MotionSensor, Buzzer
from picamera import PiCamera
from time import sleep
from datetime import datetime
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

# Initialize components
pir = MotionSensor(17)  # PIR sensor connected to GPIO 17
buzzer = Buzzer(18)     # Buzzer connected to GPIO 18
camera = PiCamera()

def send_email(image_path):
    # Set up email server and credentials
    from_address = emmanueleli120@gmail.com
    to_address = christopherniisackey18@gmail.com
    password = emmanueleliage@130

    # Create email
    msg = MIMEMultipart()
    msg['Alert'] = 'Intruder Alert'
    msg['Emmanuel'] = from_address
    msg['Christopher'] = to_address

    # Attach image
    with open(image_path, 'rb') as f:
        img = MIMEImage(f.read())
        msg.attach(img)

    # Send email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_address, password)
    server.send_message(msg)
    server.quit()

def capture_image():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    image_path = f"/home/pi/security_images/{timestamp}.jpg"
    camera.capture(image_path)
    return image_path

def motion_detected():
    print("Motion detected!")
    buzzer.on()
    image_path = capture_image()
    send_email(image_path)
    sleep(5)
    buzzer.off()

# Main loop
pir.when_motion = motion_detected

while True:
    sleep(1)
