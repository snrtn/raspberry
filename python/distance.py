import time
import board
import busio
import adafruit_vl53l0x
import cv2
from picamera2 import Picamera2

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_vl53l0x.VL53L0X(i2c)

picam2 = Picamera2()
picam2.preview_configuration.main.size = (600, 600)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")

is_camera_on = False

print("VL53L0X Distance Sensor Started...")

try:
    while True:
        distance = sensor.range
        print(f"Distance: {distance} mm")

        if distance < 300 and not is_camera_on:
            print("Camera ON")
            picam2.start()
            is_camera_on = True

        elif distance >= 300 and is_camera_on:
            print("Camera OFF")
            picam2.stop()
            is_camera_on = False

        if is_camera_on:
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imshow("Camera Preview", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.1)

except KeyboardInterrupt:
    print("System Shutdown...")
    picam2.stop()
    cv2.destroyAllWindows()

cv2.destroyAllWindows()
