import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';
import { LayoutStack, MeasuredText, type MeasuredTextProps } from './LayoutStack';

interface SceneOverlayData {
  type?: string;
  text?: string;
  subtext?: string;
  year?: number;
  percentage?: number;
  cost?: string;
  co2?: string;
  since?: number;
  icons?: string[];
  flags?: string[];
}

interface SceneOverlayProps {
  data?: SceneOverlayData;
  currentMs: number;
}

const THEME_COLORS: Record<string, string> = {
  title: '#4ADE80',
  nightmare: '#FF4444',
  takeover: '#00B4D8',
  construction: '#FFD700',
  trade: '#FFB800',
  expansion: '#4ADE80',
  environment: '#00DCFF',
  legacy: '#FFD700',
};

function BigNumber({ value, label, color = '#FFD700' }: { value: string; label?: string; color?: string }) {
  const frame = useCurrentFrame();
  const scale = spring({ frame, fps: 30, config: { damping: 10, stiffness: 80 } });
  return (
    <div style={{ margin: '8px 0', transform: `scale(${scale})`, opacity: Math.min(1, frame / 15), width: '100%', textAlign: 'center' }}>
      <MeasuredText text={value} maxFontSize={80} minFontSize={28} color={color} />
      {label && (
        <div style={{ fontSize: 22, fontWeight: 700, color: 'rgba(255,255,255,0.8)', letterSpacing: 2, marginTop: 4 }}>
          {label}
        </div>
      )}
    </div>
  );
}

function YearDisplay({ year }: { year: number }) {
  const frame = useCurrentFrame();
  const digits = String(year).split('');
  const MAX_DIGITS = 8;
  const fontSize = 96;
  const letterSpacing = 8;
  return (
    <div style={{ fontSize, color: '#FFD700', textAlign: 'center', letterSpacing, lineHeight: 1.1 }}>
      {digits.slice(0, MAX_DIGITS).map((d, i) => {
        const delay = i * 3;
        const y = spring({ frame: Math.max(0, frame - delay), fps: 30, config: { damping: 14, stiffness: 120 } });
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              fontWeight: 900,
              textShadow: '0 0 30px rgba(255,215,0,0.6)',
              transform: `translateY(${(1 - y) * -40}px)`,
              opacity: Math.min(1, Math.max(0, frame - delay) / 10),
            }}
          >
            {d}
          </span>
        );
      })}
    </div>
  );
}

const FLAG_COLORS: Record<string, { bg: string; fg: string }> = {
  USA: { bg: '#00FF00', fg: '#ffffff' },
  Panama: { bg: '#FF0000', fg: '#ffffff' },
  Colombia: { bg: '#FFD700', fg: '#000000' },
};

const ICON_STYLE: React.CSSProperties = {
  display: 'inline-block',
  fontSize: 40,
  margin: '0 12px',
  filter: 'drop-shadow(0 0 8px rgba(255,255,255,0.5))',
};

