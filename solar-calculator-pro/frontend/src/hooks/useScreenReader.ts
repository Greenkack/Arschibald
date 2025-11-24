/**
 * Custom hook for screen reader support
 * Provides live region announcements and ARIA utilities
 */

import { useEffect, useRef, useCallback } from 'react';

export type AnnouncementPriority = 'polite' | 'assertive' | 'off';

export interface UseScreenReaderOptions {
  announcePageChanges?: boolean;
  announceFormErrors?: boolean;
}

export const useScreenReader = (options: UseScreenReaderOptions = {}) => {
  const { announcePageChanges = true, announceFormErrors = true } = options;

  const liveRegionRef = useRef<HTMLDivElement | null>(null);
  const announcementQueue = useRef<Array<{ message: string; priority: AnnouncementPriority }>>([]);
  const isAnnouncing = useRef(false);

  // Create live region element if it doesn't exist
  useEffect(() => {
    if (!liveRegionRef.current) {
      const liveRegion = document.createElement('div');
      liveRegion.setAttribute('role', 'status');
      liveRegion.setAttribute('aria-live', 'polite');
      liveRegion.setAttribute('aria-atomic', 'true');
      liveRegion.className = 'sr-only';
      liveRegion.style.position = 'absolute';
      liveRegion.style.left = '-10000px';
      liveRegion.style.width = '1px';
      liveRegion.style.height = '1px';
      liveRegion.style.overflow = 'hidden';
      document.body.appendChild(liveRegion);
      liveRegionRef.current = liveRegion;
    }

    return () => {
      if (liveRegionRef.current) {
        document.body.removeChild(liveRegionRef.current);
        liveRegionRef.current = null;
      }
    };
  }, []);

  // Process announcement queue
  const processQueue = useCallback(() => {
    if (isAnnouncing.current || announcementQueue.current.length === 0) {
      return;
    }

    isAnnouncing.current = true;
    const { message, priority } = announcementQueue.current.shift()!;

    if (liveRegionRef.current) {
      liveRegionRef.current.setAttribute('aria-live', priority);
      liveRegionRef.current.textContent = message;

      // Clear after announcement
      setTimeout(() => {
        if (liveRegionRef.current) {
          liveRegionRef.current.textContent = '';
        }
        isAnnouncing.current = false;
        processQueue();
      }, 100);
    }
  }, []);

  // Announce message to screen reader
  const announce = useCallback(
    (message: string, priority: AnnouncementPriority = 'polite') => {
      if (!message.trim()) return;

      announcementQueue.current.push({ message, priority });
      processQueue();
    },
    [processQueue]
  );

  // Announce error
  const announceError = useCallback(
    (error: string) => {
      if (announceFormErrors) {
        announce(`Error: ${error}`, 'assertive');
      }
    },
    [announce, announceFormErrors]
  );

  // Announce success
  const announceSuccess = useCallback(
    (message: string) => {
      announce(`Success: ${message}`, 'polite');
    },
    [announce]
  );

  // Announce loading state
  const announceLoading = useCallback(
    (message: string = 'Loading') => {
      announce(message, 'polite');
    },
    [announce]
  );

  // Announce page change
  const announcePageChange = useCallback(
    (pageName: string) => {
      if (announcePageChanges) {
        announce(`Navigated to ${pageName}`, 'polite');
      }
    },
    [announce, announcePageChanges]
  );

  // Generate unique ID for ARIA relationships
  const generateId = useCallback((prefix: string = 'aria') => {
    return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  // Get ARIA props for form field
  const getFieldAriaProps = useCallback(
    (
      label: string,
      error?: string,
      description?: string,
      required?: boolean
    ) => {
      const labelId = generateId('label');
      const errorId = error ? generateId('error') : undefined;
      const descId = description ? generateId('desc') : undefined;

      const describedBy = [descId, errorId].filter(Boolean).join(' ');

      return {
        'aria-label': label,
        'aria-required': required,
        'aria-invalid': !!error,
        'aria-describedby': describedBy || undefined,
        'aria-errormessage': errorId,
        labelId,
        errorId,
        descId,
      };
    },
    [generateId]
  );

  // Get ARIA props for button
  const getButtonAriaProps = useCallback(
    (
      label: string,
      options: {
        pressed?: boolean;
        expanded?: boolean;
        controls?: string;
        disabled?: boolean;
      } = {}
    ) => {
      return {
        'aria-label': label,
        'aria-pressed': options.pressed,
        'aria-expanded': options.expanded,
        'aria-controls': options.controls,
        'aria-disabled': options.disabled,
      };
    },
    []
  );

  // Get ARIA props for dialog
  const getDialogAriaProps = useCallback(
    (title: string, description?: string) => {
      const titleId = generateId('dialog-title');
      const descId = description ? generateId('dialog-desc') : undefined;

      return {
        role: 'dialog',
        'aria-modal': true,
        'aria-labelledby': titleId,
        'aria-describedby': descId,
        titleId,
        descId,
      };
    },
    [generateId]
  );

  // Get ARIA props for list
  const getListAriaProps = useCallback(
    (label: string, itemCount: number) => {
      return {
        role: 'list',
        'aria-label': label,
        'aria-setsize': itemCount,
      };
    },
    []
  );

  // Get ARIA props for list item
  const getListItemAriaProps = useCallback((index: number, total: number) => {
    return {
      role: 'listitem',
      'aria-posinset': index + 1,
      'aria-setsize': total,
    };
  }, []);

  return {
    announce,
    announceError,
    announceSuccess,
    announceLoading,
    announcePageChange,
    generateId,
    getFieldAriaProps,
    getButtonAriaProps,
    getDialogAriaProps,
    getListAriaProps,
    getListItemAriaProps,
  };
};

// Screen reader only CSS class utility
export const srOnlyClass = {
  position: 'absolute' as const,
  left: '-10000px',
  width: '1px',
  height: '1px',
  overflow: 'hidden' as const,
  clip: 'rect(0, 0, 0, 0)',
  whiteSpace: 'nowrap' as const,
  border: 0,
};
