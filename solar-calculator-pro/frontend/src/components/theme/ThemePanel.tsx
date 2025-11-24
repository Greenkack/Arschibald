/**
 * Theme Panel Component
 * Main panel that combines all theme-related components
 */

import React from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { ThemeSelector } from './ThemeSelector';
import { CustomThemeCreator } from './CustomThemeCreator';
import { ThemeImportExport } from './ThemeImportExport';
import { ThemePreview } from './ThemePreview';
import { DarkModeToggle } from './DarkModeToggle';
import './ThemePanel.css';

export const ThemePanel: React.FC = () => {
  return (
    <div className="theme-panel">
      <div className="theme-panel-header">
        <h2>Theme Settings</h2>
        <DarkModeToggle />
      </div>

      <TabView>
        <TabPanel header="Presets">
          <ThemeSelector />
        </TabPanel>

        <TabPanel header="Preview">
          <ThemePreview />
        </TabPanel>

        <TabPanel header="Import/Export">
          <ThemeImportExport />
        </TabPanel>
      </TabView>

      <CustomThemeCreator />
    </div>
  );
};
