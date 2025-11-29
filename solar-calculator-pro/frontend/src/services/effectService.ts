/**
 * Task 205: Effect Engine Core
 * ============================
 * Centralized effect management service for animations, transitions, shadows, and visual effects.
 */

// ============================================================================
// Types and Interfaces
// ============================================================================

export type AnimationType = 
  | 'fade' | 'slide' | 'scale' | 'rotate' | 'bounce' | 'shake' 
  | 'pulse' | 'flip' | 'swing' | 'wobble' | 'zoom' | 'none';

export type TransitionTiming = 
  | 'linear' | 'ease' | 'ease-in' | 'ease-out' | 'ease-in-out' 
  | 'spring' | 'bounce' | 'elastic';

export type ShadowSize = 'none' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'inner';

export type BlurAmount = 'none' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl';

export interface AnimationConfig {
  type: AnimationType;
  duration: number; // ms
  delay: number; // ms
  timing: TransitionTiming;
  iterations: number | 'infinite';
  direction: 'normal' | 'reverse' | 'alternate' | 'alternate-reverse';
  fillMode: 'none' | 'forwards' | 'backwards' | 'both';
}

export interface TransitionConfig {
  property: string | string[];
  duration: number; // ms
  timing: TransitionTiming;
  delay: number; // ms
}

export interface ShadowConfig {
  size: ShadowSize;
  color?: string;
  opacity?: number;
  custom?: {
    x: number;
    y: number;
    blur: number;
    spread: number;
    color: string;
  };
}

export interface BlurConfig {
  amount: BlurAmount;
  custom?: number; // px
}

export interface BorderConfig {
  width: number;
  style: 'solid' | 'dashed' | 'dotted' | 'double' | 'groove' | 'ridge' | 'none';
  color: string;
  radius: number | string;
}

export interface HoverEffectConfig {
  scale?: number;
  translateY?: number;
  shadow?: ShadowSize;
  brightness?: number;
  opacity?: number;
  borderColor?: string;
  backgroundColor?: string;
  transition?: TransitionConfig;
}

export interface EffectPreset {
  name: string;
  description: string;
  animation?: Partial<AnimationConfig>;
  transition?: Partial<TransitionConfig>;
  shadow?: ShadowConfig;
  blur?: BlurConfig;
  border?: Partial<BorderConfig>;
  hover?: HoverEffectConfig;
}

// ============================================================================
// Default Configurations
// ============================================================================

const DEFAULT_ANIMATION: AnimationConfig = {
  type: 'fade',
  duration: 300,
  delay: 0,
  timing: 'ease-out',
  iterations: 1,
  direction: 'normal',
  fillMode: 'both',
};

const DEFAULT_TRANSITION: TransitionConfig = {
  property: 'all',
  duration: 200,
  timing: 'ease',
  delay: 0,
};

// ============================================================================
// CSS Generation Utilities
// ============================================================================

const TIMING_FUNCTIONS: Record<TransitionTiming, string> = {
  linear: 'linear',
  ease: 'ease',
  'ease-in': 'ease-in',
  'ease-out': 'ease-out',
  'ease-in-out': 'ease-in-out',
  spring: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
  bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  elastic: 'cubic-bezier(0.68, -0.6, 0.32, 1.6)',
};

const SHADOW_PRESETS: Record<ShadowSize, string> = {
  none: 'none',
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.05)',
};

const BLUR_PRESETS: Record<BlurAmount, string> = {
  none: 'blur(0)',
  sm: 'blur(4px)',
  md: 'blur(8px)',
  lg: 'blur(12px)',
  xl: 'blur(16px)',
  '2xl': 'blur(24px)',
  '3xl': 'blur(40px)',
};

// ============================================================================
// Animation Keyframes
// ============================================================================

