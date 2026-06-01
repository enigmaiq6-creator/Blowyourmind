import React from 'react';
import { interpolate, useCurrentFrame, useVideoConfig, Easing, Video, Img, spring } from 'remotion';

interface TriviaQuizProps {
  question: string;
  option_a: string;
  option_b: string;
  option_c: string;
  correct_option: string; // 'A', 'B', or 'C'
  explanation: string;
  trivia_step: 'question' | 'countdown' | 'reveal';
  question_number: number;
  total_questions?: number;
  backgroundImageUrl?: string;
  videoUrl?: string;
  audioDurationMs?: number;
}

const OPTION_COLORS: Record<string, { bg: string; glow: string; text: string }> = {
  A: { bg: '#C62828', glow: 'rgba(198,40,40,0.55)',   text: '#ffffff' },
  B: { bg: '#1565C0', glow: 'rgba(21,101,192,0.55)',  text: '#ffffff' },
  C: { bg: '#E65100', glow: 'rgba(230,81,0,0.55)',    text: '#ffffff' },
};
const CORRECT_COLOR = { bg: '#1B5E20', border: '#00E676', glow: 'rgba(0,230,118,0.55)', text: '#ffffff' };
const WRONG_ALPHA   = 0.22;

export const TriviaQuiz: React.FC<TriviaQuizProps> = ({
  question,
  option_a,
  option_b,
  option_c,
  correct_option,
  explanation,
  trivia_step,
  question_number,
  total_questions = 5,
  backgroundImageUrl,
  videoUrl,
  audioDurationMs = 10000,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const progress = frame / durationInFrames;

  const isQuestion  = trivia_step === 'question';
  const isCountdown = trivia_step === 'countdown';
  const isReveal    = trivia_step === 'reveal';

  // ── Global entrance spring ───────────────────────────────────────
  const globalIn = spring({ frame, fps, config: { damping: 18, stiffness: 100 }, durationInFrames: 18 });

  // ── Background slow Ken-Burns ────────────────────────────────────
  const bgScale = interpolate(frame, [0, durationInFrames], [1.0, 1.06], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  // ── Countdown number (3 → 2 → 1) ─────────────────────────────────
  const countdownNum = isCountdown ? Math.max(1, 3 - Math.floor(progress * 3)) : 3;
  const countdownPulse = 1 + Math.sin(frame * 0.25) * 0.06;

  // ── Reveal entrance spring ───────────────────────────────────────
  const revealIn = spring({ frame: frame - 6, fps, config: { damping: 14, stiffness: 80 }, durationInFrames: 22 });

  // ── Option rendering ─────────────────────────────────────────────
  const renderOption = (letter: 'A' | 'B' | 'C', text: string, index: number) => {
    const isCorrect = correct_option === letter;

    // Staggered entrance per option (only on question step)
    const staggeredIn = spring({
      frame: frame - index * 5,
      fps,
      config: { damping: 16, stiffness: 90 },
      durationInFrames: 20,
    });
    const translateY = interpolate(staggeredIn, [0, 1], [70, 0]);

    // Determine visual state
    let bg          = OPTION_COLORS[letter].bg;
    let glow        = OPTION_COLORS[letter].glow;
    let border      = '3px solid transparent';
    let opacity     = 1;
    let scale       = 1;
    let badgeBg     = 'rgba(0,0,0,0.30)';
    let checkmark   = null as React.ReactNode;

    if (isReveal) {
      if (isCorrect) {
        bg      = CORRECT_COLOR.bg;
        glow    = CORRECT_COLOR.glow;
        border  = `4px solid ${CORRECT_COLOR.border}`;
        scale   = interpolate(revealIn, [0, 1], [1, 1.03]);
        badgeBg = 'rgba(0,0,0,0.25)';
        checkmark = (
          <span style={{ fontSize: 44, marginLeft: 16, lineHeight: 1 }}>✅</span>
        );
      } else {
        bg      = '#111122';
        glow    = 'transparent';
        opacity = interpolate(revealIn, [0, 1], [1, WRONG_ALPHA]);
        scale   = interpolate(revealIn, [0, 1], [1, 0.96]);
        badgeBg = 'rgba(255,255,255,0.08)';
      }
    }

    return (
      <div
        key={letter}
        style={{
          display: 'flex',
          alignItems: 'center',
          background: bg,
          border,
          borderRadius: 24,
          padding: '20px 32px',
          marginBottom: 20,
          boxShadow: glow !== 'transparent' ? `0 6px 28px ${glow}` : 'none',
          opacity,
          transform: isQuestion
            ? `translateY(${translateY}px) scale(${scale})`
            : `scale(${scale})`,
        }}
      >
        {/* Letter badge */}
        <div style={{
          width: 56, height: 56,
          borderRadius: '50%',
          background: badgeBg,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 26, fontWeight: 900,
          color: '#ffffff',
          fontFamily: '"Arial Black", Impact, sans-serif',
          flexShrink: 0,
          marginRight: 24,
        }}>
          {letter}
        </div>

        {/* Option text */}
        <div style={{
          fontSize: 36,
          fontWeight: 800,
          color: '#ffffff',
          fontFamily: 'Inter, system-ui, sans-serif',
          lineHeight: 1.2,
          flex: 1,
        }}>
          {text}
        </div>

        {/* Correct checkmark on reveal */}
        {isReveal && isCorrect && checkmark}
      </div>
    );
  };

  const progressBarPct = (question_number / total_questions) * 100;

  return (
    <div style={{
      width: 1080, height: 1920,
      position: 'relative', overflow: 'hidden',
      backgroundColor: '#050510',
      fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
    }}>

      {/* ── BACKGROUND ─────────────────────────────────────────────── */}
      <div style={{
        position: 'absolute', inset: 0,
        transform: `scale(${bgScale})`,
        zIndex: 1,
        transformOrigin: 'center center',
      }}>
        {videoUrl ? (
          <Video src={videoUrl} style={{ width: '100%', height: '100%', objectFit: 'cover' }} loop muted />
        ) : backgroundImageUrl ? (
          <Img src={backgroundImageUrl} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        ) : (
          <div style={{
            width: '100%', height: '100%',
            background: 'linear-gradient(160deg, #0D1117 0%, #161B22 60%, #1a1a35 100%)',
          }} />
        )}
        {/* Heavy but clean dark overlay */}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'rgba(4, 4, 14, 0.68)',
        }} />
      </div>

      {/* ── FULL-SCREEN CONTENT COLUMN ──────────────────────────────── */}
      <div style={{
        position: 'relative', zIndex: 5,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        padding: '72px 60px 90px',
      }}>

        {/* ── 1. TOP: "Question X/N" badge + progress bar ─────────── */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 20,
          marginBottom: 36,
          transform: `translateY(${interpolate(globalIn, [0,1], [-60,0])}px)`,
          opacity: globalIn,
        }}>
          <div style={{
            background: 'linear-gradient(90deg, #D50000, #FF6D00)',
            borderRadius: 40,
            padding: '14px 36px',
            fontSize: 28,
            fontWeight: 900,
            color: '#fff',
            letterSpacing: 2,
            textTransform: 'uppercase' as const,
            fontFamily: '"Arial Black", sans-serif',
            boxShadow: '0 4px 24px rgba(213,0,0,0.45)',
            flexShrink: 0,
          }}>
            Q {question_number}/{total_questions}
          </div>

          {/* Progress bar */}
          <div style={{
            flex: 1, height: 10,
            background: 'rgba(255,255,255,0.12)',
            borderRadius: 10, overflow: 'hidden',
          }}>
            <div style={{
              width: `${progressBarPct}%`,
              height: '100%',
              background: 'linear-gradient(90deg, #D50000, #FF6D00)',
              borderRadius: 10,
              boxShadow: '0 0 14px rgba(255,109,0,0.6)',
            }} />
          </div>
        </div>

        {/* ── 2. QUESTION CARD (always at top) ──────────────────────── */}
        <div style={{
          background: 'rgba(255,255,255,0.08)',
          backdropFilter: 'blur(28px)',
          border: '1.5px solid rgba(255,255,255,0.14)',
          borderRadius: 32,
          padding: '44px 52px',
          marginBottom: 36,
          boxShadow: '0 16px 56px rgba(0,0,0,0.45)',
          transform: `scale(${interpolate(globalIn, [0,1], [0.96, 1])})`,
          opacity: globalIn,
        }}>
          <div style={{
            fontSize: 52,
            fontWeight: 900,
            color: '#FFFFFF',
            lineHeight: 1.25,
            textShadow: '0 2px 14px rgba(0,0,0,0.7)',
            fontFamily: '"Arial Black", Impact, sans-serif',
          }}>
            {question}
          </div>
        </div>

        {/* ── 3. OPTIONS (A, B, C) — directly under the question ────── */}
        {!isCountdown && (
          <div>
            {renderOption('A', option_a, 0)}
            {renderOption('B', option_b, 1)}
            {renderOption('C', option_c, 2)}
          </div>
        )}

        {/* ── 4. COUNTDOWN — centered, fills remaining space ─────────── */}
        {isCountdown && (
          <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 40,
          }}>
            {/* Pulsing rings */}
            <div style={{ position: 'relative', width: 280, height: 280 }}>
              {[0, 1, 2].map((i) => (
                <div key={i} style={{
                  position: 'absolute',
                  inset: i * 18,
                  borderRadius: '50%',
                  border: `${5 - i}px solid rgba(255,224,0,${0.18 + i * 0.16})`,
                  transform: `scale(${1 + Math.sin(frame * 0.22 + i) * (0.06 - i * 0.015)})`,
                }} />
              ))}
              {/* Core circle */}
              <div style={{
                position: 'absolute',
                inset: 36,
                borderRadius: '50%',
                background: 'rgba(255,224,0,0.10)',
                border: '4px solid #FFE000',
                boxShadow: '0 0 50px rgba(255,224,0,0.50), inset 0 0 30px rgba(255,224,0,0.08)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <div style={{
                  fontSize: 100,
                  fontWeight: 900,
                  color: '#FFE000',
                  fontFamily: '"Arial Black", Impact, sans-serif',
                  lineHeight: 1,
                  textShadow: '0 0 36px rgba(255,224,0,0.90)',
                  transform: `scale(${countdownPulse})`,
                }}>
                  {countdownNum}
                </div>
              </div>
            </div>

            <div style={{
              fontSize: 44,
              fontWeight: 900,
              color: 'rgba(255,255,255,0.90)',
              letterSpacing: 5,
              textTransform: 'uppercase' as const,
              textShadow: '0 2px 12px rgba(0,0,0,0.6)',
              fontFamily: '"Arial Black", sans-serif',
            }}>
              THINK FAST!
            </div>
          </div>
        )}

        {/* ── 5. REVEAL EXPLANATION (below the options) ──────────────── */}
        {isReveal && (
          <div style={{
            marginTop: 28,
            background: 'rgba(0,200,83,0.10)',
            border: '2px solid rgba(0,230,118,0.35)',
            backdropFilter: 'blur(20px)',
            borderRadius: 28,
            padding: '28px 44px',
            boxShadow: '0 0 40px rgba(0,200,83,0.14)',
            transform: `translateY(${interpolate(revealIn, [0,1], [70, 0])}px)`,
            opacity: revealIn,
          }}>
            <div style={{
              color: '#00E676',
              fontSize: 22,
              fontWeight: 900,
              letterSpacing: 3,
              textTransform: 'uppercase' as const,
              marginBottom: 10,
              fontFamily: '"Arial Black", sans-serif',
            }}>
              💡 DID YOU KNOW?
            </div>
            <div style={{
              color: '#FFFFFF',
              fontSize: 32,
              fontWeight: 600,
              lineHeight: 1.45,
            }}>
              {explanation}
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
