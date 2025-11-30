/**
 * Theme Selector Component (Modern - shadcn/ui)
 * Allows users to select from predefined theme presets
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Palette } from 'lucide-react';
import { useThemeStore } from '../../store/themeStore';
import { getThemePresetNames } from '../../theme/themePresets';

export const ThemeSelectorModern: React.FC = () => {
  const { theme, setPreset, openCustomThemeCreator } = useThemeStore();
  
  const presetOptions = getThemePresetNames().map(name => ({
    label: name.charAt(0).toUpperCase() + name.slice(1),
    value: name,
  }));

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Theme Preset</h3>
        <Button
          variant="ghost"
          size="sm"
          onClick={openCustomThemeCreator}
          className="gap-2"
        >
          <Palette className="h-4 w-4" />
          Create Custom
        </Button>
      </div>

      {/* Theme Dropdown */}
      <Select value={theme.preset} onValueChange={setPreset}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Select a theme" />
        </SelectTrigger>
        <SelectContent>
          {presetOptions.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Color Swatches Preview */}
      <div className="rounded-lg border p-4 bg-muted/30">
        <div className="grid grid-cols-6 gap-2">
          <div className="space-y-1">
            <div
              className="h-12 w-full rounded-md border shadow-sm"
              style={{ backgroundColor: theme.colors.primary }}
              title="Primary"
            />
            <p className="text-xs text-center text-muted-foreground">Primary</p>
          </div>
          <div className="space-y-1">
            <div
              className="h-12 w-full rounded-md border shadow-sm"
              style={{ backgroundColor: theme.colors.secondary }}
              title="Secondary"
            />
            <p className="text-xs text-center text-muted-foreground">Secondary</p>
          </div>
          <div className="space-y-1">
            <div
              className="h-12 w-full rounded-md border shadow-sm"
              style={{ backgroundColor: theme.colors.accent }}
              title="Accent"
            />
            <p className="text-xs text-center text-muted-foreground">Accent</p>
          </div>
          <div className="space-y-1">
            <div
              className="h-12 w-full rounded-md border shadow-sm"
              style={{ backgroundColor: theme.colors.success }}
              title="Success"
            />
            <p className="text-xs text-center text-muted-foreground">Success</p>
          </div>
          <div className="space-y-1">
            <div
              className="h-12 w-full rounded-md border shadow-sm"
              style={{ backgroundColor: theme.colors.warning }}
              title="Warning"
            />
            <p className="text-xs text-center text-muted-foreground">Warning</p>
          </div>
          <div className="space-y-1">
            <div
              className="h-12 w-full rounded-md border shadow-sm"
              style={{ backgroundColor: theme.colors.error }}
              title="Error"
            />
            <p className="text-xs text-center text-muted-foreground">Error</p>
          </div>
        </div>
      </div>
    </div>
  );
};
