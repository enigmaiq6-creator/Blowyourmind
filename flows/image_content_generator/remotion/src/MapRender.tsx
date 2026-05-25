import React from 'react';
import { interpolate, useCurrentFrame, useVideoConfig } from 'remotion';

interface MapProps {
  latitude: number;
  longitude: number;
  zoom: number;
  pitch: number;
  bearing: number;
  highlightRegion?: string;
  arrowDirection?: string;
  floatingLabel?: string;
}

// Slippy Map Web Mercator formulas
function latRad(lat: number) {
  const sin = Math.sin((lat * Math.PI) / 180);
  const radX2 = Math.log((1 + sin) / (1 - sin)) / 2;
  return Math.max(Math.min(radX2, Math.PI), -Math.PI) / 2;
}

function getTileX(lon: number, zoom: number) {
  return ((lon + 180) / 360) * Math.pow(2, zoom);
}

function getTileY(lat: number, zoom: number) {
  return (0.5 - latRad(lat) / Math.PI) * Math.pow(2, zoom);
}

// Simplified regional coordinates for glowing outlines
const REGIONS: Record<string, { lat: number; lon: number }[]> = {
  colombia: [
    { lat: 12.4, lon: -71.7 },
    { lat: 11.2, lon: -74.2 },
    { lat: 10.4, lon: -75.3 },
    { lat: 8.4, lon: -76.8 },
    { lat: 7.2, lon: -77.9 },
    { lat: 1.4, lon: -78.8 },
    { lat: 0.8, lon: -77.5 },
    { lat: -0.1, lon: -75.2 },
    { lat: -4.2, lon: -69.9 },
    { lat: 1.2, lon: -66.9 },
    { lat: 6.2, lon: -67.4 },
    { lat: 6.2, lon: -72.0 },
    { lat: 9.1, lon: -72.9 },
    { lat: 12.2, lon: -72.2 },
    { lat: 12.4, lon: -71.7 } // Close polygon
  ],
  andes: [
    { lat: -15.0, lon: -69.0 },
    { lat: -10.0, lon: -76.0 },
    { lat: -5.0, lon: -79.0 },
    { lat: 0.0, lon: -78.5 },
    { lat: 3.0, lon: -76.5 },
    { lat: 8.0, lon: -73.0 }
  ],
  amazonas: [
    { lat: -4.2, lon: -69.9 },
    { lat: -8.0, lon: -65.0 },
    { lat: -3.0, lon: -60.0 },
    { lat: 2.0, lon: -62.0 },
    { lat: 1.0, lon: -67.0 },
    { lat: -1.0, lon: -72.0 },
    { lat: -4.2, lon: -69.9 }
  ]
};

