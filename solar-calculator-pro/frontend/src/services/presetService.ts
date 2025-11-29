/**
 * Task 208: Preset System
 * =======================
 * Centralized preset management for themes, emojis, and effects.
 */

import { themeService, ThemePreset } from './themeService';
import { emojiService, EmojiConfig } from './emojiService';
import { effectService, EffectPreset } from './effectService';

// ============================================================================
// Types
// ============================================================================

export interface UIPreset {
  id: string;
  name: string;
  description: string;
  icon: string;
  isSystem: boolean;
  isCustom: boolean;
  createdAt?: string;
  updatedAt?: string;
  config: PresetConfig;
}

export interface PresetConfig {
  theme: string;
  emojis: {
    enabled: boolean;
    style: 'native' | 'twemoji' | 'noto';
    animateOnHover: boolean;
  };
  effects: {
    preset: string;
    animationSpeed: number; // 0.5 - 2.0
    shadowIntensity: number; // 0 - 100
    enableTransitions: boolean;
    enableAnimations: boolean;
  };
  accessibility: {
    reducedMotion: boolean;
    highContrast: boolean;
    largeText: boolean;
  };
}

// ============================================================================
// System Presets
// ============================================================================

export const SYSTEM_PRESETS: Record<string, UIPreset> = {
  minimal: {
    id: 'minimal',
    name: 'Minimal',
    description: 'Reduzierte Effekte für maximale Performance und Fokus',
    icon: '🎯',
    isSystem: true,
    isCustom: false,
    config: {
      theme: 'light',
      emojis: {
        enabled: false,
        style: 'native',
        animateOnHover: false,
      },
      effects: {
        preset: 'minimal',
        animationSpeed: 1.5,
        shadowIntensity: 20,
        enableTransitions: true,
        enableAnimations: false,
      },
      accessibility: {
        reducedMotion: true,
        highContrast: false,
        largeText: false,
      },
    },
  },
  standard: {
    id: 'standard',
    name: 'Standard',
    description: 'Ausgewogene Einstellungen für den täglichen Gebrauch',
    icon: '⚖️',
    isSystem: true,
    isCustom: false,
    config: {
      theme: 'light',
      emojis: {
        enabled: true,
        style: 'native',
        animateOnHover: false,
      },
      effects: {
        preset: 'standard',
        animationSpeed: 1.0,
        shadowIntensity: 50,
        enableTransitions: true,
        enableAnimations: true,
      },
      accessibility: {
        reducedMotion: false,
        highContrast: false,
        largeText: false,
      },
    },
  },
  enhanced: {
    id: 'enhanced',
    name: 'Erweitert',
    description: 'Mehr visuelle Effekte und Animationen',
    icon: '✨',
    isSystem: true,
    isCustom: false,
    config: {
      theme: 'light',
      emojis: {
        enabled: true,
        style: 'native',
        animateOnHover: true,
      },
      effects: {
        preset: 'playful',
        animationSpeed: 1.0,
        shadowIntensity: 70,
        enableTransitions: true,
        enableAnimations: true,
      },
      accessibility: {
        reducedMotion: false,
        highContrast: false,
        largeText: false,
      },
    },
  },
  maximum: {
    id: 'maximum',
    name: 'Maximum',
    description: 'Alle Effekte aktiviert für maximale visuelle Wirkung',
    icon: '🚀',
    isSystem: true,
    isCustom: false,
    config: {
      theme: 'light',
      emojis: {
        enabled: true,
        style: 'native',
        animateOnHover: true,
      },
      effects: {
        preset: 'dramatic',
        animationSpeed: 1.0,
        shadowIntensity: 100,
        enableTransitions: true,
        enableAnimations: true,
      },
      accessibility: {
        reducedMotion: false,
        highContrast: false,
        largeText: false,
      },
    },
  },
  darkMode: {
    id: 'darkMode',
    name: 'Dunkelmodus',
    description: 'Dunkles Theme mit reduzierten Effekten',
    icon: '🌙',
    isSystem: true,
    isCustom: false,
    config: {
      theme: 'dark',
      emojis: {
        enabled: true,
        style: 'native',
        animateOnHover: false,
      },
      effects: {
        preset: 'subtle',
        animationSpeed: 1.0,
        shadowIntensity: 40,
        enableTransitions: true,
        enableAnimations: true,
      },
      accessibility: {
        reducedMotion: false,
        highContrast: false,
        largeText: false,
      },
    },
  },
  accessible: {
    id: 'accessible',
    name: 'Barrierefrei',
    description: 'Optimiert für Barrierefreiheit mit hohem Kontrast',
    icon: '♿',
    isSystem: true,
    isCustom: false,
    config: {
      theme: 'highContrast',
      emojis: {
        enabled: false,
        style: 'native',
        animateOnHover: false,
      },
      effects: {
        preset: 'minimal',
        animationSpeed: 1.5,
        shadowIntensity: 0,
        enableTransitions: false,
        enableAnimations: false,
      },
      accessibility: {
        reducedMotion: true,
        highContrast: true,
        largeText: true,
      },
    },
  },
};

