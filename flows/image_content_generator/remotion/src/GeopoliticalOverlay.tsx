import React from 'react';
import { interpolate, useCurrentFrame, Easing } from 'remotion';
import { THEME } from './VisualIdentity';

// ─── Data Types ────────────────────────────────────────

export interface ExtrudedCountryData {
  name: string;
  iso3: string;
  flagUrl?: string;
}

export interface DistanceArrowData {
  fromLat: number;
  fromLng: number;
  toLat: number;
  toLng: number;
  label: string;
  startMs: number;
  durationMs: number;
}

export interface YearTransitionData {
  year: number;
  startMs: number;
  durationMs: number;
}

export interface ThematicIconData {
  type: 'alliance' | 'conflict' | 'colonial' | 'erosion';
  lat: number;
  lng: number;
  label?: string;
  startMs: number;
}

export interface BoundaryLineData {
  waypoints: {lat: number; lng: number}[];
  colorA: string;
  colorB: string;
  startMs: number;
  durationMs: number;
}

export interface HistoricalOverlayData {
  waypoints: {lat: number; lng: number}[];
  color: string;
  opacity: number;
  label: string;
  startMs: number;
  durationMs: number;
}

export interface GeopoliticalData {
  extrudedCountries?: ExtrudedCountryData[];
  distanceArrows?: DistanceArrowData[];
  yearTransitions?: YearTransitionData[];
  thematicIcons?: ThematicIconData[];
  boundaryLines?: BoundaryLineData[];
  historicalOverlays?: HistoricalOverlayData[];
}

// ─── ISO3 → flag image ────────────────────────────────

const ISO3_TO_2: Record<string, string> = {
  AFG:'AF',ALB:'AL',DZA:'DZ',AND:'AD',AGO:'AO',ARG:'AR',ARM:'AM',AUS:'AU',AUT:'AT',AZE:'AZ',
  BHS:'BS',BHR:'BH',BGD:'BD',BRB:'BB',BLR:'BY',BEL:'BE',BLZ:'BZ',BEN:'BJ',BTN:'BT',
  BOL:'BO',BIH:'BA',BWA:'BW',BRA:'BR',BRN:'BN',BGR:'BG',BFA:'BF',BDI:'BI',CPV:'CV',
  KHM:'KH',CMR:'CM',CAN:'CA',CAF:'CF',TCD:'TD',CHL:'CL',CHN:'CN',COL:'CO',COM:'KM',
  COG:'CG',COD:'CD',CRI:'CR',CIV:'CI',HRV:'HR',CUB:'CU',CYP:'CY',CZE:'CZ',DNK:'DK',
  DJI:'DJ',DMA:'DM',DOM:'DO',ECU:'EC',EGY:'EG',SLV:'SV',GNQ:'GQ',ERI:'ER',EST:'EE',
  SWZ:'SZ',ETH:'ET',FJI:'FJ',FIN:'FI',FRA:'FR',GAB:'GA',GMB:'GM',GEO:'GE',DEU:'DE',
  GHA:'GH',GRC:'GR',GRD:'GD',GTM:'GT',GIN:'GN',GNB:'GW',GUY:'GY',HTI:'HT',HND:'HN',
  HUN:'HU',ISL:'IS',IND:'IN',IDN:'ID',IRN:'IR',IRQ:'IQ',IRL:'IE',ISR:'IL',ITA:'IT',
  JAM:'JM',JPN:'JP',JOR:'JO',KAZ:'KZ',KEN:'KE',KIR:'KI',PRK:'KP',KOR:'KR',KWT:'KW',
  KGZ:'KG',LAO:'LA',LVA:'LV',LBN:'LB',LSO:'LS',LBR:'LR',LBY:'LY',LIE:'LI',LTU:'LT',
  LUX:'LU',MDG:'MG',MWI:'MW',MYS:'MY',MDV:'MV',MLI:'ML',MLT:'MT',MHL:'MH',MRT:'MR',
  MUS:'MU',MEX:'MX',FSM:'FM',MDA:'MD',MCO:'MC',MNG:'MN',MNE:'ME',MAR:'MA',MOZ:'MZ',
  MMR:'MM',NAM:'NA',NRU:'NR',NPL:'NP',NLD:'NL',NZL:'NZ',NIC:'NI',NER:'NE',NGA:'NG',
  MKD:'MK',NOR:'NO',OMN:'OM',PAK:'PK',PLW:'PW',PAN:'PA',PNG:'PG',PRY:'PY',PER:'PE',
  PHL:'PH',POL:'PL',PRT:'PT',QAT:'QA',ROU:'RO',RUS:'RU',RWA:'RW',KNA:'KN',LCA:'LC',
  VCT:'VC',WSM:'WS',SMR:'SM',STP:'ST',SAU:'SA',SEN:'SN',SRB:'RS',SYC:'SC',SLE:'SL',
  SGP:'SG',SVK:'SK',SVN:'SI',SLB:'SB',SOM:'SO',ZAF:'ZA',SSD:'SS',ESP:'ES',LKA:'LK',
  SDN:'SD',SUR:'SR',SWE:'SE',CHE:'CH',SYR:'SY',TJK:'TJ',TZA:'TZ',THA:'TH',TLS:'TL',
  TGO:'TG',TON:'TO',TTO:'TT',TUN:'TN',TUR:'TR',TKM:'TM',TUV:'TV',UGA:'UG',UKR:'UA',
  ARE:'AE',GBR:'GB',USA:'US',URY:'UY',UZB:'UZ',VUT:'VU',VAT:'VA',VEN:'VE',VNM:'VN',
  YEM:'YE',ZMB:'ZM',ZWE:'ZW',
};

