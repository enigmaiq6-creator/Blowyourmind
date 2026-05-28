import { useCurrentFrame, useVideoConfig } from 'remotion';
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
  for (let i = 0; i < words.length; i += 3) {
    const chunk = words.slice(i, i + 3);
    phrases.push({
      words: chunk,
      start: chunk[0].start,
      end: chunk[chunk.length - 1].end
    });
  }

  return (
    <div style={{ flex: 1, backgroundColor: 'transparent', position: 'relative', overflow: 'hidden' }}>
      
      {topHeadline && (
        <div style={{
          position: 'absolute',
          top: 280,
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: '#ff0000',
          padding: '15px 40px',
          borderRadius: '10px',
          zIndex: 100,
          boxShadow: '0 8px 20px rgba(0,0,0,0.6)',
          border: '4px solid #FFFF00',
          width: '80%',
          textAlign: 'center'
        }}>
          <h1 style={{
            color: '#ffffff',
            fontFamily: 'Impact, sans-serif',
            fontSize: 70,
            textTransform: 'uppercase',
            margin: 0,
            lineHeight: 1.1,
            textShadow: '3px 3px 0 #000'
          }}>
            {topHeadline}
          </h1>
        </div>
      )}

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
              justifyContent: 'flex-end',
              paddingBottom: 350
          }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '10px 25px', maxWidth: '90%' }}>
              {phrase.words.map((word, wi) => {
                const wStart = (word.start / 1000) * fps;
                const wEnd = (word.end / 1000) * fps;
                const isCurrentWord = frame >= wStart && frame < wEnd;

                return (
                  <span
                    key={wi}
                    style={{
                      fontSize: 70,
                      fontFamily: 'Impact, sans-serif',
                      fontWeight: 'bold',
                      color: isCurrentWord ? '#FFFF00' : '#FFFFFF',
                      textTransform: 'uppercase',
                      display: 'inline-block',
                      lineHeight: 1.0,
                      textShadow: '4px 4px 5px rgba(0,0,0,1)'
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
