import { interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import React from 'react';

interface Word {
  text: string;
  start: number; // in ms
  end: number; // in ms
}

export const Subtitles: React.FC<{ words: Word[], topHeadline?: string }> = ({ words, topHeadline }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Group words into phrases of 1-2 words for extremely fast pacing
  const phrases: { words: Word[], start: number, end: number }[] = [];
  for (let i = 0; i < words.length; i += 2) {
    const chunk = words.slice(i, i + 2);
    phrases.push({
      words: chunk,
      start: chunk[0].start,
      end: chunk[chunk.length - 1].end
    });
  }

  return (
    <div style={{ flex: 1, backgroundColor: 'transparent', position: 'relative', overflow: 'hidden' }}>
      
      {/* Top Headline (Curiosity Gap) */}
      {topHeadline && (
        <div style={{
          position: 'absolute',
          top: 150, // High at the top but below safe zones
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 100,
          width: '90%',
          textAlign: 'center'
        }}>
          <h1 style={{
            color: '#FFFFFF',
            fontFamily: 'Impact, sans-serif',
            fontSize: 75,
            fontWeight: '900',
            textTransform: 'uppercase',
            margin: 0,
            lineHeight: 1.1,
            // Thick black stroke using webkit text stroke + intense text shadow
            WebkitTextStroke: '4px #000000',
            textShadow: '8px 8px 10px rgba(0,0,0,0.8)'
          }}>
            {topHeadline}
          </h1>
        </div>
      )}

      {/* Center Subtitles */}
      {phrases.map((phrase, pi) => {
        const startFrame = (phrase.start / 1000) * fps;
        const endFrame = (phrase.end / 1000) * fps;
        const isActivePhrase = frame >= startFrame && frame < endFrame;

        if (!isActivePhrase) return null;

        return (
          <div key={pi} style={{ 
              position: 'absolute', 
              inset: 0, 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              justifyContent: 'center', // Centered precisely
          }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '15px 30px', maxWidth: '85%' }}>
              {phrase.words.map((word, wi) => {
                const wStart = (word.start / 1000) * fps;
                const wEnd = (word.end / 1000) * fps;
                const isCurrentWord = frame >= wStart && frame < wEnd;

                return (
                  <span
                    key={wi}
                    style={{
                      fontSize: 85, // Large and heavy
                      fontFamily: 'Impact, sans-serif',
                      fontWeight: '900',
                      color: isCurrentWord ? '#FFD700' : '#FFFFFF',
                      textTransform: 'uppercase',
                      display: 'inline-block',
                      lineHeight: 1.0,
                      WebkitTextStroke: '3px #000000', // Thick black stroke
                      textShadow: '5px 5px 15px rgba(0,0,0,0.9)' // Extra depth
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
