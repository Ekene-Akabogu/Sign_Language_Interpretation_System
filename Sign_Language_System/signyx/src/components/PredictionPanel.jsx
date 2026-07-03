import { AUDIO_MODES, BACKEND_URL } from "../utils/constants";

/**
 * PredictionPanel
 * Shows: detection status, current sign + confidence,
 *        audio mode selector, backend notice
 *
 * Props:
 *   handDetected      {bool}
 *   prediction        {sign, confidence}
 *   audioMode         {string}
 *   camActive         {bool}
 *   onAudioModeChange {fn(mode)}
 */
export default function PredictionPanel({
  handDetected,
  prediction,
  audioMode,
  camActive,
  onAudioModeChange,
}) {
  const confPct = Math.round((prediction.confidence || 0) * 100);
  const signLabel =
    prediction.sign === "—"       ? "Waiting..."
    : prediction.sign === "space"  ? "SPACE"
    : prediction.sign === "del"    ? "DELETE"
    : prediction.sign === "nothing"? "No gesture"
    : `ASL Letter "${prediction.sign}"`;

  return (
    <div className="prediction-panel">
      <div className="panel-title">Detection</div>

      {/* Hand detection status */}
      <div className={`detection-status ${handDetected ? "detected" : "no-hand"}`}>
        <div className={`status-dot ${handDetected ? "active" : "error"}`} />
        {handDetected ? "✋ Hand Detected" : "No Hand Detected"}
      </div>

      {/* Current sign */}
      <div className="current-sign">
        <div className="current-sign-letter">{prediction.sign}</div>
        <div className="current-sign-name">{signLabel}</div>
        <div className="conf-row">
          <span className="conf-label">Confidence</span>
          <span className="conf-value">{confPct}%</span>
        </div>
        <div className="conf-track">
          <div className="conf-fill" style={{ width: `${confPct}%` }} />
        </div>
      </div>

      {/* Audio mode selector */}
      <div className="audio-mode">
        <div className="audio-mode-title">🔊 Audio Output Mode</div>
        <div className="audio-mode-opts">
          {[
            { mode: AUDIO_MODES.OFF,       label: "Off — no audio"              },
            { mode: AUDIO_MODES.ON_ADD,    label: "Speak when sign is added"    },
            { mode: AUDIO_MODES.ON_DETECT, label: "Speak every detected sign"   },
            { mode: AUDIO_MODES.SENTENCE,  label: "Speak full sentence only"    },
          ].map(({ mode, label }) => (
            <div
              key={mode}
              className={`audio-opt ${audioMode === mode ? "selected" : ""}`}
              onClick={() => onAudioModeChange(mode)}
            >
              <div className="audio-opt-dot" />
              {label}
            </div>
          ))}
        </div>
      </div>

      {/* Backend notice — shown only when camera not started */}
      {!camActive && (
        <div className="backend-notice">
          <b>Backend:</b> Ensure FastAPI is running at <b>{BACKEND_URL}</b>.<br />
          Set <b>VITE_BACKEND_URL</b> in <b>.env</b> to your Render URL when deployed.
        </div>
      )}
    </div>
  );
}