export const MapRender: React.FC<MapProps> = ({
  latitude,
  longitude,
  zoom,
  pitch,
  bearing,
  highlightRegion = 'none',
  arrowDirection = 'none',
  floatingLabel = 'none'
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // 1. Continuous camera flight animations (Cinematic)
  const animatedZoom = interpolate(frame, [0, durationInFrames], [zoom, zoom + 0.5], {
    extrapolateRight: 'clamp'
  });
  
  const animatedBearing = interpolate(frame, [0, durationInFrames], [bearing, bearing + 12], {
    extrapolateRight: 'clamp'
  });

  const animatedPitch = interpolate(frame, [0, durationInFrames], [pitch, pitch - 5], {
    extrapolateRight: 'clamp'
  });

  // Base map zoom settings for tiles
  const baseZoom = Math.floor(animatedZoom);
  const TILE_SIZE = 256;
  const numTiles = 5; // 5x5 Grid covers the screen nicely when rotated/tilted

  // Target Mercator position
  const targetX = getTileX(longitude, baseZoom);
  const targetY = getTileY(latitude, baseZoom);

  const centerTileX = Math.floor(targetX);
  const centerTileY = Math.floor(targetY);

  // Sub-pixel offsets for centering the coordinate on screen
  const offsetX = (targetX - centerTileX) * TILE_SIZE;
  const offsetY = (targetY - centerTileY) * TILE_SIZE;

  // Grid boundaries
  const startTileX = centerTileX - Math.floor(numTiles / 2);
  const startTileY = centerTileY - Math.floor(numTiles / 2);

  // Projection function: Convert lat/lon to pixels relative to map center
  const project = (lat: number, lon: number) => {
    const x = getTileX(lon, baseZoom) * TILE_SIZE;
    const y = getTileY(lat, baseZoom) * TILE_SIZE;
    
    // Pixel offset from the target coordinate
    const rx = x - targetX * TILE_SIZE;
    const ry = y - targetY * TILE_SIZE;
    return { x: rx, y: ry };
  };

  // Render tile images
  const tiles: React.ReactNode[] = [];
  for (let i = 0; i < numTiles; i++) {
    for (let j = 0; j < numTiles; j++) {
      const tileX = startTileX + i;
      const tileY = startTileY + j;
      
      // Calculate tile position relative to grid center
      const posX = (i - Math.floor(numTiles / 2)) * TILE_SIZE - offsetX;
      const posY = (j - Math.floor(numTiles / 2)) * TILE_SIZE - offsetY;

      // ESRI World Imagery (Beautiful Global Satellite Tiles, High-Res, No Key Needed)
      const tileUrl = `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${baseZoom}/${tileY}/${tileX}`;

      tiles.push(
        <img
          key={`${tileX}-${tileY}`}
          src={tileUrl}
          style={{
            position: 'absolute',
            left: posX + (numTiles * TILE_SIZE) / 2,
            top: posY + (numTiles * TILE_SIZE) / 2,
            width: TILE_SIZE,
            height: TILE_SIZE,
            border: 'none',
            outline: 'none',
            display: 'block'
          }}
          alt="Satellite Tile"
        />
      );
    }
  }

  // Draw Highlighted Region Outlines
  const regionName = highlightRegion.toLowerCase().trim();
  const activeRegionCoords = REGIONS[regionName];
  let regionPathData = '';
  
  if (activeRegionCoords) {
    const projectedPoints = activeRegionCoords.map(c => project(c.lat, c.lon));
    const startPoint = projectedPoints[0];
    if (startPoint) {
      const scaleFactor = Math.pow(2, animatedZoom - baseZoom);
      const points = projectedPoints.map(p => ({
        x: p.x * scaleFactor + (numTiles * TILE_SIZE) / 2,
        y: p.y * scaleFactor + (numTiles * TILE_SIZE) / 2
      }));
      
      if (regionName === 'andes') {
        // Line-based region (Andes mountain range)
        regionPathData = `M ${points[0].x} ${points[0].y} ` + points.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ');
      } else {
        // Polygon-based region
        regionPathData = `M ${points[0].x} ${points[0].y} ` + points.slice(1).map(p => `L ${p.x} ${p.y}`).join(' ') + ' Z';
      }
    }
  }

  // Draw Wind/Barrier Arrow
  let arrowPathData = '';
  const isArrowActive = arrowDirection !== 'none';
  if (isArrowActive) {
    const scaleFactor = Math.pow(2, animatedZoom - baseZoom);
    // Draw an arrow pointing from ocean to mountains/land (default: Pacific to Colombia)
    const arrowStart = project(latitude - 1.0, longitude - 3.0); // South-West (Pacific Ocean)
    const arrowEnd = project(latitude, longitude); // Center target
    
    const pStart = {
      x: arrowStart.x * scaleFactor + (numTiles * TILE_SIZE) / 2,
      y: arrowStart.y * scaleFactor + (numTiles * TILE_SIZE) / 2
    };
    const pEnd = {
      x: arrowEnd.x * scaleFactor + (numTiles * TILE_SIZE) / 2,
      y: arrowEnd.y * scaleFactor + (numTiles * TILE_SIZE) / 2
    };

    arrowPathData = `M ${pStart.x} ${pStart.y} L ${pEnd.x} ${pEnd.y}`;
  }

  // Neon color system based on selected region
  const neonColor = regionName === 'colombia' 
    ? '#00ffff'  // Cyan neon
    : regionName === 'andes'
    ? '#ffaa00'  // Golden mountain ridge
    : regionName === 'amazonas'
    ? '#39ff14'  // Lime green forest glow
    : '#ff007f'; // Hot pink default

  // Radar pulse animation
  const pulseScale = interpolate(frame % 45, [0, 45], [0.1, 1.8]);
  const pulseOpacity = interpolate(frame % 45, [0, 30, 45], [0.8, 0.4, 0]);

  return (
    <div
      style={{
        flex: 1,
        backgroundColor: '#0a0b10',
        width: 1080,
        height: 1920,
        position: 'relative',
        overflow: 'hidden',
        fontFamily: "'Inter', sans-serif"
      }}
    >
      {/* 3D Map Transform Wrapper */}
      <div
        style={{
          position: 'absolute',
          width: numTiles * TILE_SIZE,
          height: numTiles * TILE_SIZE,
          left: '50%',
          top: '50%',
          marginLeft: -(numTiles * TILE_SIZE) / 2,
          marginTop: -(numTiles * TILE_SIZE) / 2,
          transform: `perspective(1200px) rotateX(${animatedPitch}deg) rotateZ(${animatedBearing}deg) scale(${Math.pow(2, animatedZoom - baseZoom)})`,
          transformStyle: 'preserve-3d'
        }}
      >
        {/* Render Satellite Tiles */}
        <div style={{ position: 'absolute', inset: 0 }}>{tiles}</div>

        {/* Vector Overlay Layer (Borders and Arrows) */}
        <svg
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            pointerEvents: 'none',
            overflow: 'visible',
            zIndex: 10
          }}
        >
          <defs>
            {/* Glow Filter for Premium Neon Aesthetic */}
            <filter id="neon-glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="8" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            
            {/* Arrowhead marker */}
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="6"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#ff007f" />
            </marker>
          </defs>

          {/* Glowing Region Outline */}
          {regionPathData && (
            <path
              d={regionPathData}
              fill={regionName === 'andes' ? 'none' : `${neonColor}22`} // Transparent inside fill
              stroke={neonColor}
              strokeWidth={regionName === 'andes' ? 8 : 4}
              strokeLinecap="round"
              strokeLinejoin="round"
              filter="url(#neon-glow)"
              style={{
                boxShadow: '0 0 15px rgba(0,0,0,0.5)'
              }}
            />
          )}

          {/* Animated Directional / Weather Arrow */}
          {arrowPathData && (
            <path
              d={arrowPathData}
              fill="none"
              stroke="#ff007f"
              strokeWidth="6"
              strokeDasharray="15, 10"
              strokeDashoffset={frame * 2} // Animate flow direction
              markerEnd="url(#arrowhead)"
              filter="url(#neon-glow)"
            />
          )}

          {/* Target Location Pulse */}
          <circle
            cx={(numTiles * TILE_SIZE) / 2}
            cy={(numTiles * TILE_SIZE) / 2}
            r={15 * pulseScale}
            fill="none"
            stroke="#ffffff"
            strokeWidth="3"
            opacity={pulseOpacity}
          />
          <circle
            cx={(numTiles * TILE_SIZE) / 2}
            cy={(numTiles * TILE_SIZE) / 2}
            r="6"
            fill="#ffffff"
          />
        </svg>
      </div>

      {/* 2D HUD / Data Visualization Layer (Always facing camera, not rotated) */}
      {floatingLabel && floatingLabel !== 'none' && (
        <div
          style={{
            position: 'absolute',
            left: '50%',
            top: '40%', // Positioned elegantly near the center
            transform: 'translate(-50%, -50%)',
            zIndex: 100,
            animation: 'fadeIn 1s ease-out'
          }}
        >
          {/* Neon Glassmorphic Data Card */}
          <div
            style={{
              background: 'rgba(10, 11, 16, 0.75)',
              backdropFilter: 'blur(12px)',
              WebkitBackdropFilter: 'blur(12px)',
              border: `2px solid ${neonColor}`,
              borderRadius: '16px',
              padding: '16px 28px',
              boxShadow: `0 8px 32px rgba(0,0,0,0.4), 0 0 15px ${neonColor}44`,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minWidth: '220px'
            }}
          >
            {/* Title / Description */}
            <span
              style={{
                color: '#8f9cae',
                fontSize: '18px',
                fontWeight: '600',
                textTransform: 'uppercase',
                letterSpacing: '2px',
                marginBottom: '4px'
              }}
            >
              {highlightRegion === 'none' ? 'Métrica Clave' : highlightRegion}
            </span>
            
            {/* Large Glowing Demographics / Stat */}
            <span
              style={{
                color: '#ffffff',
                fontSize: '42px',
                fontWeight: '800',
                textShadow: `0 0 10px ${neonColor}`,
                lineHeight: 1.1
              }}
            >
              {floatingLabel}
            </span>
          </div>

          {/* Indicator pin line pointing to target center */}
          <div
            style={{
              width: '2px',
              height: '80px',
              background: `linear-gradient(to bottom, ${neonColor}, transparent)`,
              margin: '0 auto'
            }}
          />
        </div>
      )}

      {/* Cinematic Vignette Overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(circle, transparent 20%, rgba(10,11,16,0.85) 95%)',
          pointerEvents: 'none',
          zIndex: 50
        }}
      />
    </div>
  );
};
