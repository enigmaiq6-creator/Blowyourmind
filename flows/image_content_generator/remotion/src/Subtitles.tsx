import { useCurrentFrame, useVideoConfig, interpolate, Easing } from 'remotion';
import React from 'react';

interface Word {
  text: string;
  start: number;
  end: number;
}

const ACCENT = '#FFB800';
const TEXT_SHADOW = '0 2px 12px rgba(0,0,0,0.7), 0 4px 24px rgba(0,0,0,0.3)';

export const Subtitles: React.FC<{ words: Word[], topHeadline?: string }> = ({ words, topHeadline }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const phrases: { words: Word[], start: number, end: number }[] = [];
  for (let i = 0; i < words.length; i += 4) {
    const chunk = words.slice(i, i + 4);
    phrases.push({
      words: chunk,
      start: chunk[0].start,
      end: chunk[chunk.length - 1].end
    });
  }

  const nowMs = (frame / fps) * 1000;

  return (
    <div style={{ flex: 1, backgroundColor: '#00FF00', position: 'relative', overflow: 'hidden' }}>
      
      {topHeadline && (
        <div style={{
          position: 'absolute', top: 180, left: '50%', transform: 'translateX(-50%)',
          zIndex: 100, textAlign: 'center', width: '86%',
        }}>
          <span style={{
            color: '#ffffff', fontSize: 52, fontWeight: 900,
            fontFamily: '"Montserrat Black", Inter, Arial Black, sans-serif',
            textTransform: 'uppercase', letterSpacing: '0.06em',
            textShadow: '0 4px 20px rgba(0,0,0,0.6), 0 2px 4px rgba(0,0,0,0.8)',
          }}>
            {topHeadline}
          </span>
          <div style={{
            width: 80, height: 3, margin: '12px auto 0',
            background: `linear-gradient(90deg, transparent, ${ACCENT}, transparent)`,
          }}/>
        </div>
      )}

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
            position: 'absolute', left: 0, right: 0, bottom: 160,
            transform: `translateY(${phraseEnter}px)`,
            opacity: phraseOpacity,
            display: 'flex', justifyContent: 'center', zIndex: 100,
            pointerEvents: 'none',
          }}>
            <div style={{
              display: 'inline-flex', flexWrap: 'wrap', justifyContent: 'center',
              alignItems: 'baseline', gap: 6, padding: '8px 16px',
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
                    fontSize: isCurrentWord ? 48 : 42,
                    fontFamily: '"Montserrat Bold", Inter, Arial, sans-serif',
                    fontWeight: 700,
                    color: isCurrentWord ? '#ffffff' : 'rgba(255,255,255,0.5)',
                    textShadow: isCurrentWord ? TEXT_SHADOW : '0 1px 6px rgba(0,0,0,0.5)',
                    lineHeight: 1.3,
                    letterSpacing: '0.02em',
                    transform: `translateY(${wordSlideUp}px)`,
                    opacity: wordFadeIn,
                    transition: 'color 0.08s ease',
                  }}>
                    {word.text}
                    {isCurrentWord && (
                      <div style={{
                        position: 'absolute', bottom: -2, left: '5%', right: '5%',
                        height: 2.5,
                        background: ACCENT,
                        borderRadius: 1,
                        boxShadow: `0 0 8px ${ACCENT}66`,
                      }}/>
                    )}
                  </span>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
};
