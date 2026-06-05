import React from 'react';
import { interpolate, Easing } from 'remotion';
import { THEME } from './VisualIdentity';

export interface LowerThirdItem {
  icon: string;
  label: string;
  value: string;
  color?: string;
}

interface LowerThirdProps {
  items: LowerThirdItem[];
  frame: number;
  progress: number;
}

export const LowerThird: React.FC<LowerThirdProps> = ({ items, progress }) => {
  if (!items.length) return null;

  const cycleMs = 5000;
  const currentMs = progress * cycleMs * items.length;
  const itemIdx = Math.min(
    Math.floor(currentMs / cycleMs),
    items.length - 1
  );
  const itemProgress = (currentMs % cycleMs) / cycleMs;

  const visible = itemProgress < 0.75;
  const slideIn = interpolate(
    Math.min(itemProgress / 0.12, 1),
    [0, 1],
    [20, 0],
    { easing: Easing.out(Easing.ease), extrapolateLeft: 'clamp' }
  );
  const fadeOut = interpolate(
    Math.max((itemProgress - 0.65) / 0.1, 0),
    [0, 1],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );

  const item = items[itemIdx];
  const color = item.color || THEME.accent;

  if (!visible) return null;

  return (
    <div style={{
      position: 'absolute', bottom: 320, left: 40, zIndex: 200,
      opacity: fadeOut,
      transform: `translateX(${slideIn}px)`,
      pointerEvents: 'none',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 10,
      }}>
        <div style={{
          width: 3, height: 32,
          background: color, borderRadius: 2, opacity: 0.5,
        }} />
        <span style={{
          fontSize: 22, lineHeight: 1,
        }}>
          {item.icon}
        </span>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
        }}>
          <span style={{
            color: THEME.textSecondary,
            fontSize: 10,
            fontWeight: 700,
            letterSpacing: 2,
            textTransform: 'uppercase',
          }}>
            {item.label}
          </span>
          <span style={{
            color: THEME.textPrimary,
            fontSize: 24,
            fontWeight: 900,
            fontFamily: THEME.fontFamily,
            lineHeight: 1.1,
            textShadow: '0 2px 4px rgba(0,0,0,0.8)',
          }}>
            {item.value}
          </span>
        </div>
      </div>
    </div>
  );
};
