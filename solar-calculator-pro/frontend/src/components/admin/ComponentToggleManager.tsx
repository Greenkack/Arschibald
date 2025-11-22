/**
 * Component Toggle Manager
 * 
 * Admin interface for managing component-level feature toggles.
 */

import React, { useState } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { InputSwitch } from 'primereact/inputswitch';
import { Button } from 'primereact/button';
import { Message } from 'primereact/message';
import { ProgressSpinner } from 'primereact/progressspinner';
import { useComponentToggles } from '../../hooks/useComponentToggles';
import './ComponentToggleManager.css';

interface ChartToggle {
  key: string;
  name: string;
  description: string;
}

interface ExportFormat {
  key: string;
  name: string;
  description: string;
}

interface Theme {
  key: string;
  name: string;
  description: string;
}

interface Language {
  code: string;
  name: string;
  nativeName: string;
}

export const ComponentToggleManager: React.FC = () => {
  const {
    visibleCharts,
    toggleChart,
    availableExportFormats,
    toggleExportFormat,
    availableThemes,
    toggleTheme,
    availableLanguages,
    toggleLanguage,
    bulkToggle,
    resetToDefaults,
    loading,
    error,
    refresh
  } = useComponentToggles();

  const [activeIndex, setActiveIndex] = useState(0);

  // Chart definitions
  const chartTypes: ChartToggle[] = [
    { key: 'line_chart', name: 'Line Chart', description: 'Time series and trend visualization' },
    { key: 'bar_chart', name: 'Bar Chart', description: 'Comparison and categorical data' },
    { key: 'pie_chart', name: 'Pie Chart', description: 'Proportional data visualization' },
    { key: 'area_chart', name: 'Area Chart', description: 'Cumulative data over time' },
    { key: 'donut_chart', name: 'Donut Chart', description: 'Proportional data with center space' },
    { key: 'scatter_chart', name: 'Scatter Chart', description: 'Correlation and distribution' },
    { key: 'radar_chart', name: 'Radar Chart', description: 'Multi-dimensional comparison' },
    { key: 'waterfall_chart', name: 'Waterfall Chart', description: 'Sequential value changes' }
  ];

  // Export format definitions
  const exportFormats: ExportFormat[] = [
    { key: 'pdf', name: 'PDF', description: 'Portable Document Format' },
    { key: 'excel', name: 'Excel', description: 'Microsoft Excel spreadsheet' },
    { key: 'csv', name: 'CSV', description: 'Comma-separated values' },
    { key: 'json', name: 'JSON', description: 'JavaScript Object Notation' },
    { key: 'xml', name: 'XML', description: 'Extensible Markup Language' }
  ];

  // Theme definitions
  const themes: Theme[] = [
    { key: 'light', name: 'Light Theme', description: 'Standard light color scheme' },
    { key: 'dark', name: 'Dark Theme', description: 'Dark color scheme for low-light environments' },
    { key: 'high_contrast', name: 'High Contrast', description: 'Enhanced visibility theme' },
    { key: 'custom', name: 'Custom Theme', description: 'User-defined color scheme' }
  ];

  // Language definitions
  const languages: Language[] = [
    { code: 'de', name: 'German', nativeName: 'Deutsch' },
    { code: 'en', name: 'English', nativeName: 'English' },
    { code: 'fr', name: 'French', nativeName: 'Français' },
    { code: 'es', name: 'Spanish', nativeName: 'Español' },
    { code: 'it', name: 'Italian', nativeName: 'Italiano' },
    { code: 'nl', name: 'Dutch', nativeName: 'Nederlands' },
    { code: 'pl', name: 'Polish', nativeName: 'Polski' },
    { code: 'cs', name: 'Czech', nativeName: 'Čeština' }
  ];

  // Toggle handlers
  const handleChartToggle = async (chartKey: string, enabled: boolean) => {
    try {
      await toggleChart(chartKey, enabled);
    } catch (err) {
      console.error('Failed to toggle chart:', err);
    }
  };

  const handleExportFormatToggle = async (formatKey: string, enabled: boolean) => {
    try {
      await toggleExportFormat(formatKey, enabled);
    } catch (err) {
      console.error('Failed to toggle export format:', err);
    }
  };

  const handleThemeToggle = async (themeKey: string, enabled: boolean) => {
    try {
      await toggleTheme(themeKey, enabled);
    } catch (err) {
      console.error('Failed to toggle theme:', err);
    }
  };

  const handleLanguageToggle = async (languageCode: string, enabled: boolean) => {
    try {
      await toggleLanguage(languageCode, enabled);
    } catch (err) {
      console.error('Failed to toggle language:', err);
    }
  };

  // Bulk operations
  const handleBulkToggle = async (category: string, enabled: boolean) => {
    try {
      await bulkToggle(category, enabled);
    } catch (err) {
      console.error('Failed to bulk toggle:', err);
    }
  };

  const handleResetToDefaults = async () => {
    if (window.confirm('Are you sure you want to reset all toggles to default values?')) {
      try {
        await resetToDefaults();
      } catch (err) {
        console.error('Failed to reset to defaults:', err);
      }
    }
  };

  // Template functions for DataTable
  const toggleBodyTemplate = (rowData: any, isEnabled: boolean, onToggle: (key: string, enabled: boolean) => void) => {
    return (
      <InputSwitch
        checked={isEnabled}
        onChange={(e) => onToggle(rowData.key || rowData.code, e.value)}
      />
    );
  };

  if (loading && !visibleCharts.length) {
    return (
      <div className="component-toggle-manager-loading">
        <ProgressSpinner />
        <p>Loading component toggles...</p>
      </div>
    );
  }

  return (
    <div className="component-toggle-manager">
      <div className="component-toggle-header">
        <h2>Component Toggle Manager</h2>
        <div className="component-toggle-actions">
          <Button
            label="Refresh"
            icon="pi pi-refresh"
            onClick={refresh}
            className="p-button-outlined"
          />
          <Button
            label="Reset to Defaults"
            icon="pi pi-undo"
            onClick={handleResetToDefaults}
            className="p-button-outlined p-button-warning"
          />
        </div>
      </div>

      {error && (
        <Message severity="error" text={error} className="component-toggle-error" />
      )}

      <TabView activeIndex={activeIndex} onTabChange={(e) => setActiveIndex(e.index)}>
        {/* Chart Visibility Tab */}
        <TabPanel header="Charts" leftIcon="pi pi-chart-line">
          <div className="toggle-tab-content">
            <div className="toggle-tab-header">
              <h3>Chart Visibility Toggles</h3>
              <div className="bulk-actions">
                <Button
                  label="Enable All"
                  size="small"
                  onClick={() => handleBulkToggle('chart', true)}
                />
                <Button
                  label="Disable All"
                  size="small"
                  className="p-button-secondary"
                  onClick={() => handleBulkToggle('chart', false)}
                />
              </div>
            </div>
            
            <DataTable value={chartTypes} responsiveLayout="scroll">
              <Column field="name" header="Chart Type" />
              <Column field="description" header="Description" />
              <Column
                header="Visible"
                body={(rowData) => toggleBodyTemplate(
                  rowData,
                  visibleCharts.includes(rowData.key),
                  handleChartToggle
                )}
                style={{ width: '100px', textAlign: 'center' }}
              />
            </DataTable>
          </div>
        </TabPanel>

        {/* Export Formats Tab */}
        <TabPanel header="Export Formats" leftIcon="pi pi-download">
          <div className="toggle-tab-content">
            <div className="toggle-tab-header">
              <h3>Export Format Toggles</h3>
              <div className="bulk-actions">
                <Button
                  label="Enable All"
                  size="small"
                  onClick={() => handleBulkToggle('export_format', true)}
                />
                <Button
                  label="Disable All"
                  size="small"
                  className="p-button-secondary"
                  onClick={() => handleBulkToggle('export_format', false)}
                />
              </div>
            </div>
            
            <DataTable value={exportFormats} responsiveLayout="scroll">
              <Column field="name" header="Format" />
              <Column field="description" header="Description" />
              <Column
                header="Available"
                body={(rowData) => toggleBodyTemplate(
                  rowData,
                  availableExportFormats.includes(rowData.key),
                  handleExportFormatToggle
                )}
                style={{ width: '100px', textAlign: 'center' }}
              />
            </DataTable>
          </div>
        </TabPanel>

        {/* UI Themes Tab */}
        <TabPanel header="Themes" leftIcon="pi pi-palette">
          <div className="toggle-tab-content">
            <div className="toggle-tab-header">
              <h3>UI Theme Toggles</h3>
              <div className="bulk-actions">
                <Button
                  label="Enable All"
                  size="small"
                  onClick={() => handleBulkToggle('ui_theme', true)}
                />
                <Button
                  label="Disable All"
                  size="small"
                  className="p-button-secondary"
                  onClick={() => handleBulkToggle('ui_theme', false)}
                />
              </div>
            </div>
            
            <DataTable value={themes} responsiveLayout="scroll">
              <Column field="name" header="Theme" />
              <Column field="description" header="Description" />
              <Column
                header="Available"
                body={(rowData) => toggleBodyTemplate(
                  rowData,
                  availableThemes.includes(rowData.key),
                  handleThemeToggle
                )}
                style={{ width: '100px', textAlign: 'center' }}
              />
            </DataTable>
          </div>
        </TabPanel>

        {/* Languages Tab */}
        <TabPanel header="Languages" leftIcon="pi pi-globe">
          <div className="toggle-tab-content">
            <div className="toggle-tab-header">
              <h3>Language Toggles</h3>
              <div className="bulk-actions">
                <Button
                  label="Enable All"
                  size="small"
                  onClick={() => handleBulkToggle('language', true)}
                />
                <Button
                  label="Disable All"
                  size="small"
                  className="p-button-secondary"
                  onClick={() => handleBulkToggle('language', false)}
                />
              </div>
            </div>
            
            <DataTable value={languages} responsiveLayout="scroll">
              <Column field="name" header="Language" />
              <Column field="nativeName" header="Native Name" />
              <Column field="code" header="Code" />
              <Column
                header="Available"
                body={(rowData) => toggleBodyTemplate(
                  rowData,
                  availableLanguages.includes(rowData.code),
                  handleLanguageToggle
                )}
                style={{ width: '100px', textAlign: 'center' }}
              />
            </DataTable>
          </div>
        </TabPanel>
      </TabView>
    </div>
  );
};
