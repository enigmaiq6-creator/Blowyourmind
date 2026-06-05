import React from 'react';
import { interpolate, useCurrentFrame, Easing } from 'remotion';

export interface HexIconData {
  latitude: number;
  longitude: number;
  icon: string;
  label?: string;
  value?: string;
  color?: string;
}

export interface RouteWaypoint {
  latitude: number;
  longitude: number;
  zoom: number;
  pitch: number;
  bearing: number;
}

export interface RouteData {
  waypoints: RouteWaypoint[];
  color?: string;
  label?: string;
  dot_labels?: string[];
}

export interface RegionData {
  name: string;
  center_latitude: number;
  center_longitude: number;
  color: string;
  label?: string;
  radius_km?: number;
}

type ProjectFn = (lat: number, lon: number) => { x: number; y: number };

const HEX_SIZE = 44;
const HEX_BORDER = 3;

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

export const HexIconMarker: React.FC<{
  data: HexIconData;
  project: ProjectFn;
  frame: number;
  sceneStartMs: number;
  index: number;
}> = ({ data, project, frame, sceneStartMs, index }) => {
  const pos = project(data.latitude, data.longitude);
  const color = data.color || '#FF0078';
  const delay = index * 10;
  const opacity = interpolate(
    Math.max(frame - delay, 0), [0, 8], [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  if (opacity <= 0) return null;

  const bounce = interpolate(
    Math.max(frame - delay, 0), [0, 12], [20, 0],
    { easing: Easing.out(Easing.back), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  const glowPhase = ((frame + index * 30) % 60) / 60;
  const glowPulse = interpolate(glowPhase, [0, 0.5, 1], [0.6, 1, 0.6], { easing: Easing.inOut(Easing.ease) });

  return (
    <g opacity={opacity} transform={`translate(${pos.x}, ${pos.y + bounce})`}>
      <path
        d={hexPath(0, 0, HEX_SIZE)}
        fill="rgba(10,11,16,0.85)"
        stroke={color}
        strokeWidth={HEX_BORDER}
        strokeOpacity={glowPulse}
        filter={`url(#hex-glow-${index})`}
      />
      <text
        x={0} y={4} textAnchor="middle" dominantBaseline="central"
        fontSize={28} fill="#fff"
      >
        {data.icon}
      </text>
      {data.value && (
        <text
          x={0} y={HEX_SIZE + 18} textAnchor="middle"
          fill={color} fontSize={16} fontWeight={900}
          fontFamily='"Montserrat Black", "Arial Black", sans-serif'
          stroke="#000" strokeWidth={3} paintOrder="stroke"
        >
          {data.value}
        </text>
      )}
      {data.label && (
        <text
          x={0} y={HEX_SIZE + (data.value ? 38 : 18)} textAnchor="middle"
          fill="#fff" fontSize={12} fontWeight={700}
          stroke="#000" strokeWidth={2} paintOrder="stroke"
          letterSpacing="0.05em"
        >
          {data.label}
        </text>
      )}
    </g>
  );
};

function bezierPathD(pts: { x: number; y: number }[]): string {
  if (pts.length < 2) return '';
  if (pts.length === 2) return `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)} L ${pts[1].x.toFixed(1)} ${pts[1].y.toFixed(1)}`;
  let d = `M ${pts[0].x.toFixed(1)} ${pts[0].y.toFixed(1)}`;
  for (let i = 1; i < pts.length; i++) {
    const prev = pts[i - 1];
    const curr = pts[i];
    const next = pts[i + 1] || curr;
    const prev2 = pts[i - 2] || prev;
    const cp1x = prev.x + (curr.x - prev2.x) * 0.25;
    const cp1y = prev.y + (curr.y - prev2.y) * 0.25;
    const cp2x = curr.x - (next.x - prev.x) * 0.25;
    const cp2y = curr.y - (next.y - prev.y) * 0.25;
    d += ` C ${cp1x.toFixed(1)} ${cp1y.toFixed(1)}, ${cp2x.toFixed(1)} ${cp2y.toFixed(1)}, ${curr.x.toFixed(1)} ${curr.y.toFixed(1)}`;
  }
  return d;
}

export const RouteLine: React.FC<{
  data: RouteData;
  project: ProjectFn;
  frame: number;
  durationInFrames: number;
  index: number;
}> = ({ data, project, frame, durationInFrames, index }) => {
  const color = data.color || '#FF0078';
  const wps = data.waypoints;
  if (wps.length < 2) return null;

  const pts = wps.map(wp => project(wp.latitude, wp.longitude));
  const pathD = bezierPathD(pts);
  const totalLength = pts.reduce((acc, p, i) => {
    if (i === 0) return 0;
    const dx = p.x - pts[i - 1].x;
    const dy = p.y - pts[i - 1].y;
    return acc + Math.sqrt(dx * dx + dy * dy);
  }, 0);
  const delay = index * 8;
  const animFrame = Math.max(frame - delay, 0);
  const progress = Math.min(animFrame / (durationInFrames * 0.7), 1);

  return (
    <g>
      <defs>
        <filter id={`route-glow-${index}`}>
          <feGaussianBlur stdDeviation="3" result="blur"/>
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <marker id={`route-head-${index}`} markerWidth="8" markerHeight="6" refX="5" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill={color}/>
        </marker>
      </defs>

      <path
        d={pathD}
        fill="none" stroke={color} strokeWidth={3}
        strokeDasharray={`${progress * totalLength} ${totalLength}`}
        strokeLinecap="round"
        filter={`url(#route-glow-${index})`}
        markerEnd={`url(#route-head-${index})`}
      />

      <path
        d={pathD}
        fill="none" stroke={color} strokeWidth={12}
        strokeDasharray={`4 ${totalLength * 0.15}`}
        strokeDashoffset={-((frame * 3) % (totalLength * 0.15))}
        strokeLinecap="round"
        opacity={0.5}
      />

      {pts.map((p, i) => {
        const dotDelay = delay + (i / pts.length) * durationInFrames * 0.5;
        const dotOp = interpolate(
          Math.max(frame - dotDelay, 0), [0, 6], [0, 1],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        );
        const dotSize = interpolate(
          (frame + i * 15) % 40, [0, 20, 40], [5, 9, 5],
          { easing: Easing.inOut(Easing.ease) }
        );
        return (
          <g key={`rt-dot-${i}`} opacity={dotOp}>
            <circle cx={p.x} cy={p.y} r={dotSize + 4} fill="none" stroke={color} strokeWidth={1.5} opacity={0.3}/>
            <circle cx={p.x} cy={p.y} r={dotSize} fill={color} stroke="#fff" strokeWidth={2}/>
            {data.dot_labels && data.dot_labels[i] && (
              <text
                x={p.x} y={p.y - 16} textAnchor="middle"
                fill="#fff" fontSize={11} fontWeight={700}
                stroke="#000" strokeWidth={3} paintOrder="stroke"
              >
                {data.dot_labels[i]}
              </text>
            )}
          </g>
        );
      })}

      {data.label && (
        <text
          x={pts[Math.floor(pts.length / 2)].x}
          y={pts[Math.floor(pts.length / 2)].y - 28}
          textAnchor="middle"
          fill={color} fontSize={14} fontWeight={900}
          fontFamily='"Montserrat Black", "Arial Black", sans-serif'
          stroke="#000" strokeWidth={4} paintOrder="stroke"
          letterSpacing="0.1em"
        >
          {data.label}
        </text>
      )}
    </g>
  );
};

export const RegionOverlay: React.FC<{
  data: RegionData;
  project: ProjectFn;
  frame: number;
  index: number;
}> = ({ data, project, frame, index }) => {
  const pos = project(data.center_latitude, data.center_longitude);
  const radiusPx = Math.max(20, data.radius_km || 200) * 0.15;
  const delay = index * 6;
  const opacity = interpolate(
    Math.max(frame - delay, 0), [0, 10], [0, 1],
    { easing: Easing.out(Easing.ease), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  const scale = interpolate(
    Math.max(frame - delay, 0), [0, 15], [0.3, 1],
    { easing: Easing.out(Easing.back), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  if (opacity <= 0) return null;

  const color = data.color || '#FF0078';

  return (
    <g opacity={opacity} transform={`translate(${pos.x}, ${pos.y}) scale(${scale})`}>
      <circle cx={0} cy={0} r={radiusPx} fill={color} opacity={0.18} stroke={color} strokeWidth={2} strokeOpacity={0.5}/>
      <circle cx={0} cy={0} r={radiusPx} fill="none" stroke={color} strokeWidth={1} strokeDasharray="6,4" opacity={0.3}/>
      {data.label && (
        <>
          <rect
            x={-80} y={-12} width={160} height={24} rx={4}
            fill="rgba(10,11,16,0.82)" stroke={color} strokeWidth={1.5}
          />
          <text
            x={0} y={6} textAnchor="middle"
            fill={color} fontSize={13} fontWeight={900}
            fontFamily='"Montserrat Black", "Arial Black", sans-serif'
            letterSpacing="0.08em"
          >
            {data.label}
          </text>
        </>
      )}
    </g>
  );
};

export function generateHexGlowFilters(count: number): React.ReactNode[] {
  const filters: React.ReactNode[] = [];
  for (let i = 0; i < count; i++) {
    filters.push(
      <filter key={`hex-glow-${i}`} id={`hex-glow-${i}`} x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="4" result="blur"/>
        <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    );
  }
  return filters;
}
