import cv2
import json
import numpy as np
import tensorflow as tf
import time
import tkinter as tk
from PIL import Image, ImageTk
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Load sign language model
print("Loading model...")
model = tf.keras.models.load_model("models/sign_language_model.keras")
with open("models/class_labels.json", "r") as f:
    class_labels = json.load(f)
print("Model loaded!")

# Load MediaPipe Hand Landmarker
print("Loading MediaPipe hand detector...")
base_options = python.BaseOptions(model_asset_path="models/hand_landmarker.task")
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
hand_detector = vision.HandLandmarker.create_from_options(options)
print("Hand detector loaded!")

# Initialize camera
print("Warming up camera...")
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(2)
for _ in range(10):
    cap.read()
print("Camera ready!")

# Setup tkinter window
root = tk.Tk()
root.title("Sign Language Interpreter")
root.configure(bg="#1e1e1e")

# UI Elements
video_label = tk.Label(root, bg="#1e1e1e")
video_label.pack(pady=10, padx=10)

sign_label = tk.Label(root, text="Sign: -", font=("Helvetica", 32, "bold"),
                      fg="#00ff88", bg="#1e1e1e")
sign_label.pack()

confidence_label = tk.Label(root, text="Confidence: -", font=("Helvetica", 16),
                             fg="white", bg="#1e1e1e")
confidence_label.pack(pady=5)

hand_status_label = tk.Label(root, text="No hand detected", font=("Helvetica", 12),
                              fg="#ff4444", bg="#1e1e1e")
hand_status_label.pack()

instruction_label = tk.Label(root, text="Show your hand to the camera",
                              font=("Helvetica", 12), fg="#aaaaaa", bg="#1e1e1e")
instruction_label.pack(pady=5)

prediction_history = []
HISTORY_SIZE = 5

def get_hand_crop(frame, padding=80):
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = hand_detector.detect(mp_image)

    if not result.hand_landmarks:
        return None, None

    landmarks = result.hand_landmarks[0]
    xs = [lm.x * w for lm in landmarks]
    ys = [lm.y * h for lm in landmarks]

    x_min = max(0, int(min(xs)) - padding)
    x_max = min(w, int(max(xs)) + padding)
    y_min = max(0, int(min(ys)) - padding)
    y_max = min(h, int(max(ys)) + padding)

    # Make it square to match training images
    box_w = x_max - x_min
    box_h = y_max - y_min
    size = max(box_w, box_h)

    cx = (x_min + x_max) // 2
    cy = (y_min + y_max) // 2

    x_min = max(0, cx - size // 2)
    x_max = min(w, cx + size // 2)
    y_min = max(0, cy - size // 2)
    y_max = min(h, cy + size // 2)

    crop = frame[y_min:y_max, x_min:x_max]
    return crop, (x_min, y_min, x_max, y_max)

def update_frame():
    ret, frame = cap.read()
    if ret and frame is not None:
        frame = cv2.flip(frame, 1)

        hand_crop, bbox = get_hand_crop(frame)

        if hand_crop is not None and hand_crop.size > 0:
            # Draw bounding box
            x_min, y_min, x_max, y_max = bbox
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 100), 2)
            cv2.putText(frame, "Hand detected", (x_min, y_min - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 100), 2)

            # Predict on cropped hand
            img = cv2.resize(hand_crop, (224, 224))
            img = img / 255.0
            img = np.expand_dims(img, axis=0)
            
            cv2.imwrite("debug_crop.jpg", hand_crop)
            
            predictions = model.predict(img, verbose=0)
            confidence = float(np.max(predictions))
            predicted_index = int(np.argmax(predictions))
            predicted_label = class_labels[str(predicted_index)]

            # Smooth predictions
            prediction_history.append(predicted_label)
            if len(prediction_history) > HISTORY_SIZE:
                prediction_history.pop(0)
            smoothed_label = max(set(prediction_history), key=prediction_history.count)

            # Update UI
            sign_label.config(text=f"Sign: {smoothed_label}")
            confidence_label.config(text=f"Confidence: {confidence*100:.1f}%")
            hand_status_label.config(text="✋ Hand Detected", fg="#00ff88")

        else:
            prediction_history.clear()
            sign_label.config(text="Sign: -")
            confidence_label.config(text="Confidence: -")
            hand_status_label.config(text="No hand detected", fg="#ff4444")
            cv2.putText(frame, "Show your hand to the camera", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

        # Convert frame to tkinter image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        video_label.img_tk = img_tk
        video_label.config(image=img_tk)

    root.after(30, update_frame)

def on_close():
    cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.bind("<q>", lambda e: on_close())

# Start
update_frame()
root.mainloop()

print("Closed.")