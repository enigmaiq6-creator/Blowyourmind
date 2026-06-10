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
import { HexIconMarker, RouteLine, RegionOverlay, generateHexGlowFilters } from './MapOverlays';
import type { HexIconData, RouteData, RegionData } from './MapOverlays';
import { CountryScan } from './CountryScan';
import { LowerThird, type LowerThirdItem } from './LowerThird';
import { GeopoliticalOverlay, type GeopoliticalData } from './GeopoliticalOverlay';
import { SceneOverlay } from './SceneOverlay';
import { THEME } from './VisualIdentity';
import { feature } from 'topojson-client';

const tileBlobCache = new Map<string, string>();

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

interface NarrationCue {
  word: string;
  startMs: number;
  endMs: number;
  eventType?: 'pin_drop' | 'label_flash' | 'vignette_slide' | 'arrow_animate' | 'camera_zoom';
  target?: string;
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
  narrationCues?: NarrationCue[];
  subtitleWords?: { word: string; startMs: number; endMs: number }[];
  sceneStartMs?: number;
  hexIcons?: HexIconData[];
  routes?: RouteData[];
  regions?: RegionData[];
  mapStyle?: 'dark' | 'satellite';
  scanEffect?: boolean;
  lowerThirdData?: LowerThirdItem[];
  geopolitical?: GeopoliticalData;
  sceneOverlay?: any;
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

const MAP_STYLES = {
  dark: { urlTemplate: 'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png' },
  satellite: { urlTemplate: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}' },
  hillshade: { urlTemplate: 'https://a.tile.openstreetmap.de/hillshading/{z}/{x}/{y}.png' },
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

const MapTile = React.memo<{
  tileX: number; tileY: number; baseZoom: number;
  posX: number; posY: number; mapW: number; TILE_SIZE: number;
  onTileLoad: () => void; onTileError: (key: string) => void; tileKey: string;
  mapStyle: string; opacity?: number;
}>(({ tileX, tileY, baseZoom, posX, posY, mapW, TILE_SIZE, onTileLoad, onTileError, tileKey, mapStyle, opacity = 1 }) => {
  const styleDef = MAP_STYLES[mapStyle as keyof typeof MAP_STYLES] ?? MAP_STYLES.dark;
  const tileUrl = styleDef.urlTemplate
    .replace('{z}', String(baseZoom))
    .replace('{x}', String(tileX))
    .replace('{y}', String(tileY));

  const cachedSrc = tileBlobCache.get(tileKey);
  const [src, setSrc] = useState(cachedSrc || tileUrl);
  const [isFailed, setIsFailed] = useState(false);
  const loadedRef = useRef(false);

  const handleLoad = useCallback(() => {
    if (!loadedRef.current) {
      loadedRef.current = true;
      if (!tileBlobCache.has(tileKey)) {
        tileBlobCache.set(tileKey, src);
      }
      onTileLoad();
    }
  }, [onTileLoad, tileKey, src]);

  const handleError = useCallback(() => {
    if (src === tileUrl && mapStyle !== 'satellite') {
      const fallbackUrl = MAP_STYLES.dark.urlTemplate
        .replace('{z}', String(baseZoom))
        .replace('{x}', String(tileX))
        .replace('{y}', String(tileY));
      setSrc(fallbackUrl);
    } else if (!loadedRef.current) {
      setIsFailed(true);
      onTileError(tileKey);
    }
  }, [src, tileUrl, mapStyle, baseZoom, tileX, tileY, onTileError, tileKey]);

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
        opacity,
      }}
      alt=""
    />
  );
});

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
  narrationCues = [],
  subtitleWords = [],
  sceneStartMs = 0,
  hexIcons = [],
  routes = [],
  regions = [],
  mapStyle = 'dark',
  scanEffect = false,
  lowerThirdData = [],
  geopolitical = undefined,
  sceneOverlay = undefined,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  const [handle] = useState(() => delayRender('loading'));
  const [tilesLoaded, setTilesLoaded] = useState(0);
  const [countryGeo, setCountryGeo]   = useState<any>(null);
  const [geoFetchDone, setGeoFetchDone] = useState(false);

  const TILE_SIZE = 512;
  const numTiles  = 3;
  // We render two tile layers per cell (satellite + hillshade), so total = 2 × (numTiles²)
  const TOTAL_TILES = numTiles * numTiles * 2;

  const countryKey = normalizeCountry(highlightRegion);
  const countryCode = COUNTRY_CODES[countryKey] ?? '';
  const hasCountry = highlightRegion !== 'none' && !!countryCode;

  useEffect(() => {
    // Allow a small buffer: require at least 80% of tiles to be ready to avoid
    // holding render indefinitely when hillshade tiles occasionally fail to load.
    const tilesReady = tilesLoaded >= Math.ceil(TOTAL_TILES * 0.8);
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
    const url = `https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json`;
    fetch(url)
      .then(r => r.json())
      .then(topology => {
        try {
          const feat = feature(topology, topology.objects.countries);
          const matched = (feat as any).features.find((f: any) => f.id === countryCode);
          setCountryGeo(matched?.geometry ?? null);
        } catch {
          // fallback
        }
        setGeoFetchDone(true);
      })
      .catch(() => setGeoFetchDone(true));
  }, [countryCode, hasCountry, visualType]);

  const onTileLoad = useCallback(() => setTilesLoaded(prev => prev + 1), []);
  const onTileError = useCallback((_key: string) => {
    setTilesLoaded(prev => prev + 1);
  }, []);

  const progress = frame / durationInFrames;
  // Smoother ease: gentler cubic that avoids abrupt mid-scene acceleration
  const easeFn = (t: number) => Easing.bezier(0.45, 0.0, 0.55, 1.0)(Math.min(Math.max(t, 0), 1));
  // Path ease: holds ~5% at start and end so camera feels like it "lands" before moving
  // bezier(0.5, 0, 0.5, 1) is a smooth symmetric S-curve — much less jarring than 0.85/0.15
  const pathEase = (t: number) => {
    // Map progress into a 0.05..0.95 window to create natural hold at start/end
    const held = Math.min(Math.max((t - 0.05) / 0.90, 0), 1);
    return Easing.bezier(0.5, 0.0, 0.5, 1.0)(held);
  };
  const isMapScene = visualType === 'map_3d';

  const hasPath = cameraPath.length >= 2;
  const interpWaypoint = (key: keyof CameraWaypointData, defaultVal: number): number => {
    if (!hasPath) return defaultVal;
    const segs = cameraPath.length - 1;
    const easedProgress = pathEase(progress);
    const raw = easedProgress * segs;
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

  const currentMs = sceneStartMs + (frame / fps) * 1000;

  const activeCue = useMemo(() => {
    if (!narrationCues.length) return null;
    const now = currentMs;
    for (const cue of narrationCues) {
      if (now >= cue.startMs && now <= cue.endMs) {
        return cue;
      }
    }
    return null;
  }, [currentMs, narrationCues]);

  const cueFlashIntensity = activeCue && (activeCue.eventType === 'label_flash' || activeCue.eventType === 'pin_drop')
    ? interpolate(
        Math.min((currentMs - activeCue.startMs) / 200, 1),
        [0, 0.5, 1],
        [0, 1, 0.6],
        { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
      )
    : 1;

  const cueZoomBoost = activeCue?.eventType === 'camera_zoom'
    ? interpolate(
        Math.min((currentMs - activeCue.startMs) / 300, 1),
        [0, 0.3, 1],
        [0, 2.5, 0],
        { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
      )
    : 0;

  const animatedZoom    = (hasPath ? camZoom : interpolate(progress, [0, 0.15, 0.85, 1], [zoom, zoom + 0.1, zoom + 0.6, zoom + 0.4], { easing: easeFn, extrapolateRight: 'clamp' })) + cueZoomBoost;
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

  const project = useCallback((lat: number, lon: number) => ({
    x: (getTileX(lon, tileZoomBase) - targetX) * TILE_SIZE + mapW / 2,
    y: (getTileY(lat, tileZoomBase) - targetY) * TILE_SIZE + mapW / 2,
  }), [tileZoomBase, targetX, targetY, TILE_SIZE, mapW]);

  const scaleF = Math.pow(2, animatedZoom - tileZoomBase);

  const colors = COUNTRY_COLORS[countryCode] ?? COUNTRY_COLORS.DEFAULT;

  const countryPath = countryGeo ? geometryToPath(countryGeo, project) : '';

  const pulsePhase = (frame % 50) / 50;
  const pulseScale   = interpolate(pulsePhase, [0, 0.5, 1], [0.15, 1.6, 0.15], { easing: Easing.inOut(Easing.ease) });
  const pulseOpacity = interpolate(pulsePhase, [0, 0.4, 0.7, 1], [0.7, 0.5, 0.1, 0.7], { easing: Easing.inOut(Easing.ease) });
  const glowPhase = (frame % 70) / 70;
  const glowPulse    = interpolate(glowPhase, [0, 0.5, 1], [0.55, 1.0, 0.55], { easing: Easing.inOut(Easing.ease) });
  const drawProgress = interpolate(frame, [0, 50], [1, 0], {
    easing: Easing.out(Easing.ease),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const countryFillOpacity = interpolate(frame, [25, 50], [0, 1], {
    easing: Easing.out(Easing.ease),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const showArrow = arrowDirection && arrowDirection !== 'none';
  const arrowA = showArrow ? project(latitude - 1.2, longitude - 2.5) : null;
  const arrowB = showArrow ? project(latitude, longitude) : null;

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
        fontFamily: '"Montserrat Black", "Arial Black", Inter, sans-serif',
        perspective: '1500px', overflow: 'hidden',
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
            position: 'absolute', inset: 0,
            transform: `translateY(${floatY}px) rotateX(${rotX}deg) rotateY(${rotY}deg)`,
            overflow: 'hidden',
          }}>
            <img src={resolvedUrl} style={{
              width: '100%', height: '100%',
              objectFit: 'cover',
              transform: `scale(${kenBurnsScale})`,
            }} alt="" />
            <div style={{
              position: 'absolute', inset: 0,
              background: 'linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 30%, transparent 70%, rgba(0,0,0,0.4) 100%)',
              pointerEvents: 'none',
            }} />
            <div style={{
              position: 'absolute', inset: 0,
              background: 'radial-gradient(ellipse at center, transparent 40%, rgba(5,5,5,0.3) 100%)',
              pointerEvents: 'none',
            }} />
          </div>
        ) : (
          <div style={{
            width: 1080, height: 1920,
            background: 'linear-gradient(135deg, #0a0a1a 0%, #150a2e 50%, #0a0a1a 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <span style={{ color: 'rgba(255,255,255,0.2)', fontSize: 40, textAlign: 'center', padding: 40 }}>
              🌍
            </span>
          </div>
        )}
        <div style={{
          position: 'absolute', left: 0, right: 0, bottom: 0, height: 200,
          background: 'linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 100%)',
          pointerEvents: 'none', zIndex: 200,
        }}/>
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
            mapStyle={mapStyle}
          />
        );
        ts.push(
          <MapTile key={`hill-${key}`}
            tileX={tileX} tileY={tileY} baseZoom={tileZoomBase}
            posX={posX} posY={posY} mapW={mapW} TILE_SIZE={TILE_SIZE}
            onTileLoad={onTileLoad}
            onTileError={onTileError}
            tileKey={`hill-${key}`}
            mapStyle="hillshade"
            opacity={0.3}
          />
        );
      }
    }
    return ts;
  };

  // Fade-in during first 8 frames to mask any tile-load flash at scene start
  const mapFadeIn = interpolate(frame, [0, 8], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div style={{
      width: 1080, height: 1920, position: 'relative',
      backgroundColor: '#0a0b10', overflow: 'hidden', fontFamily: '"Montserrat Black", "Arial Black", Inter, sans-serif',
    }}>
      <div style={{
        position: 'absolute',
        width: mapW, height: mapW,
        left: '50%', top: '50%',
        marginLeft: -mapW / 2, marginTop: -mapW / 2,
        opacity: mapFadeIn,
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
            <filter id="country-glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="blur1"/>
              <feGaussianBlur stdDeviation="8" result="blur2"/>
              <feGaussianBlur stdDeviation="18" result="blur3"/>
              <feMerge>
                <feMergeNode in="blur3"/>
                <feMergeNode in="blur2"/>
                <feMergeNode in="blur1"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            <filter id="country-glow-intense" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="4" result="blur1"/>
              <feGaussianBlur stdDeviation="12" result="blur2"/>
              <feGaussianBlur stdDeviation="28" result="blur3"/>
              <feMerge>
                <feMergeNode in="blur3"/>
                <feMergeNode in="blur2"/>
                <feMergeNode in="blur1"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            <filter id="arrow-glow">
              <feGaussianBlur stdDeviation="4" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
            <marker id="arrow-head" markerWidth="10" markerHeight="7" refX="6" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#FF0078"/>
            </marker>
            {generateHexGlowFilters(Math.max(hexIcons.length, 1))}
          </defs>

          {countryPath && (
            <>
              <path
                d={countryPath}
                fill={colors.fill}
                fillOpacity={countryFillOpacity}
                stroke={colors.stroke}
                strokeWidth={8}
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity={glowPulse}
                filter="url(#country-glow-intense)"
                pathLength={1}
                strokeDasharray="1"
                strokeDashoffset={drawProgress}
              />
              <path
                d={countryPath}
                fill="none"
                stroke={colors.stroke}
                strokeWidth={3}
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity={0.9}
                pathLength={1}
                strokeDasharray="1"
                strokeDashoffset={drawProgress}
              />
            </>
          )}

          {scanEffect && countryCode && (
            <CountryScan
              project={project}
              countryPath={countryPath}
              frame={frame}
              durationInFrames={durationInFrames}
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

          {hexIcons.map((hx, i) => (
            <HexIconMarker key={`hx-${i}`} data={hx} project={project} frame={frame} sceneStartMs={sceneStartMs} index={i} />
          ))}

          {routes.map((rt, i) => (
            <RouteLine key={`rt-${i}`} data={rt} project={project} frame={frame} durationInFrames={durationInFrames} index={i} />
          ))}

          {regions.map((rg, i) => (
            <RegionOverlay key={`rg-${i}`} data={rg} project={project} frame={frame} index={i} />
          ))}
        </svg>
      </div>

      {floatingLabel && floatingLabel !== 'none' && (() => {
        const autoFade = interpolate(
          currentMs, [0, 300, 3500, 4200],
          [0, 1, 1, 0],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        );
        const cueShow = activeCue?.eventType === 'label_flash' || activeCue?.eventType === 'pin_drop'
          ? interpolate(
              Math.min((currentMs - activeCue.startMs) / 200, 1),
              [0, 0.5, 1],
              [0, 1, 0.6],
              { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
            )
          : 0;
        const finalOpacity = Math.max(autoFade, cueShow);
        if (finalOpacity < 0.01) return null;

        const slideUp = interpolate(
          currentMs, [0, 400, 3500, 4200],
          [24, 0, 0, -12],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
        );

        return (
        <div style={{
          position: 'absolute', top: '40%', left: 0, right: 0,
          textAlign: 'center', zIndex: 100,
          opacity: finalOpacity,
          transform: `translateY(${slideUp}px)`,
          pointerEvents: 'none',
        }}>
          <div style={{
            fontSize: 13, fontWeight: 700, letterSpacing: 4,
            color: colors.stroke, textTransform: 'uppercase',
            marginBottom: 2, fontFamily: THEME.fontFamily,
          }}>
            {countryCode ? highlightRegion.toUpperCase() : 'KEY METRIC'}
          </div>
          <div style={{
            width: 40, height: 2, background: colors.stroke,
            margin: '0 auto 6px', opacity: 0.5,
          }}/>
          <div style={{
            fontSize: 52, fontWeight: 900, color: '#fff',
            textShadow: `0 0 30px ${colors.stroke}88, 0 2px 4px rgba(0,0,0,0.8)`,
            lineHeight: 1.1, letterSpacing: '0.02em',
            fontFamily: THEME.fontFamily,
          }}>
            {floatingLabel}
          </div>
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
        return (
          <div style={{
            position: 'absolute', right: 36, top: '42%', zIndex: 80,
            display: 'flex', flexDirection: 'column', gap: 20,
            pointerEvents: 'none',
          }}>
            {vignettes.map((v, i) => {
              const delay = i * 12;
              if (frame < delay) return null;
              const elapsed = Math.max(frame - delay, 0);
              const slideX = interpolate(
                elapsed, [0, 8], [40, 0],
                { easing: Easing.out(Easing.ease), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
              );
              const fadeIn = interpolate(
                elapsed, [0, 6], [0, 1],
                { easing: Easing.out(Easing.ease), extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
              );
              const fadeOut = interpolate(
                elapsed, [80, 95], [1, 0],
                { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
              );
              const opacity = fadeIn * fadeOut;
              if (opacity < 0.01) return null;
              return (
                <div key={`vg-${i}`} style={{
                  opacity, transform: `translateX(${slideX}px)`,
                  display: 'flex', alignItems: 'center', gap: 14,
                  background: 'rgba(10, 11, 16, 0.75)',
                  backdropFilter: 'blur(8px)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderLeft: `4px solid ${colors.stroke}`,
                  padding: '12px 18px',
                  borderRadius: '8px',
                  boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
                  minWidth: 240,
                }}>
                  <div style={{ fontSize: 26 }}>{v.icon}</div>
                  <div style={{
                    display: 'flex', flexDirection: 'column', gap: 2,
                  }}>
                    <span style={{
                      color: 'rgba(255, 255, 255, 0.5)', fontSize: 10, fontWeight: 700,
                      letterSpacing: 2, textTransform: 'uppercase',
                    }}>
                      {v.title}
                    </span>
                    <span style={{
                      color: '#fff', fontSize: 24, fontWeight: 900,
                      fontFamily: THEME.fontFamily,
                      textShadow: `0 0 15px ${colors.stroke}33`,
                      lineHeight: 1.15,
                    }}>
                      {v.value}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        );
      })()}

      {lowerThirdData.length > 0 && (
        <LowerThird
          items={lowerThirdData}
          frame={frame}
          progress={progress}
        />
      )}

      {geopolitical && (
        <GeopoliticalOverlay
          geopolitical={geopolitical}
          currentMs={currentMs}
        />
      )}

      <SceneOverlay data={sceneOverlay} currentMs={currentMs} />

    </div>
  );
};