function flagUrl(iso3: string): string {
  const cc = ISO3_TO_2[iso3.toUpperCase()];
  return cc ? `https://flagcdn.com/w160/${cc.toLowerCase()}.png` : '';
}

// ─── Projection helpers ────────────────────────────────

function latRad(lat: number): number { return Math.sin(lat * Math.PI / 180); }

interface Point { x: number; y: number; }

function project(lat: number, lng: number): Point {
  const x = (lng + 180) / 360 * 1080;
  const y = (90 - lat) / 180 * 1920;
  return { x, y };
}

// ─── Icons (SVG paths) ─────────────────────────────────

const ICON_PATHS: Record<string, string> = {
  alliance: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z',
  conflict: 'M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-2-3.5l6-4.5-6-4.5v9z',
  colonial: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z',
  erosion: 'M12 2c-5.33 4.55-8 8.48-8 11.8 0 4.98 3.8 8.2 8 8.2s8-3.22 8-8.2c0-3.32-2.67-7.25-8-11.8z',
};

const ICON_COLORS: Record<string, string> = {
  alliance: '#4ADE80',
  conflict: '#FF4444',
  colonial: '#FBBF24',
  erosion: '#00B4D8',
};

// ─── Main Component ────────────────────────────────────

interface Props {
  geopolitical?: GeopoliticalData;
  currentMs: number;
}

