import { useEffect, useRef, useState } from 'react';

interface Props {
  active: boolean;
}

export default function WebcamViewer({ active }: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let stream: MediaStream | null = null;
    if (!active) {
      return () => {};
    }
    (async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        setError('Unable to access webcam');
        console.error(err);
      }
    })();

    return () => {
      stream?.getTracks().forEach((t) => t.stop());
    };
  }, [active]);

  return (
    <div className="card">
      <div className="flex" style={{ justifyContent: 'space-between' }}>
        <div>
          <div className="small">Webcam preview</div>
          <div className="badge">
            <span className={`status-dot ${active ? '' : 'danger'}`}></span>
            {active ? 'Live' : 'Stopped'}
          </div>
        </div>
      </div>
      <div className="video-frame" style={{ marginTop: 12 }}>
        <video ref={videoRef} autoPlay playsInline muted style={{ width: '100%' }} />
      </div>
      {error && <div className="small" style={{ color: '#f08f6c', marginTop: 8 }}>{error}</div>}
    </div>
  );
}