const ANIMATION_KEYFRAMES: Record<AnimationType, string> = {
  none: '',
  fade: `
    @keyframes effectFade {
      from { opacity: 0; }
      to { opacity: 1; }
    }
  `,
  slide: `
    @keyframes effectSlide {
      from { transform: translateY(-20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
  `,
  scale: `
    @keyframes effectScale {
      from { transform: scale(0.8); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }
  `,
  rotate: `
    @keyframes effectRotate {
      from { transform: rotate(-180deg); opacity: 0; }
      to { transform: rotate(0deg); opacity: 1; }
    }
  `,
  bounce: `
    @keyframes effectBounce {
      0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
      40% { transform: translateY(-20px); }
      60% { transform: translateY(-10px); }
    }
  `,
  shake: `
    @keyframes effectShake {
      0%, 100% { transform: translateX(0); }
      10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
      20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
  `,
  pulse: `
    @keyframes effectPulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.05); }
    }
  `,
  flip: `
    @keyframes effectFlip {
      from { transform: perspective(400px) rotateY(90deg); opacity: 0; }
      to { transform: perspective(400px) rotateY(0deg); opacity: 1; }
    }
  `,
  swing: `
    @keyframes effectSwing {
      20% { transform: rotate(15deg); }
      40% { transform: rotate(-10deg); }
      60% { transform: rotate(5deg); }
      80% { transform: rotate(-5deg); }
      100% { transform: rotate(0deg); }
    }
  `,
  wobble: `
    @keyframes effectWobble {
      0% { transform: translateX(0%); }
      15% { transform: translateX(-25%) rotate(-5deg); }
      30% { transform: translateX(20%) rotate(3deg); }
      45% { transform: translateX(-15%) rotate(-3deg); }
      60% { transform: translateX(10%) rotate(2deg); }
      75% { transform: translateX(-5%) rotate(-1deg); }
      100% { transform: translateX(0%); }
    }
  `,
  zoom: `
    @keyframes effectZoom {
      from { transform: scale(0); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }
  `,
};

// ============================================================================
// Effect Presets
// ============================================================================

export const EFFECT_PRESETS: Record<string, EffectPreset> = {
  subtle: {
    name: 'Subtle',
    description: 'Minimal, professional effects',
    animation: { type: 'fade', duration: 200 },
    transition: { duration: 150, timing: 'ease' },
    shadow: { size: 'sm' },
    hover: { scale: 1.02, shadow: 'md' },
  },
  standard: {
    name: 'Standard',
    description: 'Balanced effects for everyday use',
    animation: { type: 'fade', duration: 300 },
    transition: { duration: 200, timing: 'ease-out' },
    shadow: { size: 'md' },
    hover: { scale: 1.03, shadow: 'lg', translateY: -2 },
  },
  playful: {
    name: 'Playful',
    description: 'Fun, bouncy effects',
    animation: { type: 'bounce', duration: 500 },
    transition: { duration: 300, timing: 'bounce' },
    shadow: { size: 'lg' },
    hover: { scale: 1.05, shadow: 'xl', translateY: -4 },
  },
  dramatic: {
    name: 'Dramatic',
    description: 'Bold, attention-grabbing effects',
    animation: { type: 'zoom', duration: 400 },
    transition: { duration: 250, timing: 'spring' },
    shadow: { size: 'xl' },
    hover: { scale: 1.08, shadow: '2xl', translateY: -6 },
  },
  minimal: {
    name: 'Minimal',
    description: 'Almost no effects',
    animation: { type: 'none', duration: 0 },
    transition: { duration: 100, timing: 'linear' },
    shadow: { size: 'none' },
    hover: { opacity: 0.9 },
  },
};

// ============================================================================
// Effect Engine Service Class
// ============================================================================

class EffectService {
  private currentPreset: string = 'standard';
  private customEffects: Map<string, EffectPreset> = new Map();
  private injectedStyles: Set<string> = new Set();

  constructor() {
    this.injectBaseKeyframes();
  }

  // --------------------------------------------------------------------------
  // Initialization
  // --------------------------------------------------------------------------

  private injectBaseKeyframes(): void {
    if (typeof document === 'undefined') return;
    
    const styleId = 'effect-engine-keyframes';
    if (document.getElementById(styleId)) return;

    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = Object.values(ANIMATION_KEYFRAMES).join('\n');
    document.head.appendChild(style);
  }

  // --------------------------------------------------------------------------
  // Animation Generation
  // --------------------------------------------------------------------------

  generateAnimation(config: Partial<AnimationConfig> = {}): string {
    const merged = { ...DEFAULT_ANIMATION, ...config };
    
    if (merged.type === 'none') return 'none';

    const animationName = `effect${merged.type.charAt(0).toUpperCase() + merged.type.slice(1)}`;
    const timing = TIMING_FUNCTIONS[merged.timing];
    const iterations = merged.iterations === 'infinite' ? 'infinite' : merged.iterations;

    return `${animationName} ${merged.duration}ms ${timing} ${merged.delay}ms ${iterations} ${merged.direction} ${merged.fillMode}`;
  }

  getAnimationStyle(config: Partial<AnimationConfig> = {}): React.CSSProperties {
    return {
      animation: this.generateAnimation(config),
    };
  }

