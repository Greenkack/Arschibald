/**
 * Task 206: Component-Specific Effects
 * =====================================
 * Reusable effect wrapper components for buttons, inputs, cards, menus, etc.
 */

import React, { useState, useCallback, useMemo, forwardRef } from 'react';
import { effectService, useHoverEffect, HoverEffectConfig, AnimationConfig, ShadowSize } from '../../services/effectService';
import './EffectWrapper.css';

// ============================================================================
// Types
// ============================================================================

export type EffectVariant = 'subtle' | 'standard' | 'playful' | 'dramatic' | 'minimal' | 'none';

export interface BaseEffectProps {
  variant?: EffectVariant;
  animation?: Partial<AnimationConfig>;
  hoverEffect?: HoverEffectConfig;
  shadow?: ShadowSize;
  className?: string;
  disabled?: boolean;
}

// ============================================================================
// Effect Wrapper - Generic wrapper for any element
// ============================================================================

interface EffectWrapperProps extends BaseEffectProps {
  children: React.ReactNode;
  as?: keyof JSX.IntrinsicElements;
  onClick?: () => void;
  style?: React.CSSProperties;
}

export const EffectWrapper = forwardRef<HTMLDivElement, EffectWrapperProps>(({
  children,
  as: Component = 'div',
  variant = 'standard',
  animation,
  hoverEffect,
  shadow,
  className = '',
  disabled = false,
  onClick,
  style,
  ...props
}, ref) => {
  const [isHovered, setIsHovered] = useState(false);

  const effectClass = disabled ? '' : `effect-${variant}`;
  const shadowClass = shadow && !disabled ? `shadow-${shadow}` : '';
  const animationStyle = animation && !disabled 
    ? effectService.getAnimationStyle(animation) 
    : {};

  const hoverStyles = useMemo(() => {
    if (!hoverEffect || disabled) return { base: {}, hover: {} };
    return effectService.generateHoverStyles(hoverEffect);
  }, [hoverEffect, disabled]);

  const combinedStyle = {
    ...style,
    ...animationStyle,
    ...hoverStyles.base,
    ...(isHovered ? hoverStyles.hover : {}),
  };

  return React.createElement(
    Component,
    {
      ref,
      className: `effect-wrapper ${effectClass} ${shadowClass} ${className}`.trim(),
      style: combinedStyle,
      onClick: disabled ? undefined : onClick,
      onMouseEnter: () => !disabled && setIsHovered(true),
      onMouseLeave: () => setIsHovered(false),
      ...props,
    },
    children
  );
});

EffectWrapper.displayName = 'EffectWrapper';

// ============================================================================
// Button Effect - Specialized for buttons
// ============================================================================

interface ButtonEffectProps extends BaseEffectProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  ripple?: boolean;
}

export const ButtonEffect: React.FC<ButtonEffectProps> = ({
  children,
  variant = 'standard',
  animation,
  hoverEffect,
  shadow = 'sm',
  className = '',
  disabled = false,
  onClick,
  type = 'button',
  ripple = true,
}) => {
  const [rippleStyle, setRippleStyle] = useState<React.CSSProperties | null>(null);

  const handleClick = useCallback((e: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled) return;
    
    if (ripple) {
      const button = e.currentTarget;
      const rect = button.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      setRippleStyle({
        left: x,
        top: y,
      });
      
      setTimeout(() => setRippleStyle(null), 600);
    }
    
    onClick?.();
  }, [disabled, ripple, onClick]);

  const defaultHover: HoverEffectConfig = hoverEffect || {
    scale: 1.02,
    translateY: -1,
    shadow: 'md',
  };

  return (
    <EffectWrapper
      as="button"
      variant={variant}
      animation={animation}
      hoverEffect={defaultHover}
      shadow={shadow}
      className={`button-effect ${ripple ? 'ripple-enabled' : ''} ${className}`}
      disabled={disabled}
      onClick={handleClick as any}
    >
      {children}
      {rippleStyle && (
        <span 
          className="ripple-circle" 
          style={rippleStyle}
        />
      )}
    </EffectWrapper>
  );
};

