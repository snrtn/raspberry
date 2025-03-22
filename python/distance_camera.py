import cv2
import pytesseract
import numpy as np
import re
import os
from pyzbar.pyzbar import decode
from picamera2 import Picamera2

# Initialize camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 1130)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

compiled_patterns = [
    re.compile(r'\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b'),
    re.compile(r'\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b'),
    re.compile(r'\b\d{1,2}[./-]\d{4}\b')
]

def enhance_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    contrast = cv2.convertScaleAbs(gray, alpha=1.5, beta=10)
    blurred = cv2.GaussianBlur(contrast, (3, 3), 0)
    denoised = cv2.medianBlur(blurred, 3)
    return denoised

def detect_dates(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    gray = cv2.filter2D(gray, -1, sharpen_kernel)
    _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(thresholded, config="--psm 6 -c tessedit_char_whitelist=0123456789./-")

    matched_dates = []
    for pattern in compiled_patterns:
        matches = pattern.findall(text)
        matched_dates.extend(matches)
    return matched_dates

print("Starting Barcode and Date Detection System...")
barcode_data = None

try:
    while True:
        frame = picam2.capture_array()

        if barcode_data is None:
            processed_frame = enhance_image(frame)
            barcodes = decode(processed_frame)
            if barcodes:
                barcode_data = barcodes[0].data.decode()
                pts = np.array([barcodes[0].polygon], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
                cv2.putText(frame, f"Barcode: {barcode_data}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                print(f"Detected Barcode: {barcode_data}")

        else:
            dates_detected = detect_dates(frame)
            if dates_detected:
                date_text = ', '.join(dates_detected)
                cv2.putText(frame, date_text, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                print(f"Detected Dates: {date_text}")
                os.system('aplay /usr/share/sounds/alsa/Front_Center.wav')

        cv2.imshow("Barcode and Date Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("System Shutdown...")

finally:
    picam2.stop()
    cv2.destroyAllWindows()
