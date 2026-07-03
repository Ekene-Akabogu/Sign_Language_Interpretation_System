import { useState, useEffect, useCallback } from "react";

import WebcamPanel    from "./components/WebcamPanel";
import PredictionPanel from "./components/PredictionPanel";
import SentencePanel  from "./components/SentencePanel";
import HistoryPanel   from "./components/HistoryPanel";

import { speak }       from "./utils/speech";
import { styles }      from "./utils/styles";
import { AUDIO_MODES, HISTORY_MAX } from "./utils/constants";

export default function App() {
  // ── State ──────────────────────────────────────────────────
  const [camActive,    setCamActive]    = useState(false);
  const [handDetected, setHandDetected] = useState(false);
  const [prediction,   setPrediction]   = useState({ sign: "—", confidence: 0 });
  const [history,      setHistory]      = useState([]);
  const [sentence,     setSentence]     = useState("");
  const [newLetter,    setNewLetter]    = useState(false);
  const [backendOk,    setBackendOk]    = useState(null);
  const [audioMode,    setAudioMode]    = useState(AUDIO_MODES.ON_ADD);
  const [isSpeaking,   setIsSpeaking]   = useState(false);

  // ── Callbacks passed down to WebcamPanel ───────────────────
  const handlePrediction = useCallback((sign, confidence) => {
    setPrediction({ sign, confidence });
  }, []);

  const handleLetterChange = useCallback(() => {
    setNewLetter(true);
    setTimeout(() => setNewLetter(false), 200);
  }, []);

  const handleHistory = useCallback((entry) => {
    setHistory(prev => {
      if (prev.length && prev[prev.length - 1].sign === entry.sign) return prev;
      return [...prev.slice(-HISTORY_MAX + 1), entry];
    });
  }, []);

  // ── Sentence builder ───────────────────────────────────────
  const addToSentence = useCallback(() => {
    const s = prediction.sign;
    if (!s || s === "—" || s === "nothing") return;

    if (s === "space") {
      setSentence(prev => prev + " ");
      if (audioMode === AUDIO_MODES.ON_ADD)
        speak("space", () => setIsSpeaking(true), () => setIsSpeaking(false));
    } else if (s === "del") {
      setSentence(prev => prev.slice(0, -1));
      if (audioMode === AUDIO_MODES.ON_ADD)
        speak("delete", () => setIsSpeaking(true), () => setIsSpeaking(false));
    } else {
      setSentence(prev => prev + s);
      if (audioMode === AUDIO_MODES.ON_ADD)
        speak(s, () => setIsSpeaking(true), () => setIsSpeaking(false));
    }
  }, [prediction.sign, audioMode]);

  const clearSentence = useCallback(() => setSentence(""), []);

  const copySentence = useCallback(() => {
    if (sentence) navigator.clipboard?.writeText(sentence);
  }, [sentence]);

  const speakSentence = useCallback(() => {
    if (sentence.trim())
      speak(sentence.trim(), () => setIsSpeaking(true), () => setIsSpeaking(false));
  }, [sentence]);

  const speakChip = useCallback((sign) => {
    if (audioMode === AUDIO_MODES.OFF) return;
    const label = sign === "del" ? "delete" : sign;
    speak(label, () => setIsSpeaking(true), () => setIsSpeaking(false));
  }, [audioMode]);

  // ── Keyboard shortcuts ─────────────────────────────────────
  useEffect(() => {
    const handler = (e) => {
      if (e.code === "Space"     && camActive && document.activeElement.tagName !== "INPUT") {
        e.preventDefault(); addToSentence();
      }
      if (e.code === "Backspace" && e.ctrlKey) clearSentence();
      if (e.code === "KeyC" && e.ctrlKey) copySentence();
      if (e.code === "Enter"     && e.ctrlKey) speakSentence();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [camActive, addToSentence, clearSentence, speakSentence]);

  const audioOn = audioMode !== AUDIO_MODES.OFF;

  // ── Render ─────────────────────────────────────────────────
  return (
    <>
      <style>{styles}</style>
      <div className="app">

        {/* Header */}
        <header className="header">
          <div className="logo">
            <div className="logo-icon">👌🏽</div>
            <div className="logo-text">Signyx</div>
          </div>
          <div className="header-right">
            <button
              className={`audio-btn ${audioOn ? "on" : ""}`}
              onClick={() =>
                setAudioMode(m => m === AUDIO_MODES.OFF ? AUDIO_MODES.ON_ADD : AUDIO_MODES.OFF)
              }
            >
              <span>{audioOn ? "🔊" : "🔇"}</span>
              {audioOn ? "Audio On" : "Audio Off"}
            </button>
            <div className="header-status">
              <div className={`status-dot ${camActive ? (backendOk === false ? "error" : "active") : ""}`} />
              {camActive ? (backendOk === false ? "BACKEND UNREACHABLE" : "LIVE") : "STANDBY"}
            </div>
          </div>
        </header>

        {/* Main grid */}
        <main className="main">

          <WebcamPanel
            camActive={camActive}
            prediction={prediction}
            newLetter={newLetter}
            isSpeaking={isSpeaking}
            audioMode={audioMode}
            onCamStart={() => setCamActive(true)}
            onPrediction={handlePrediction}
            onHandDetected={setHandDetected}
            onBackendStatus={setBackendOk}
            onHistory={handleHistory}
            onLetterChange={handleLetterChange}
            onSpeakStart={() => setIsSpeaking(true)}
            onSpeakEnd={() => setIsSpeaking(false)}
          />

          <PredictionPanel
            handDetected={handDetected}
            prediction={prediction}
            audioMode={audioMode}
            camActive={camActive}
            onAudioModeChange={setAudioMode}
          />

          <SentencePanel
            sentence={sentence}
            onAdd={addToSentence}
            onSpeak={speakSentence}
            onCopy={copySentence}
            onClear={clearSentence}
          />

          <HistoryPanel
            history={history}
            onChipClick={speakChip}
          />

        </main>
      </div>
    </>
  );
}