import subprocess

# Example command: listing files in the current directory
command = "libcamera-still -o image2.jpg"
process = subprocess.run(command, shell=True, capture_output=True, text=True)

