import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  delayRender,
  continueRender,
  staticFile,
} from 'remotion';

interface SubWord {
  word: string;
  start: number;
  duration?: number;
}

interface SubtitleItem {
  text?: string;
  word?: string;
  start: number;
  end?: number;
  duration?: number;
}

interface MapProps {
  visualType?: string;
  narration?: string;
  subs?: SubtitleItem[];
  imageFile?: string;
  latitude: number;
  longitude: number;
  zoom: number;
  pitch: number;
  bearing: number;
  highlightRegion?: string;
  arrowDirection?: string;
  floatingLabel?: string;
}

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

const COUNTRY_CODES: Record<string, string> = {
  colombia: 'COL', brasil: 'BRA', brazil: 'BRA',
  mexico: 'MEX', argentina: 'ARG', peru: 'PER',
  venezuela: 'VEN', ecuador: 'ECU', chile: 'CHL',
  usa: 'USA', 'estados unidos': 'USA', 'united states': 'USA',
  bolivia: 'BOL', paraguay: 'PRY', uruguay: 'URY',
  cuba: 'CUB', panama: 'PAN', costa_rica: 'CRI',
  antartida: 'ATA', antartica: 'ATA', antarctica: 'ATA',
};

const COUNTRY_COLORS: Record<string, { fill: string; stroke: string }> = {
  COL: { fill: 'rgba(255,223,0,0.22)',  stroke: '#FFE000' },
  BRA: { fill: 'rgba(0,210,90,0.20)',   stroke: '#00D25A' },
  MEX: { fill: 'rgba(255,80,40,0.22)',  stroke: '#FF5028' },
  ARG: { fill: 'rgba(100,160,255,0.22)',stroke: '#64A0FF' },
  PER: { fill: 'rgba(255,100,200,0.22)',stroke: '#FF64C8' },
  VEN: { fill: 'rgba(255,50,50,0.22)',  stroke: '#FF3232' },
  ECU: { fill: 'rgba(200,100,255,0.22)',stroke: '#C864FF' },
  CHL: { fill: 'rgba(0,220,255,0.22)',  stroke: '#00DCFF' },
  USA: { fill: 'rgba(50,100,255,0.18)', stroke: '#3264FF' },
  BOL: { fill: 'rgba(255,180,0,0.22)',  stroke: '#FFB400' },
  ATA: { fill: 'rgba(200,240,255,0.20)',stroke: '#C8F0FF' },
  DEFAULT: { fill: 'rgba(255,0,120,0.20)', stroke: '#FF0078' },
};

function normalizeCountry(name: string): string {
  return name.toLowerCase().trim()
    .normalize('NFD').replace(/\p{Diacritic}/gu, '')
    .replace(/\s+/g, '_');
}

function ringToPath(ring: number[][], projectFn: (lat: number, lon: number) => {x: number, y: number}): string {
  const pts = ring.map(([lon, lat]) => projectFn(lat, lon));
  return pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ') + ' Z';
}

function geometryToPath(geometry: any, projectFn: (lat: number, lon: number) => {x: number, y: number}): string {
  if (!geometry) return '';
  const paths: string[] = [];
  if (geometry.type === 'Polygon') {
    paths.push(ringToPath(geometry.coordinates[0], projectFn));
  } else if (geometry.type === 'MultiPolygon') {
    for (const polygon of geometry.coordinates) {
      paths.push(ringToPath(polygon[0], projectFn));
    }
  }
  return paths.join(' ');
}

const MapTile: React.FC<{
  tileX: number; tileY: number; baseZoom: number;
  posX: number; posY: number; mapW: number; TILE_SIZE: number;
  onTileLoad: () => void; onTileError: (key: string) => void; tileKey: string;
}> = ({ tileX, tileY, baseZoom, posX, posY, mapW, TILE_SIZE, onTileLoad, onTileError, tileKey }) => {
  const [src, setSrc] = useState(
    `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${baseZoom}/${tileY}/${tileX}`
  );
  const [isFailed, setIsFailed] = useState(false);
  const loadedRef = useRef(false);

  const handleLoad = () => {
    if (!loadedRef.current) {
      loadedRef.current = true;
      onTileLoad();
    }
  };

  const handleError = () => {
    if (src.includes('arcgisonline')) {
      setSrc(`https://tile.openstreetmap.org/${baseZoom}/${tileX}/${tileY}.png`);
    } else if (!loadedRef.current) {
      setIsFailed(true);
      onTileError(tileKey);
    }
  };

  if (isFailed) return null;

  return (
    <img
      src={src}
      onLoad={handleLoad}
      onError={handleError}
      style={{
        position: 'absolute',
        left: posX + mapW / 2, top: posY + mapW / 2,
        width: TILE_SIZE, height: TILE_SIZE,
        display: 'block',
      }}
      alt=""
    />
  );
};

