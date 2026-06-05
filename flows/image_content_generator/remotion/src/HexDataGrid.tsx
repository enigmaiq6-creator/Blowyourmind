import React from 'react';
import { interpolate, useCurrentFrame, useVideoConfig, Easing } from 'remotion';
import { THEME, GRADIENTS } from './VisualIdentity';

interface HexGridItem {
  icon: string;
  label?: string;
  value?: string;
  color?: string;
}

interface HexDataGridProps {
  title?: string;
  items?: HexGridItem[];
  audioDurationMs?: number;
}

const GRID_COLS = 3;
const HEX_W = 200;
const HEX_H = 180;
const GAP_X = 40;
const GAP_Y = 30;

function hexPath(cx: number, cy: number, size: number): string {
  const pts: string[] = [];
  for (let i = 0; i < 6; i++) {
    const angle = (Math.PI / 3) * i - Math.PI / 6;
    const x = cx + size * Math.cos(angle);
    const y = cy + size * Math.sin(angle);
    pts.push(`${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`);
  }
  return pts.join(' ') + ' Z';
}

const ITEM_COLORS = ['#FF0078', '#00DCFF', '#FFE000', '#00D25A', '#C864FF', '#FF8C00'];

export const HexDataGrid: React.FC<HexDataGridProps> = ({
  title = '',
  items = [],
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const progress = frame / durationInFrames;

  const totalItems = items.length > 0 ? items.length : 6;
  const rows = Math.ceil(totalItems / GRID_COLS);
  const gridW = GRID_COLS * (HEX_W + GAP_X) - GAP_X;
  const gridH = rows * (HEX_H + GAP_Y) - GAP_Y;
  const startX = (1080 - gridW) / 2;
  const startY = (1920 - gridH) / 2 + 60;

  return (
    <div style={{
      width: 1080, height: 1920,
      background: 'radial-gradient(ellipse at 50% 50%, #0a0b10 0%, #050508 100%)',
      position: 'relative', overflow: 'hidden',
      fontFamily: THEME.fontFamily,
    }}>
      <div style={{
        position: 'absolute', width: 900, height: 900,
        borderRadius: '50%', top: '50%', left: '50%',
        transform: 'translate(-50%, -50%)',
        background: 'radial-gradient(circle, rgba(255,0,120,0.06) 0%, transparent 70%)',
      }}/>

      {title && (
        <div style={{
          position: 'absolute', top: 120, left: 0, right: 0,
          textAlign: 'center', zIndex: 10,
        }}>
          <div style={{
            color: '#8f9cae', fontSize: 20, fontWeight: 700,
            letterSpacing: 6, textTransform: 'uppercase',
          }}>
            {title}
          </div>
          <div style={{
            width: 60, height: 3,
            background: 'linear-gradient(90deg, transparent, #FF0078, transparent)',
            margin: '16px auto 0',
          }}/>
        </div>
      )}

      <svg
        width={1080} height={1920}
        style={{ position: 'absolute', inset: 0 }}
      >
        <defs>
          {(items.length > 0 ? items : Array(6).fill(null)).map((_, i) => (
            <filter key={`hglow-${i}`} id={`hglow-${i}`} x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="5" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
          ))}
        </defs>

        <g>
        {(items.length > 0 ? items : Array(6).fill(null)).map((_, i) => {
          const col = i % GRID_COLS;
          const row = Math.floor(i / GRID_COLS);
          const cx = startX + col * (HEX_W + GAP_X) + HEX_W / 2;
          const cy = startY + row * (HEX_H + GAP_Y) + HEX_H / 2;
          const col2 = (i + 1) % GRID_COLS;
          const row2 = Math.floor((i + 1) / GRID_COLS);
          const nx = startX + col2 * (HEX_W + GAP_X) + HEX_W / 2;
          const ny = startY + row2 * (HEX_H + GAP_Y) + HEX_H / 2;
          const delay = i * 6;
          const lineOpacity = interpolate(
            Math.max(frame - delay - 5, 0), [0, 15], [0, 0.12],
            { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
          );
          if (lineOpacity > 0 && col + 1 < GRID_COLS) {
            return (
              <line key={`conn-${i}`}
                x1={cx} y1={cy} x2={nx} y2={ny}
                stroke="rgba(255,255,255,0.06)"
                strokeWidth={1}
                strokeDasharray="4,6"
                opacity={lineOpacity}
              />
            );
          }
          return null;
        })}
      </g>

      {(items.length > 0 ? items : Array(6).fill(null)).map((item, i) => {
          const col = i % GRID_COLS;
          const row = Math.floor(i / GRID_COLS);
          const cx = startX + col * (HEX_W + GAP_X) + HEX_W / 2;
          const cy = startY + row * (HEX_H + GAP_Y) + HEX_H / 2;
          const delay = i * 6;
          const opacity = interpolate(
            Math.max(frame - delay, 0), [0, 10], [0, 1],
            { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
          );
          const scale = interpolate(
            Math.max(frame - delay, 0), [0, 14], [0.4, 1],
            { easing: Easing.out(Easing.back), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
          );
          const fillColor = item && (item as HexGridItem).color
            ? (item as HexGridItem).color || ITEM_COLORS[i % ITEM_COLORS.length]
            : ITEM_COLORS[i % ITEM_COLORS.length];
          const pulsePhase = ((frame + i * 20) % 60) / 60;
          const glowPulse = interpolate(pulsePhase, [0, 0.5, 1], [0.5, 1, 0.5], { easing: Easing.inOut(Easing.ease) });

          const matrixBlink = ((frame + i * 11) % 90) > 80;
          const blinkOpacity = matrixBlink ? 0.3 : 1;

          if (opacity <= 0) return null;

          const icon = item ? (item as HexGridItem).icon : '📊';
          const label = item ? (item as HexGridItem).label : '';
          const value = item ? (item as HexGridItem).value : '';

          return (
            <g key={`hex-${i}`} opacity={opacity * blinkOpacity} transform={`translate(${cx}, ${cy}) scale(${scale})`}>
              <path
                d={hexPath(0, 0, HEX_W / 2)}
                fill="rgba(10,11,16,0.75)"
                stroke={fillColor}
                strokeWidth={2.5}
                strokeOpacity={glowPulse}
                filter={`url(#hglow-${i})`}
              />
              <text
                x={0} y={-8} textAnchor="middle" dominantBaseline="central"
                fontSize={36} fill="#fff"
              >
                {icon}
              </text>
              {value && (
                <text
                  x={0} y={30} textAnchor="middle"
                  fill={fillColor} fontSize={20} fontWeight={900}
                  fontFamily='"Arial Black", Inter, sans-serif'
                  stroke="#000" strokeWidth={3} paintOrder="stroke"
                >
                  {value}
                </text>
              )}
              {label && (
                <text
                  x={0} y={HEX_W / 2 + 20} textAnchor="middle"
                  fill="rgba(255,255,255,0.7)" fontSize={11} fontWeight={700}
                  letterSpacing="0.08em"
                >
                  {label}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      <div style={{
        position: 'absolute', inset: 0,
        background: 'radial-gradient(ellipse at center, transparent 30%, rgba(5,5,8,0.85) 100%)',
        pointerEvents: 'none',
      }}/>
    </div>
  );
};