  // --------------------------------------------------------------------------
  // Transition Generation
  // --------------------------------------------------------------------------

  generateTransition(config: Partial<TransitionConfig> = {}): string {
    const merged = { ...DEFAULT_TRANSITION, ...config };
    const timing = TIMING_FUNCTIONS[merged.timing];
    const properties = Array.isArray(merged.property) 
      ? merged.property.join(', ') 
      : merged.property;

    return `${properties} ${merged.duration}ms ${timing} ${merged.delay}ms`;
  }

  getTransitionStyle(config: Partial<TransitionConfig> = {}): React.CSSProperties {
    return {
      transition: this.generateTransition(config),
    };
  }

  // --------------------------------------------------------------------------
  // Shadow Generation
  // --------------------------------------------------------------------------

  generateShadow(config: ShadowConfig): string {
    if (config.custom) {
      const { x, y, blur, spread, color } = config.custom;
      return `${x}px ${y}px ${blur}px ${spread}px ${color}`;
    }
    
    let shadow = SHADOW_PRESETS[config.size];
    
    if (config.color && config.size !== 'none') {
      // Replace default color with custom color
      shadow = shadow.replace(/rgb\([^)]+\)/g, config.color);
    }
    
    return shadow;
  }

  getShadowStyle(config: ShadowConfig): React.CSSProperties {
    return {
      boxShadow: this.generateShadow(config),
    };
  }

  // --------------------------------------------------------------------------
  // Blur Generation
  // --------------------------------------------------------------------------

  generateBlur(config: BlurConfig): string {
    if (config.custom !== undefined) {
      return `blur(${config.custom}px)`;
    }
    return BLUR_PRESETS[config.amount];
  }

  getBlurStyle(config: BlurConfig): React.CSSProperties {
    return {
      filter: this.generateBlur(config),
    };
  }

  // --------------------------------------------------------------------------
  // Border Generation
  // --------------------------------------------------------------------------

  generateBorder(config: Partial<BorderConfig>): React.CSSProperties {
    const styles: React.CSSProperties = {};
    
    if (config.width !== undefined) {
      styles.borderWidth = `${config.width}px`;
    }
    if (config.style) {
      styles.borderStyle = config.style;
    }
    if (config.color) {
      styles.borderColor = config.color;
    }
    if (config.radius !== undefined) {
      styles.borderRadius = typeof config.radius === 'number' 
        ? `${config.radius}px` 
        : config.radius;
    }
    
    return styles;
  }

  // --------------------------------------------------------------------------
  // Hover Effect Generation
  // --------------------------------------------------------------------------

  generateHoverStyles(config: HoverEffectConfig): {
    base: React.CSSProperties;
    hover: React.CSSProperties;
  } {
    const base: React.CSSProperties = {};
    const hover: React.CSSProperties = {};

    // Add transition
    if (config.transition) {
      base.transition = this.generateTransition(config.transition);
    } else {
      base.transition = this.generateTransition({ duration: 200 });
    }

    // Build hover transforms
    const transforms: string[] = [];
    
    if (config.scale !== undefined) {
      transforms.push(`scale(${config.scale})`);
    }
    if (config.translateY !== undefined) {
      transforms.push(`translateY(${config.translateY}px)`);
    }
    
    if (transforms.length > 0) {
      hover.transform = transforms.join(' ');
    }

    // Other hover properties
    if (config.shadow) {
      hover.boxShadow = SHADOW_PRESETS[config.shadow];
    }
    if (config.brightness !== undefined) {
      hover.filter = `brightness(${config.brightness})`;
    }
    if (config.opacity !== undefined) {
      hover.opacity = config.opacity;
    }
    if (config.borderColor) {
      hover.borderColor = config.borderColor;
    }
    if (config.backgroundColor) {
      hover.backgroundColor = config.backgroundColor;
    }

    return { base, hover };
  }

  // --------------------------------------------------------------------------
  // Preset Management
  // --------------------------------------------------------------------------

  setPreset(presetName: string): void {
    if (EFFECT_PRESETS[presetName] || this.customEffects.has(presetName)) {
      this.currentPreset = presetName;
    } else {
      console.warn(`Effect preset "${presetName}" not found`);
    }
  }

  getPreset(presetName?: string): EffectPreset | undefined {
    const name = presetName || this.currentPreset;
    return EFFECT_PRESETS[name] || this.customEffects.get(name);
  }

  getCurrentPreset(): EffectPreset | undefined {
    return this.getPreset(this.currentPreset);
  }

  getAllPresets(): Record<string, EffectPreset> {
    const custom: Record<string, EffectPreset> = {};
    this.customEffects.forEach((preset, name) => {
      custom[name] = preset;
    });
    return { ...EFFECT_PRESETS, ...custom };
  }

  addCustomPreset(name: string, preset: EffectPreset): void {
    this.customEffects.set(name, preset);
  }

  removeCustomPreset(name: string): boolean {
    return this.customEffects.delete(name);
  }

  // --------------------------------------------------------------------------
  // Combined Effect Generation
  // --------------------------------------------------------------------------

  getPresetStyles(presetName?: string): React.CSSProperties {
    const preset = this.getPreset(presetName);
    if (!preset) return {};

    const styles: React.CSSProperties = {};

    if (preset.animation) {
      Object.assign(styles, this.getAnimationStyle(preset.animation));
    }
    if (preset.transition) {
      Object.assign(styles, this.getTransitionStyle(preset.transition));
    }
    if (preset.shadow) {
      Object.assign(styles, this.getShadowStyle(preset.shadow));
    }
    if (preset.blur) {
      Object.assign(styles, this.getBlurStyle(preset.blur));
    }
    if (preset.border) {
      Object.assign(styles, this.generateBorder(preset.border));
    }

    return styles;
  }

  // --------------------------------------------------------------------------
  // CSS Class Generation
  // --------------------------------------------------------------------------

  generateCSSClass(className: string, preset: EffectPreset): string {
    const styles = this.getPresetStyles();
    const hoverStyles = preset.hover 
      ? this.generateHoverStyles(preset.hover) 
      : { base: {}, hover: {} };

    const baseCSS = this.stylesToCSS({ ...styles, ...hoverStyles.base });
    const hoverCSS = this.stylesToCSS(hoverStyles.hover);

    return `
      .${className} {
        ${baseCSS}
      }
      .${className}:hover {
        ${hoverCSS}
      }
    `;
  }

  private stylesToCSS(styles: React.CSSProperties): string {
    return Object.entries(styles)
      .map(([key, value]) => {
        const cssKey = key.replace(/([A-Z])/g, '-$1').toLowerCase();
        return `${cssKey}: ${value};`;
      })
      .join('\n        ');
  }

  // --------------------------------------------------------------------------
  // Dynamic Style Injection
  // --------------------------------------------------------------------------

  injectStyles(id: string, css: string): void {
    if (typeof document === 'undefined') return;
    if (this.injectedStyles.has(id)) return;

    const style = document.createElement('style');
    style.id = `effect-${id}`;
    style.textContent = css;
    document.head.appendChild(style);
    this.injectedStyles.add(id);
  }

  removeStyles(id: string): void {
    if (typeof document === 'undefined') return;
    
    const style = document.getElementById(`effect-${id}`);
    if (style) {
      style.remove();
      this.injectedStyles.delete(id);
    }
  }
}

