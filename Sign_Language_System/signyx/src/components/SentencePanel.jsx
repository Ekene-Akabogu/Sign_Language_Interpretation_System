/**
 * SentencePanel
 * Shows: sentence display, Add/Speak/Copy/Clear buttons, keyboard hints
 *
 * Props:
 *   sentence   {string}
 *   onAdd      {fn()}   — adds current sign to sentence
 *   onSpeak    {fn()}   — speaks full sentence aloud
 *   onCopy     {fn()}   — copies sentence to clipboard
 *   onClear    {fn()}   — clears sentence
 */
export default function SentencePanel({ sentence, onAdd, onSpeak, onCopy, onClear }) {
  return (
    <div className="sentence-panel">
      <div className="panel-title">Sentence Builder</div>

      {/* Sentence display */}
      <div className="sentence-display">
        {sentence ? (
          <>
            {sentence}
            <span className="cursor" />
          </>
        ) : (
          <span style={{ color: "var(--muted)", fontSize: "14px", fontFamily: "var(--font-mono)" }}>
            Start signing to build a sentence...
          </span>
        )}
      </div>

      {/* Action buttons */}
      <div className="sentence-actions">
        <button className="btn primary"   onClick={onAdd}>+ Add Sign</button>
        <button className="btn speak-all" onClick={onSpeak}>▶ Speak</button>
        <button className="btn"           onClick={onCopy}>Copy</button>
        <button className="btn danger"    onClick={onClear}>Clear</button>
      </div>

      {/* Keyboard shortcut hints */}
      <div className="add-hint">
        <kbd>Space</kbd> Add &nbsp;·&nbsp;
        <kbd>Ctrl+Enter</kbd> Speak &nbsp;·&nbsp;
        <br/>
        <kbd>Ctrl+c</kbd> Copy&nbsp;·&nbsp;
        <kbd>Ctrl+⌫</kbd> Clear
      </div>
    </div>
  );
}