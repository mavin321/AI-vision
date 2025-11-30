import React, { useEffect, useState } from 'react';
import WebcamViewer from './components/WebcamViewer';
import GesturePreview from './components/GesturePreview';
import KeyMappingsEditor from './components/KeyMappingsEditor';
import { GestureStatus, connectGestureStream, getGestureStatus, toggleGesture } from './api/client';

function App() {
  const [status, setStatus] = useState<GestureStatus>({ enabled: true });
  const [previewEnabled, setPreviewEnabled] = useState(false);

  useEffect(() => {
    (async () => {
      const data = await getGestureStatus();
      setStatus(data);
    })();
    const ws = connectGestureStream((payload) => {
      setStatus((prev) => ({ ...prev, latest: payload }));
    });
    return () => ws.close();
  }, []);

  const handleToggle = async (enabled: boolean) => {
    const data = await toggleGesture(enabled);
    setStatus(data);
  };

  const current = status.latest;

  return (
    <div className="app-shell">
      <header className="flex" style={{ justifyContent: 'space-between', marginBottom: 18 }}>
        <div>
          <h1>Local AI Vision Keyboard</h1>
          <div className="small">Webcam gestures → keyboard macros. Runs locally.</div>
        </div>
        <div className="badge">
          <span className={`status-dot ${status.enabled ? '' : 'danger'}`}></span>
          {status.enabled ? 'Detecting' : 'Paused'}
        </div>
      </header>
      <div className="grid">
        <WebcamViewer active={status.enabled && previewEnabled} />
        <GesturePreview
          label={current?.label}
          confidence={current?.confidence}
          enabled={status.enabled}
          onToggle={handleToggle}
        />
      </div>
      <div style={{ marginTop: 16 }}>
        <KeyMappingsEditor />
      </div>
      <div style={{ marginTop: 12 }} className="flex">
        <button className="secondary" onClick={() => setPreviewEnabled((v) => !v)}>
          {previewEnabled ? 'Disable local preview' : 'Enable local preview'}
        </button>
        <span className="small">Keep preview off if it conflicts with backend camera access.</span>
      </div>
    </div>
  );
}

export default App;