export const GeopoliticalOverlay: React.FC<Props> = ({ geopolitical, currentMs }) => {
  const frame = useCurrentFrame();
  if (!geopolitical) return null;

  return (
    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', zIndex: 150 }}>
      {/* Year transitions */}
      {geopolitical.yearTransitions?.map((yt, i) => {
        const active = currentMs >= yt.startMs && currentMs < yt.startMs + yt.durationMs;
        if (!active) return null;
        const progress = Math.min((currentMs - yt.startMs) / yt.durationMs, 1);
        const scale = interpolate(progress, [0, 0.3, 1], [0.3, 1.2, 2.5], { easing: Easing.out(Easing.ease) });
        const opacity = interpolate(progress, [0, 0.2, 0.7, 1], [0, 0.15, 0.12, 0]);
        const blur = interpolate(progress, [0, 1], [0, 8]);
        return (
          <div key={`yt-${i}`} style={{
            position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
            opacity, filter: `blur(${blur}px)`,
          }}>
            <span style={{
              fontSize: 320, fontWeight: 900, color: '#ffffff',
              fontFamily: '"Montserrat Black", Inter, Arial Black, sans-serif',
              textShadow: '0 0 60px rgba(255,255,255,0.1)',
              transform: `scale(${scale})`,
              letterSpacing: '0.08em',
            }}>
              {yt.year}
            </span>
          </div>
        );
      })}

      {/* Extruded country flags */}
      {geopolitical.extrudedCountries?.map((ec, i) => {
        const url = ec.flagUrl || flagUrl(ec.iso3);
        if (!url) return null;
        const pos = project(
          (i * 20 + 10) > 90 ? 0 : i * 20 + 10,
          i * 40 - 180
        );
        const pulse = interpolate(Math.sin(frame / 30 + i), [-1, 1], [0.9, 1]);
        return (
          <div key={`flag-${i}`} style={{
            position: 'absolute', left: pos.x - 40, top: pos.y - 30,
            width: 80, height: 60,
            transform: `scale(${pulse})`,
            filter: 'drop-shadow(0 4px 16px rgba(0,0,0,0.5))',
          }}>
            <img src={url} width={80} height={60} style={{ borderRadius: 4, objectFit: 'cover' }}/>
          </div>
        );
      })}

      {/* Distance arrows */}
      {geopolitical.distanceArrows?.map((da, i) => {
        const active = currentMs >= da.startMs && currentMs < da.startMs + da.durationMs;
        if (!active) return null;
        const from = project(da.fromLat, da.fromLng);
        const to = project(da.toLat, da.toLng);
        const progress = Math.min((currentMs - da.startMs) / 300, 1);
        const pathProgress = Math.min((currentMs - da.startMs) / da.durationMs, 1);
        const drawProgress = interpolate(pathProgress, [0, 1], [0, 1], { easing: Easing.out(Easing.ease) });

        const mx = (from.x + to.x) / 2;
        const my = (from.y + to.y) / 2;
        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const cx = mx - dy * 0.15;
        const cy = my + dx * 0.15;

        const endX = from.x + (to.x - from.x) * drawProgress;
        const endY = from.y + (to.y - from.y) * drawProgress;
        const cEndX = from.x + (cx - from.x) * drawProgress;
        const cEndY = from.y + (cy - from.y) * drawProgress;

        const arrowOpacity = Math.min(progress * 2, 1);

        return (
          <svg key={`arrow-${i}`} style={{ position: 'absolute', inset: 0, width: 1080, height: 1920, opacity: arrowOpacity }}>
            <defs>
              <marker id={`arrowhead-${i}`} markerWidth={10} markerHeight={7} refX={9} refY={3.5} orient="auto" markerUnits="userSpaceOnUse">
                <polygon points="0 0, 10 3.5, 0 7" fill="#FFEA00"/>
              </marker>
            </defs>
            <path d={`M${from.x},${from.y} Q${cEndX},${cEndY} ${endX},${endY}`}
              fill="none" stroke="#FFEA00" strokeWidth={2.5}
              strokeDasharray={drawProgress < 1 ? `${drawProgress * 200},200` : 'none'}
              markerEnd={`url(#arrowhead-${i})`}
              style={{ filter: 'drop-shadow(0 0 6px rgba(255,234,0,0.5))' }}
            />
            {drawProgress > 0.5 && (
              <text x={cEndX} y={cEndY - 16} textAnchor="middle"
                fill="#ffffff" fontSize={20} fontWeight={700}
                fontFamily='"Montserrat Bold", Inter, sans-serif'
                style={{ textShadow: '0 0 12px rgba(0,0,0,0.8), 0 2px 4px rgba(0,0,0,0.9)' }}
              >
                {da.label}
              </text>
            )}
          </svg>
        );
      })}

      {/* Thematic icons */}
      {geopolitical.thematicIcons?.map((ti, i) => {
        const active = currentMs >= ti.startMs && currentMs < ti.startMs + 3000;
        if (!active) return null;
        const pos = project(ti.lat, ti.lng);
        const localProgress = Math.min(Math.max((currentMs - ti.startMs) / 400, 0), 1);
        const popScale = interpolate(localProgress, [0, 0.3, 1], [0, 1.2, 1], { easing: Easing.out(Easing.back) });
        const iconOpacity = interpolate(localProgress, [0, 0.2, 1], [0, 1, 1]);
        const color = ICON_COLORS[ti.type] || '#ffffff';

        return (
          <div key={`icon-${i}`} style={{
            position: 'absolute', left: pos.x - 30, top: pos.y - 30,
            width: 60, height: 60, borderRadius: '50%',
            background: `${color}22`, border: `2px solid ${color}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            transform: `scale(${popScale})`, opacity: iconOpacity,
            boxShadow: `0 0 20px ${color}44, 0 4px 12px rgba(0,0,0,0.4)`,
            backdropFilter: 'blur(4px)',
          }}>
            <svg width={32} height={32} viewBox="0 0 24 24" fill={color}>
              <path d={ICON_PATHS[ti.type] || ICON_PATHS.conflict}/>
            </svg>
            {ti.label && (
              <div style={{
                position: 'absolute', bottom: -24, left: '50%', transform: 'translateX(-50%)',
                fontSize: 11, color: '#ffffff', fontWeight: 700, whiteSpace: 'nowrap',
                fontFamily: THEME.fontFamily, textShadow: '0 1px 6px rgba(0,0,0,0.8)',
                letterSpacing: '0.04em',
              }}>
                {ti.label}
              </div>
            )}
          </div>
        );
      })}

      {/* Boundary lines */}
      {geopolitical.boundaryLines?.map((bl, i) => {
        const active = currentMs >= bl.startMs && currentMs < bl.startMs + bl.durationMs;
        if (!active || bl.waypoints.length < 2) return null;
        const progress = Math.min((currentMs - bl.startMs) / bl.durationMs, 1);
        const pathStr = bl.waypoints.map((wp, wi) => {
          const p = project(wp.lat, wp.lng);
          return `${wi === 0 ? 'M' : 'L'}${p.x},${p.y}`;
        }).join(' ');

        return (
          <svg key={`bl-${i}`} style={{ position: 'absolute', inset: 0, width: 1080, height: 1920 }}>
            <path d={pathStr} fill="none" stroke={bl.colorA} strokeWidth={4}
              strokeDasharray={`${8 * progress},${8 * (1 - progress) > 0 ? 8 * (1 - progress) : 0}`}
              opacity={progress}
            />
            <path d={pathStr} fill="none" stroke={bl.colorB} strokeWidth={4}
              strokeDasharray={`${8 * progress},${8 * (1 - progress) > 0 ? 8 * (1 - progress) : 0}`}
              strokeDashoffset={4} opacity={progress}
            />
          </svg>
        );
      })}

      {/* Historical overlays */}
      {geopolitical.historicalOverlays?.map((ho, i) => {
        const active = currentMs >= ho.startMs && currentMs < ho.startMs + ho.durationMs;
        if (!active || ho.waypoints.length < 3) return null;
        const progress = Math.min((currentMs - ho.startMs) / 500, 1);
        const pathStr = ho.waypoints.map((wp, wi) => {
          const p = project(wp.lat, wp.lng);
          return `${wi === 0 ? 'M' : 'L'}${p.x},${p.y}`;
        }).join(' ') + ' Z';

        return (
          <svg key={`ho-${i}`} style={{ position: 'absolute', inset: 0, width: 1080, height: 1920 }}>
            <path d={pathStr} fill={ho.color} fillOpacity={ho.opacity * progress}
              stroke={ho.color} strokeWidth={1.5} strokeOpacity={progress * 0.6}
              strokeDasharray="6,4"
            />
            <text x={540} y={960} textAnchor="middle" fill="#ffffff"
              fontSize={28} fontWeight={700} opacity={progress * 0.7}
              fontFamily={THEME.fontFamily}
              style={{ textShadow: '0 0 20px rgba(0,0,0,0.8)' }}
            >
              {ho.label}
            </text>
          </svg>
        );
      })}
    </div>
  );
};
