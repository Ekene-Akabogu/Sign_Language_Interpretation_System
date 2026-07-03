import { useRef, useCallback, useEffect } from "react";
import { predictFrame } from "../utils/api";
import { CAPTURE_INTERVAL, SMOOTHING_FRAMES, AUDIO_MODES } from "../utils/constants";
import { speak } from "../utils/speech";

export default function WebcamPanel({
  camActive,
  prediction,
  newLetter,
  isSpeaking,
  audioMode,
  onCamStart,
  onPrediction,
  onHandDetected,
  onBackendStatus,
  onHistory,
  onLetterChange,
  onSpeakStart,
  onSpeakEnd,
}) {
  const videoRef    = useRef(null);
  const canvasRef   = useRef(null);
  const smoothBuf   = useRef([]);
  const lastLetter  = useRef(null);
  const lastTimeRef = useRef(0);
  const runningRef  = useRef(false);

  // ✅ START CAMERA (with better constraints)
  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: 640,
          height: 480,
          facingMode: "user",
          advanced: [
            { zoom: 1 },
            { focusMode: "manual" },
            { exposureMode: "manual" },
          ],
        },
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        onCamStart();
      }
    } catch (err) {
      alert("Camera access denied. Please allow camera permissions.");
    }
  }, [onCamStart]);

  // ✅ CAPTURE FRAME (optimized)
  const captureFrame = useCallback(async () => {
    if (runningRef.current) return; // 🚫 prevent overlapping calls
    runningRef.current = true;

    const video  = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas || video.readyState < 2) {
      runningRef.current = false;
      return;
    }

    const ctx = canvas.getContext("2d");

    canvas.width  = video.videoWidth  || 640;
    canvas.height = video.videoHeight || 480;

    ctx.drawImage(video, 0, 0);

    // ✅ use toBlob instead of toDataURL (faster)
    canvas.toBlob(async (blob) => {
      if (!blob) {
        runningRef.current = false;
        return;
      }

      const reader = new FileReader();
      reader.onloadend = async () => {
        try {
          const base64 = reader.result.split(",")[1];
          const data   = await predictFrame(base64);

          if (!data) {
            onBackendStatus(false);
            onHandDetected(false);
            runningRef.current = false;
            return;
          }

          onBackendStatus(true);

          if (data.hand_detected) {
            onHandDetected(true);

            // ✅ smoothing
            smoothBuf.current.push(data.sign);
            if (smoothBuf.current.length > SMOOTHING_FRAMES)
              smoothBuf.current.shift();

            const freq = {};
            smoothBuf.current.forEach(s => (freq[s] = (freq[s] || 0) + 1));
            const smoothed = Object.entries(freq).sort((a, b) => b[1] - a[1])[0][0];

            onPrediction(smoothed, data.confidence);

            // ✅ detect change
            if (smoothed !== lastLetter.current) {
              onLetterChange();

              if (audioMode === AUDIO_MODES.ON_DETECT) {
                const lbl =
                  smoothed === "space"
                    ? "space"
                    : smoothed === "del"
                    ? "delete"
                    : smoothed === "nothing"
                    ? ""
                    : smoothed;

                if (lbl) speak(lbl, onSpeakStart, onSpeakEnd);
              }

              lastLetter.current = smoothed;
            }

            onHistory({
              sign: smoothed,
              conf: data.confidence,
              id: Date.now(),
            });

            // ✅ draw bounding box (cleaner)
            if (data.bbox) {
              const [x1, y1, x2, y2] = data.bbox;

              ctx.strokeStyle = "#00e5ff";
              ctx.lineWidth   = 2;
              ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
            }
          } else {
            onHandDetected(false);
            smoothBuf.current = [];
          }
        } catch {
          onBackendStatus(false);
          onHandDetected(false);
        }

        runningRef.current = false;
      };

      reader.readAsDataURL(blob);
    }, "image/jpeg", 0.7);
  }, [
    audioMode,
    onPrediction,
    onHandDetected,
    onBackendStatus,
    onHistory,
    onLetterChange,
    onSpeakStart,
    onSpeakEnd,
  ]);

  // ✅ SMOOTH LOOP (NO LAG)
  const loop = useCallback(
    (time) => {
      if (time - lastTimeRef.current > CAPTURE_INTERVAL) {
        lastTimeRef.current = time;
        captureFrame();
      }
      requestAnimationFrame(loop);
    },
    [captureFrame]
  );

  useEffect(() => {
    if (camActive) requestAnimationFrame(loop);
  }, [camActive, loop]);

  const confPct = Math.round((prediction.confidence || 0) * 100);

  return (
    <div className="cam-panel">
      <div className="cam-header">
        <span className="cam-label">Live Feed</span>
        {!camActive && (
          <button className="start-btn" onClick={startCamera}>
            Start Camera
          </button>
        )}
      </div>

      <div className="cam-body">
        {!camActive && (
          <div className="no-cam">
            <div className="no-cam-icon">📷</div>
            <div>Click "Start Camera" to begin</div>
          </div>
        )}

        <video
          ref={videoRef}
          muted
          playsInline
          style={{ display: camActive ? "block" : "none" }}
        />

        <canvas
          ref={canvasRef}
          style={{ display: camActive ? "block" : "none" }}
        />

        {/* Speaking indicator */}
        {camActive && isSpeaking && (
          <div className="speaking-indicator">
            <div className="speak-bars">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="speak-bar" />
              ))}
            </div>
            Speaking...
          </div>
        )}

        {/* Prediction overlay */}
        {camActive && (
          <div className="cam-overlay">
            <div className="cam-prediction-badge">
              <div className={`big-letter ${newLetter ? "new" : ""}`}>
                {prediction.sign}
              </div>
              <div className="badge-info">
                <div className="badge-conf">{confPct}% confident</div>
                <div className="badge-conf-bar">
                  <div
                    className="badge-conf-fill"
                    style={{ width: `${confPct}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}