// ============================================================================
// Preset Service Class
// ============================================================================

const STORAGE_KEY = 'solar-calculator-presets';
const ACTIVE_PRESET_KEY = 'solar-calculator-active-preset';

class PresetService {
  private customPresets: Map<string, UIPreset> = new Map();
  private activePresetId: string = 'standard';
  private listeners: Set<(preset: UIPreset) => void> = new Set();

  constructor() {
    this.loadFromStorage();
  }

  // --------------------------------------------------------------------------
  // Storage
  // --------------------------------------------------------------------------

  private loadFromStorage(): void {
    if (typeof localStorage === 'undefined') return;

    try {
      // Load custom presets
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const presets = JSON.parse(stored) as UIPreset[];
        presets.forEach(preset => {
          this.customPresets.set(preset.id, preset);
        });
      }

      // Load active preset
      const activeId = localStorage.getItem(ACTIVE_PRESET_KEY);
      if (activeId && (SYSTEM_PRESETS[activeId] || this.customPresets.has(activeId))) {
        this.activePresetId = activeId;
      }
    } catch (error) {
      console.error('Failed to load presets from storage:', error);
    }
  }

  private saveToStorage(): void {
    if (typeof localStorage === 'undefined') return;

    try {
      const presets = Array.from(this.customPresets.values());
      localStorage.setItem(STORAGE_KEY, JSON.stringify(presets));
      localStorage.setItem(ACTIVE_PRESET_KEY, this.activePresetId);
    } catch (error) {
      console.error('Failed to save presets to storage:', error);
    }
  }

  // --------------------------------------------------------------------------
  // Preset Management
  // --------------------------------------------------------------------------

  getPreset(id: string): UIPreset | undefined {
    return SYSTEM_PRESETS[id] || this.customPresets.get(id);
  }

  getActivePreset(): UIPreset {
    return this.getPreset(this.activePresetId) || SYSTEM_PRESETS.standard;
  }

  getActivePresetId(): string {
    return this.activePresetId;
  }

  getAllPresets(): UIPreset[] {
    return [
      ...Object.values(SYSTEM_PRESETS),
      ...Array.from(this.customPresets.values()),
    ];
  }

  getSystemPresets(): UIPreset[] {
    return Object.values(SYSTEM_PRESETS);
  }

  getCustomPresets(): UIPreset[] {
    return Array.from(this.customPresets.values());
  }

  // --------------------------------------------------------------------------
  // Apply Preset
  // --------------------------------------------------------------------------

  applyPreset(id: string): boolean {
    const preset = this.getPreset(id);
    if (!preset) {
      console.warn(`Preset "${id}" not found`);
      return false;
    }

    this.activePresetId = id;
    this.applyConfig(preset.config);
    this.saveToStorage();
    this.notifyListeners(preset);
    return true;
  }

  private applyConfig(config: PresetConfig): void {
    // Apply theme
    themeService.setTheme(config.theme);

    // Apply emoji settings
    emojiService.setConfig({
      enabled: config.emojis.enabled,
      animateOnHover: config.emojis.animateOnHover,
    });

    // Apply effect settings
    effectService.setPreset(config.effects.preset);

    // Apply accessibility settings
    this.applyAccessibilitySettings(config.accessibility);

    // Apply animation speed
    this.setAnimationSpeed(config.effects.animationSpeed);
  }

  private applyAccessibilitySettings(settings: PresetConfig['accessibility']): void {
    if (typeof document === 'undefined') return;

    const root = document.documentElement;
    
    if (settings.reducedMotion) {
      root.classList.add('reduced-motion');
    } else {
      root.classList.remove('reduced-motion');
    }

    if (settings.highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }

    if (settings.largeText) {
      root.classList.add('large-text');
    } else {
      root.classList.remove('large-text');
    }
  }

  private setAnimationSpeed(speed: number): void {
    if (typeof document === 'undefined') return;
    document.documentElement.style.setProperty('--animation-speed', `${speed}`);
  }

  // --------------------------------------------------------------------------
  // Custom Preset Management
  // --------------------------------------------------------------------------

  createPreset(name: string, description: string, config: PresetConfig): UIPreset {
    const id = `custom-${Date.now()}`;
    const preset: UIPreset = {
      id,
      name,
      description,
      icon: '⭐',
      isSystem: false,
      isCustom: true,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      config,
    };

    this.customPresets.set(id, preset);
    this.saveToStorage();
    return preset;
  }

  updatePreset(id: string, updates: Partial<Omit<UIPreset, 'id' | 'isSystem'>>): boolean {
    const preset = this.customPresets.get(id);
    if (!preset) {
      console.warn(`Custom preset "${id}" not found`);
      return false;
    }

    const updated: UIPreset = {
      ...preset,
      ...updates,
      updatedAt: new Date().toISOString(),
    };

    this.customPresets.set(id, updated);
    this.saveToStorage();
    return true;
  }

  deletePreset(id: string): boolean {
    if (SYSTEM_PRESETS[id]) {
      console.warn('Cannot delete system preset');
      return false;
    }

    const deleted = this.customPresets.delete(id);
    if (deleted) {
      if (this.activePresetId === id) {
        this.applyPreset('standard');
      }
      this.saveToStorage();
    }
    return deleted;
  }

  duplicatePreset(id: string, newName: string): UIPreset | null {
    const source = this.getPreset(id);
    if (!source) return null;

    return this.createPreset(
      newName,
      `Kopie von ${source.name}`,
      { ...source.config }
    );
  }

  // --------------------------------------------------------------------------
  // Save Current State
  // --------------------------------------------------------------------------

  saveCurrentAsPreset(name: string, description: string): UIPreset {
    const config = this.getCurrentConfig();
    return this.createPreset(name, description, config);
  }

  getCurrentConfig(): PresetConfig {
    const activePreset = this.getActivePreset();
    return { ...activePreset.config };
  }

  // --------------------------------------------------------------------------
  // Export/Import
  // --------------------------------------------------------------------------

  exportPreset(id: string): string | null {
    const preset = this.getPreset(id);
    if (!preset) return null;

    return JSON.stringify({
      version: '1.0',
      preset: {
        name: preset.name,
        description: preset.description,
        icon: preset.icon,
        config: preset.config,
      },
    }, null, 2);
  }

  importPreset(jsonString: string): UIPreset | null {
    try {
      const data = JSON.parse(jsonString);
      if (!data.preset || !data.preset.config) {
        throw new Error('Invalid preset format');
      }

      return this.createPreset(
        data.preset.name || 'Importiertes Preset',
        data.preset.description || '',
        data.preset.config
      );
    } catch (error) {
      console.error('Failed to import preset:', error);
      return null;
    }
  }

  exportAllCustomPresets(): string {
    const presets = this.getCustomPresets();
    return JSON.stringify({
      version: '1.0',
      presets: presets.map(p => ({
        name: p.name,
        description: p.description,
        icon: p.icon,
        config: p.config,
      })),
    }, null, 2);
  }

  // --------------------------------------------------------------------------
  // Listeners
  // --------------------------------------------------------------------------

  subscribe(listener: (preset: UIPreset) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(preset: UIPreset): void {
    this.listeners.forEach(listener => listener(preset));
  }

  // --------------------------------------------------------------------------
  // Reset
  // --------------------------------------------------------------------------

  resetToDefault(): void {
    this.applyPreset('standard');
  }

  clearAllCustomPresets(): void {
    this.customPresets.clear();
    this.saveToStorage();
  }
}

