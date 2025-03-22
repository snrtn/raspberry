import cv2
import pytesseract
import os
import re
import numpy as np
from pyzbar.pyzbar import decode
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.start()

window_name = "Live Camera Feed"
cv2.namedWindow(window_name)

compiled_patterns = [
    re.compile(r'\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b'),
    re.compile(r'\b\d{1,2}[./-]\d{1,2}[./-]\d{4}\b'),
    re.compile(r'\b\d{1,2}[./-]\d{4}\b')
]

while True:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    for barcode in decode(frame):
        barcode_data = barcode.data.decode('utf-8')
        barcode_text = "Barcode: " + barcode_data
        cv2.putText(frame, barcode_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        print(f"Scanned Barcode Data: {barcode_data}")
    
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    
    sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    gray = cv2.filter2D(gray, -1, sharpen_kernel)
    
    edges = cv2.Canny(gray, 50, 150)
    dilated = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, contours, -1, (255), thickness=cv2.FILLED)
    processed = cv2.bitwise_and(gray, gray, mask=mask)
    
    _, thresholded = cv2.threshold(processed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(thresholded, config="--psm 6 -c tessedit_char_whitelist=0123456789./-")
    
    matched_dates = []
    
    for pattern in compiled_patterns:
        matches = pattern.findall(text)
        for match in matches:
            if any(sep in match for sep in ['/', '-', '.', ' ']):
                matched_dates.append(match)
    
    if matched_dates:
        date_text = ', '.join(matched_dates)
        print(f"Detected Expiry Dates: {date_text}")
        os.system('aplay /usr/share/sounds/alsa/Front_Center.wav')
    else:
        date_text = ""
    
    frame_display = frame.copy()
    if date_text:
        cv2.putText(frame_display, date_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow(window_name, frame_display)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
