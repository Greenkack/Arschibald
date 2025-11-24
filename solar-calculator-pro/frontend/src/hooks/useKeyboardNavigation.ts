/**
 * Custom hook for keyboard navigation support
 * Provides comprehensive keyboard shortcuts and navigation
 */

import { useEffect, useCallback, useRef } from 'react';

export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  alt?: boolean;
  shift?: boolean;
  meta?: boolean;
  handler: (event: KeyboardEvent) => void;
  description: string;
  category?: string;
}

export interface UseKeyboardNavigationOptions {
  shortcuts?: KeyboardShortcut[];
  enableFocusTrap?: boolean;
  enableArrowNavigation?: boolean;
  onEscape?: () => void;
}

export const useKeyboardNavigation = (options: UseKeyboardNavigationOptions = {}) => {
  const {
    shortcuts = [],
    enableFocusTrap = false,
    enableArrowNavigation = false,
    onEscape,
  } = options;

  const containerRef = useRef<HTMLElement | null>(null);
  const focusableElements = useRef<HTMLElement[]>([]);
  const currentFocusIndex = useRef<number>(0);

  // Get all focusable elements within container
  const getFocusableElements = useCallback(() => {
    if (!containerRef.current) return [];

    const selector = [
      'a[href]',
      'button:not([disabled])',
      'textarea:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
    ].join(', ');

    return Array.from(
      containerRef.current.querySelectorAll<HTMLElement>(selector)
    ).filter((el) => {
      // Filter out hidden elements
      const style = window.getComputedStyle(el);
      return style.display !== 'none' && style.visibility !== 'hidden';
    });
  }, []);

  // Update focusable elements list
  const updateFocusableElements = useCallback(() => {
    focusableElements.current = getFocusableElements();
  }, [getFocusableElements]);

  // Handle keyboard shortcuts
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      // Check for registered shortcuts
      for (const shortcut of shortcuts) {
        const ctrlMatch = shortcut.ctrl ? event.ctrlKey : !event.ctrlKey;
        const altMatch = shortcut.alt ? event.altKey : !event.altKey;
        const shiftMatch = shortcut.shift ? event.shiftKey : !event.shiftKey;
        const metaMatch = shortcut.meta ? event.metaKey : !event.metaKey;

        if (
          event.key === shortcut.key &&
          ctrlMatch &&
          altMatch &&
          shiftMatch &&
          metaMatch
        ) {
          event.preventDefault();
          shortcut.handler(event);
          return;
        }
      }

      // Handle Escape key
      if (event.key === 'Escape' && onEscape) {
        event.preventDefault();
        onEscape();
        return;
      }

      // Handle arrow navigation
      if (enableArrowNavigation && focusableElements.current.length > 0) {
        if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
          event.preventDefault();
          currentFocusIndex.current =
            (currentFocusIndex.current + 1) % focusableElements.current.length;
          focusableElements.current[currentFocusIndex.current]?.focus();
        } else if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
          event.preventDefault();
          currentFocusIndex.current =
            currentFocusIndex.current === 0
              ? focusableElements.current.length - 1
              : currentFocusIndex.current - 1;
          focusableElements.current[currentFocusIndex.current]?.focus();
        }
      }

      // Handle Tab key for focus trap
      if (enableFocusTrap && event.key === 'Tab') {
        if (focusableElements.current.length === 0) return;

        const firstElement = focusableElements.current[0];
        const lastElement =
          focusableElements.current[focusableElements.current.length - 1];

        if (event.shiftKey) {
          // Shift + Tab
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement?.focus();
          }
        } else {
          // Tab
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement?.focus();
          }
        }
      }
    },
    [shortcuts, enableFocusTrap, enableArrowNavigation, onEscape]
  );

  // Setup keyboard event listeners
  useEffect(() => {
    updateFocusableElements();
    document.addEventListener('keydown', handleKeyDown);

    // Update focusable elements on DOM changes
    const observer = new MutationObserver(updateFocusableElements);
    if (containerRef.current) {
      observer.observe(containerRef.current, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['disabled', 'tabindex', 'hidden'],
      });
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      observer.disconnect();
    };
  }, [handleKeyDown, updateFocusableElements]);

  // Focus first element
  const focusFirst = useCallback(() => {
    if (focusableElements.current.length > 0) {
      currentFocusIndex.current = 0;
      focusableElements.current[0]?.focus();
    }
  }, []);

  // Focus last element
  const focusLast = useCallback(() => {
    if (focusableElements.current.length > 0) {
      currentFocusIndex.current = focusableElements.current.length - 1;
      focusableElements.current[currentFocusIndex.current]?.focus();
    }
  }, []);

  // Focus specific element by index
  const focusElement = useCallback((index: number) => {
    if (index >= 0 && index < focusableElements.current.length) {
      currentFocusIndex.current = index;
      focusableElements.current[index]?.focus();
    }
  }, []);

  return {
    containerRef,
    focusFirst,
    focusLast,
    focusElement,
    focusableElements: focusableElements.current,
  };
};

// Global keyboard shortcuts registry
export const globalShortcuts: KeyboardShortcut[] = [
  {
    key: 's',
    ctrl: true,
    handler: () => {
      // Save action - will be overridden by specific contexts
    },
    description: 'Save current work',
    category: 'General',
  },
  {
    key: 'k',
    ctrl: true,
    handler: () => {
      // Open command palette
    },
    description: 'Open command palette',
    category: 'Navigation',
  },
  {
    key: '/',
    ctrl: true,
    handler: () => {
      // Open search
    },
    description: 'Open search',
    category: 'Navigation',
  },
  {
    key: '?',
    shift: true,
    handler: () => {
      // Show keyboard shortcuts help
    },
    description: 'Show keyboard shortcuts',
    category: 'Help',
  },
];
