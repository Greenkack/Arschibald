/**
 * Task 207: Customization UI Panel
 * =================================
 * Main customization panel with tabs for themes, emojis, effects, and presets.
 */

import React, { useState, useCallback, useMemo } from 'react';
import { themeService, ThemePreset, THEME_PRESETS } from '../../services/themeService';
import { emojiService, EmojiCategory, EMOJI_MAPPINGS } from '../../services/emojiService';
import { effectService, EFFECT_PRESETS, EffectPreset } from '../../services/effectService';
import { CardEffect, ButtonEffect, BadgeEffect } from '../effects/EffectWrapper';
import './CustomizationPanel.css';

// ============================================================================
// Types
// ============================================================================

type TabId = 'themes' | 'emojis' | 'effects' | 'presets';

interface CustomizationState {
  theme: string;
  emojisEnabled: boolean;
  effectPreset: string;
  customColors: Record<string, string>;
}

// ============================================================================
// Tab Components
// ============================================================================

// Theme Selector Tab
const ThemeTab: React.FC<{
  currentTheme: string;
  onThemeChange: (theme: string) => void;
}> = ({ currentTheme, onThemeChange }) => {
  const themes = Object.entries(THEME_PRESETS);

  return (
    <div className="customization-tab theme-tab">
      <h3 className="tab-title">🎨 Theme auswählen</h3>
      <p className="tab-description">
        Wählen Sie ein vordefiniertes Theme oder passen Sie die Farben an.
      </p>
      
      <div className="theme-grid">
        {themes.map(([key, preset]) => (
          <div
            key={key}
            className={`theme-card ${currentTheme === key ? 'active' : ''}`}
            onClick={() => onThemeChange(key)}
          >
            <div 
              className="theme-preview"
              style={{
                background: preset.colors.background,
                borderColor: preset.colors.border,
              }}
            >
              <div 
                className="preview-header"
                style={{ background: preset.colors.primary }}
              />
              <div className="preview-content">
                <div 
                  className="preview-card"
                  style={{ 
                    background: preset.colors.card,
                    borderColor: preset.colors.border,
                  }}
                />
                <div 
                  className="preview-button"
                  style={{ background: preset.colors.primary }}
                />
              </div>
            </div>
            <div className="theme-info">
              <span className="theme-name">{preset.name}</span>
              {currentTheme === key && (
                <BadgeEffect type="primary">Aktiv</BadgeEffect>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="color-customization">
        <h4>Farben anpassen</h4>
        <div className="color-inputs">
          <ColorInput 
            label="Primärfarbe" 
            value={THEME_PRESETS[currentTheme as keyof typeof THEME_PRESETS]?.colors.primary || '#3b82f6'}
            onChange={(color) => console.log('Primary color:', color)}
          />
          <ColorInput 
            label="Akzentfarbe" 
            value={THEME_PRESETS[currentTheme as keyof typeof THEME_PRESETS]?.colors.secondary || '#8b5cf6'}
            onChange={(color) => console.log('Secondary color:', color)}
          />
        </div>
      </div>
    </div>
  );
};

// Color Input Component
const ColorInput: React.FC<{
  label: string;
  value: string;
  onChange: (color: string) => void;
}> = ({ label, value, onChange }) => (
  <div className="color-input">
    <label>{label}</label>
    <div className="color-input-wrapper">
      <input
        type="color"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="#000000"
      />
    </div>
  </div>
);

// Emoji Settings Tab
const EmojiTab: React.FC<{
  emojisEnabled: boolean;
  onToggleEmojis: (enabled: boolean) => void;
}> = ({ emojisEnabled, onToggleEmojis }) => {
  const categories = emojiService.getCategories();
  const [selectedCategory, setSelectedCategory] = useState<EmojiCategory>('navigation');

  const categoryEmojis = useMemo(() => 
    emojiService.getByCategory(selectedCategory),
    [selectedCategory]
  );

  return (
    <div className="customization-tab emoji-tab">
      <h3 className="tab-title">😊 Emoji-Einstellungen</h3>
      <p className="tab-description">
        Aktivieren oder deaktivieren Sie Emojis in der Benutzeroberfläche.
      </p>

      <div className="emoji-toggle">
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={emojisEnabled}
            onChange={(e) => onToggleEmojis(e.target.checked)}
          />
          <span className="toggle-slider" />
          <span className="toggle-text">
            Emojis {emojisEnabled ? 'aktiviert' : 'deaktiviert'}
          </span>
        </label>
      </div>

      <div className="emoji-categories">
        <h4>Emoji-Kategorien</h4>
        <div className="category-tabs">
          {categories.map((cat) => (
            <button
              key={cat}
              className={`category-tab ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {getCategoryIcon(cat)} {getCategoryLabel(cat)}
            </button>
          ))}
        </div>
      </div>

      <div className="emoji-preview">
        <h4>Vorschau: {getCategoryLabel(selectedCategory)}</h4>
        <div className="emoji-grid">
          {categoryEmojis.map((mapping) => (
            <div key={mapping.key} className="emoji-item">
              <span className="emoji-char">{mapping.emoji}</span>
              <span className="emoji-desc">{mapping.description}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Helper functions for emoji categories
const getCategoryIcon = (category: EmojiCategory): string => {
  const icons: Record<EmojiCategory, string> = {
    navigation: '🧭',
    actions: '⚡',
    status: '✅',
    energy: '☀️',
    finance: '💰',
    documents: '📄',
    alerts: '🔔',
    misc: '🎯',
  };
  return icons[category];
};

const getCategoryLabel = (category: EmojiCategory): string => {
  const labels: Record<EmojiCategory, string> = {
    navigation: 'Navigation',
    actions: 'Aktionen',
    status: 'Status',
    energy: 'Energie',
    finance: 'Finanzen',
    documents: 'Dokumente',
    alerts: 'Benachrichtigungen',
    misc: 'Sonstiges',
  };
  return labels[category];
};

// Effects Configuration Tab
const EffectsTab: React.FC<{
  currentPreset: string;
  onPresetChange: (preset: string) => void;
}> = ({ currentPreset, onPresetChange }) => {
  const presets = Object.entries(EFFECT_PRESETS);

  return (
    <div className="customization-tab effects-tab">
      <h3 className="tab-title">✨ Effekte konfigurieren</h3>
      <p className="tab-description">
        Wählen Sie einen Effekt-Stil für Animationen und Übergänge.
      </p>

      <div className="effect-presets">
        {presets.map(([key, preset]) => (
          <div
            key={key}
            className={`effect-preset-card ${currentPreset === key ? 'active' : ''}`}
            onClick={() => onPresetChange(key)}
          >
            <div className="preset-header">
              <span className="preset-name">{preset.name}</span>
              {currentPreset === key && (
                <BadgeEffect type="primary">Aktiv</BadgeEffect>
              )}
            </div>
            <p className="preset-description">{preset.description}</p>
            <div className="preset-demo">
              <ButtonEffect variant={key as any}>
                Hover mich
              </ButtonEffect>
            </div>
          </div>
        ))}
      </div>

      <div className="effect-settings">
        <h4>Erweiterte Einstellungen</h4>
        <div className="setting-row">
          <label>Animationsgeschwindigkeit</label>
          <input type="range" min="0.5" max="2" step="0.1" defaultValue="1" />
        </div>
        <div className="setting-row">
          <label>Schatten-Intensität</label>
          <input type="range" min="0" max="100" step="10" defaultValue="50" />
        </div>
      </div>
    </div>
  );
};

// Presets Tab
const PresetsTab: React.FC<{
  onApplyPreset: (preset: string) => void;
  onSavePreset: () => void;
}> = ({ onApplyPreset, onSavePreset }) => {
  const systemPresets = [
    { id: 'minimal', name: 'Minimal', description: 'Reduzierte Effekte, schnelle Performance', icon: '🎯' },
    { id: 'standard', name: 'Standard', description: 'Ausgewogene Einstellungen für den Alltag', icon: '⚖️' },
    { id: 'enhanced', name: 'Erweitert', description: 'Mehr visuelle Effekte und Animationen', icon: '✨' },
    { id: 'maximum', name: 'Maximum', description: 'Alle Effekte aktiviert', icon: '🚀' },
  ];

  return (
    <div className="customization-tab presets-tab">
      <h3 className="tab-title">📦 Voreinstellungen</h3>
      <p className="tab-description">
        Schnell zwischen verschiedenen Konfigurationen wechseln.
      </p>

      <div className="system-presets">
        <h4>System-Voreinstellungen</h4>
        <div className="preset-list">
          {systemPresets.map((preset) => (
            <div key={preset.id} className="preset-item">
              <span className="preset-icon">{preset.icon}</span>
              <div className="preset-info">
                <span className="preset-name">{preset.name}</span>
                <span className="preset-desc">{preset.description}</span>
              </div>
              <ButtonEffect 
                variant="subtle"
                onClick={() => onApplyPreset(preset.id)}
              >
                Anwenden
              </ButtonEffect>
            </div>
          ))}
        </div>
      </div>

      <div className="custom-presets">
        <h4>Eigene Voreinstellungen</h4>
        <p className="empty-state">
          Noch keine eigenen Voreinstellungen gespeichert.
        </p>
        <ButtonEffect onClick={onSavePreset}>
          💾 Aktuelle Einstellungen speichern
        </ButtonEffect>
      </div>
    </div>
  );
};

// Live Preview Panel
const LivePreview: React.FC<{
  state: CustomizationState;
}> = ({ state }) => {
  return (
    <div className="live-preview">
      <h4>Live-Vorschau</h4>
      <div className="preview-container">
        <CardEffect variant={state.effectPreset as any} shadow="md">
          <div className="preview-card-content">
            <h5>{state.emojisEnabled ? '☀️ ' : ''}Solar Calculator</h5>
            <p>Beispieltext für die Vorschau</p>
            <div className="preview-buttons">
              <ButtonEffect variant={state.effectPreset as any}>
                {state.emojisEnabled ? '💾 ' : ''}Speichern
              </ButtonEffect>
              <ButtonEffect variant={state.effectPreset as any}>
                {state.emojisEnabled ? '❌ ' : ''}Abbrechen
              </ButtonEffect>
            </div>
          </div>
        </CardEffect>
      </div>
    </div>
  );
};

// ============================================================================
// Main Customization Panel
// ============================================================================

export const CustomizationPanel: React.FC<{
  isOpen: boolean;
  onClose: () => void;
}> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<TabId>('themes');
  const [state, setState] = useState<CustomizationState>({
    theme: 'light',
    emojisEnabled: true,
    effectPreset: 'standard',
    customColors: {},
  });

  const handleThemeChange = useCallback((theme: string) => {
    setState(prev => ({ ...prev, theme }));
    themeService.setTheme(theme);
  }, []);

  const handleToggleEmojis = useCallback((enabled: boolean) => {
    setState(prev => ({ ...prev, emojisEnabled: enabled }));
    emojiService.toggleEmojis(enabled);
  }, []);

  const handleEffectPresetChange = useCallback((preset: string) => {
    setState(prev => ({ ...prev, effectPreset: preset }));
    effectService.setPreset(preset);
  }, []);

  const handleApplyPreset = useCallback((presetId: string) => {
    // Apply system preset
    switch (presetId) {
      case 'minimal':
        handleThemeChange('light');
        handleToggleEmojis(false);
        handleEffectPresetChange('minimal');
        break;
      case 'standard':
        handleThemeChange('light');
        handleToggleEmojis(true);
        handleEffectPresetChange('standard');
        break;
      case 'enhanced':
        handleThemeChange('light');
        handleToggleEmojis(true);
        handleEffectPresetChange('playful');
        break;
      case 'maximum':
        handleThemeChange('light');
        handleToggleEmojis(true);
        handleEffectPresetChange('dramatic');
        break;
    }
  }, [handleThemeChange, handleToggleEmojis, handleEffectPresetChange]);

  const handleSavePreset = useCallback(() => {
    // Save current state as custom preset
    console.log('Saving preset:', state);
    alert('Voreinstellung gespeichert!');
  }, [state]);

  const handleResetDefaults = useCallback(() => {
    setState({
      theme: 'light',
      emojisEnabled: true,
      effectPreset: 'standard',
      customColors: {},
    });
    themeService.setTheme('light');
    emojiService.toggleEmojis(true);
    effectService.setPreset('standard');
  }, []);

  if (!isOpen) return null;

  const tabs: { id: TabId; label: string; icon: string }[] = [
    { id: 'themes', label: 'Themes', icon: '🎨' },
    { id: 'emojis', label: 'Emojis', icon: '😊' },
    { id: 'effects', label: 'Effekte', icon: '✨' },
    { id: 'presets', label: 'Presets', icon: '📦' },
  ];

  return (
    <div className="customization-panel-overlay" onClick={onClose}>
      <div className="customization-panel" onClick={(e) => e.stopPropagation()}>
        <div className="panel-header">
          <h2>⚙️ Anpassungen</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="panel-tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`panel-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="panel-content">
          <div className="tab-content">
            {activeTab === 'themes' && (
              <ThemeTab 
                currentTheme={state.theme}
                onThemeChange={handleThemeChange}
              />
            )}
            {activeTab === 'emojis' && (
              <EmojiTab
                emojisEnabled={state.emojisEnabled}
                onToggleEmojis={handleToggleEmojis}
              />
            )}
            {activeTab === 'effects' && (
              <EffectsTab
                currentPreset={state.effectPreset}
                onPresetChange={handleEffectPresetChange}
              />
            )}
            {activeTab === 'presets' && (
              <PresetsTab
                onApplyPreset={handleApplyPreset}
                onSavePreset={handleSavePreset}
              />
            )}
          </div>

          <LivePreview state={state} />
        </div>

        <div className="panel-footer">
          <ButtonEffect variant="subtle" onClick={handleResetDefaults}>
            🔄 Zurücksetzen
          </ButtonEffect>
          <ButtonEffect onClick={onClose}>
            ✅ Fertig
          </ButtonEffect>
        </div>
      </div>
    </div>
  );
};

export default CustomizationPanel;
