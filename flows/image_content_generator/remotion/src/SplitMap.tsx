import React from 'react';
import { interpolate, useCurrentFrame, useVideoConfig, Easing } from 'remotion';

interface SplitMapCamera {
  latitude: number;
  longitude: number;
  zoom: number;
  label: string;
}

interface SplitMapProps {
  leftCamera: SplitMapCamera;
  rightCamera: SplitMapCamera;
  leftTitle?: string;
  rightTitle?: string;
  comparisonLabel?: string;
  audioDurationMs?: number;
}

export const SplitMap: React.FC<SplitMapProps> = ({
  leftCamera,
  rightCamera,
  leftTitle = 'THEN',
  rightTitle = 'NOW',
  comparisonLabel = '',
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = frame / durationInFrames;

  const slideIn = interpolate(progress, [0, 0.3], [60, 0], {
    easing: Easing.out(Easing.ease),
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  const getTileUrl = (cam: SplitMapCamera) => {
    const z = Math.floor(cam.zoom);
    const lat = cam.latitude;
    const lon = cam.longitude;
    const x = Math.floor(((lon + 180) / 360) * Math.pow(2, z));
    const latRad = Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360));
    const y = Math.floor((1 - latRad / Math.PI) * Math.pow(2, z - 1));
    return `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${z}/${y}/${x}`;
  };

  const dividerPos = interpolate(progress, [0, 0.5, 1], [0.5, 0.5, 0.3], {
    easing: Easing.inOut(Easing.ease),
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  return (
    <div style={{
      width: 1080, height: 1920,
      position: 'relative', overflow: 'hidden',
      backgroundColor: '#050508', fontFamily: 'Inter, sans-serif',
    }}>
      <div style={{
        position: 'absolute', left: 0, top: 0, bottom: 0,
        width: `${dividerPos * 100}%`, overflow: 'hidden',
      }}>
        <img
          src={getTileUrl(leftCamera)}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          alt="left map"
        />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(135deg, rgba(255,0,120,0.25), transparent)',
        }} />
      </div>

      <div style={{
        position: 'absolute',
        left: `${dividerPos * 100}%`, top: 0, bottom: 0,
        right: 0, overflow: 'hidden',
      }}>
        <img
          src={getTileUrl(rightCamera)}
          style={{
            width: '100%', height: '100%', objectFit: 'cover',
            position: 'absolute', left: `-${dividerPos * 100}%`,
          }}
          alt="right map"
        />
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(225deg, rgba(0,220,255,0.25), transparent)',
        }} />
      </div>

      <div style={{
        position: 'absolute', left: `${dividerPos * 100}%`, top: 0, bottom: 0,
        width: 4,
        background: 'linear-gradient(to bottom, #FF0078, #00DCFF)',
        boxShadow: '0 0 20px rgba(255,0,120,0.5), 0 0 40px rgba(0,220,255,0.3)',
        zIndex: 10,
      }} />

      <div style={{
        position: 'absolute', top: 80, left: 0, right: 0,
        display: 'flex', justifyContent: 'space-between',
        padding: '0 60px', zIndex: 20,
        transform: `translateY(${slideIn}px)`,
      }}>
        <div style={{
          background: 'rgba(10,11,16,0.8)', backdropFilter: 'blur(12px)',
          padding: '16px 32px', borderRadius: 12,
          border: '2px solid #FF0078',
        }}>
          <span style={{
            color: '#FF0078', fontSize: 14, fontWeight: 700,
            letterSpacing: 3, textTransform: 'uppercase',
          }}>
            {leftTitle}
          </span>
          <div style={{ color: '#fff', fontSize: 20, fontWeight: 600, marginTop: 4 }}>
            {leftCamera.label}
          </div>
        </div>
        <div style={{
          background: 'rgba(10,11,16,0.8)', backdropFilter: 'blur(12px)',
          padding: '16px 32px', borderRadius: 12,
          border: '2px solid #00DCFF',
          textAlign: 'right',
        }}>
          <span style={{
            color: '#00DCFF', fontSize: 14, fontWeight: 700,
            letterSpacing: 3, textTransform: 'uppercase',
          }}>
            {rightTitle}
          </span>
          <div style={{ color: '#fff', fontSize: 20, fontWeight: 600, marginTop: 4 }}>
            {rightCamera.label}
          </div>
        </div>
      </div>

      {comparisonLabel && (
        <div style={{
          position: 'absolute', bottom: 120, left: 0, right: 0,
          textAlign: 'center', zIndex: 20,
          transform: `translateY(${-slideIn}px)`,
          opacity: interpolate(progress, [0.5, 0.7], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }),
        }}>
          <div style={{
            display: 'inline-block',
            background: 'rgba(10,11,16,0.85)', backdropFilter: 'blur(16px)',
            padding: '20px 48px', borderRadius: 16,
            border: '2px solid rgba(255,255,255,0.1)',
          }}>
            <span style={{
              color: '#fff', fontSize: 36, fontWeight: 900,
              fontFamily: '"Arial Black", sans-serif',
              textShadow: '0 0 30px rgba(255,0,120,0.3)',
            }}>
              {comparisonLabel}
            </span>
          </div>
        </div>
      )}

      <div style={{
        position: 'absolute', inset: 0,
        background: 'radial-gradient(ellipse at center, transparent 20%, rgba(5,5,8,0.7) 100%)',
        pointerEvents: 'none', zIndex: 5,
      }} />
    </div>
  );
};
