export const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;500;600;700;800&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg:        #080c10;
    --surface:   #0d1117;
    --panel:     #111820;
    --border:    #1e2a36;
    --accent:    #00e5ff;
    --accent2:   #7fff6e;
    --warn:      #ff4d6d;
    --text:      #e8f0f8;
    --muted:     #4a6070;
    --font-head: 'Syne', sans-serif;
    --font-mono: 'Space Mono', monospace;
  }
  body { background: var(--bg); color: var(--text); font-family: var(--font-head); min-height: 100vh; overflow-x: hidden; }
  body::before {
    content: ''; position: fixed; inset: 0;
    background-image: linear-gradient(rgba(0,229,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(0,229,255,0.02) 1px, transparent 1px);
    background-size: 40px 40px; pointer-events: none; z-index: 0;
  }
  .app { position: relative; z-index: 1; min-height: 100vh; display: flex; flex-direction: column; }

  .header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 32px; border-bottom: 1px solid var(--border);
    background: rgba(8,12,16,0.9); backdrop-filter: blur(12px);
    position: sticky; top: 0; z-index: 100;
  }
  .logo { display: flex; align-items: center; gap: 12px; }
  .logo-icon { width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-family: 'Space Mono', monospace; font-weight: 700; color: #000; letter-spacing: -1px; font-size: 28px; }
  .logo-text { font-weight: 800; font-size: 18px; letter-spacing: -0.3px; }
  .logo-text span { color: var(--accent); }
  .header-right { display: flex; align-items: center; gap: 16px; }
  .header-status { display: flex; align-items: center; gap: 8px; font-family: var(--font-mono); font-size: 11px; color: var(--muted); }
  .status-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--muted); transition: background 0.3s, box-shadow 0.3s; }
  .status-dot.active { background: var(--accent2); box-shadow: 0 0 8px var(--accent2); animation: pulse 2s infinite; }
  .status-dot.error  { background: var(--warn); box-shadow: 0 0 8px var(--warn); }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
  .audio-btn { display: flex; align-items: center; gap: 7px; padding: 7px 14px; border-radius: 8px; border: 1px solid var(--border); background: var(--panel); color: var(--muted); font-family: var(--font-mono); font-size: 11px; cursor: pointer; transition: all 0.2s; text-transform: uppercase; letter-spacing: 1px; }
  .audio-btn:hover { border-color: var(--accent); color: var(--accent); }
  .audio-btn.on { border-color: var(--accent2); color: var(--accent2); background: rgba(127,255,110,0.07); }

  .main { flex: 1; display: grid; grid-template-columns: 1fr 400px; grid-template-rows: auto 1fr; gap: 20px; padding: 24px; max-width: 1400px; margin: 0 auto; width: 100%; }

  .cam-panel { grid-row: 1 / 3; background: var(--surface); border: 1px solid var(--border); border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; }
  .cam-header { padding: 14px 20px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
  .cam-label { font-family: var(--font-mono); font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; }
  .cam-body { flex: 1; position: relative; background: #000; min-height: 420px; }
  video, canvas { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
  canvas { pointer-events: none; }
  .cam-overlay { position: absolute; inset: 0; display: flex; align-items: flex-end; padding: 20px; background: linear-gradient(to top, rgba(8,12,16,0.85) 0%, transparent 50%); pointer-events: none; }
  .cam-prediction-badge { display: flex; align-items: center; gap: 16px; }
  .big-letter { font-family: var(--font-head); font-weight: 800; font-size: 96px; line-height: 1; color: var(--accent); text-shadow: 0 0 40px rgba(0,229,255,0.5); transition: all 0.15s ease; min-width: 80px; }
  .big-letter.new { animation: letterPop 0.2s ease; }
  @keyframes letterPop { 0%{transform:scale(0.7);opacity:0.3} 60%{transform:scale(1.1)} 100%{transform:scale(1);opacity:1} }
  .badge-info { display: flex; flex-direction: column; gap: 4px; }
  .badge-conf { font-family: var(--font-mono); font-size: 13px; color: var(--accent2); }
  .badge-conf-bar { width: 120px; height: 4px; background: var(--border); border-radius: 2px; overflow: hidden; }
  .badge-conf-fill { height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent2)); border-radius: 2px; transition: width 0.2s ease; }
  .no-cam { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; color: var(--muted); font-family: var(--font-mono); font-size: 13px; }
  .no-cam-icon { font-size: 48px; opacity: 0.3; }

  .speaking-indicator { position: absolute; top: 16px; right: 16px; display: flex; align-items: center; gap: 6px; padding: 6px 12px; background: rgba(0,229,255,0.15); border: 1px solid rgba(0,229,255,0.4); border-radius: 20px; font-family: var(--font-mono); font-size: 10px; color: var(--accent); pointer-events: none; animation: fadeIn 0.2s ease; }
  @keyframes fadeIn { from{opacity:0;transform:translateY(-4px)} to{opacity:1;transform:translateY(0)} }
  .speak-bars { display: flex; align-items: flex-end; gap: 2px; height: 14px; }
  .speak-bar { width: 3px; background: var(--accent); border-radius: 2px; animation: speakBar 0.6s ease-in-out infinite alternate; }
  .speak-bar:nth-child(1){height:6px;animation-delay:0s}
  .speak-bar:nth-child(2){height:12px;animation-delay:0.15s}
  .speak-bar:nth-child(3){height:8px;animation-delay:0.3s}
  .speak-bar:nth-child(4){height:14px;animation-delay:0.1s}
  .speak-bar:nth-child(5){height:5px;animation-delay:0.25s}
  @keyframes speakBar { from{transform:scaleY(0.4)} to{transform:scaleY(1)} }

  .prediction-panel { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 24px; display: flex; flex-direction: column; gap: 16px; }
  .panel-title { font-family: var(--font-mono); font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: var(--muted); padding-bottom: 12px; border-bottom: 1px solid var(--border); }
  .detection-status { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-radius: 8px; background: var(--panel); border: 1px solid var(--border); font-family: var(--font-mono); font-size: 12px; transition: all 0.3s; }
  .detection-status.detected { border-color: rgba(127,255,110,0.3); background: rgba(127,255,110,0.05); color: var(--accent2); }
  .detection-status.no-hand  { border-color: rgba(255,77,109,0.3);  background: rgba(255,77,109,0.05);  color: var(--warn); }
  .current-sign { text-align: center; padding: 16px; background: var(--panel); border-radius: 12px; border: 1px solid var(--border); }
  .current-sign-letter { font-family: var(--font-head); font-weight: 800; font-size: 64px; color: var(--accent); line-height: 1; text-shadow: 0 0 30px rgba(0,229,255,0.4); }
  .current-sign-name { font-size: 12px; color: var(--muted); margin-top: 4px; font-family: var(--font-mono); }
  .conf-row { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
  .conf-label { font-family: var(--font-mono); font-size: 11px; color: var(--muted); }
  .conf-value { font-family: var(--font-mono); font-size: 13px; color: var(--accent2); }
  .conf-track { height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; margin-top: 6px; }
  .conf-fill { height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent2)); border-radius: 3px; transition: width 0.25s ease; }

  .audio-mode { background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 14px; }
  .audio-mode-title { font-family: var(--font-mono); font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 10px; }
  .audio-mode-opts { display: flex; flex-direction: column; gap: 6px; }
  .audio-opt { display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-radius: 7px; border: 1px solid var(--border); background: var(--surface); cursor: pointer; transition: all 0.15s; font-family: var(--font-mono); font-size: 11px; color: var(--muted); }
  .audio-opt:hover { border-color: var(--accent); color: var(--text); }
  .audio-opt.selected { border-color: var(--accent); background: rgba(0,229,255,0.07); color: var(--accent); }
  .audio-opt-dot { width: 8px; height: 8px; border-radius: 50%; border: 1px solid currentColor; flex-shrink: 0; }
  .audio-opt.selected .audio-opt-dot { background: var(--accent); border-color: var(--accent); }

  .sentence-panel { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 24px; display: flex; flex-direction: column; gap: 14px; }
  .sentence-display { min-height: 64px; background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; font-family: var(--font-head); font-size: 22px; font-weight: 600; color: var(--text); letter-spacing: 2px; word-break: break-all; line-height: 1.5; }
  .cursor { display: inline-block; width: 2px; height: 22px; background: var(--accent); margin-left: 2px; vertical-align: middle; animation: blink 1s infinite; }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
  .sentence-actions { display: flex; gap: 8px; flex-wrap: wrap; }
  .btn { flex: 1; padding: 9px 12px; border-radius: 8px; border: 1px solid var(--border); background: var(--panel); color: var(--text); font-family: var(--font-mono); font-size: 11px; cursor: pointer; transition: all 0.15s; text-transform: uppercase; letter-spacing: 1px; white-space: nowrap; }
  .btn:hover { border-color: var(--accent); color: var(--accent); background: rgba(0,229,255,0.05); }
  .btn.primary { background: var(--accent); color: var(--bg); border-color: var(--accent); font-weight: 700; }
  .btn.primary:hover { background: #33eaff; }
  .btn.speak-all { border-color: rgba(127,255,110,0.4); color: var(--accent2); background: rgba(127,255,110,0.05); }
  .btn.speak-all:hover { background: rgba(127,255,110,0.12); }
  .btn.danger:hover { border-color: var(--warn); color: var(--warn); background: rgba(255,77,109,0.05); }
  .add-hint { font-family: var(--font-mono); font-size: 10px; color: var(--muted); text-align: center; line-height: 1.8; }
  kbd { background: var(--panel); border: 1px solid var(--border); padding: 1px 5px; border-radius: 4px; font-family: var(--font-mono); font-size: 10px; }

  .history-panel { grid-column: 1 / 3; background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 20px 24px; }
  .history-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; min-height: 44px; align-items: center; }
  .history-chip { display: flex; align-items: center; gap: 6px; padding: 5px 10px; background: var(--panel); border: 1px solid var(--border); border-radius: 6px; font-family: var(--font-mono); font-size: 12px; animation: chipIn 0.2s ease; cursor: pointer; transition: border-color 0.15s; }
  .history-chip:hover { border-color: var(--accent2); }
  @keyframes chipIn { from{transform:scale(0.8) translateY(4px);opacity:0} to{transform:scale(1) translateY(0);opacity:1} }
  .chip-letter { font-weight: 700; color: var(--accent); font-size: 14px; }
  .chip-conf { color: var(--muted); font-size: 10px; }
  .history-empty { font-family: var(--font-mono); font-size: 12px; color: var(--muted); }

  .start-btn { padding: 12px 28px; background: linear-gradient(135deg, var(--accent), var(--accent2)); color: var(--bg); border: none; border-radius: 10px; font-family: var(--font-mono); font-weight: 700; font-size: 13px; cursor: pointer; text-transform: uppercase; letter-spacing: 1.5px; transition: all 0.2s; }
  .start-btn:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(0,229,255,0.25); }
  .backend-notice { background: rgba(0,229,255,0.05); border: 1px solid rgba(0,229,255,0.2); border-radius: 10px; padding: 12px 16px; font-family: var(--font-mono); font-size: 11px; color: var(--muted); line-height: 1.7; }
  .backend-notice b { color: var(--accent); }
`;