export const MapRender: React.FC<MapProps> = ({
  visualType = 'map_3d',
  narration = '',
  subs = [],
  imageFile = '',
  latitude,
  longitude,
  zoom,
  pitch,
  bearing,
  highlightRegion = 'none',
  arrowDirection = 'none',
  floatingLabel = 'none',
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  const [handle] = useState(() => delayRender('loading'));
  const [tilesLoaded, setTilesLoaded] = useState(0);
  const [countryGeo, setCountryGeo]   = useState<any>(null);
  const [geoFetchDone, setGeoFetchDone] = useState(false);

  const onTileError = useCallback((_key: string) => {
    setTilesLoaded(prev => prev + 1);
  }, []);

  const TILE_SIZE = 256;
  const numTiles  = 5;
  const TOTAL_TILES = numTiles * numTiles;

  const countryKey = normalizeCountry(highlightRegion);
  const countryCode = COUNTRY_CODES[countryKey] ?? '';
  const hasCountry = highlightRegion !== 'none' && !!countryCode;

  useEffect(() => {
    const tilesReady = tilesLoaded >= TOTAL_TILES;
    const geoReady = !hasCountry || geoFetchDone;
    if ((visualType !== 'map_3d') || (tilesReady && geoReady)) {
      continueRender(handle);
    }
  }, [tilesLoaded, geoFetchDone, handle, visualType, hasCountry, TOTAL_TILES]);

  useEffect(() => {
    if (!hasCountry || visualType !== 'map_3d') {
      setGeoFetchDone(true);
      return;
    }
    const url = `https://raw.githubusercontent.com/johan/world.geo.json/master/countries/${countryCode}.geo.json`;
    fetch(url)
      .then(r => r.json())
      .then(data => {
        const feat = data.features?.[0];
        setCountryGeo(feat?.geometry ?? null);
        setGeoFetchDone(true);
      })
      .catch(() => setGeoFetchDone(true));
  }, [countryCode, hasCountry, visualType]);

  const onTileLoad = useCallback(() => setTilesLoaded(prev => prev + 1), []);

  const animatedZoom    = interpolate(frame, [0, durationInFrames], [zoom, zoom + 0.5], { extrapolateRight: 'clamp' });
  const animatedBearing = interpolate(frame, [0, durationInFrames], [bearing, bearing + 6], { extrapolateRight: 'clamp' });
  const animatedPitch   = interpolate(frame, [0, durationInFrames], [pitch, Math.max(pitch - 5, 0)], { extrapolateRight: 'clamp' });

  const baseZoom    = Math.floor(zoom);
  const targetX     = getTileX(longitude, baseZoom);
  const targetY     = getTileY(latitude, baseZoom);
  const centerTileX = Math.floor(targetX);
  const centerTileY = Math.floor(targetY);
  const offsetX     = (targetX - centerTileX) * TILE_SIZE;
  const offsetY     = (targetY - centerTileY) * TILE_SIZE;
  const startTileX  = centerTileX - Math.floor(numTiles / 2);
  const startTileY  = centerTileY - Math.floor(numTiles / 2);
  const mapW        = numTiles * TILE_SIZE;

  const project = useCallback((lat: number, lon: number) => ({
    x: (getTileX(lon, baseZoom) - targetX) * TILE_SIZE + mapW / 2,
    y: (getTileY(lat, baseZoom) - targetY) * TILE_SIZE + mapW / 2,
  }), [baseZoom, targetX, targetY, mapW]);

  const scaleF = Math.pow(2, animatedZoom - baseZoom);

  const colors = COUNTRY_COLORS[countryCode] ?? COUNTRY_COLORS.DEFAULT;

  const countryPath = countryGeo ? geometryToPath(countryGeo, project) : '';

  const pulseScale   = interpolate(frame % 45, [0, 45], [0.1, 1.8]);
  const pulseOpacity = interpolate(frame % 45, [0, 30, 45], [0.8, 0.4, 0]);
  const glowPulse    = interpolate(frame % 60, [0, 30, 60], [0.65, 1.0, 0.65]);

  const showArrow = arrowDirection && arrowDirection !== 'none';
  const arrowA = showArrow ? project(latitude - 1.2, longitude - 2.5) : null;
  const arrowB = showArrow ? project(latitude, longitude) : null;

  const normalizeSubs = (items: SubtitleItem[]): SubWord[] => {
    return items.map(item => {
      if (item.word) {
        return { word: item.word, start: item.start, duration: item.duration ?? 500 };
      }
      if (item.text) {
        const dur = item.end ? item.end - item.start : 500;
        return { word: item.text, start: item.start, duration: dur };
      }
      return { word: '', start: item.start, duration: 500 };
    });
  };

  const renderSubtitles = () => {
    const normalized = normalizeSubs(subs);
    if (normalized.length === 0) return null;

    const chunks: SubWord[][] = [];
    for (let i = 0; i < normalized.length; i += 4) chunks.push(normalized.slice(i, i + 4));

    const nowMs = (frame / fps) * 1000;
    let idx = -1;
    for (let i = 0; i < chunks.length; i++) {
      const start = chunks[i][0].start;
      const nextStart = chunks[i + 1]?.[0].start ?? Infinity;
      if (nowMs >= start && nowMs < nextStart) { idx = i; break; }
    }
    if (idx === -1) return null;

    const chunk = chunks[idx];
    return (
      <div style={{
        position: 'absolute', bottom: 160, left: 0, right: 0,
        display: 'flex', flexWrap: 'wrap', justifyContent: 'center',
        alignItems: 'center', gap: 8, padding: '0 40px', zIndex: 300,
      }}>
        {chunk.map((sub, i) => {
          const active = nowMs >= sub.start && nowMs <= sub.start + sub.duration + 200;
          return (
            <span key={`${idx}-${i}`} style={{
              display: 'inline-block',
              color: active ? '#FFEA00' : '#FFFFFF',
              fontSize: 52,
              fontWeight: 900,
              fontFamily: 'Inter, Arial Black, sans-serif',
              textTransform: 'uppercase',
              letterSpacing: '0.02em',
              textShadow: active
                ? '0 0 30px rgba(255,234,0,0.9), 0 4px 20px rgba(0,0,0,1)'
                : '0 4px 20px rgba(0,0,0,1)',
              WebkitTextStroke: '2px rgba(0,0,0,0.85)',
              opacity: active ? 1 : 0.6,
              lineHeight: 1.2,
            }}>
              {sub.word}
            </span>
          );
        })}
      </div>
    );
  };

  if (visualType !== 'map_3d') {
    const resolvedUrl = imageFile ? staticFile(`temp_images/${imageFile}`) : '';
    const floatY  = interpolate(frame % 120, [0, 60, 120], [0, -18, 0]);
    const rotX    = interpolate(frame, [0, durationInFrames], [4, -4], { extrapolateRight: 'clamp' });
    const rotY    = interpolate(frame, [0, durationInFrames], [-4, 4], { extrapolateRight: 'clamp' });
    const bgScale = interpolate(frame, [0, durationInFrames], [1, 1.12], { extrapolateRight: 'clamp' });
    const kenBurnsScale = interpolate(frame, [0, durationInFrames], [1.0, 1.06], { extrapolateRight: 'clamp' });

    return (
      <div style={{
        width: 1080, height: 1920, position: 'relative', backgroundColor: '#050505',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        fontFamily: 'Inter, sans-serif', perspective: '1500px', overflow: 'hidden',
      }}>
        {resolvedUrl && (
          <div style={{
            position: 'absolute', inset: -200,
            backgroundImage: `url(${resolvedUrl})`,
            backgroundSize: 'cover', backgroundPosition: 'center',
            filter: 'blur(80px) brightness(0.3)',
            transform: `scale(${bgScale})`,
          }} />
        )}
        {resolvedUrl ? (
          <div style={{
            width: 860, height: 1420, borderRadius: 40,
            transformStyle: 'preserve-3d',
            transform: `translateY(${floatY}px) rotateX(${rotX}deg) rotateY(${rotY}deg)`,
            boxShadow: '0 60px 120px rgba(0,0,0,0.9), 0 0 60px rgba(255,255,255,0.06)',
            overflow: 'hidden', border: '3px solid rgba(255,255,255,0.12)',
          }}>
            <img src={resolvedUrl} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${kenBurnsScale})` }} alt="" />
            <div style={{
              position: 'absolute', inset: 0,
              background: 'linear-gradient(135deg, rgba(255,255,255,0.2) 0%, transparent 55%)',
              pointerEvents: 'none',
            }} />
          </div>
        ) : (
          <div style={{
            width: 860, height: 1420, borderRadius: 40,
            background: 'linear-gradient(135deg, #0d0d2b 0%, #1a0533 50%, #0d0d2b 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: '3px solid rgba(255,255,255,0.12)',
            boxShadow: '0 60px 120px rgba(0,0,0,0.9)',
          }}>
            <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 40, textAlign: 'center', padding: 40 }}>
              🌍
            </span>
          </div>
        )}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse at center, transparent 30%, rgba(5,5,5,0.65) 100%)',
          pointerEvents: 'none',
        }} />
        {renderSubtitles()}
      </div>
    );
  }

  const maxTileCoord = Math.pow(2, baseZoom) - 1;
  const clampTile = (v: number) => Math.max(0, Math.min(v, maxTileCoord));

  const tiles: React.ReactNode[] = [];
  for (let i = 0; i < numTiles; i++) {
    for (let j = 0; j < numTiles; j++) {
      const tileX = clampTile(startTileX + i);
      const tileY = clampTile(startTileY + j);
      const posX  = (i - Math.floor(numTiles / 2)) * TILE_SIZE - offsetX;
      const posY  = (j - Math.floor(numTiles / 2)) * TILE_SIZE - offsetY;
      const key = `${tileX}-${tileY}-${baseZoom}`;
      tiles.push(
        <MapTile key={key}
          tileX={tileX} tileY={tileY} baseZoom={baseZoom}
          posX={posX} posY={posY} mapW={mapW} TILE_SIZE={TILE_SIZE}
          onTileLoad={onTileLoad}
          onTileError={onTileError}
          tileKey={key}
        />
      );
    }
  }

  return (
    <div style={{
      width: 1080, height: 1920, position: 'relative',
      backgroundColor: '#0a0b10', overflow: 'hidden', fontFamily: 'Inter, sans-serif',
    }}>
      <div style={{
        position: 'absolute',
        width: mapW, height: mapW,
        left: '50%', top: '50%',
        marginLeft: -mapW / 2, marginTop: -mapW / 2,
        transform: `perspective(1200px) rotateX(${animatedPitch}deg) rotateZ(${animatedBearing}deg) scale(${scaleF})`,
        transformStyle: 'preserve-3d',
      }}>
        <div style={{ position: 'absolute', inset: 0 }}>{tiles}</div>

        <svg style={{
          position: 'absolute', inset: 0, width: '100%', height: '100%',
          overflow: 'visible', pointerEvents: 'none', zIndex: 10,
        }}>
          <defs>
            <filter id="country-glow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="8" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <filter id="arrow-glow">
              <feGaussianBlur stdDeviation="4" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <marker id="arrow-head" markerWidth="10" markerHeight="7" refX="6" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#FF0078"/>
            </marker>
          </defs>

          {countryPath && (
            <path
              d={countryPath}
              fill={colors.fill}
              stroke={colors.stroke}
              strokeWidth={4}
              strokeLinecap="round"
              strokeLinejoin="round"
              opacity={glowPulse}
              filter="url(#country-glow)"
            />
          )}

          {showArrow && arrowA && arrowB && (
            <path
              d={`M ${arrowA.x} ${arrowA.y} L ${arrowB.x} ${arrowB.y}`}
              fill="none" stroke="#FF0078" strokeWidth={5}
              strokeDasharray="16,10" strokeDashoffset={frame * -2}
              markerEnd="url(#arrow-head)" filter="url(#arrow-glow)"
            />
          )}

          <circle cx={mapW / 2} cy={mapW / 2} r={14 * pulseScale} fill="none" stroke="#FFF" strokeWidth={2.5} opacity={pulseOpacity}/>
          <circle cx={mapW / 2} cy={mapW / 2} r={6} fill="#FFF"/>
        </svg>
      </div>

      {floatingLabel && floatingLabel !== 'none' && (
        <div style={{
          position: 'absolute', top: '32%', left: '50%',
          transform: 'translate(-50%, -50%)', zIndex: 100,
        }}>
          <div style={{
            background: 'rgba(10,11,16,0.82)', backdropFilter: 'blur(16px)',
            WebkitBackdropFilter: 'blur(16px)',
            border: `2px solid ${colors.stroke}`,
            borderRadius: 18, padding: '16px 32px',
            boxShadow: `0 8px 40px rgba(0,0,0,0.5), 0 0 20px ${colors.stroke}55`,
            display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: 240,
          }}>
            <span style={{
              color: '#8f9cae', fontSize: 18, fontWeight: 600,
              textTransform: 'uppercase', letterSpacing: 2, marginBottom: 4,
            }}>
              {countryCode ? highlightRegion : 'KEY METRIC'}
            </span>
            <span style={{
              color: '#fff', fontSize: 46, fontWeight: 800,
              textShadow: `0 0 14px ${colors.stroke}`, lineHeight: 1.1,
            }}>
              {floatingLabel}
            </span>
          </div>
          <div style={{
            width: 2, height: 90,
            background: `linear-gradient(to bottom, ${colors.stroke}, transparent)`,
            margin: '0 auto',
          }}/>
        </div>
      )}

      <div style={{
        position: 'absolute', inset: 0,
        background: 'radial-gradient(ellipse at center, transparent 18%, rgba(10,11,16,0.88) 95%)',
        pointerEvents: 'none', zIndex: 50,
      }}/>

      {renderSubtitles()}
    </div>
  );
};
