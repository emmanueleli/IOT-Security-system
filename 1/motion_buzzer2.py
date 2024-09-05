import RPi.GPIO as GPIO
import time

# Pin configuration
PIR_PIN = 17        # GPIO pin for PIR sensor
BUZZER_PIN = 18     # GPIO pin for buzzer

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)      # Set PIR pin as input
GPIO.setup(BUZZER_PIN, GPIO.OUT)  # Set Buzzer pin as output

def beep_buzzer():
    """Function to beep the buzzer twice: one low and one high."""
    # First beep - low
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(0.2)  # Short beep
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    time.sleep(0.1)  # Short pause

    # Second beep - high
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(0.5)  # Longer beep
    GPIO.output(BUZZER_PIN, GPIO.LOW)

def main():
    print("PIR Motion Sensor and Buzzer Test (CTRL+C to exit)")
    time.sleep(0)  # Allow PIR sensor to settle
    print("Ready")

    try:
        while True:
            pir_state = GPIO.input(PIR_PIN)  # Read the state of the PIR sensor
            print(f"PIR Sensor State: {pir_state}")  # Print the state for debugging
            
            if pir_state:
                print("Motion Detected!")
                beep_buzzer()  # Trigger the beeping sequence
                time.sleep(0)  # Wait 2 seconds to avoid multiple triggers
            else:
                GPIO.output(BUZZER_PIN, GPIO.LOW)  # Ensure buzzer is off
            time.sleep(0.1)  # Small delay to prevent excessive CPU usage

    except KeyboardInterrupt:
        print("Program interrupted")

    finally:
        GPIO.cleanup()  # Clean up GPIO settings

if __name__ == "__main__":
    main()