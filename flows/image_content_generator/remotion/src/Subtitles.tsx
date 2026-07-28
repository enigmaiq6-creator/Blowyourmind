import { useCurrentFrame, useVideoConfig, interpolate, Easing } from 'remotion';
import React from 'react';

interface Word {
  text: string;
  start: number;
  end: number;
}

const ACCENT = '#00FFFF';

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
      {/* Top Headline (subject name) */}
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
        </div>
      )}

      {/* Word Karaoke - positioned between subjects and character */}
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
            position: 'absolute', left: 0, right: 0, top: 615,
            transform: `translateY(${phraseEnter}px)`,
            opacity: phraseOpacity,
            display: 'flex', justifyContent: 'center', zIndex: 100,
            pointerEvents: 'none',
          }}>
            <div style={{
              display: 'inline-flex', flexWrap: 'wrap', justifyContent: 'center',
              alignItems: 'baseline', gap: 8, padding: '12px 20px',
              background: 'rgba(0,0,0,0.5)',
              borderRadius: 12,
              maxWidth: '92%',
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
                    fontSize: isCurrentWord ? 62 : 50,
                    fontFamily: '"Montserrat Bold", Inter, Arial, sans-serif',
                    fontWeight: 700,
                    color: isCurrentWord ? ACCENT : '#ffffff',
                    WebkitTextStroke: isCurrentWord ? '3px #000000' : '2px #000000',
                    textShadow: isCurrentWord
                      ? '0 2px 12px rgba(0,0,0,0.9), 0 0 20px #00FFFF44'
                      : '0 2px 8px rgba(0,0,0,0.6)',
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
                        background: ACCENT,
                        borderRadius: 2,
                        boxShadow: `0 0 14px ${ACCENT}88`,
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
