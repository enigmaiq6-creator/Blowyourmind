import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import {
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  delayRender,
  continueRender,
  staticFile,
  Easing,
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

interface MapPinData {
  latitude: number;
  longitude: number;
  label: string;
  value?: string;
}

interface MapVignetteData {
  icon: string;
  title: string;
  value: string;
}

interface CameraWaypointData {
  latitude: number;
  longitude: number;
  zoom: number;
  pitch: number;
  bearing: number;
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
  pins?: MapPinData[];
  vignettes?: MapVignetteData[];
  cameraPath?: CameraWaypointData[];
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
  usa: 'USA', 'estados unidos': 'USA', 'united states': 'USA', 'america': 'USA',
  bolivia: 'BOL', paraguay: 'PRY', uruguay: 'URY',
  cuba: 'CUB', panama: 'PAN', costa_rica: 'CRI',
  antartida: 'ATA', antartica: 'ATA', antarctica: 'ATA',
  canada: 'CAN', australia: 'AUS', india: 'IND',
  china: 'CHN', russia: 'RUS', 'south africa': 'ZAF',
  uk: 'GBR', 'united kingdom': 'GBR', france: 'FRA',
  japan: 'JPN', indonesia: 'IDN', germany: 'DEU',
  italy: 'ITA', spain: 'ESP',
  egypt: 'EGY', nigeria: 'NGA', kenya: 'KEN',
  'new zealand': 'NZL', 'south korea': 'KOR',
  saudi_arabia: 'SAU', turkiye: 'TUR', turkey: 'TUR',
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
  CAN: { fill: 'rgba(255,80,80,0.18)',  stroke: '#FF5050' },
  AUS: { fill: 'rgba(255,180,50,0.20)', stroke: '#FFB432' },
  IND: { fill: 'rgba(255,140,0,0.20)',  stroke: '#FF8C00' },
  CHN: { fill: 'rgba(200,50,50,0.18)',  stroke: '#C83232' },
  RUS: { fill: 'rgba(100,100,200,0.18)',stroke: '#6464C8' },
  ZAF: { fill: 'rgba(255,200,0,0.20)',  stroke: '#FFC800' },
  GBR: { fill: 'rgba(50,80,200,0.20)',  stroke: '#3250C8' },
  FRA: { fill: 'rgba(50,100,200,0.20)', stroke: '#3264C8' },
  JPN: { fill: 'rgba(200,50,100,0.20)', stroke: '#C83264' },
  IDN: { fill: 'rgba(200,100,50,0.20)', stroke: '#C86432' },
  DEU: { fill: 'rgba(200,180,50,0.18)', stroke: '#C8B432' },
  ITA: { fill: 'rgba(50,180,100,0.20)', stroke: '#32B464' },
  ESP: { fill: 'rgba(200,100,50,0.20)', stroke: '#C86432' },
  EGY: { fill: 'rgba(200,150,50,0.20)', stroke: '#C89632' },
  NGA: { fill: 'rgba(50,180,100,0.18)', stroke: '#32B464' },
  KEN: { fill: 'rgba(200,100,50,0.20)', stroke: '#C86432' },
  NZL: { fill: 'rgba(50,180,200,0.20)', stroke: '#32B4C8' },
  KOR: { fill: 'rgba(200,50,150,0.20)', stroke: '#C83296' },
  SAU: { fill: 'rgba(50,180,80,0.18)',  stroke: '#32B450' },
  TUR: { fill: 'rgba(200,100,50,0.20)', stroke: '#C86432' },
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
  pins = [],
  vignettes = [],
  cameraPath = [],
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  const [handle] = useState(() => delayRender('loading'));
  const [tilesLoaded, setTilesLoaded] = useState(0);
  const [countryGeo, setCountryGeo]   = useState<any>(null);
  const [geoFetchDone, setGeoFetchDone] = useState(false);

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
  const onTileError = useCallback((_key: string) => {
    setTilesLoaded(prev => prev + 1);
  }, []);

  const progress = frame / durationInFrames;
  const easeFn = (t: number) => Easing.inOut(Easing.ease)(t);
  const isMapScene = visualType === 'map_3d';

  const hasPath = cameraPath.length >= 2;
  const interpWaypoint = (key: keyof CameraWaypointData, defaultVal: number): number => {
    if (!hasPath) return defaultVal;
    const segs = cameraPath.length - 1;
    const raw = progress * segs;
    const idx = Math.min(Math.floor(raw), segs - 1);
    const local = raw - idx;
    const from = cameraPath[idx][key] as number;
    const to = cameraPath[idx + 1][key] as number;
    return from + (to - from) * easeFn(local);
  };

  const camLat = interpWaypoint('latitude', latitude);
  const camLon = interpWaypoint('longitude', longitude);
  const camZoom = interpWaypoint('zoom', zoom);
  const camPitch = interpWaypoint('pitch', pitch);
  const camBearing = interpWaypoint('bearing', bearing);

  const animatedZoom    = hasPath ? camZoom : interpolate(progress, [0, 0.15, 0.85, 1], [zoom, zoom + 0.1, zoom + 0.6, zoom + 0.4], { easing: easeFn, extrapolateRight: 'clamp' });
  const animatedBearing = hasPath ? camBearing : interpolate(progress, [0, 0.5, 1], [bearing, bearing + 4, bearing + 6], { easing: easeFn, extrapolateRight: 'clamp' });
  const animatedPitch   = hasPath ? camPitch : interpolate(progress, [0, 0.3, 1], [pitch, pitch - 3, Math.max(pitch - 6, 0)], { easing: easeFn, extrapolateRight: 'clamp' });

  // ── Tile zoom: dynamic for camera path, fixed for single-scene ──
  const curLat = hasPath ? camLat : latitude;
  const curLon = hasPath ? camLon : longitude;
  const tileZoomBase = hasPath
    ? Math.max(2, Math.min(Math.floor(animatedZoom), 18))
    : Math.floor(zoom);

  const targetX     = getTileX(curLon, tileZoomBase);
  const targetY     = getTileY(curLat, tileZoomBase);
  const centerTileX = Math.floor(targetX);
  const centerTileY = Math.floor(targetY);
  const offsetX     = (targetX - centerTileX) * TILE_SIZE;
  const offsetY     = (targetY - centerTileY) * TILE_SIZE;
  const startTileX  = centerTileX - Math.floor(numTiles / 2);
  const startTileY  = centerTileY - Math.floor(numTiles / 2);
  const mapW        = numTiles * TILE_SIZE;

  const project = (lat: number, lon: number) => ({
    x: (getTileX(lon, tileZoomBase) - targetX) * TILE_SIZE + mapW / 2,
    y: (getTileY(lat, tileZoomBase) - targetY) * TILE_SIZE + mapW / 2,
  });

  const scaleF = Math.pow(2, animatedZoom - tileZoomBase);

  const colors = COUNTRY_COLORS[countryCode] ?? COUNTRY_COLORS.DEFAULT;

  const countryPath = countryGeo ? geometryToPath(countryGeo, project) : '';

  const pulsePhase = (frame % 50) / 50;
  const pulseScale   = interpolate(pulsePhase, [0, 0.5, 1], [0.15, 1.6, 0.15], { easing: Easing.inOut(Easing.ease) });
  const pulseOpacity = interpolate(pulsePhase, [0, 0.4, 0.7, 1], [0.7, 0.5, 0.1, 0.7], { easing: Easing.inOut(Easing.ease) });
  const glowPhase = (frame % 70) / 70;
  const glowPulse    = interpolate(glowPhase, [0, 0.5, 1], [0.55, 1.0, 0.55], { easing: Easing.inOut(Easing.ease) });

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

    const subtitleEnter = interpolate(
      Math.min((nowMs - chunk[0].start) / 150, 1),
      [0, 1],
      [12, 0],
      { easing: Easing.out(Easing.ease) }
    );

    return (
      <div style={{
        position: 'absolute', left: 0, right: 0,
        top: '46%', transform: `translateY(calc(-50% + ${subtitleEnter}px))`,
        display: 'flex', justifyContent: 'center', zIndex: 300,
        pointerEvents: 'none',
      }}>
        <div style={{
          display: 'inline-flex', flexWrap: 'wrap', justifyContent: 'center',
          alignItems: 'center', gap: 8, padding: '24px 40px',
          background: 'rgba(0,0,0,0.55)',
          borderRadius: 16,
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          maxWidth: '88%',
          boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
        }}>
          {chunk.map((sub, i) => {
            const active = nowMs >= sub.start && nowMs <= sub.start + sub.duration + 200;
            const wordScale = active ? interpolate(Math.min((nowMs - sub.start) / 120, 1), [0, 1], [0.88, 1], { easing: Easing.out(Easing.back) }) : 1;
            return (
              <span key={`${idx}-${i}`} style={{
                display: 'inline-block',
                color: active ? '#FFEA00' : 'rgba(255,255,255,0.75)',
                fontSize: 56,
                fontWeight: 900,
                fontFamily: '"Montserrat Black", Inter, Arial Black, sans-serif',
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
                textShadow: active
                  ? '0 0 30px rgba(255,234,0,0.6), 0 2px 8px rgba(0,0,0,0.9)'
                  : '0 2px 8px rgba(0,0,0,0.9)',
                WebkitTextStroke: active ? '1.5px rgba(0,0,0,0.5)' : '1px rgba(0,0,0,0.3)',
                opacity: active ? 1 : 0.45,
                lineHeight: 1.15,
                transform: `scale(${wordScale})`,
                transition: 'color 0.05s ease',
              }}>
                {sub.word}
              </span>
            );
          })}
        </div>
      </div>
    );
  };

  if (visualType !== 'map_3d') {
    const resolvedUrl = imageFile ? staticFile(`temp_images/${imageFile}`) : '';
    const floatT = (frame % 150) / 150;
    const floatY  = interpolate(floatT, [0, 0.5, 1], [0, -14, 0], { easing: Easing.inOut(Easing.ease) });
    const rotX    = interpolate(progress, [0, 1], [3, -3], { easing: easeFn, extrapolateRight: 'clamp' });
    const rotY    = interpolate(progress, [0, 1], [-3, 3], { easing: easeFn, extrapolateRight: 'clamp' });
    const bgScale = interpolate(progress, [0, 1], [1, 1.1], { easing: easeFn, extrapolateRight: 'clamp' });
    const kenBurnsScale = interpolate(progress, [0, 1], [1.0, 1.05], { easing: easeFn, extrapolateRight: 'clamp' });

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
            filter: 'blur(80px) brightness(0.25)',
            transform: `scale(${bgScale})`,
          }} />
        )}
        {resolvedUrl ? (
          <div style={{
            width: 860, height: 1420, borderRadius: 40,
            transformStyle: 'preserve-3d',
            transform: `translateY(${floatY}px) rotateX(${rotX}deg) rotateY(${rotY}deg)`,
            boxShadow: '0 60px 120px rgba(0,0,0,0.9), 0 0 80px rgba(255,255,255,0.08)',
            overflow: 'hidden', border: '2px solid rgba(255,255,255,0.1)',
          }}>
            <img src={resolvedUrl} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${kenBurnsScale})` }} alt="" />
            <div style={{
              position: 'absolute', inset: 0,
              background: 'linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 50%, rgba(0,0,0,0.2) 100%)',
              pointerEvents: 'none',
            }} />
          </div>
        ) : (
          <div style={{
            width: 860, height: 1420, borderRadius: 40,
            background: 'linear-gradient(135deg, #0a0a1a 0%, #150a2e 50%, #0a0a1a 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: '2px solid rgba(255,255,255,0.1)',
            boxShadow: '0 60px 120px rgba(0,0,0,0.9)',
          }}>
            <span style={{ color: 'rgba(255,255,255,0.2)', fontSize: 40, textAlign: 'center', padding: 40 }}>
              🌍
            </span>
          </div>
        )}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'radial-gradient(ellipse at center, transparent 28%, rgba(5,5,5,0.7) 100%)',
          pointerEvents: 'none',
        }}/>
        <div style={{
          position: 'absolute', inset: 0,
          background: `repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.04) 2px, rgba(0,0,0,0.04) 4px)`,
          pointerEvents: 'none', opacity: 0.3,
        }}/>
        {renderSubtitles()}
      </div>
    );
  }

  const maxTileCoord = Math.pow(2, tileZoomBase) - 1;
  const clampTile = (v: number) => Math.max(0, Math.min(v, maxTileCoord));

  const tilesKey = `${tileZoomBase}-${centerTileX}-${centerTileY}-${hasPath ? 'd' : 's'}`;
  const renderTiles = () => {
    const ts: React.ReactNode[] = [];
    for (let i = 0; i < numTiles; i++) {
      for (let j = 0; j < numTiles; j++) {
        const tileX = clampTile(startTileX + i);
        const tileY = clampTile(startTileY + j);
        const posX  = (i - Math.floor(numTiles / 2)) * TILE_SIZE - offsetX;
        const posY  = (j - Math.floor(numTiles / 2)) * TILE_SIZE - offsetY;
        const key = `${tilesKey}-${tileX}-${tileY}`;
        ts.push(
          <MapTile key={key}
            tileX={tileX} tileY={tileY} baseZoom={tileZoomBase}
            posX={posX} posY={posY} mapW={mapW} TILE_SIZE={TILE_SIZE}
            onTileLoad={onTileLoad}
            onTileError={onTileError}
            tileKey={key}
          />
        );
      }
    }
    return ts;
  };

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
        <div style={{ position: 'absolute', inset: 0 }}>
          {renderTiles()}
        </div>

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

          {pins.map((pin, i) => {
            const pinPoint = project(pin.latitude, pin.longitude);
            const pinDelay = i * 8;
            const pinOpacity = interpolate(
              Math.max(frame - pinDelay, 0), [0, 10], [0, 1],
              { easing: Easing.out(Easing.ease), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
            );
            const pinSlide = interpolate(
              Math.max(frame - pinDelay, 0), [0, 12], [18, 0],
              { easing: Easing.out(Easing.ease), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
            );
            const pPhase = ((frame - i * 20 + 60) % 60) / 60;
            const pR = interpolate(pPhase, [0, 0.5, 1], [4, 14, 4], { easing: Easing.inOut(Easing.ease) });
            const pO = interpolate(pPhase, [0, 0.5, 1], [0.5, 0.08, 0.5], { easing: Easing.inOut(Easing.ease) });
            if (pinOpacity <= 0) return null;
            return (
              <g key={`pin-${i}`} opacity={pinOpacity} transform={`translate(${pinPoint.x}, ${pinPoint.y + pinSlide})`}>
                <circle cx={0} cy={0} r={pR} fill="none" stroke="#FF0078" strokeWidth={2.5} opacity={pO} />
                <circle cx={0} cy={0} r={5} fill="#FF0078" stroke="#fff" strokeWidth={2} />
                {pin.label && (
                  <text x={0} y={-14} textAnchor="middle" fill="#fff" fontSize={13} fontWeight="bold" stroke="#000" strokeWidth={4} paintOrder="stroke">
                    {pin.label}
                  </text>
                )}
                {pin.value && (
                  <text x={0} y={-28} textAnchor="middle" fill="#FFCC00" fontSize={11} fontWeight="bold" stroke="#000" strokeWidth={3} paintOrder="stroke">
                    {pin.value}
                  </text>
                )}
              </g>
            );
          })}

          <circle cx={mapW / 2} cy={mapW / 2} r={14 * pulseScale} fill="none" stroke="#FFF" strokeWidth={2.5} opacity={pulseOpacity}/>
          <circle cx={mapW / 2} cy={mapW / 2} r={6} fill="#FFF"/>
        </svg>
      </div>

      {floatingLabel && floatingLabel !== 'none' && (() => {
        const labelSlideIn = interpolate(progress, [0, 0.2], [-80, 0], { easing: Easing.out(Easing.ease), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        const labelOpacity = interpolate(progress, [0, 0.15], [0, 1], { easing: Easing.out(Easing.ease), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        return (
        <div style={{
          position: 'absolute', top: '32%', left: '50%',
          transform: `translate(-50%, calc(-50% + ${labelSlideIn}px))`, zIndex: 100,
          opacity: labelOpacity,
        }}>
          <div style={{
            background: 'rgba(10,11,16,0.85)', backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            border: `2px solid ${colors.stroke}`,
            borderLeft: `4px solid ${colors.stroke}`,
            borderRadius: 18, padding: '18px 36px',
            boxShadow: `0 8px 40px rgba(0,0,0,0.6), 0 0 30px ${colors.stroke}44`,
            display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: 260,
          }}>
            <span style={{
              color: '#8f9cae', fontSize: 16, fontWeight: 700,
              textTransform: 'uppercase', letterSpacing: 3, marginBottom: 6,
            }}>
              {countryCode ? highlightRegion.toUpperCase() : 'KEY METRIC'}
            </span>
            <span style={{
              color: '#fff', fontSize: 52, fontWeight: 900,
              textShadow: `0 0 20px ${colors.stroke}, 0 0 60px ${colors.stroke}44`,
              lineHeight: 1.1, letterSpacing: '0.02em',
              fontFamily: '"Arial Black", Inter, sans-serif',
            }}>
              {floatingLabel}
            </span>
          </div>
          <div style={{
            width: 3, height: 80,
            background: `linear-gradient(to bottom, ${colors.stroke}, transparent)`,
            margin: '0 auto', opacity: 0.7,
          }}/>
        </div>);
      })()}

      <div style={{
        position: 'absolute', inset: 0,
        background: 'radial-gradient(ellipse at center, transparent 15%, rgba(10,11,16,0.92) 98%)',
        pointerEvents: 'none', zIndex: 50,
      }}/>

      <div style={{
        position: 'absolute', inset: 0,
        background: `repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.06) 2px, rgba(0,0,0,0.06) 4px)`,
        pointerEvents: 'none', zIndex: 45, opacity: 0.5,
      }}/>

      <div style={{
        position: 'absolute', inset: 0,
        background: `radial-gradient(circle at 50% 50%, transparent 40%, rgba(0,0,0,0.3) 100%)`,
        pointerEvents: 'none', zIndex: 46, opacity: 0.3,
      }}/>

      {vignettes.length > 0 && (() => {
        const cardGap = 76;
        const cardStartY = 460;
        return (
          <div style={{
            position: 'absolute', right: 36, top: cardStartY, zIndex: 80,
            display: 'flex', flexDirection: 'column', gap: cardGap,
            pointerEvents: 'none',
          }}>
            {vignettes.map((v, i) => {
              const delay = i * 12;
              if (frame < delay) return null;
              const slideX = interpolate(
                Math.max(frame - delay, 0), [0, 14], [60, 0],
                { easing: Easing.out(Easing.ease), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
              );
              const op = interpolate(
                Math.max(frame - delay, 0), [0, 10], [0, 1],
                { easing: Easing.out(Easing.ease), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
              );
              return (
                <div key={`vg-${i}`} style={{
                  opacity: op, transform: `translateX(${slideX}px)`,
                  background: 'rgba(10,11,16,0.78)', backdropFilter: 'blur(12px)',
                  WebkitBackdropFilter: 'blur(12px)',
                  borderRadius: 16, padding: '14px 20px',
                  border: '1px solid rgba(255,255,255,0.08)',
                  borderLeft: `3px solid ${colors.stroke}`,
                  minWidth: 220,
                  boxShadow: `0 4px 24px rgba(0,0,0,0.5), 0 0 20px ${colors.stroke}22`,
                  display: 'flex', flexDirection: 'column', gap: 2,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
                    <span style={{ fontSize: 18 }}>{v.icon}</span>
                    <span style={{ color: '#8f9cae', fontSize: 10, fontWeight: 700, letterSpacing: 2, textTransform: 'uppercase' }}>
                      {v.title}
                    </span>
                  </div>
                  <span style={{
                    color: '#fff', fontSize: 30, fontWeight: 900,
                    fontFamily: '"Arial Black", Inter, sans-serif',
                    textShadow: `0 0 20px ${colors.stroke}44`,
                    lineHeight: 1.15,
                  }}>
                    {v.value}
                  </span>
                </div>
              );
            })}
          </div>
        );
      })()}

      {renderSubtitles()}
    </div>
  );
};