// ============================================================================
// Singleton Export
// ============================================================================

export const effectService = new EffectService();

// ============================================================================
// React Hooks
// ============================================================================

import { useState, useCallback, useMemo } from 'react';

export function useAnimation(config: Partial<AnimationConfig> = {}) {
  const style = useMemo(() => effectService.getAnimationStyle(config), [config]);
  return { style, css: effectService.generateAnimation(config) };
}

export function useTransition(config: Partial<TransitionConfig> = {}) {
  const style = useMemo(() => effectService.getTransitionStyle(config), [config]);
  return { style, css: effectService.generateTransition(config) };
}

export function useShadow(config: ShadowConfig) {
  const style = useMemo(() => effectService.getShadowStyle(config), [config]);
  return { style, css: effectService.generateShadow(config) };
}

export function useHoverEffect(config: HoverEffectConfig) {
  const [isHovered, setIsHovered] = useState(false);
  const { base, hover } = useMemo(() => effectService.generateHoverStyles(config), [config]);

  const handlers = {
    onMouseEnter: useCallback(() => setIsHovered(true), []),
    onMouseLeave: useCallback(() => setIsHovered(false), []),
  };

  const style = isHovered ? { ...base, ...hover } : base;

  return { style, isHovered, handlers };
}

export function useEffectPreset(presetName?: string) {
  const preset = effectService.getPreset(presetName);
  const styles = useMemo(() => effectService.getPresetStyles(presetName), [presetName]);
  
  return { preset, styles };
}

export default effectService;
