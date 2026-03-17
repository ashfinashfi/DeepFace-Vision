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

def analyze_frame(frame: np.ndarray) -> np.ndarray:
    try:
        # analyze the frame, enforce_detection=False to avoid exceptions when no face is found
        results = DeepFace.analyze(
            img_path=frame,
            actions=['age', 'gender', 'emotion'],
            enforce_detection=False,
            silent=True
        )
        
        # results can be a list or a dict (if single face). Ensure it's a list.
        if not isinstance(results, list):
            results = [results]
            
        for face in results:
            # We want to draw bounding box
            region = face.get('region', {})
            x = region.get('x', 0)
            y = region.get('y', 0)
            w = region.get('w', 0)
            h = region.get('h', 0)
            
            # If no face detected or region is invalid
            if w == 0 or h == 0 or x + y + w + h == 0:
                continue
                
            age = face.get('age', 'N/A')
            gender = face.get('dominant_gender', 'N/A')
            emotion = face.get('dominant_emotion', 'N/A')
            
            # Draw bounding box
            box_color = (0, 255, 150) # Vivid green for premium feel
            cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
            
            # Add a dark semi-transparent rectangle behind text for better readability
            overlay = frame.copy()
            cv2.rectangle(overlay, (x, y - 50), (x + w, y), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
            
            # Prepare text
            text_age_gen = f"{gender}, {age}"
            text_emotion = f"{emotion.capitalize()}"
            
            # Draw text above bounding box
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, text_age_gen, (x + 5, y - 28), font, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, text_emotion, (x + 5, y - 8), font, 0.7, box_color, 2)
            
    except Exception as e:
        logger.debug(f"Error in analysis (likely no face): {e}")
        
    return frame
