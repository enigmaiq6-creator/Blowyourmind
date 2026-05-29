import { useCurrentFrame, useVideoConfig, interpolate, Easing } from 'remotion';
import React from 'react';

interface Word {
  text: string;
  start: number;
  end: number;
}

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
    <div style={{ flex: 1, backgroundColor: 'transparent', position: 'relative', overflow: 'hidden' }}>
      
      {topHeadline && (
        <div style={{
          position: 'absolute',
          top: 180,
          left: '50%',
          transform: 'translateX(-50%)',
          background: 'rgba(200,20,20,0.92)',
          padding: '14px 36px',
          borderRadius: 12,
          zIndex: 100,
          boxShadow: '0 8px 30px rgba(0,0,0,0.5)',
          border: '3px solid #FFD700',
          width: '82%',
          textAlign: 'center'
        }}>
          <span style={{
            color: '#ffffff',
            fontFamily: '"Montserrat Black", Inter, Arial Black, sans-serif',
            fontSize: 64,
            fontWeight: 900,
            textTransform: 'uppercase',
            lineHeight: 1.1,
            textShadow: '3px 3px 0 rgba(0,0,0,0.8)',
            letterSpacing: '0.02em',
          }}>
            {topHeadline}
          </span>
        </div>
      )}

      {phrases.map((phrase, pi) => {
        const startMs = phrase.start;
        const endMs = phrase.end;
        const active = nowMs >= startMs && nowMs < endMs;
        if (!active) return null;

        const phraseEnter = interpolate(
          Math.min((nowMs - startMs) / 120, 1),
          [0, 1],
          [14, 0],
          { easing: Easing.out(Easing.ease) }
        );

        return (
          <div key={pi} style={{ 
            position: 'absolute', left: 0, right: 0, top: '46%',
            transform: `translateY(calc(-50% + ${phraseEnter}px))`,
            display: 'flex', justifyContent: 'center', zIndex: 100,
            pointerEvents: 'none',
          }}>
            <div style={{
              display: 'inline-flex', flexWrap: 'wrap', justifyContent: 'center',
              alignItems: 'center', gap: 8, padding: '24px 40px',
              background: 'rgba(0,0,0,0.6)',
              borderRadius: 16,
              backdropFilter: 'blur(14px)',
              WebkitBackdropFilter: 'blur(14px)',
              maxWidth: '88%',
              boxShadow: '0 8px 32px rgba(0,0,0,0.35)',
            }}>
              {phrase.words.map((word, wi) => {
                const wStart = word.start;
                const wEnd = word.end;
                const isCurrentWord = nowMs >= wStart && nowMs < wEnd;
                const wordScale = isCurrentWord
                  ? interpolate(Math.min((nowMs - wStart) / 120, 1), [0, 1], [0.88, 1], { easing: Easing.out(Easing.back) })
                  : 1;

                return (
                  <span
                    key={wi}
                    style={{
                      fontSize: 56,
                      fontFamily: '"Montserrat Black", Inter, Arial Black, sans-serif',
                      fontWeight: 900,
                      color: isCurrentWord ? '#FFEA00' : 'rgba(255,255,255,0.7)',
                      textTransform: 'uppercase',
                      display: 'inline-block',
                      lineHeight: 1.15,
                      letterSpacing: '0.04em',
                      textShadow: isCurrentWord
                        ? '0 0 30px rgba(255,234,0,0.5), 0 2px 8px rgba(0,0,0,0.9)'
                        : '0 2px 8px rgba(0,0,0,0.9)',
                      WebkitTextStroke: isCurrentWord ? '1.5px rgba(0,0,0,0.4)' : '1px rgba(0,0,0,0.25)',
                      opacity: isCurrentWord ? 1 : 0.4,
                      transform: `scale(${wordScale})`,
                    }}
                  >
                    {word.text}
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
