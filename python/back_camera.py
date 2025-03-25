import RPi.GPIO as GPIO
import time
import board
import busio
import adafruit_vl53l0x
import cv2
from picamera2 import Picamera2

# GPIO setup
LED_PINS = {"red": 5, "green": 6, "yellow": 13} 
BUTTON_PIN = 16
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

for pin in LED_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Distance sensor setup
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_vl53l0x.VL53L0X(i2c)

# Camera setup
picam2 = Picamera2()
picam2.preview_configuration.main.size = (600, 600)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")

# States
system_on = False
prev_button_state = False

print("Ready. Press button to start...")

try:
    while True:
        button_state = GPIO.input(BUTTON_PIN)

        if button_state and not prev_button_state:
            system_on = not system_on
            if not system_on:
                print("System OFF")
                picam2.stop()
                cv2.destroyAllWindows()
                for pin in LED_PINS.values():
                    GPIO.output(pin, GPIO.LOW)
            else:
                print("System ON")
                picam2.start()
            time.sleep(0.3)

        prev_button_state = button_state

        if system_on:
            distance = sensor.range
            print(f"Distance: {distance} mm")
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Determine color and LED
            border_color = (255, 255, 255)  # Default white

            # Turn off all LEDs first
            for pin in LED_PINS.values():
                GPIO.output(pin, GPIO.LOW)

            if distance > 300:
                border_color = (0, 255, 0)  # Green
                GPIO.output(LED_PINS["green"], GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(LED_PINS["green"], GPIO.LOW)
            elif distance > 100:
                border_color = (0, 255, 255)  # Yellow
                GPIO.output(LED_PINS["yellow"], GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(LED_PINS["yellow"], GPIO.LOW)
            else:
                border_color = (0, 0, 255)  # Red
                GPIO.output(LED_PINS["red"], GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(LED_PINS["red"], GPIO.LOW)

            # Draw thick border
            thickness = 10
            cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), border_color, thickness)
            cv2.imshow("Camera Preview", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Interrupted. Cleaning up...")
    picam2.stop()
    cv2.destroyAllWindows()
    GPIO.cleanup()

cv2.destroyAllWindows()
GPIO.cleanup()