// ============================================================================
// Singleton Export
// ============================================================================

export const presetService = new PresetService();

// ============================================================================
// React Hook
// ============================================================================

import { useState, useEffect, useCallback } from 'react';

export function usePreset() {
  const [activePreset, setActivePreset] = useState<UIPreset>(presetService.getActivePreset());

  useEffect(() => {
    const unsubscribe = presetService.subscribe(setActivePreset);
    return unsubscribe;
  }, []);

  const applyPreset = useCallback((id: string) => {
    presetService.applyPreset(id);
  }, []);

  const saveCurrentAsPreset = useCallback((name: string, description: string) => {
    return presetService.saveCurrentAsPreset(name, description);
  }, []);

  return {
    activePreset,
    activePresetId: presetService.getActivePresetId(),
    allPresets: presetService.getAllPresets(),
    systemPresets: presetService.getSystemPresets(),
    customPresets: presetService.getCustomPresets(),
    applyPreset,
    saveCurrentAsPreset,
    createPreset: presetService.createPreset.bind(presetService),
    deletePreset: presetService.deletePreset.bind(presetService),
    exportPreset: presetService.exportPreset.bind(presetService),
    importPreset: presetService.importPreset.bind(presetService),
    resetToDefault: presetService.resetToDefault.bind(presetService),
  };
}

export default presetService;
