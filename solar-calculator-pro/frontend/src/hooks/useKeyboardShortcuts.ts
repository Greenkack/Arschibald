/**
 * Keyboard Shortcuts Hook
 * 
 * Provides keyboard shortcut functionality with:
 * - Global shortcuts
 * - Context-specific shortcuts
 * - Customization support
 * - Conflict detection
 * - Help system
 */

import { useEffect, useCallback, useRef } from 'react';
import { useShortcutStore } from '../store/shortcutStore';

export interface ShortcutConfig {
  key: string;
  ctrl?: boolean;
  alt?: boolean;
  shift?: boolean;
  meta?: boolean;
  description: string;
  category: string;
  context?: string;
  handler: () => void;
  enabled?: boolean;
}

export interface ShortcutContext {
  name: string;
  active: boolean;
  shortcuts: ShortcutConfig[];
}

export const useKeyboardShortcuts = (
  shortcuts: ShortcutConfig[],
  context?: string,
  enabled: boolean = true
) => {
  const { registerShortcuts, unregisterShortcuts, isEnabled, hasConflict } = useShortcutStore();
  const shortcutsRef = useRef<ShortcutConfig[]>(shortcuts);

  // Update shortcuts ref when they change
  useEffect(() => {
    shortcutsRef.current = shortcuts;
  }, [shortcuts]);

  // Handle keyboard events
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!enabled || !isEnabled()) return;

    const activeShortcuts = shortcutsRef.current.filter(s => 
      s.enabled !== false && (!s.context || s.context === context)
    );

    for (const shortcut of activeShortcuts) {
      const matches = 
        event.key.toLowerCase() === shortcut.key.toLowerCase() &&
        !!event.ctrlKey === !!shortcut.ctrl &&
        !!event.altKey === !!shortcut.alt &&
        !!event.shiftKey === !!shortcut.shift &&
        !!event.metaKey === !!shortcut.meta;

      if (matches) {
        // Check for conflicts
        if (hasConflict(shortcut, context)) {
          console.warn(`Shortcut conflict detected: ${formatShortcut(shortcut)}`);
          continue;
        }

        event.preventDefault();
        event.stopPropagation();
        shortcut.handler();
        break;
      }
    }
  }, [enabled, context, isEnabled, hasConflict]);

  // Register shortcuts on mount
  useEffect(() => {
    if (enabled) {
      registerShortcuts(shortcuts, context);
      window.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      unregisterShortcuts(shortcuts, context);
    };
  }, [enabled, context, handleKeyDown, registerShortcuts, unregisterShortcuts, shortcuts]);

  return {
    enabled,
    context,
    shortcuts: shortcutsRef.current,
  };
};

/**
 * Format shortcut for display
 */
export const formatShortcut = (shortcut: ShortcutConfig): string => {
  const parts: string[] = [];
  
  if (shortcut.ctrl) parts.push('Ctrl');
  if (shortcut.alt) parts.push('Alt');
  if (shortcut.shift) parts.push('Shift');
  if (shortcut.meta) parts.push('Cmd');
  parts.push(shortcut.key.toUpperCase());
  
  return parts.join('+');
};

/**
 * Parse shortcut string (e.g., "Ctrl+S")
 */
export const parseShortcut = (shortcutString: string): Partial<ShortcutConfig> => {
  const parts = shortcutString.split('+').map(p => p.trim().toLowerCase());
  const key = parts[parts.length - 1];
  
  return {
    key,
    ctrl: parts.includes('ctrl'),
    alt: parts.includes('alt'),
    shift: parts.includes('shift'),
    meta: parts.includes('cmd') || parts.includes('meta'),
  };
};

/**
 * Check if two shortcuts conflict
 */
export const shortcutsConflict = (
  a: ShortcutConfig,
  b: ShortcutConfig,
  context?: string
): boolean => {
  // Different contexts don't conflict
  if (a.context && b.context && a.context !== b.context) {
    return false;
  }

  // Check if keys match
  return (
    a.key.toLowerCase() === b.key.toLowerCase() &&
    !!a.ctrl === !!b.ctrl &&
    !!a.alt === !!b.alt &&
    !!a.shift === !!b.shift &&
    !!a.meta === !!b.meta
  );
};
