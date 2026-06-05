import React from 'react';
import { interpolate, useCurrentFrame, Easing } from 'remotion';

type ProjectFn = (lat: number, lon: number) => { x: number; y: number };

interface CountryScanProps {
  project: ProjectFn;
  countryPath: string;
  frame: number;
  durationInFrames: number;
}

export const CountryScan: React.FC<CountryScanProps> = ({
  project,
  countryPath,
  frame,
  durationInFrames,
}) => {
  const progress = frame / durationInFrames;
  const scanY = interpolate(progress, [0, 1], [0, 1], {
    easing: Easing.inOut(Easing.ease),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const scanOpacity = interpolate(
    Math.sin(progress * Math.PI),
    [0, 1],
    [0.0, 0.8],
  );

  const gradientId = `scan-grad`;

  return (
    <g>
      <defs>
        <linearGradient id={gradientId} x1="0" y1={0} x2="0" y2={1}>
          <stop offset="0%" stopColor="transparent" />
          <stop offset={`${scanY * 100}%`} stopColor="transparent" />
          <stop offset={`${(scanY + 0.02) * 100}%`} stopColor="rgba(100,200,255,0.4)" />
          <stop offset={`${(scanY + 0.06) * 100}%`} stopColor="rgba(100,200,255,0.15)" />
          <stop offset={`${(scanY + 0.12) * 100}%`} stopColor="transparent" />
          <stop offset="100%" stopColor="transparent" />
        </linearGradient>
        <clipPath id="country-clip">
          <path d={countryPath} />
        </clipPath>
        <filter id="scan-glow">
          <feGaussianBlur stdDeviation="6" />
        </filter>
      </defs>

      <rect
        x="-2000"
        y="-2000"
        width="4000"
        height="4000"
        fill={`url(#${gradientId})`}
        clipPath="url(#country-clip)"
        opacity={scanOpacity}
        filter="url(#scan-glow)"
      />
    </g>
  );
};
