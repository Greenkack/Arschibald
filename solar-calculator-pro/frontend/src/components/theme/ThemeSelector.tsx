/**
 * Theme Selector Component
 * Allows users to select from predefined theme presets
 */

import React from 'react';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import { useThemeStore } from '../../store/themeStore';
import { getThemePresetNames } from '../../theme/themePresets';
import './ThemeSelector.css';

export const ThemeSelector: React.FC = () => {
  const { theme, setPreset, openCustomThemeCreator } = useThemeStore();
  
  const presetOptions = getThemePresetNames().map(name => ({
    label: name.charAt(0).toUpperCase() + name.slice(1),
    value: name,
  }));

  return (
    <div className="theme-selector">
      <div className="theme-selector-header">
        <h3>Theme Preset</h3>
        <Button
          label="Create Custom"
          icon="pi pi-palette"
          className="p-button-text"
          onClick={openCustomThemeCreator}
        />
      </div>

      <Dropdown
        value={theme.preset}
        options={presetOptions}
        onChange={(e) => setPreset(e.value)}
        placeholder="Select a theme"
        className="w-full"
      />

      <div className="theme-preview">
        <div className="theme-preview-colors">
          <div
            className="color-swatch"
            style={{ backgroundColor: theme.colors.primary }}
            title="Primary"
          />
          <div
            className="color-swatch"
            style={{ backgroundColor: theme.colors.secondary }}
            title="Secondary"
          />
          <div
            className="color-swatch"
            style={{ backgroundColor: theme.colors.accent }}
            title="Accent"
          />
          <div
            className="color-swatch"
            style={{ backgroundColor: theme.colors.success }}
            title="Success"
          />
          <div
            className="color-swatch"
            style={{ backgroundColor: theme.colors.warning }}
            title="Warning"
          />
          <div
            className="color-swatch"
            style={{ backgroundColor: theme.colors.error }}
            title="Error"
          />
        </div>
      </div>
    </div>
  );
};
