import cv2
import numpy as np
from analyzer import analyze_frame, cached_labels

# Create a mock color image (like a face)
img = np.zeros((480, 640, 3), dtype=np.uint8)

# Download a sample face for testing
import urllib.request
url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/lena.jpg"
req = urllib.request.urlopen(url)
arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
img = cv2.imdecode(arr, -1)

print("Original cached labels:", cached_labels)
# Run analyze frame 16 times to trigger the 15th frame modulo
for i in range(16):
    analyze_frame(img)

print("Final cached labels:", cached_labels)
