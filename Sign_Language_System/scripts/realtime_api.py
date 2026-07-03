import os
import io
import json
import base64

import numpy as np
import cv2
import mediapipe as mp
import tensorflow as tf

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="Signyx API",
    description="Real-time ASL hand gesture recognition using MobileNetV2 + MediaPipe",
    version="1.0.0"
)

# ── CORS — allows React frontend on Vercel to call this API ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # replace "*" with your Vercel URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load model & labels ───────────────────────────────────────
print("Loading MobileNetV2 model...")
model = tf.keras.models.load_model("models/sign_language_model.keras")

print("Loading class labels...")
with open("models/class_labels.json") as f:
    class_labels = json.load(f)
class_names = [class_labels[str(i)] for i in range(29)]

# ── Load MediaPipe Hand Landmarker ────────────────────────────
print("Loading MediaPipe hand landmarker...")
BaseOptions           = mp.tasks.BaseOptions
HandLandmarker        = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode     = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="models/hand_landmarker.task"),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1,
)
hand_detector = HandLandmarker.create_from_options(options)
print("All models loaded. Ready.")

IMG_SIZE = (224, 224)


# ── Request / Response schemas ────────────────────────────────
class PredictRequest(BaseModel):
    image: str          # base64-encoded JPEG frame from the React frontend

class PredictResponse(BaseModel):
    hand_detected: bool
    sign:          str | None
    confidence:    float
    bbox:          list[int] | None
    top5:          dict[str, float] | None


# ── Hand crop helper ──────────────────────────────────────────
def get_hand_crop(frame: np.ndarray, padding: int = 20, scale: float = 1.2):
    """
    Detect hand landmarks and return a square cropped region + bounding box.
    
    padding → small buffer around hand
    scale   → how much to expand box (1.0 = tight, 1.2 = slightly bigger)
    """

    h, w = frame.shape[:2]

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = hand_detector.detect(mp_image)

    if not result.hand_landmarks:
        return None, None

    landmarks = result.hand_landmarks[0]

    xs = [lm.x * w for lm in landmarks]
    ys = [lm.y * h for lm in landmarks]

    # ✅ tighter initial box
    x_min = max(0, int(min(xs)) - padding)
    x_max = min(w, int(max(xs)) + padding)
    y_min = max(0, int(min(ys)) - padding)
    y_max = min(h, int(max(ys)) + padding)

    # ✅ compute width/height
    box_w = x_max - x_min
    box_h = y_max - y_min

    # ✅ controlled square size (not too big)
    size = int(max(box_w, box_h) * scale)

    cx = (x_min + x_max) // 2
    cy = (y_min + y_max) // 2

    x_min = max(0, cx - size // 2)
    x_max = min(w, cx + size // 2)
    y_min = max(0, cy - size // 2)
    y_max = min(h, cy + size // 2)

    crop = frame[y_min:y_max, x_min:x_max]
    bbox = [x_min, y_min, x_max, y_max]

    return crop, bbox


# ── Routes ────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "Signyx API is running",
        "docs":    "/docs",
        "health":  "/health"
    }


@app.get("/health")
def health():
    return {
        "status":  "ok",
        "model":   "MobileNetV2",
        "classes": 29,
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest):
    # 1. Decode base64 image
    try:
        img_bytes = base64.b64decode(payload.image)
        img_pil   = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        frame     = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image data")

    # 2. Detect hand and crop
    crop, bbox = get_hand_crop(frame)

    if crop is None or crop.size == 0:
        return PredictResponse(
            hand_detected=False,
            sign=None,
            confidence=0.0,
            bbox=None,
            top5=None
        )

    # 3. Preprocess
    crop_rgb   = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    resized    = cv2.resize(crop_rgb, IMG_SIZE)
    normalised = resized.astype(np.float32) / 255.0
    batch      = np.expand_dims(normalised, axis=0)

    # 4. Predict
    probs      = model.predict(batch, verbose=0)[0]
    class_idx  = int(np.argmax(probs))
    confidence = float(probs[class_idx])
    sign       = class_names[class_idx]

    # top 5 predictions
    top5_idx = np.argsort(probs)[-5:][::-1]
    top5     = { class_names[i]: round(float(probs[i]), 4) for i in top5_idx }

    return PredictResponse(
        hand_detected=True,
        sign=sign,
        confidence=round(confidence, 4),
        bbox=bbox,
        top5=top5
    )


# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8088))
    print(f"Starting Signyx API on port {port}...")
    uvicorn.run("realtime_api:app", host="0.0.0.0", port=port, reload=False)