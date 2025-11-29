/**
 * Task 206: Component-Specific Effects - Index
 * =============================================
 * Export all effect components and utilities.
 */

export {
  EffectWrapper,
  ButtonEffect,
  InputEffect,
  CardEffect,
  MenuEffect,
  MenuItemEffect,
  DropdownEffect,
  ModalEffect,
  ToastEffect,
  BadgeEffect,
  SkeletonEffect,
  type BaseEffectProps,
  type EffectVariant,
} from './EffectWrapper';

// Re-export effect service utilities
export {
  effectService,
  useAnimation,
  useTransition,
  useShadow,
  useHoverEffect,
  useEffectPreset,
  EFFECT_PRESETS,
  type AnimationType,
  type TransitionTiming,
  type ShadowSize,
  type BlurAmount,
  type AnimationConfig,
  type TransitionConfig,
  type ShadowConfig,
  type BlurConfig,
  type BorderConfig,
  type HoverEffectConfig,
  type EffectPreset,
} from '../../services/effectService';
