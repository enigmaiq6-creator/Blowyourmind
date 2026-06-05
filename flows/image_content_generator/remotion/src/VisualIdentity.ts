export const THEME = {
  bg: '#0a0b10',
  bgAlt: '#050508',
  bgGradient: 'linear-gradient(135deg, #0a0b10 0%, #150a2e 50%, #0a0b10 100%)',
  textPrimary: '#ffffff',
  textSecondary: '#8f9cae',
  textTertiary: 'rgba(255,255,255,0.4)',
  accent: '#FF0078',
  accentCyan: '#00DCFF',
  accentGold: '#FFE000',
  accentGreen: '#00D25A',
  accentPurple: '#C864FF',
  accentOrange: '#FF8C00',
  glassBg: 'rgba(10,11,16,0.78)',
  glassBorder: 'rgba(255,255,255,0.08)',
  glassBlur: 'blur(20px)',
  fontFamily: '"Montserrat Black", "Arial Black", Inter, sans-serif',
} as const;

export const GRADIENTS = {
  scanline: `repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.06) 2px, rgba(0,0,0,0.06) 4px)`,
  vignette: 'radial-gradient(ellipse at center, transparent 15%, rgba(10,11,16,0.92) 98%)',
  glowPink: 'radial-gradient(circle, rgba(255,0,120,0.06) 0%, transparent 70%)',
  glowPinkStrong: 'radial-gradient(circle, rgba(255,0,120,0.08) 0%, transparent 70%)',
} as const;
