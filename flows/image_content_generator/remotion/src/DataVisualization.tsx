import React from 'react';
import { interpolate, useCurrentFrame, useVideoConfig, Easing } from 'remotion';

interface DataPoint {
  label: string;
  value: number;
  color?: string;
}

interface DataVizProps {
  chartType?: 'bar' | 'number_counter' | 'globe_stat';
  title?: string;
  dataPoints?: DataPoint[];
  mainValue?: string;
  mainLabel?: string;
  subtitle?: string;
  audioDurationMs?: number;
}

const COLORS = ['#FF0078', '#00DCFF', '#FFE000', '#00D25A', '#C864FF'];

export const DataVisualization: React.FC<DataVizProps> = ({
  chartType = 'number_counter',
  title = '',
  dataPoints = [],
  mainValue = '',
  mainLabel = '',
  subtitle = '',
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();
  const progress = frame / durationInFrames;

  if (chartType === 'bar') {
    return (
      <div style={{
        width: 1080, height: 1920,
        background: 'linear-gradient(135deg, #0a0b10 0%, #1a0a2e 100%)',
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        padding: 80, fontFamily: 'Inter, sans-serif',
      }}>
        {title && (
          <div style={{
            color: '#8f9cae', fontSize: 24, fontWeight: 700,
            letterSpacing: 4, textTransform: 'uppercase',
            marginBottom: 60, textAlign: 'center',
          }}>
            {title}
          </div>
        )}
        <div style={{
          display: 'flex', gap: 40, alignItems: 'flex-end',
          height: 600, padding: '0 40px',
        }}>
          {(dataPoints.length > 0 ? dataPoints : [
            { label: 'DATA A', value: 75 },
            { label: 'DATA B', value: 50 },
            { label: 'DATA C', value: 90 },
            { label: 'DATA D', value: 30 },
          ]).map((dp, i) => {
            const delay = i * 5;
            const animProgress = interpolate(
              Math.max(frame - delay, 0),
              [0, 20],
              [0, dp.value / 100],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.back) }
            );
            const color = dp.color || COLORS[i % COLORS.length];
            return (
              <div key={i} style={{
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', gap: 16, flex: 1,
              }}>
                <span style={{
                  color: '#fff', fontSize: 28, fontWeight: 900,
                  fontFamily: '"Arial Black", sans-serif',
                }}>
                  {Math.round(animProgress * 100)}%
                </span>
                <div style={{
                  width: '100%', maxWidth: 120, borderRadius: 12,
                  background: 'rgba(255,255,255,0.05)',
                  height: 400, position: 'relative', overflow: 'hidden',
                }}>
                  <div style={{
                    position: 'absolute', bottom: 0, left: 0, right: 0,
                    height: `${animProgress * 400}px`,
                    background: `linear-gradient(to top, ${color}, ${color}88)`,
                    borderRadius: 12,
                    boxShadow: `0 0 30px ${color}44`,
                    transition: 'height 0.1s ease',
                  }} />
                </div>
                <span style={{
                  color: '#8f9cae', fontSize: 18, fontWeight: 600,
                  textTransform: 'uppercase', letterSpacing: 2,
                }}>
                  {dp.label}
                </span>
              </div>
            );
          })}
        </div>
        {subtitle && (
          <div style={{
            color: 'rgba(255,255,255,0.5)', fontSize: 18, marginTop: 60,
            textAlign: 'center', maxWidth: 800,
          }}>
            {subtitle}
          </div>
        )}
      </div>
    );
  }

  const countUp = interpolate(progress, [0, 0.8], [0, 1], {
    easing: Easing.out(Easing.ease),
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  const parsedMain = mainValue ? parseFloat(mainValue.replace(/[^0-9.-]/g, '')) : 0;
  const displayNum = Math.round(parsedMain * countUp).toLocaleString();
  const suffix = mainValue.replace(/[0-9.,\s]/g, '').trim();

  return (
    <div style={{
      width: 1080, height: 1920,
      background: 'radial-gradient(ellipse at center, #0a0b10 0%, #050508 100%)',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Inter, sans-serif', position: 'relative',
      overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', width: 800, height: 800,
        borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(255,0,120,0.08) 0%, transparent 70%)',
        top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
      }} />
      {title && (
        <div style={{
          color: '#8f9cae', fontSize: 20, fontWeight: 700,
          letterSpacing: 5, textTransform: 'uppercase',
          marginBottom: 20, zIndex: 2,
        }}>
          {title}
        </div>
      )}
      <div style={{
        fontSize: 140, fontWeight: 900,
        fontFamily: '"Arial Black", Inter, sans-serif',
        color: '#fff',
        textShadow: '0 0 40px rgba(255,0,120,0.4), 0 0 120px rgba(255,0,120,0.15)',
        zIndex: 2,
        lineHeight: 1,
      }}>
        {displayNum}
        {suffix && (
          <span style={{ fontSize: 60, color: '#FF0078', marginLeft: 10 }}>
            {suffix}
          </span>
        )}
      </div>
      {mainLabel && (
        <div style={{
          color: 'rgba(255,255,255,0.7)', fontSize: 28, fontWeight: 600,
          marginTop: 20, zIndex: 2, textTransform: 'uppercase',
          letterSpacing: 3,
        }}>
          {mainLabel}
        </div>
      )}
      {subtitle && (
        <div style={{
          color: 'rgba(255,255,255,0.4)', fontSize: 18, marginTop: 40,
          textAlign: 'center', maxWidth: 700, zIndex: 2, lineHeight: 1.5,
        }}>
          {subtitle}
        </div>
      )}
      <div style={{
        position: 'absolute', inset: 0,
        background: 'radial-gradient(ellipse at center, transparent 30%, rgba(5,5,8,0.8) 100%)',
        zIndex: 1,
      }} />
    </div>
  );
};
