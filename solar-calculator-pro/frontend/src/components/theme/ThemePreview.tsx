/**
 * Theme Preview Component
 * Shows a live preview of the current theme with sample UI elements
 */

import React from 'react';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Card } from 'primereact/card';
import { Message } from 'primereact/message';
import { useThemeStore } from '../../store/themeStore';
import './ThemePreview.css';

export const ThemePreview: React.FC = () => {
  const { theme } = useThemeStore();

  return (
    <div className="theme-preview-container">
      <h3>Live Preview</h3>
      <p className="preview-description">See how your theme looks with actual UI components</p>

      <div className="preview-grid">
        {/* Buttons Section */}
        <Card title="Buttons" className="preview-card">
          <div className="button-group">
            <Button label="Primary" />
            <Button label="Secondary" className="p-button-secondary" />
            <Button label="Success" className="p-button-success" />
            <Button label="Warning" className="p-button-warning" />
            <Button label="Danger" className="p-button-danger" />
            <Button label="Info" className="p-button-info" />
          </div>
        </Card>

        {/* Inputs Section */}
        <Card title="Inputs" className="preview-card">
          <div className="input-group">
            <InputText placeholder="Text Input" className="w-full" />
            <InputText placeholder="Disabled Input" disabled className="w-full" />
          </div>
        </Card>

        {/* Messages Section */}
        <Card title="Messages" className="preview-card">
          <div className="message-group">
            <Message severity="success" text="Success message" />
            <Message severity="info" text="Info message" />
            <Message severity="warn" text="Warning message" />
            <Message severity="error" text="Error message" />
          </div>
        </Card>

        {/* Typography Section */}
        <Card title="Typography" className="preview-card">
          <div className="typography-group">
            <h1>Heading 1</h1>
            <h2>Heading 2</h2>
            <h3>Heading 3</h3>
            <p>
              This is a paragraph with normal text. It demonstrates how the theme's typography settings
              affect regular content.
            </p>
            <p>
              <strong>Bold text</strong> and <em>italic text</em> are also styled according to the theme.
            </p>
          </div>
        </Card>

        {/* Colors Section */}
        <Card title="Color Palette" className="preview-card">
          <div className="color-palette">
            <div className="color-item">
              <div className="color-box" style={{ backgroundColor: theme.colors.primary }} />
              <span>Primary</span>
            </div>
            <div className="color-item">
              <div className="color-box" style={{ backgroundColor: theme.colors.secondary }} />
              <span>Secondary</span>
            </div>
            <div className="color-item">
              <div className="color-box" style={{ backgroundColor: theme.colors.accent }} />
              <span>Accent</span>
            </div>
            <div className="color-item">
              <div className="color-box" style={{ backgroundColor: theme.colors.success }} />
              <span>Success</span>
            </div>
            <div className="color-item">
              <div className="color-box" style={{ backgroundColor: theme.colors.warning }} />
              <span>Warning</span>
            </div>
            <div className="color-item">
              <div className="color-box" style={{ backgroundColor: theme.colors.error }} />
              <span>Error</span>
            </div>
          </div>
        </Card>

        {/* Surface Section */}
        <Card title="Surfaces" className="preview-card">
          <div className="surface-group">
            <div className="surface-item" style={{ backgroundColor: theme.colors.background }}>
              <span style={{ color: theme.colors.text }}>Background</span>
            </div>
            <div className="surface-item" style={{ backgroundColor: theme.colors.surface }}>
              <span style={{ color: theme.colors.text }}>Surface</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