// ============================================================================
// Input Effect - Specialized for input fields
// ============================================================================

interface InputEffectProps extends BaseEffectProps {
  children: React.ReactNode;
  focused?: boolean;
  error?: boolean;
  success?: boolean;
}

export const InputEffect: React.FC<InputEffectProps> = ({
  children,
  variant = 'subtle',
  shadow = 'sm',
  className = '',
  disabled = false,
  focused = false,
  error = false,
  success = false,
}) => {
  const stateClass = error ? 'input-error' : success ? 'input-success' : '';
  const focusClass = focused ? 'input-focused' : '';

  return (
    <EffectWrapper
      variant={variant}
      shadow={focused ? 'md' : shadow}
      className={`input-effect ${stateClass} ${focusClass} ${className}`}
      disabled={disabled}
    >
      {children}
    </EffectWrapper>
  );
};

// ============================================================================
// Card Effect - Specialized for cards
// ============================================================================

interface CardEffectProps extends BaseEffectProps {
  children: React.ReactNode;
  onClick?: () => void;
  interactive?: boolean;
  elevated?: boolean;
}

export const CardEffect: React.FC<CardEffectProps> = ({
  children,
  variant = 'standard',
  animation,
  hoverEffect,
  shadow = 'md',
  className = '',
  disabled = false,
  onClick,
  interactive = false,
  elevated = false,
}) => {
  const defaultHover: HoverEffectConfig = hoverEffect || (interactive ? {
    scale: 1.02,
    translateY: -4,
    shadow: 'lg',
  } : {});

  return (
    <EffectWrapper
      variant={interactive ? variant : 'minimal'}
      animation={animation}
      hoverEffect={interactive ? defaultHover : undefined}
      shadow={elevated ? 'lg' : shadow}
      className={`card-effect ${interactive ? 'interactive' : ''} ${className}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </EffectWrapper>
  );
};

// ============================================================================
// Menu Effect - Specialized for menus and dropdowns
// ============================================================================

interface MenuEffectProps extends BaseEffectProps {
  children: React.ReactNode;
  open?: boolean;
}

export const MenuEffect: React.FC<MenuEffectProps> = ({
  children,
  variant = 'subtle',
  animation,
  shadow = 'lg',
  className = '',
  open = true,
}) => {
  const menuAnimation: Partial<AnimationConfig> = animation || {
    type: open ? 'scale' : 'fade',
    duration: 200,
    timing: 'ease-out',
  };

  return (
    <EffectWrapper
      variant={variant}
      animation={open ? menuAnimation : undefined}
      shadow={shadow}
      className={`menu-effect ${open ? 'open' : 'closed'} ${className}`}
    >
      {children}
    </EffectWrapper>
  );
};

// ============================================================================
// Menu Item Effect - Specialized for menu items
// ============================================================================

interface MenuItemEffectProps extends BaseEffectProps {
  children: React.ReactNode;
  onClick?: () => void;
  active?: boolean;
  icon?: React.ReactNode;
}

export const MenuItemEffect: React.FC<MenuItemEffectProps> = ({
  children,
  variant = 'subtle',
  hoverEffect,
  className = '',
  disabled = false,
  onClick,
  active = false,
  icon,
}) => {
  const defaultHover: HoverEffectConfig = hoverEffect || {
    backgroundColor: 'var(--hover-bg, rgba(0, 0, 0, 0.05))',
    translateY: 0,
  };

  return (
    <EffectWrapper
      variant={variant}
      hoverEffect={defaultHover}
      className={`menu-item-effect ${active ? 'active' : ''} ${className}`}
      disabled={disabled}
      onClick={onClick}
    >
      {icon && <span className="menu-item-icon">{icon}</span>}
      <span className="menu-item-content">{children}</span>
    </EffectWrapper>
  );
};

// ============================================================================
// Dropdown Effect - Specialized for dropdowns
// ============================================================================

interface DropdownEffectProps extends BaseEffectProps {
  children: React.ReactNode;
  open?: boolean;
  position?: 'bottom' | 'top' | 'left' | 'right';
}

export const DropdownEffect: React.FC<DropdownEffectProps> = ({
  children,
  variant = 'subtle',
  animation,
  shadow = 'lg',
  className = '',
  open = false,
  position = 'bottom',
}) => {
  const getAnimation = (): Partial<AnimationConfig> => {
    if (animation) return animation;
    
    switch (position) {
      case 'top':
        return { type: 'slide', duration: 200 };
      case 'left':
      case 'right':
        return { type: 'scale', duration: 200 };
      default:
        return { type: 'slide', duration: 200 };
    }
  };

  if (!open) return null;

  return (
    <EffectWrapper
      variant={variant}
      animation={getAnimation()}
      shadow={shadow}
      className={`dropdown-effect position-${position} ${className}`}
    >
      {children}
    </EffectWrapper>
  );
};

// ============================================================================
// Modal Effect - Specialized for modals/dialogs
// ============================================================================

interface ModalEffectProps extends BaseEffectProps {
  children: React.ReactNode;
  open?: boolean;
  onClose?: () => void;
}

export const ModalEffect: React.FC<ModalEffectProps> = ({
  children,
  variant = 'standard',
  animation,
  shadow = '2xl',
  className = '',
  open = false,
  onClose,
}) => {
  const modalAnimation: Partial<AnimationConfig> = animation || {
    type: 'zoom',
    duration: 300,
    timing: 'spring',
  };

  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <EffectWrapper
        variant={variant}
        animation={modalAnimation}
        shadow={shadow}
        className={`modal-effect ${className}`}
        onClick={(e: any) => e.stopPropagation()}
      >
        {children}
      </EffectWrapper>
    </div>
  );
};

// ============================================================================
// Toast Effect - Specialized for toast notifications
// ============================================================================

interface ToastEffectProps extends BaseEffectProps {
  children: React.ReactNode;
  type?: 'info' | 'success' | 'warning' | 'error';
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
}

export const ToastEffect: React.FC<ToastEffectProps> = ({
  children,
  variant = 'standard',
  animation,
  shadow = 'lg',
  className = '',
  type = 'info',
  position = 'top-right',
}) => {
  const toastAnimation: Partial<AnimationConfig> = animation || {
    type: 'slide',
    duration: 300,
    timing: 'spring',
  };

  return (
    <EffectWrapper
      variant={variant}
      animation={toastAnimation}
      shadow={shadow}
      className={`toast-effect toast-${type} toast-${position} ${className}`}
    >
      {children}
    </EffectWrapper>
  );
};

// ============================================================================
// Badge Effect - Specialized for badges
// ============================================================================

interface BadgeEffectProps extends BaseEffectProps {
  children: React.ReactNode;
  pulse?: boolean;
  type?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
}

export const BadgeEffect: React.FC<BadgeEffectProps> = ({
  children,
  variant = 'subtle',
  animation,
  className = '',
  pulse = false,
  type = 'default',
}) => {
  const badgeAnimation: Partial<AnimationConfig> = animation || (pulse ? {
    type: 'pulse',
    duration: 2000,
    iterations: 'infinite',
  } : {});

  return (
    <EffectWrapper
      variant={variant}
      animation={badgeAnimation}
      className={`badge-effect badge-${type} ${pulse ? 'pulsing' : ''} ${className}`}
    >
      {children}
    </EffectWrapper>
  );
};

// ============================================================================
// Skeleton Effect - Loading placeholder
// ============================================================================

interface SkeletonEffectProps {
  width?: string | number;
  height?: string | number;
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
  className?: string;
}

export const SkeletonEffect: React.FC<SkeletonEffectProps> = ({
  width = '100%',
  height = '1rem',
  variant = 'text',
  className = '',
}) => {
  const style: React.CSSProperties = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  };

  return (
    <div 
      className={`skeleton-effect skeleton-${variant} ${className}`}
      style={style}
    />
  );
};

export default EffectWrapper;
