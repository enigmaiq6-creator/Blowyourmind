import React from 'react';
import { interpolate, useCurrentFrame, useVideoConfig } from 'remotion';

const PADDING = 20;
const MIN_MARGIN = 16;

interface StackItem {
  key: string;
  render: (opts: { opacity: number; frame: number }) => React.ReactNode;
  height: number;
  marginTop?: number;
}

interface LayoutStackProps {
  items: StackItem[];
  style?: React.CSSProperties;
  align?: 'center' | 'flex-start' | 'flex-end';
  zone?: 'top' | 'middle' | 'bottom';
}

const ZONE_TOP = 'top';
const ZONE_CENTER = 'middle';
const ZONE_BOTTOM = 'bottom';

export const LayoutStack: React.FC<LayoutStackProps> = ({
  items,
  style,
  align = 'center',
  zone = 'top',
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const progress = frame / durationInFrames;
  const opacity = interpolate(progress, [0, 0.04, 0.85, 0.95], [0, 1, 1, 0]);

  const getZoneStyle = (): React.CSSProperties => {
    switch (zone) {
      case 'top':
        return { top: 60, bottom: 'auto' };
      case 'middle':
        return { top: '50%', bottom: 'auto', transform: 'translateY(-50%)' };
      case 'bottom':
        return { top: 'auto', bottom: 180 };
    }
  };

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        right: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: align,
        justifyContent: 'flex-start',
        padding: PADDING,
        gap: MIN_MARGIN,
        pointerEvents: 'none',
        zIndex: 160,
        opacity,
        ...getZoneStyle(),
        ...style,
      }}
    >
      {items.map((item) => (
        <div
          key={item.key}
          style={{
            width: '100%',
            maxWidth: '92%',
            marginTop: item.marginTop ?? 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: align,
          }}
        >
          {item.render({ opacity, frame })}
        </div>
      ))}
    </div>
  );
};

export const autoScaleFontSize = (
  text: string,
  maxWidth: number,
  maxFontSize: number,
  minFontSize: number = 24,
  charWidthEstimate: number = 14
): number => {
  const estimatedWidth = text.length * charWidthEstimate;
  if (estimatedWidth <= maxWidth) return maxFontSize;
  const scaled = Math.floor((maxWidth / estimatedWidth) * maxFontSize);
  return Math.max(minFontSize, scaled);
};

export interface MeasuredTextProps {
  text: string;
  maxWidth?: number;
  maxFontSize?: number;
  minFontSize?: number;
  weight?: number;
  color?: string;
  className?: string;
}

export const MeasuredText: React.FC<MeasuredTextProps> = ({
  text,
  maxWidth = 920,
  maxFontSize = 80,
  minFontSize = 20,
  weight = 900,
  color = '#ffffff',
}) => {
  const fontSize = autoScaleFontSize(text, maxWidth, maxFontSize, minFontSize);

  return (
    <span
      style={{
        fontSize,
        fontWeight: weight,
        color,
        textAlign: 'center',
        lineHeight: 1.15,
        wordBreak: 'break-word',
        maxWidth: '100%',
        textShadow: '0 2px 20px rgba(0,0,0,0.8), 0 0 40px rgba(0,0,0,0.5)',
      }}
    >
      {text}
    </span>
  );
};
