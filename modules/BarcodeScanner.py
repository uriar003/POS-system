import cv2                          # OpenCV is under Apache License 2.0, so it is free to use commercially
import numpy as np
from pyzbar.pyzbar import decode    # PyzBar is under the MIT License, which among other things permits modification and re-sale

# img = cv2.imread('1.png')
# set to 0 to use internal PC/laptop webcam, 1 for peripheral such as an external USB cam
cap = cv2.VideoCapture(1)
cap.set(3, 640)
cap.set(4, 480)

while True:     # probably change this bad condition
    success, img = cap.read()
    for barcode in decode(img):
        print(barcode.data)
        myData = barcode.data.decode('utf-8')
        print(myData)

        # bounding box to track scans
        pts = np.array([barcode.polygon], np.int32)
        pts = pts.reshape(-1, 1, 2)
        cv2.polylines(img, [pts], True, (255, 0, 255), 5)

    cv2.imshow('Result', img)
    cv2.waitKey(1)