import { useEffect, useState } from 'react';
import { baseURL } from '../api/client';

interface Props {
  active: boolean;
}

export default function WebcamViewer({ active }: Props) {
  const [src, setSrc] = useState<string>('');

  useEffect(() => {
    let timer: number | undefined;
    if (!active) {
      setSrc('');
      return () => {};
    }
    const tick = () => {
      const url = `${baseURL}/api/gesture/frame?ts=${Date.now()}`;
      setSrc(url);
    };
    tick();
    // Pull frames frequently for smoother preview (~20 fps default loop)
    timer = window.setInterval(tick, 50);
    return () => {
      if (timer) window.clearInterval(timer);
    };
  }, [active]);

  return (
    <div className="card">
      <div className="flex" style={{ justifyContent: 'space-between' }}>
        <div>
          <div className="small">Backend preview</div>
          <div className="badge">
            <span className={`status-dot ${active ? '' : 'danger'}`}></span>
            {active ? 'Live' : 'Stopped'}
          </div>
        </div>
      </div>
      <div className="video-frame" style={{ marginTop: 12 }}>
        {src ? (
          <img src={src} alt="preview" style={{ width: '100%', display: 'block' }} />
        ) : (
          <div className="small" style={{ padding: 20, textAlign: 'center' }}>
            Preview disabled
          </div>
        )}
      </div>
    </div>
  );
}
