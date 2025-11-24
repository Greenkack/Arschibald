/**
 * Custom hook for focus management
 * Handles focus trapping, restoration, and visible focus indicators
 */

import { useEffect, useRef, useCallback, useState } from 'react';

export interface UseFocusManagementOptions {
  trapFocus?: boolean;
  restoreFocus?: boolean;
  initialFocus?: HTMLElement | null;
  autoFocus?: boolean;
}

export const useFocusManagement = (options: UseFocusManagementOptions = {}) => {
  const {
    trapFocus = false,
    restoreFocus = true,
    initialFocus = null,
    autoFocus = false,
  } = options;

  const containerRef = useRef<HTMLElement | null>(null);
  const previouslyFocusedElement = useRef<HTMLElement | null>(null);
  const [isFocusVisible, setIsFocusVisible] = useState(false);

  // Store previously focused element
  useEffect(() => {
    if (restoreFocus) {
      previouslyFocusedElement.current = document.activeElement as HTMLElement;
    }

    return () => {
      // Restore focus on unmount
      if (restoreFocus && previouslyFocusedElement.current) {
        previouslyFocusedElement.current.focus();
      }
    };
  }, [restoreFocus]);

  // Auto focus on mount
  useEffect(() => {
    if (autoFocus) {
      if (initialFocus) {
        initialFocus.focus();
      } else if (containerRef.current) {
        const firstFocusable = containerRef.current.querySelector<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        firstFocusable?.focus();
      }
    }
  }, [autoFocus, initialFocus]);

  // Track focus-visible state (keyboard vs mouse)
  useEffect(() => {
    const handleMouseDown = () => setIsFocusVisible(false);
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        setIsFocusVisible(true);
      }
    };

    document.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  // Focus trap implementation
  useEffect(() => {
    if (!trapFocus || !containerRef.current) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab' || !containerRef.current) return;

      const focusableElements = containerRef.current.querySelectorAll<HTMLElement>(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [trapFocus]);

  // Focus first element in container
  const focusFirst = useCallback(() => {
    if (!containerRef.current) return;

    const firstFocusable = containerRef.current.querySelector<HTMLElement>(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    firstFocusable?.focus();
  }, []);

  // Focus last element in container
  const focusLast = useCallback(() => {
    if (!containerRef.current) return;

    const focusableElements = containerRef.current.querySelectorAll<HTMLElement>(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    const lastElement = focusableElements[focusableElements.length - 1];
    lastElement?.focus();
  }, []);

  // Check if element is focusable
  const isFocusable = useCallback((element: HTMLElement): boolean => {
    if (element.hasAttribute('disabled')) return false;
    if (element.getAttribute('tabindex') === '-1') return false;

    const style = window.getComputedStyle(element);
    if (style.display === 'none' || style.visibility === 'hidden') return false;

    const tagName = element.tagName.toLowerCase();
    const focusableTags = ['a', 'button', 'input', 'select', 'textarea'];

    return (
      focusableTags.includes(tagName) ||
      element.hasAttribute('tabindex') ||
      element.hasAttribute('contenteditable')
    );
  }, []);

  // Get all focusable elements in container
  const getFocusableElements = useCallback((): HTMLElement[] => {
    if (!containerRef.current) return [];

    const elements = containerRef.current.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex], [contenteditable]'
    );

    return Array.from(elements).filter(isFocusable);
  }, [isFocusable]);

  // Move focus to next focusable element
  const focusNext = useCallback(() => {
    const focusableElements = getFocusableElements();
    const currentIndex = focusableElements.indexOf(
      document.activeElement as HTMLElement
    );

    if (currentIndex < focusableElements.length - 1) {
      focusableElements[currentIndex + 1]?.focus();
    } else {
      focusableElements[0]?.focus(); // Wrap to first
    }
  }, [getFocusableElements]);

  // Move focus to previous focusable element
  const focusPrevious = useCallback(() => {
    const focusableElements = getFocusableElements();
    const currentIndex = focusableElements.indexOf(
      document.activeElement as HTMLElement
    );

    if (currentIndex > 0) {
      focusableElements[currentIndex - 1]?.focus();
    } else {
      focusableElements[focusableElements.length - 1]?.focus(); // Wrap to last
    }
  }, [getFocusableElements]);

  // Create focus trap scope
  const createFocusTrap = useCallback(() => {
    const focusableElements = getFocusableElements();
    if (focusableElements.length === 0) return;

    // Focus first element
    focusableElements[0]?.focus();

    // Return cleanup function
    return () => {
      if (previouslyFocusedElement.current) {
        previouslyFocusedElement.current.focus();
      }
    };
  }, [getFocusableElements]);

  return {
    containerRef,
    isFocusVisible,
    focusFirst,
    focusLast,
    focusNext,
    focusPrevious,
    getFocusableElements,
    createFocusTrap,
    isFocusable,
  };
};

// Focus visible CSS utility
export const focusVisibleStyles = {
  outline: '2px solid var(--primary-color)',
  outlineOffset: '2px',
  borderRadius: '4px',
};

// Skip to content link component helper
export const createSkipLink = (targetId: string, label: string = 'Skip to main content') => {
  return {
    href: `#${targetId}`,
    className: 'skip-link',
    children: label,
    style: {
      position: 'absolute' as const,
      left: '-9999px',
      zIndex: 999,
      padding: '1rem',
      backgroundColor: 'var(--primary-color)',
      color: 'white',
      textDecoration: 'none',
      ':focus': {
        left: '0',
        top: '0',
      },
    },
  };
};
