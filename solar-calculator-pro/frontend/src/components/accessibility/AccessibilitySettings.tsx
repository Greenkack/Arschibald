/**
 * Accessibility Settings Component
 * Provides user interface for configuring accessibility preferences
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { InputSwitch } from 'primereact/inputswitch';
import { Slider } from 'primereact/slider';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import './AccessibilitySettings.css';

export interface AccessibilityPreferences {
  // Visual
  highContrast: boolean;
  reducedMotion: boolean;
  fontSize: number; // 100 = default, 150 = 1.5x
  focusIndicator: 'default' | 'enhanced' | 'high-contrast';
  
  // Screen Reader
  screenReaderOptimized: boolean;
  announcePageChanges: boolean;
  announceFormErrors: boolean;
  verboseDescriptions: boolean;
  
  // Keyboard
  keyboardShortcuts: boolean;
  focusTrap: boolean;
  skipLinks: boolean;
  
  // Content
  autoplayMedia: boolean;
  flashingContent: boolean;
  
  // Language
  language: string;
}

const defaultPreferences: AccessibilityPreferences = {
  highContrast: false,
  reducedMotion: false,
  fontSize: 100,
  focusIndicator: 'default',
  screenReaderOptimized: false,
  announcePageChanges: true,
  announceFormErrors: true,
  verboseDescriptions: false,
  keyboardShortcuts: true,
  focusTrap: true,
  skipLinks: true,
  autoplayMedia: false,
  flashingContent: false,
  language: 'de',
};

export const AccessibilitySettings: React.FC = () => {
  const [preferences, setPreferences] = useState<AccessibilityPreferences>(defaultPreferences);
  const [hasChanges, setHasChanges] = useState(false);

  // Load preferences from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('accessibility-preferences');
    if (saved) {
      try {
        setPreferences(JSON.parse(saved));
      } catch (error) {
        console.error('Failed to load accessibility preferences:', error);
      }
    }
  }, []);

  // Apply preferences to document
  useEffect(() => {
    applyPreferences(preferences);
  }, [preferences]);

  const applyPreferences = (prefs: AccessibilityPreferences) => {
    const root = document.documentElement;

    // High contrast
    if (prefs.highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }

    // Reduced motion
    if (prefs.reducedMotion) {
      root.classList.add('reduced-motion');
    } else {
      root.classList.remove('reduced-motion');
    }

    // Font size
    root.style.fontSize = `${prefs.fontSize}%`;

    // Focus indicator
    root.setAttribute('data-focus-indicator', prefs.focusIndicator);

    // Screen reader optimized
    if (prefs.screenReaderOptimized) {
      root.classList.add('screen-reader-optimized');
    } else {
      root.classList.remove('screen-reader-optimized');
    }

    // Keyboard shortcuts
    root.setAttribute('data-keyboard-shortcuts', prefs.keyboardShortcuts.toString());

    // Skip links
    if (prefs.skipLinks) {
      root.classList.add('show-skip-links');
    } else {
      root.classList.remove('show-skip-links');
    }
  };

  const updatePreference = <K extends keyof AccessibilityPreferences>(
    key: K,
    value: AccessibilityPreferences[K]
  ) => {
    setPreferences((prev) => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const savePreferences = () => {
    localStorage.setItem('accessibility-preferences', JSON.stringify(preferences));
    setHasChanges(false);
    
    // Announce save success
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', 'polite');
    announcement.textContent = 'Accessibility preferences saved successfully';
    announcement.style.position = 'absolute';
    announcement.style.left = '-10000px';
    document.body.appendChild(announcement);
    setTimeout(() => document.body.removeChild(announcement), 1000);
  };

  const resetPreferences = () => {
    setPreferences(defaultPreferences);
    setHasChanges(true);
  };

  const focusIndicatorOptions = [
    { label: 'Default', value: 'default' },
    { label: 'Enhanced', value: 'enhanced' },
    { label: 'High Contrast', value: 'high-contrast' },
  ];

  return (
    <div className="accessibility-settings">
      <h1>Accessibility Settings</h1>
      <p className="settings-description">
        Configure accessibility features to improve your experience with the application.
      </p>

      {/* Visual Settings */}
      <Card title="Visual Settings" className="settings-card">
        <div className="setting-item">
          <label htmlFor="high-contrast">
            <strong>High Contrast Mode</strong>
            <span className="setting-description">
              Increases contrast between text and background for better readability
            </span>
          </label>
          <InputSwitch
            inputId="high-contrast"
            checked={preferences.highContrast}
            onChange={(e) => updatePreference('highContrast', e.value)}
          />
        </div>

        <div className="setting-item">
          <label htmlFor="reduced-motion">
            <strong>Reduced Motion</strong>
            <span className="setting-description">
              Minimizes animations and transitions
            </span>
          </label>
          <InputSwitch
            inputId="reduced-motion"
            checked={preferences.reducedMotion}
            onChange={(e) => updatePreference('reducedMotion', e.value)}
          />
        </div>

        <div className="setting-item">
          <label htmlFor="font-size">
            <strong>Font Size: {preferences.fontSize}%</strong>
            <span className="setting-description">
              Adjust text size throughout the application
            </span>
          </label>
          <Slider
            id="font-size"
            value={preferences.fontSize}
            onChange={(e) => updatePreference('fontSize', e.value as number)}
            min={75}
            max={200}
            step={25}
            aria-label="Font size percentage"
          />
        </div>

        <div className="setting-item">
          <label htmlFor="focus-indicator">
            <strong>Focus Indicator Style</strong>
            <span className="setting-description">
              Choose how focused elements are highlighted
            </span>
          </label>
          <Dropdown
            inputId="focus-indicator"
            value={preferences.focusIndicator}
            options={focusIndicatorOptions}
            onChange={(e) => updatePreference('focusIndicator', e.value)}
            aria-label="Focus indicator style"
          />
        </div>
      </Card>

      {/* Screen Reader Settings */}
      <Card title="Screen Reader Settings" className="settings-card">
        <div className="setting-item">
          <label htmlFor="screen-reader-optimized">
            <strong>Screen Reader Optimized</strong>
            <span className="setting-description">
              Optimizes interface for screen reader users
            </span>
          </label>
          <InputSwitch
            inputId="screen-reader-optimized"
            checked={preferences.screenReaderOptimized}
            onChange={(e) => updatePreference('screenReaderOptimized', e.value)}
          />
        </div>

        <div className="setting-item">
          <label htmlFor="announce-page-changes">
            <strong>Announce Page Changes</strong>
            <span className="setting-description">
              Announces when navigating to a new page
            </span>
          </label>
          <InputSwitch
            inputId="announce-page-changes"
            checked={preferences.announcePageChanges}
            onChange={(e) => updatePreference('announcePageChanges', e.value)}
          />
        </div>

        <div className="setting-item">
          <label htmlFor="announce-form-errors">
            <strong>Announce Form Errors</strong>
            <span className="setting-description">
              Announces form validation errors immediately
            </span>
          </label>
          <InputSwitch
            inputId="announce-form-errors"
            checked={preferences.announceFormErrors}
            onChange={(e) => updatePreference('announceFormErrors', e.value)}
          />
        </div>

        <div className="setting-item">
          <label htmlFor="verbose-descriptions">
            <strong>Verbose Descriptions</strong>
            <span className="setting-description">
              Provides more detailed descriptions of UI elements
            </span>
          </label>
          <InputSwitch
            inputId="verbose-descriptions"
            checked={preferences.verboseDescriptions}
            onChange={(e) => updatePreference('verboseDescriptions', e.value)}
          />
        </div>
      </Card>

      {/* Keyboard Settings */}
      <Card title="Keyboard Navigation" className="settings-card">
        <div className="setting-item">
          <label htmlFor="keyboard-shortcuts">
            <strong>Keyboard Shortcuts</strong>
            <span className="setting-description">
              Enable keyboard shortcuts for common actions
            </span>
          </label>
          <InputSwitch
            inputId="keyboard-shortcuts"
            checked={preferences.keyboardShortcuts}
            onChange={(e) => updatePreference('keyboardShortcuts', e.value)}
          />
        </div>

        <div className="setting-item">
          <label htmlFor="focus-trap">
            <strong>Focus Trap in Dialogs</strong>
            <span className="setting-description">
              Keeps focus within modal dialogs
            </span>
          </label>
          <InputSwitch
            inputId="focus-trap"
            checked={preferences.focusTrap}
            onChange={(e) => updatePreference('focusTrap', e.value)}
          />
        </div>

        <div className="setting-item">
          <label htmlFor="skip-links">
            <strong>Skip Navigation Links</strong>
            <span className="setting-description">
              Shows links to skip to main content
            </span>
          </label>
          <InputSwitch
            inputId="skip-links"
            checked={preferences.skipLinks}
            onChange={(e) => updatePreference('skipLinks', e.value)}
          />
        </div>
      </Card>

      {/* Content Settings */}
      <Card title="Content Preferences" className="settings-card">
        <div className="setting-item">
          <label htmlFor="autoplay-media">
            <strong>Autoplay Media</strong>
            <span className="setting-description">
              Automatically play videos and animations
            </span>
          </label>
          <InputSwitch
            inputId="autoplay-media"
            checked={preferences.autoplayMedia}
            onChange={(e) => updatePreference('autoplayMedia', e.value)}
          />
        </div>

        <div className="setting-item">
          <label htmlFor="flashing-content">
            <strong>Allow Flashing Content</strong>
            <span className="setting-description">
              Show content with flashing or rapid changes
            </span>
          </label>
          <InputSwitch
            inputId="flashing-content"
            checked={preferences.flashingContent}
            onChange={(e) => updatePreference('flashingContent', e.value)}
          />
        </div>
      </Card>

      {/* Action Buttons */}
      <div className="settings-actions">
        <Button
          label="Save Preferences"
          icon="pi pi-check"
          onClick={savePreferences}
          disabled={!hasChanges}
          aria-label="Save accessibility preferences"
        />
        <Button
          label="Reset to Defaults"
          icon="pi pi-refresh"
          onClick={resetPreferences}
          className="p-button-secondary"
          aria-label="Reset accessibility preferences to defaults"
        />
      </div>
    </div>
  );
};
