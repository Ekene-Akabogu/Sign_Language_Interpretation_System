/**
 * HistoryPanel
 * Shows: scrollable list of recent prediction chips
 *        each chip is clickable to hear the sign spoken
 *
 * Props:
 *   history      {Array<{id, sign, conf}>}
 *   onChipClick  {fn(sign)}
 */
export default function HistoryPanel({ history, onChipClick }) {
  return (
    <div className="history-panel">
      <div className="panel-title">
        Prediction History — click any chip to hear it
      </div>

      <div className="history-row">
        {history.length === 0 ? (
          <span className="history-empty">
            No predictions yet — start signing!
          </span>
        ) : (
          [...history].reverse().map(h => (
            <div
              key={h.id}
              className="history-chip"
              onClick={() => onChipClick(h.sign)}
            >
              <span className="chip-letter">{h.sign}</span>
              <span className="chip-conf">{Math.round(h.conf * 100)}%</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}