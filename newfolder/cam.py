from picamera import PiCamera

def capture_image():
    """Capture image using PiCamera."""
    global latest_image_path
    camera = PiCamera()
    camera.resolution = (640, 480)
    image_name = f'intruder_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
    image_path = os.path.join('static', image_name)
    
    camera.capture(image_path)
    latest_image_path = image_name  # Update the latest image path
    camera.close()
    
    return image_path