export const SceneOverlay: React.FC<SceneOverlayProps> = ({ data, currentMs }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  if (!data || !data.type) return null;

  const themeColor = THEME_COLORS[data.type] || '#FFFFFF';

  const knownTypes = ['title', 'nightmare', 'takeover', 'construction', 'trade', 'expansion', 'environment', 'legacy'];
  const isKnown = knownTypes.includes(data.type);

  if (!isKnown) {
    return (
      <AbsoluteFill style={{ zIndex: 160, pointerEvents: 'none' }}>
        <LayoutStack items={[{
          key: 'generic',
          height: 80,
          render: () => (
            <div style={{ textTransform: 'uppercase', textAlign: 'center' }}>
              <MeasuredText text={data.type || ''} maxFontSize={72} minFontSize={32} color={themeColor} />
            </div>
          ),
        }]} zone="top" />
      </AbsoluteFill>
    );
  }

  const items: Array<{
    key: string;
    render: (opts: { opacity: number; frame: number }) => React.ReactNode;
    height: number;
    marginTop?: number;
  }> = [];

  switch (data.type) {
    case 'title':
      if (data.subtext) {
        items.push({
          key: 'subtext',
          height: 36,
          render: () => (
            <div style={{ fontSize: 26, color: themeColor, letterSpacing: 6, textAlign: 'center', fontWeight: 700 }}>
              {data.subtext}
            </div>
          ),
        });
      }
      items.push({
        key: 'text',
        height: 90,
        render: () => <BigNumber value={data.text || ''} color={themeColor} />,
      });
      break;

    case 'nightmare':
      items.push({
        key: 'label',
        height: 72,
        render: () => (
          <div style={{ fontSize: 56, color: '#FF4444', fontWeight: 900, textAlign: 'center', textShadow: '0 0 40px rgba(255,68,68,0.3)' }}>
            NIGHTMARE
          </div>
        ),
      });
      if (data.icons?.length) {
        items.push({
          key: 'icons',
          height: 60,
          render: () => (
            <div style={{ textAlign: 'center' }}>
              {data.icons!.map((icon, i) => {
                const delay = i * 5;
                const s = spring({ frame: Math.max(0, frame - delay), fps: 30, config: { damping: 8, stiffness: 60 } });
                return (
                  <span key={i} style={{ ...ICON_STYLE, transform: `scale(${s})`, opacity: Math.min(1, (frame - delay) / 15) }}>
                    {icon}
                  </span>
                );
              })}
            </div>
          ),
        });
      }
      break;

    case 'takeover':
      items.push({
        key: 'year',
        height: 100,
        render: () => <YearDisplay year={1903} />,
      });
      items.push({
        key: 'label',
        height: 40,
        render: () => (
          <div style={{ color: '#00B4D8', fontSize: 30, fontWeight: 700, letterSpacing: 4, textAlign: 'center', margin: '4px 0' }}>
            US TAKEOVER
          </div>
        ),
      });
      if (data.flags?.length) {
        items.push({
          key: 'flags',
          height: 50,
          render: () => (
            <div style={{ display: 'flex', justifyContent: 'center', gap: 16 }}>
              {data.flags!.map((flag, i) => {
                const fc = FLAG_COLORS[flag];
                const delay = i * 5;
                const s = spring({ frame: Math.max(0, frame - delay), fps: 30, config: { damping: 10, stiffness: 80 } });
                return (
                  <div key={i} style={{
                    width: 56, height: 36, borderRadius: 4,
                    backgroundColor: fc?.bg || '#333',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: fc?.fg || 'white', fontWeight: 900, fontSize: 12,
                    transform: `scale(${s})`,
                    boxShadow: '0 2px 12px rgba(0,0,0,0.5)',
                  }}>
                    {flag}
                  </div>
                );
              })}
            </div>
          ),
        });
      }
      break;

    case 'construction':
      items.push({
        key: 'label',
        height: 32,
        render: () => (
          <div style={{ fontSize: 22, color: '#00DCFF', letterSpacing: 4, textAlign: 'center', fontWeight: 700 }}>
            FIRST TRANSIT
          </div>
        ),
      });
      items.push({
        key: 'year',
        height: 100,
        render: () => <YearDisplay year={data.year || 1914} />,
      });
      items.push({
        key: 'ship',
        height: 28,
        render: () => (
          <div style={{ fontSize: 18, color: 'rgba(255,255,255,0.7)', textAlign: 'center', letterSpacing: 2 }}>
            SS ANCON
          </div>
        ),
      });
      break;

    case 'trade':
      items.push({
        key: 'percentage',
        height: 90,
        render: () => <BigNumber value={`${data.percentage || 0}%`} label="OF GLOBAL TRADE" color="#FFB800" />,
      });
      items.push({
        key: 'detail',
        height: 24,
        render: () => (
          <div style={{ fontSize: 16, color: 'rgba(255,255,255,0.6)', textAlign: 'center', letterSpacing: 2 }}>
            14,000 SHIPS • $2.5B/YEAR
          </div>
        ),
      });
      break;

    case 'expansion':
      items.push({
        key: 'label',
        height: 36,
        render: () => (
          <div style={{ fontSize: 26, color: '#4ADE80', letterSpacing: 6, textAlign: 'center', fontWeight: 700 }}>
            EXPANSION
          </div>
        ),
      });
      items.push({
        key: 'year',
        height: 100,
        render: () => <YearDisplay year={data.year || 2016} />,
      });
      items.push({
        key: 'cost',
        height: 90,
        render: () => <BigNumber value={`$${data.cost || '5.4B'}`} label="INVESTMENT" color="#FFD700" />,
      });
      break;

    case 'environment':
      items.push({
        key: 'value',
        height: 90,
        render: () => <BigNumber value={`${data.co2 || '500M'}`} label="TONS CO2 SAVED / YEAR" color="#00DCFF" />,
      });
      break;

    case 'legacy':
      items.push({
        key: 'since',
        height: 32,
        render: () => (
          <div style={{ fontSize: 22, color: '#FFD700', letterSpacing: 6, textAlign: 'center', fontWeight: 700 }}>
            SINCE {data.since || 1914}
          </div>
        ),
      });
      items.push({
        key: 'main',
        height: 56,
        render: () => <MeasuredText text="1 MILLION+ SHIPS" maxFontSize={46} minFontSize={24} />,
      });
      items.push({
        key: 'tagline',
        height: 28,
        render: () => (
          <div style={{ fontSize: 18, color: 'rgba(255,255,255,0.7)', textAlign: 'center', letterSpacing: 2 }}>
            THE CANAL THAT CHANGED THE WORLD
          </div>
        ),
      });
      break;
  }

  return (
    <AbsoluteFill style={{ zIndex: 160, pointerEvents: 'none' }}>
      <LayoutStack items={items} zone="top" />
    </AbsoluteFill>
  );
};
