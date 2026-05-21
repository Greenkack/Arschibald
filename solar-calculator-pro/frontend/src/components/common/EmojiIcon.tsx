/**
 * Task 202: Emoji Integration Across Components
 * ==============================================
 * Reusable emoji icon component with accessibility support.
 */

import React from 'react';
import { emojiService, useEmoji } from '../../services/emojiService';
import './EmojiIcon.css';

export interface EmojiIconProps {
  /** Emoji key from the emoji mappings */
  emojiKey: string;
  /** Optional size (small, medium, large) */
  size?: 'small' | 'medium' | 'large';
  /** Show fallback text instead of emoji */
  showFallback?: boolean;
  /** Additional CSS class */
  className?: string;
  /** Animate on hover */
  animate?: boolean;
  /** Click handler */
  onClick?: () => void;
  /** Custom aria-label override */
  ariaLabel?: string;
}

export const EmojiIcon: React.FC<EmojiIconProps> = ({
  emojiKey,
  size = 'medium',
  showFallback = false,
  className = '',
  animate = false,
  onClick,
  ariaLabel,
}) => {
  const { emoji, fallback, ariaLabel: defaultAriaLabel } = useEmoji(emojiKey);
  
  const sizeClass = `emoji-icon--${size}`;
  const animateClass = animate ? 'emoji-icon--animate' : '';
  const clickableClass = onClick ? 'emoji-icon--clickable' : '';
  
  const content = showFallback || !emoji ? fallback : emoji;
  const label = ariaLabel || defaultAriaLabel;
  
  return (
    <span
      className={`emoji-icon ${sizeClass} ${animateClass} ${clickableClass} ${className}`}
      role="img"
      aria-label={label}
      title={label}
      onClick={onClick}
    >
      {content}
    </span>
  );
};

// Button with emoji
export interface EmojiButtonProps {
  emojiKey: string;
  label: string;
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'text';
  size?: 'small' | 'medium' | 'large';
  className?: string;
  emojiPosition?: 'left' | 'right';
}

export const EmojiButton: React.FC<EmojiButtonProps> = ({
  emojiKey,
  label,
  onClick,
  disabled = false,
  variant = 'primary',
  size = 'medium',
  className = '',
  emojiPosition = 'left',
}) => {
  const { emoji } = useEmoji(emojiKey);
  
  return (
    <button
      className={`emoji-button emoji-button--${variant} emoji-button--${size} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {emojiPosition === 'left' && emoji && <span className="emoji-button__icon">{emoji}</span>}
      <span className="emoji-button__label">{label}</span>
      {emojiPosition === 'right' && emoji && <span className="emoji-button__icon">{emoji}</span>}
    </button>
  );
};

// Menu item with emoji
export interface EmojiMenuItemProps {
  emojiKey: string;
  label: string;
  onClick?: () => void;
  active?: boolean;
  disabled?: boolean;
  className?: string;
}

export const EmojiMenuItem: React.FC<EmojiMenuItemProps> = ({
  emojiKey,
  label,
  onClick,
  active = false,
  disabled = false,
  className = '',
}) => {
  const { emoji, ariaLabel } = useEmoji(emojiKey);
  
  return (
    <div
      className={`emoji-menu-item ${active ? 'emoji-menu-item--active' : ''} ${disabled ? 'emoji-menu-item--disabled' : ''} ${className}`}
      onClick={disabled ? undefined : onClick}
      role="menuitem"
      aria-label={ariaLabel}
      aria-disabled={disabled}
    >
      {emoji && <span className="emoji-menu-item__icon">{emoji}</span>}
      <span className="emoji-menu-item__label">{label}</span>
    </div>
  );
};

// Badge with emoji
export interface EmojiBadgeProps {
  emojiKey: string;
  count?: number;
  showZero?: boolean;
  className?: string;
}

export const EmojiBadge: React.FC<EmojiBadgeProps> = ({
  emojiKey,
  count,
  showZero = false,
  className = '',
}) => {
  const { emoji } = useEmoji(emojiKey);
  
  if (count === 0 && !showZero) {
    return null;
  }
  
  return (
    <span className={`emoji-badge ${className}`}>
      {emoji && <span className="emoji-badge__icon">{emoji}</span>}
      {count !== undefined && <span className="emoji-badge__count">{count}</span>}
    </span>
  );
};

// Status indicator with emoji
export interface EmojiStatusProps {
  status: 'success' | 'error' | 'warning' | 'info' | 'pending' | 'active' | 'inactive';
  label?: string;
  showLabel?: boolean;
  className?: string;
}

export const EmojiStatus: React.FC<EmojiStatusProps> = ({
  status,
  label,
  showLabel = true,
  className = '',
}) => {
  const emojiKey = `status.${status}`;
  const { emoji, fallback } = useEmoji(emojiKey);
  
  return (
    <span className={`emoji-status emoji-status--${status} ${className}`}>
      <span className="emoji-status__icon">{emoji}</span>
      {showLabel && <span className="emoji-status__label">{label || fallback}</span>}
    </span>
  );
};

// Tab with emoji
export interface EmojiTabProps {
  emojiKey: string;
  label: string;
  active?: boolean;
  onClick?: () => void;
  className?: string;
}

export const EmojiTab: React.FC<EmojiTabProps> = ({
  emojiKey,
  label,
  active = false,
  onClick,
  className = '',
}) => {
  const { emoji } = useEmoji(emojiKey);
  
  return (
    <div
      className={`emoji-tab ${active ? 'emoji-tab--active' : ''} ${className}`}
      onClick={onClick}
      role="tab"
      aria-selected={active}
    >
      {emoji && <span className="emoji-tab__icon">{emoji}</span>}
      <span className="emoji-tab__label">{label}</span>
    </div>
  );
};

export default EmojiIcon;
