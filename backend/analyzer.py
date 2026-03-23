import cv2
from deepface import DeepFace
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("analyzer")

# Preload deepface model(s) to avoid delay on first frame
print("Initializing DeepFace models...")
try:
    # Dummy call to initialize the models
    dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
    DeepFace.analyze(img_path=dummy_img, actions=['age', 'gender', 'emotion'], enforce_detection=False)
except Exception:
    pass
print("DeepFace models loaded!")

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

cached_labels = {'age': 'N/A', 'gender': 'N/A', 'emotion': 'N/A'}
frame_counter = 0

def analyze_frame(frame: np.ndarray) -> np.ndarray:
    global frame_counter, cached_labels
    try:
        # Fast Face Detection on grayscale image
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        
        # If faces are found, get the biggest one
        if len(faces) > 0:
            # Sort by area (w*h) descending to track the most prominent face
            faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
            x, y, w, h = faces[0]
            
            # Every 15th frame, run heavy DeepFace on the heavily cropped face to update cached labels
            if frame_counter % 15 == 0:
                face_crop = frame[max(0, y):y+h, max(0, x):x+w]
                if face_crop.size > 0:
                    try:
                        res = DeepFace.analyze(face_crop, actions=['age', 'gender', 'emotion'], enforce_detection=False, silent=True)
                        if isinstance(res, list):
                            res = res[0]
                        cached_labels['age'] = res.get('age', 'N/A')
                        cached_labels['gender'] = res.get('dominant_gender', 'N/A')
                        cached_labels['emotion'] = res.get('dominant_emotion', 'N/A')
                    except:
                        pass
            
            # Draw premium bounding box instantaneously
            box_color = (0, 255, 150) # Vivid green for premium feel
            cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
            
            # Draw dark semi-transparent rectangle behind text
            overlay = frame.copy()
            cv2.rectangle(overlay, (x, y - 50), (x + w, y), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
            
            # Prepare text from cached high-latency inferences
            text_age_gen = f"{cached_labels['gender']}, {cached_labels['age']}"
            text_emotion = f"{cached_labels['emotion'].capitalize()}"
            
            # Draw text
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, text_age_gen, (x + 5, y - 28), font, 0.55, (255, 255, 255), 1)
            cv2.putText(frame, text_emotion, (x + 5, y - 8), font, 0.65, box_color, 2)
            
        frame_counter += 1
        
    except Exception as e:
        logger.debug(f"Error in analysis: {e}")
        
    return frame
