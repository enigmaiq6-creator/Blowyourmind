import { useCurrentFrame, useVideoConfig, interpolate, Easing } from 'remotion';
import React from 'react';

interface Word {
  text: string;
  start: number;
  end: number;
}

const ACCENT = '#FFD700';
const STROKE = '3.5px #000000';

export const Subtitles: React.FC<{ words: Word[] }> = ({ words }) => {
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
      {phrases.map((phrase, pi) => {
        const startMs = phrase.start;
        const endMs = phrase.end;
        const active = nowMs >= startMs && nowMs < endMs;
        if (!active) return null;

        const phraseEnter = interpolate(
          Math.min((nowMs - startMs) / 120, 1),
          [0, 1],
          [15, 0],
          { easing: Easing.out(Easing.ease) }
        );

        const phraseOpacity = interpolate(
          Math.min((nowMs - startMs) / 120, 1),
          [0, 1],
          [0, 1],
          { easing: Easing.out(Easing.ease) }
        );

        return (
          <div key={pi} style={{ 
            position: 'absolute', left: 0, right: 0, top: 695,
            transform: `translateY(${phraseEnter}px)`,
            opacity: phraseOpacity,
            display: 'flex', justifyContent: 'center', zIndex: 100,
            pointerEvents: 'none',
          }}>
            <div style={{
              display: 'flex', alignItems: 'baseline', justifyContent: 'center',
              gap: 7, flexWrap: 'wrap', maxWidth: '92%',
            }}>
              {phrase.words.map((word, wi) => {
                const wStart = word.start;
                const wEnd = word.end;
                const isCurrentWord = nowMs >= wStart && nowMs < wEnd;

                const wordFadeIn = interpolate(
                  Math.min(Math.max((nowMs - wStart) / 80, 0), 1),
                  [0, 1],
                  [0, 1],
                  { easing: Easing.out(Easing.ease) }
                );

                const wordScale = isCurrentWord
                  ? interpolate(
                      Math.min(Math.max((nowMs - wStart) / 120, 0), 1),
                      [0, 1],
                      [0.9, 1],
                      { easing: Easing.out(Easing.back) }
                    )
                  : 1;

                return (
                  <span key={wi} style={{
                    position: 'relative',
                    display: 'inline-block',
                    fontSize: isCurrentWord ? 66 : 52,
                    fontFamily: '"Montserrat Bold", Inter, Arial, sans-serif',
                    fontWeight: 900,
                    color: isCurrentWord ? ACCENT : '#FFFFFF',
                    WebkitTextStroke: STROKE,
                    textShadow: isCurrentWord
                      ? `0 0 20px ${ACCENT}66, 0 4px 12px rgba(0,0,0,0.8)`
                      : '0 3px 8px rgba(0,0,0,0.7)',
                    lineHeight: 1.4,
                    letterSpacing: '0.02em',
                    transform: `scale(${wordScale})`,
                    opacity: wordFadeIn,
                    transition: 'color 0.1s ease',
                  }}>
                    {word.text}
                    {isCurrentWord && (
                      <div style={{
                        position: 'absolute', bottom: -4, left: '10%', right: '10%',
                        height: 5,
                        background: ACCENT,
                        borderRadius: 3,
                        boxShadow: `0 0 16px ${ACCENT}AA`,
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
