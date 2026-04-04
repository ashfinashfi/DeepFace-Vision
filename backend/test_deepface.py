import cv2
import numpy as np
from deepface import DeepFace

url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/lena.jpg"
import urllib.request
req = urllib.request.urlopen(url)
arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
img = cv2.imdecode(arr, -1)

# Extract a face crop manually roughly
face_crop = img[200:400, 200:400]

try:
    res = DeepFace.analyze(face_crop, actions=['age', 'gender', 'emotion'], enforce_detection=False, silent=True)
    if isinstance(res, list):
        res = res[0]
    print("SUCCESS")
    print("Age:", res.get('age'))
    print("Gender:", res.get('dominant_gender'))
    print("Emotion:", res.get('dominant_emotion'))
except Exception as e:
    print("FAILED:", e)
