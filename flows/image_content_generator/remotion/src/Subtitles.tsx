import { useCurrentFrame, useVideoConfig, interpolate, Easing } from 'remotion';
import React from 'react';

interface Word {
  text: string;
  start: number;
  end: number;
}

interface LevelMarker {
  nivel: number;
  titulo: string;
  impacto: string;
  startTime: number;
  endTime: number;
}

const ACCENT = '#00FFFF';
const TEXT_SHADOW = '0 2px 12px rgba(0,0,0,0.9), 0 4px 24px rgba(0,0,0,0.6)';
const TEXT_STROKE = '3.5px #000000';

const IMPACT_COLORS: Record<string, { from: string; to: string }> = {
  Low: { from: '#00E676', to: '#00FFAA' },
  Medium: { from: '#00BFFF', to: '#00FFFF' },
  High: { from: '#FF4500', to: '#FF6B35' },
  Extreme: { from: '#D500F9', to: '#E040FB' },
};

function getImpactGradient(impact: string): string {
  const colors = IMPACT_COLORS[impact] || IMPACT_COLORS.Medium;
  return `linear-gradient(135deg, ${colors.from}, ${colors.to})`;
}

function getImpactGlow(impact: string): string {
  const colors = IMPACT_COLORS[impact] || IMPACT_COLORS.Medium;
  return `0 0 20px ${colors.from}66, 0 0 40px ${colors.from}33`;
}

