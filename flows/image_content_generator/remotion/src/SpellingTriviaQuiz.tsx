import React from 'react';
import { interpolate, useCurrentFrame, useVideoConfig, Easing, Video, Img, spring, staticFile } from 'remotion';

interface SpellingTriviaQuizProps {
  question: string;
  option_a: string;
  option_b: string;
  option_c: string;
  correct_option: string;
  trivia_step: 'question' | 'countdown' | 'reveal';
  question_number: number;
  total_questions?: number;
  backgroundImageUrl?: string;
  videoUrl?: string;
  staticFileName?: string;
  audioDurationMs?: number;
}

const YELLOW = '#FFFF00';
const CORRECT_BORDER = '#00E676';

export const SpellingTriviaQuiz: React.FC<SpellingTriviaQuizProps> = ({
  question,
  option_a, option_b, option_c,
  correct_option,
  trivia_step,
  question_number,
  total_questions = 3,
  backgroundImageUrl,
  videoUrl,
  staticFileName,
  audioDurationMs = 20000,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const progress = frame / durationInFrames;
  const isQuestion = trivia_step === 'question';
  const isCountdown = trivia_step === 'countdown';
  const isReveal = trivia_step === 'reveal';

  const globalIn = spring({ frame, fps, config: { damping: 20, stiffness: 90 }, durationInFrames: 24 });

  const bgScale = interpolate(frame, [0, durationInFrames], [1.0, 1.12], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.ease,
  });

  const countdownSec = Math.max(0, 5 - Math.floor((frame / durationInFrames) * 5));
  const countdownPulse = 1 + Math.sin(frame * 0.2) * 0.04;

  const revealFrame = frame - 8;
  const revealSlide = spring({ frame: revealFrame, fps, config: { damping: 18, stiffness: 70 }, durationInFrames: 28 });

  const progressBarWidth = (() => {
    if (isQuestion) return 100;
    if (isCountdown) return interpolate(frame, [0, durationInFrames], [100, 0], { extrapolateRight: 'clamp' });
    return 0;
  })();

  const highlightWord = (text: string) => {
    const parts = text.split(/(SPELLED CORRECTLY|CORRECT SPELLING|DEFINITION|WORD ORIGIN|meaning|opposite|synonym)/gi);
    return parts.map((part, i) =>
      /SPELLED CORRECTLY|CORRECT SPELLING|DEFINITION|WORD ORIGIN|meaning|opposite|synonym/i.test(part)
        ? <span key={i} style={{ color: YELLOW }}>{part}</span>
        : part
    );
  };

  const renderOption = (letter: string, text: string, index: number) => {
    const isCorrect = correct_option === letter;
    const staggeredIn = spring({
      frame: frame - index * 6,
      fps, config: { damping: 18, stiffness: 80 }, durationInFrames: 24,
    });
    const translateY = interpolate(staggeredIn, [0, 1], [50, 0]);

    let bg = 'rgba(0, 0, 0, 0.65)';
    let border = '2px solid rgba(255, 255, 255, 0.18)';
    let glow = 'none';
    let opacity = 1;
    let scale = 1;
    let letterColor = '#FFFFFF';

    if (isReveal) {
      if (isCorrect) {
        bg = 'rgba(0, 180, 0, 0.30)';
        border = `3px solid ${CORRECT_BORDER}`;
        glow = `0 0 40px ${CORRECT_BORDER}55`;
        scale = interpolate(revealSlide, [0, 1], [1, 1.04]);
        letterColor = YELLOW;
      } else {
        opacity = interpolate(revealSlide, [0, 1], [1, 0.15]);
        scale = interpolate(revealSlide, [0, 1], [1, 0.94]);
      }
    }

    return (
      <div
        key={letter}
        style={{
          display: 'flex', alignItems: 'center',
          background: bg, border, borderRadius: 32,
          padding: '22px 34px', marginBottom: 18,
          boxShadow: glow, opacity,
          transform: isQuestion
            ? `translateY(${translateY}px) scale(${scale})`
            : `scale(${scale})`,
          backdropFilter: 'blur(10px)',
        }}
      >
        <div style={{
          width: 54, height: 54, borderRadius: '50%',
          background: 'rgba(255,255,255,0.14)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 26, fontWeight: 900, color: letterColor,
          fontFamily: '"Arial Black", Impact, sans-serif',
          flexShrink: 0, marginRight: 24,
        }}>
          {letter}
        </div>
        <div style={{
          fontSize: 38, fontWeight: 800, color: '#FFFFFF',
          fontFamily: '"Arial Black", Impact, sans-serif',
          lineHeight: 1.25, flex: 1,
        }}>
          {text}
        </div>
        {isReveal && isCorrect && (
          <span style={{ fontSize: 42, marginLeft: 12, color: CORRECT_BORDER }}>✓</span>
        )}
      </div>
    );
  };

  return (
    <div style={{
      width: 1080, height: 1920,
      position: 'relative', overflow: 'hidden',
      backgroundColor: '#0A0A0A',
      fontFamily: '"Arial Black", Impact, sans-serif',
    }}>
      <div style={{
        position: 'absolute', inset: 0,
        transform: `scale(${bgScale})`,
        zIndex: 1, transformOrigin: 'center center',
      }}>
        {staticFileName ? (
          <Video src={staticFile(staticFileName)} style={{ width: '100%', height: '100%', objectFit: 'cover' }} loop muted />
        ) : videoUrl ? (
          <Video src={videoUrl} style={{ width: '100%', height: '100%', objectFit: 'cover' }} loop muted />
        ) : backgroundImageUrl ? (
          <Img src={backgroundImageUrl} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        ) : (
          <div style={{
            width: '100%', height: '100%',
            background: 'linear-gradient(160deg, #0D1117 0%, #161B22 50%, #1a1a35 100%)',
          }} />
        )}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'rgba(0, 0, 0, 0.50)',
        }} />
      </div>

      <div style={{
        position: 'relative', zIndex: 5,
        height: '100%',
        display: 'flex', flexDirection: 'column',
        padding: '80px 56px',
      }}>

        {/* Progress Bar */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 18,
          marginBottom: 40,
          transform: `translateY(${interpolate(globalIn, [0,1], [-40,0])}px)`,
          opacity: globalIn,
        }}>
          <div style={{
            background: 'rgba(255,255,255,0.08)',
            borderRadius: 30, padding: '10px 26px',
            fontSize: 24, fontWeight: 900, color: '#FFFFFF',
            fontFamily: '"Arial Black", sans-serif',
            flexShrink: 0,
            border: '1px solid rgba(255,255,255,0.15)',
          }}>
            Q{question_number}/{total_questions}
          </div>
          <div style={{
            flex: 1, height: 10,
            background: 'rgba(255,255,255,0.10)',
            borderRadius: 10, overflow: 'hidden',
          }}>
            <div style={{
              width: `${Math.max(0, progressBarWidth)}%`,
              height: '100%',
              background: `linear-gradient(90deg, ${YELLOW}, #FF8C00)`,
              borderRadius: 10,
              boxShadow: `0 0 14px ${YELLOW}66`,
            }} />
          </div>
        </div>

        {/* Main content area - centered vertically, shrinks if reveal is shown */}
        <div style={{
          flex: isReveal ? 0 : 1,
          display: 'flex', flexDirection: 'column',
          justifyContent: 'center',
        }}>
          {/* Question Card */}
          <div style={{
            background: 'rgba(0, 0, 0, 0.65)',
            borderRadius: 28,
            padding: '44px 48px',
            marginBottom: 36,
            border: '1.5px solid rgba(255,255,255,0.18)',
            backdropFilter: 'blur(14px)',
            transform: `scale(${interpolate(globalIn, [0,1], [0.94, 1])})`,
            opacity: globalIn,
          }}>
            <div style={{
              fontSize: 52,
              fontWeight: 900,
              color: '#FFFFFF',
              lineHeight: 1.35,
              fontFamily: '"Arial Black", Impact, sans-serif',
              textAlign: 'center',
            }}>
              {highlightWord(question)}
            </div>
          </div>

          {/* Options */}
          <div>
            {renderOption('A', option_a, 0)}
            {renderOption('B', option_b, 1)}
            {renderOption('C', option_c, 2)}
          </div>
        </div>

        {/* Countdown - small circle in upper-right, no overlay */}
        {isCountdown && (
          <div style={{
            position: 'absolute', top: 240, right: 80, zIndex: 10,
          }}>
            <div style={{
              width: 120, height: 120, borderRadius: '50%',
              background: 'rgba(0,0,0,0.75)',
              border: `4px solid ${YELLOW}`,
              boxShadow: `0 0 40px ${YELLOW}44`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              backdropFilter: 'blur(8px)',
            }}>
              <div style={{
                fontSize: 56,
                fontWeight: 900,
                color: YELLOW,
                fontFamily: '"Arial Black", Impact, sans-serif',
                lineHeight: 1,
                textShadow: `0 0 20px ${YELLOW}88`,
                transform: `scale(${countdownPulse})`,
              }}>
                {countdownSec}
              </div>
            </div>
          </div>
        )}

        {/* Reveal - positioned right below the options */}
        {isReveal && (
          <div style={{
            marginTop: 24,
            background: 'rgba(0, 180, 0, 0.12)',
            border: `2px solid ${CORRECT_BORDER}`,
            borderRadius: 28,
            padding: '24px 40px',
            backdropFilter: 'blur(14px)',
            boxShadow: `0 0 30px ${CORRECT_BORDER}22`,
            transform: `translateY(${interpolate(revealSlide, [0,1], [40, 0])}px)`,
            opacity: revealSlide,
          }}>
            <div style={{
              color: CORRECT_BORDER,
              fontSize: 22,
              fontWeight: 900,
              letterSpacing: 3,
              textTransform: 'uppercase',
              marginBottom: 8,
              fontFamily: '"Arial Black", sans-serif',
              textAlign: 'center',
            }}>
              ✓ Correct Answer
            </div>
            <div style={{
              color: '#FFFFFF',
              fontSize: 34,
              fontWeight: 700,
              lineHeight: 1.4,
              fontFamily: 'Inter, system-ui, sans-serif',
              textAlign: 'center',
            }}>
              The correct answer is <span style={{ color: YELLOW, fontWeight: 900 }}>{correct_option}</span>!
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
