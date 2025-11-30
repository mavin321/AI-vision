interface Props {
  label?: string;
  confidence?: number;
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
}

export default function GesturePreview({ label, confidence, enabled, onToggle }: Props) {
  return (
    <div className="card">
      <div className="flex" style={{ justifyContent: 'space-between' }}>
        <div>
          <div className="small">Current gesture</div>
          <div className="gesture-label">{label || '—'}</div>
          <div className="small">Confidence: {(confidence ?? 0).toFixed(2)}</div>
        </div>
        <button className="secondary" onClick={() => onToggle(!enabled)}>
          {enabled ? 'Stop' : 'Start'} detection
        </button>
      </div>
    </div>
  );
}