export const Subtitles: React.FC<{ words: Word[], topHeadline?: string, levelMarkers?: LevelMarker[] }> = ({ words, topHeadline, levelMarkers }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const phrases: { words: Word[], start: number, end: number }[] = [];
  for (let i = 0; i < words.length; i += 3) {
    const chunk = words.slice(i, i + 3);
    phrases.push({
      words: chunk,
      start: chunk[0].start,
      end: chunk[chunk.length - 1].end
    });
  }

  const nowMs = (frame / fps) * 1000;

  // Find current level marker
  const currentLevel = levelMarkers ? levelMarkers.find(
    lm => nowMs >= lm.startTime && nowMs < lm.endTime
  ) : null;

  // Progress for current level
  const levelProgress = currentLevel
    ? interpolate(
        Math.min(Math.max((nowMs - currentLevel.startTime) / (currentLevel.endTime - currentLevel.startTime), 0), 1),
        [0, 1],
        [0, 100],
      )
    : 0;

  // Level badge animation
  const badgeScale = currentLevel
    ? interpolate(
        Math.min(Math.max((nowMs - currentLevel.startTime) / 200, 0), 1),
        [0, 1],
        [0.8, 1],
        { easing: Easing.out(Easing.back) }
      )
    : 0;

  return (
    <div style={{ flex: 1, backgroundColor: '#00FF00', position: 'relative', overflow: 'hidden' }}>
      
      {/* Top Headline */}
      {topHeadline && (
        <div style={{
          position: 'absolute', top: 180, left: '50%', transform: 'translateX(-50%)',
          zIndex: 100, textAlign: 'center', width: '86%',
        }}>
          <span style={{
            color: '#ffffff', fontSize: 52, fontWeight: 900,
            fontFamily: '"Montserrat Black", Inter, Arial Black, sans-serif',
            textTransform: 'uppercase', letterSpacing: '0.06em',
            WebkitTextStroke: '2.5px #000000',
            textShadow: '0 4px 20px rgba(0,0,0,0.8), 0 2px 4px rgba(0,0,0,0.9)',
          }}>
            {topHeadline}
          </span>
          <div style={{
            width: 100, height: 4, margin: '14px auto 0',
            background: `linear-gradient(90deg, transparent, ${ACCENT}, transparent)`,
            boxShadow: `0 0 12px ${ACCENT}66`,
          }}/>
        </div>
      )}

      {/* Level Badge + Title */}
      {currentLevel && levelMarkers && (
        <div style={{
          position: 'absolute', top: topHeadline ? 320 : 200,
          left: '50%', transform: 'translateX(-50%)',
          zIndex: 100, textAlign: 'center', width: '86%',
          display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8,
        }}>
          {/* Badge */}
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            padding: '6px 20px',
            borderRadius: 30,
            background: getImpactGradient(currentLevel.impacto),
            boxShadow: getImpactGlow(currentLevel.impacto),
            transform: `scale(${badgeScale})`,
          }}>
            <span style={{
              color: '#ffffff', fontSize: 22, fontWeight: 900,
              fontFamily: '"Montserrat Black", Inter, Arial Black, sans-serif',
              letterSpacing: '0.08em',
            }}>
              LEVEL {currentLevel.nivel}/7
            </span>
          </div>
          {/* Level Title */}
          <div style={{
            padding: '4px 16px',
            background: 'rgba(0,0,0,0.6)',
            borderRadius: 8,
            backdropFilter: 'blur(4px)',
          }}>
            <span style={{
              color: '#ffffff', fontSize: 30, fontWeight: 700,
              fontFamily: '"Montserrat Bold", Inter, Arial, sans-serif',
              letterSpacing: '0.04em',
              textShadow: '0 2px 8px rgba(0,0,0,0.5)',
            }}>
              {currentLevel.titulo}
            </span>
          </div>
        </div>
      )}

      {/* Word Karaoke */}
      {phrases.map((phrase, pi) => {
        const startMs = phrase.start;
        const endMs = phrase.end;
        const active = nowMs >= startMs && nowMs < endMs;
        if (!active) return null;

        const phraseEnter = interpolate(
          Math.min((nowMs - startMs) / 150, 1),
          [0, 1],
          [20, 0],
          { easing: Easing.out(Easing.ease) }
        );

        const phraseOpacity = interpolate(
          Math.min((nowMs - startMs) / 150, 1),
          [0, 1],
          [0, 1],
          { easing: Easing.out(Easing.ease) }
        );

        return (
          <div key={pi} style={{ 
            position: 'absolute', left: 0, right: 0, top: 640,
            transform: `translateY(${phraseEnter}px)`,
            opacity: phraseOpacity,
            display: 'flex', justifyContent: 'center', zIndex: 100,
            pointerEvents: 'none',
          }}>
            <div style={{
              display: 'inline-flex', flexWrap: 'wrap', justifyContent: 'center',
              alignItems: 'baseline', gap: 8, padding: '8px 16px',
              maxWidth: '90%',
            }}>
              {phrase.words.map((word, wi) => {
                const wStart = word.start;
                const wEnd = word.end;
                const isCurrentWord = nowMs >= wStart && nowMs < wEnd;

                const wordFadeIn = interpolate(
                  Math.min(Math.max((nowMs - wStart) / 100, 0), 1),
                  [0, 1],
                  [0, 1],
                  { easing: Easing.out(Easing.ease) }
                );

                const wordSlideUp = interpolate(
                  Math.min(Math.max((nowMs - wStart) / 100, 0), 1),
                  [0, 1],
                  [12, 0],
                  { easing: Easing.out(Easing.ease) }
                );

                return (
                  <span key={wi} style={{
                    position: 'relative',
                    display: 'inline-block',
                    fontSize: isCurrentWord ? 68 : 56,
                    fontFamily: '"Montserrat Bold", Inter, Arial, sans-serif',
                    fontWeight: 700,
                    color: isCurrentWord ? '#00FFFF' : '#ffffff',
                    WebkitTextStroke: isCurrentWord ? TEXT_STROKE : '2.5px #000000',
                    textShadow: isCurrentWord ? TEXT_SHADOW : '0 2px 10px rgba(0,0,0,0.6)',
                    lineHeight: 1.3,
                    letterSpacing: '0.02em',
                    transform: `translateY(${wordSlideUp}px)`,
                    opacity: wordFadeIn,
                    transition: 'color 0.08s ease, font-size 0.08s ease',
                  }}>
                    {word.text}
                    {isCurrentWord && (
                      <div style={{
                        position: 'absolute', bottom: -2, left: '5%', right: '5%',
                        height: 4,
                        background: currentLevel ? getImpactGradient(currentLevel.impacto) : ACCENT,
                        borderRadius: 2,
                        boxShadow: currentLevel ? getImpactGlow(currentLevel.impacto) : `0 0 14px ${ACCENT}88`,
                      }}/>
                    )}
                  </span>
                );
              })}
            </div>
          </div>
        );
      })}

      {/* Progress Bar (bottom) */}
      {levelMarkers && levelMarkers.length > 0 && (
        <div style={{
          position: 'absolute', bottom: 100, left: 60, right: 60,
          zIndex: 100,
        }}>
          {/* Level dots */}
          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            marginBottom: 8,
          }}>
            {levelMarkers.map((lm, i) => {
              const isActive = nowMs >= lm.startTime && nowMs < lm.endTime;
              const isPast = nowMs >= lm.endTime;
              return (
                <div key={i} style={{
                  width: isActive ? 14 : 10,
                  height: isActive ? 14 : 10,
                  borderRadius: '50%',
                  background: isPast || isActive
                    ? getImpactGradient(lm.impacto)
                    : 'rgba(255,255,255,0.25)',
                  boxShadow: isActive ? getImpactGlow(lm.impacto) : 'none',
                  transition: 'all 0.3s ease',
                }}/>
              );
            })}
          </div>
          {/* Level labels */}
          <div style={{
            display: 'flex', justifyContent: 'space-between',
          }}>
            {levelMarkers.map((lm, i) => (
              <span key={i} style={{
                fontSize: 11,
                fontFamily: '"Montserrat Bold", Inter, Arial, sans-serif',
                fontWeight: 700,
                color: nowMs >= lm.startTime ? '#ffffff' : 'rgba(255,255,255,0.3)',
                textAlign: 'center',
                transition: 'color 0.3s ease',
              }}>
                {lm.nivel}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
