import serial
import time

# Configure the serial port
ser = serial.Serial(
    port='/dev/serial0',  # Use the default UART port
    baudrate=9600,        # Check GSM module manual for correct baud rate (common: 9600 or 115200)
    timeout=1
)

def send_at_command(command, delay=1):
    """Send AT command to GSM module and read the response."""
    ser.write((command + '\r').encode())
    time.sleep(delay)
    while ser.in_waiting > 0:
        print(ser.readline().decode('utf-8').strip())

try:
    # Test the connection by sending "AT" command
    send_at_command("AT")

except KeyboardInterrupt:
    print("Program interrupted")

finally:
    ser.close()  # Close the serial port
