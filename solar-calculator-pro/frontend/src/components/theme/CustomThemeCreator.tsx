/**
 * Custom Theme Creator Component
 * Advanced theme customization interface
 */

import React, { useState } from 'react';
import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import { ColorPicker } from 'primereact/colorpicker';
import { Dropdown } from 'primereact/dropdown';
import { InputText } from 'primereact/inputtext';
import { TabView, TabPanel } from 'primereact/tabview';
import { useThemeStore } from '../../store/themeStore';
import { ThemeSettings } from '../../theme/themeEngine';
import './CustomThemeCreator.css';

export const CustomThemeCreator: React.FC = () => {
  const {
    theme,
    isCustomThemeCreatorOpen,
    closeCustomThemeCreator,
    updateColors,
    updateTypography,
    setMode,
  } = useThemeStore();

  const [localTheme, setLocalTheme] = useState<ThemeSettings>(theme);

  const fontSizeOptions = [
    { label: 'Small', value: 'small' },
    { label: 'Medium', value: 'medium' },
    { label: 'Large', value: 'large' },
    { label: 'Extra Large', value: 'xlarge' },
  ];

  const fontWeightOptions = [
    { label: 'Light', value: 'light' },
    { label: 'Normal', value: 'normal' },
    { label: 'Medium', value: 'medium' },
    { label: 'Bold', value: 'bold' },
  ];

  const modeOptions = [
    { label: 'Light', value: 'light' },
    { label: 'Dark', value: 'dark' },
    { label: 'Auto', value: 'auto' },
  ];

  const handleColorChange = (colorKey: keyof ThemeSettings['colors'], value: string) => {
    const newColors = {
      ...localTheme.colors,
      [colorKey]: `#${value}`,
    };
    setLocalTheme({ ...localTheme, colors: newColors });
  };

  const handleApply = () => {
    updateColors(localTheme.colors);
    updateTypography(localTheme.typography);
    setMode(localTheme.mode);
    closeCustomThemeCreator();
  };

  const handleCancel = () => {
    setLocalTheme(theme);
    closeCustomThemeCreator();
  };

  const colorFields: Array<{ key: keyof ThemeSettings['colors']; label: string }> = [
    { key: 'primary', label: 'Primary Color' },
    { key: 'secondary', label: 'Secondary Color' },
    { key: 'accent', label: 'Accent Color' },
    { key: 'background', label: 'Background Color' },
    { key: 'surface', label: 'Surface Color' },
    { key: 'text', label: 'Text Color' },
    { key: 'error', label: 'Error Color' },
    { key: 'warning', label: 'Warning Color' },
    { key: 'success', label: 'Success Color' },
    { key: 'info', label: 'Info Color' },
  ];

  return (
    <Dialog
      header="Custom Theme Creator"
      visible={isCustomThemeCreatorOpen}
      onHide={handleCancel}
      style={{ width: '800px' }}
      footer={
        <div>
          <Button label="Cancel" icon="pi pi-times" onClick={handleCancel} className="p-button-text" />
          <Button label="Apply" icon="pi pi-check" onClick={handleApply} />
        </div>
      }
    >
      <TabView>
        <TabPanel header="Colors">
          <div className="color-grid">
            {colorFields.map(({ key, label }) => (
              <div key={key} className="color-field">
                <label>{label}</label>
                <div className="color-input-group">
                  <ColorPicker
                    value={localTheme.colors[key].replace('#', '')}
                    onChange={(e) => handleColorChange(key, e.value as string)}
                  />
                  <InputText
                    value={localTheme.colors[key]}
                    onChange={(e) => handleColorChange(key, e.target.value.replace('#', ''))}
                    className="color-hex-input"
                  />
                </div>
              </div>
            ))}
          </div>
        </TabPanel>

        <TabPanel header="Typography">
          <div className="typography-settings">
            <div className="field">
              <label>Font Family</label>
              <InputText
                value={localTheme.typography.fontFamily}
                onChange={(e) =>
                  setLocalTheme({
                    ...localTheme,
                    typography: { ...localTheme.typography, fontFamily: e.target.value },
                  })
                }
                className="w-full"
              />
            </div>

            <div className="field">
              <label>Font Size</label>
              <Dropdown
                value={localTheme.typography.fontSize}
                options={fontSizeOptions}
                onChange={(e) =>
                  setLocalTheme({
                    ...localTheme,
                    typography: { ...localTheme.typography, fontSize: e.value },
                  })
                }
                className="w-full"
              />
            </div>

            <div className="field">
              <label>Font Weight</label>
              <Dropdown
                value={localTheme.typography.fontWeight}
                options={fontWeightOptions}
                onChange={(e) =>
                  setLocalTheme({
                    ...localTheme,
                    typography: { ...localTheme.typography, fontWeight: e.value },
                  })
                }
                className="w-full"
              />
            </div>
          </div>
        </TabPanel>

        <TabPanel header="Mode">
          <div className="mode-settings">
            <div className="field">
              <label>Theme Mode</label>
              <Dropdown
                value={localTheme.mode}
                options={modeOptions}
                onChange={(e) => setLocalTheme({ ...localTheme, mode: e.value })}
                className="w-full"
              />
            </div>

            <div className="mode-description">
              <p>
                <strong>Light:</strong> Always use light theme
              </p>
              <p>
                <strong>Dark:</strong> Always use dark theme
              </p>
              <p>
                <strong>Auto:</strong> Follow system preference
              </p>
            </div>
          </div>
        </TabPanel>

        <TabPanel header="Preview">
          <div className="theme-preview-panel">
            <div className="preview-section" style={{ backgroundColor: localTheme.colors.background }}>
              <h3 style={{ color: localTheme.colors.text }}>Preview</h3>
              <Button label="Primary Button" style={{ backgroundColor: localTheme.colors.primary }} />
              <Button
                label="Secondary Button"
                className="p-button-secondary"
                style={{ backgroundColor: localTheme.colors.secondary }}
              />
              <div className="preview-card" style={{ backgroundColor: localTheme.colors.surface }}>
                <p style={{ color: localTheme.colors.text }}>This is a preview of your custom theme.</p>
              </div>
            </div>
          </div>
        </TabPanel>
      </TabView>
    </Dialog>
  );
};
