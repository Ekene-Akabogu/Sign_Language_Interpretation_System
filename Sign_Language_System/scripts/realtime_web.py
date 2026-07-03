import cv2
import json
import numpy as np
import tensorflow as tf
import time
from flask import Flask, Response, render_template_string
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
print("Initializing camera...")
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(2)
for _ in range(10):
    cap.read()
print("Camera ready!")

app = Flask(__name__)

current_sign = "-"
current_confidence = 0.0
hand_detected = False
prediction_history = []
HISTORY_SIZE = 5

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Sign Language Interpreter</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #1e1e1e; color: white; font-family: Helvetica, sans-serif;
               display: flex; flex-direction: column; align-items: center; padding: 20px; }
        h1 { color: #00ff88; margin-bottom: 15px; font-size: 28px; }
        .video-container { position: relative; }
        img { border: 3px solid #00ff88; border-radius: 10px; display: block; }
        .info-box { background: #2a2a2a; border-radius: 10px; padding: 20px;
                    margin-top: 15px; text-align: center; width: 640px; }
        #prediction { font-size: 52px; font-weight: bold; color: #00ff88; }
        #confidence { font-size: 18px; color: #aaaaaa; margin-top: 5px; }
        #hand-status { font-size: 14px; margin-top: 10px; padding: 5px 15px;
                       border-radius: 20px; display: inline-block; }
        .detected { background: #00ff8833; color: #00ff88; }
        .not-detected { background: #ff444433; color: #ff4444; }
        #instruction { font-size: 13px; color: #666; margin-top: 10px; }
    </style>
    <script>
        function updatePrediction() {
            fetch('/prediction')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('prediction').innerText = data.hand ? 'Sign: ' + data.sign : 'No hand detected';
                    document.getElementById('confidence').innerText = data.hand ? 'Confidence: ' + data.confidence + '%' : '';
                    const status = document.getElementById('hand-status');
                    status.innerText = data.hand ? '✋ Hand Detected' : '✋ No Hand';
                    status.className = 'hand-status ' + (data.hand ? 'detected' : 'not-detected');
                });
        }
        setInterval(updatePrediction, 300);
    </script>
</head>
<body>
    <h1>🤟 ASL Sign Language Interpreter</h1>
    <div class="video-container">
        <img src="/video" width="640" height="480">
    </div>
    <div class="info-box">
        <div id="prediction">Sign: -</div>
        <div id="confidence">Confidence: -</div>
        <div id="hand-status" class="hand-status not-detected">✋ No Hand</div>
        <div id="instruction">Show your hand to the camera to interpret signs</div>
    </div>
</body>
</html>
"""

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

def generate_frames():
    global current_sign, current_confidence, hand_detected, prediction_history

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.05)
            continue

        frame = cv2.flip(frame, 1)

        # Detect and crop hand
        hand_crop, bbox = get_hand_crop(frame)

        if hand_crop is not None and hand_crop.size > 0:
            hand_detected = True

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

            prediction_history.append(predicted_label)
            if len(prediction_history) > HISTORY_SIZE:
                prediction_history.pop(0)
            current_sign = max(set(prediction_history), key=prediction_history.count)
            current_confidence = round(confidence * 100, 1)
        else:
            hand_detected = False
            prediction_history.clear()
            cv2.putText(frame, "Show your hand to the camera", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/prediction')
def prediction():
    return {'sign': current_sign, 'confidence': current_confidence, 'hand': hand_detected}

if __name__ == '__main__':
    print("\n✅ Open your browser and go to: http://localhost:8087\n")
    app.run(host='0.0.0.0', port=8087, debug=False, threaded=False)