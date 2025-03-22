import time
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from picamera2 import Picamera2, Preview

picam2 = Picamera2()
picam2.preview_configuration.main.size = (600, 600)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

print("Starting Barcode Detection System...")

def enhance_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    contrast = cv2.convertScaleAbs(gray, alpha=1.5, beta=10)
    blurred = cv2.GaussianBlur(contrast, (3, 3), 0)
    denoised = cv2.medianBlur(blurred, 3)
    return denoised

def scan_barcode():
    while True:
        frame = picam2.capture_array()
        processed_frame = enhance_image(frame)

        barcode_number = None
        for barcode in decode(processed_frame):
            barcode_number = barcode.data.decode('utf-8')
            print(f"Barcode Detected: {barcode_number}")

            pts = np.array([barcode.polygon], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], True, (0, 255, 0), 3)

            cv2.imshow("Barcode Scanner", frame)
            cv2.waitKey(1000)
            cv2.destroyAllWindows
            picam2.stop()
            return
            
        cv2.imshow("Barcode Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    picam2.stop()

try:
    scan_barcode()
except KeyboardInterrupt:
    print("System Shutdown...")
    picam2.stop()
