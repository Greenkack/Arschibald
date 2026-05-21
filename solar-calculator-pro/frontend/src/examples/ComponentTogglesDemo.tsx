/**
 * Component Toggles Demo
 * 
 * Demonstrates the usage of component-level feature toggles.
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { Divider } from 'primereact/divider';
import { Message } from 'primereact/message';
import { useComponentToggles } from '../hooks/useComponentToggles';
import { LineChart, BarChart, PieChart, AreaChart } from '../components/charts';

export const ComponentTogglesDemo: React.FC = () => {
  const {
    visibleCharts,
    toggleChart,
    isChartVisible,
    availableExportFormats,
    toggleExportFormat,
    isExportFormatAvailable,
    availableThemes,
    toggleTheme,
    isThemeAvailable,
    availableLanguages,
    toggleLanguage,
    isLanguageAvailable,
    loading,
    error
  } = useComponentToggles();

  const [demoData] = useState({
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    values: [65, 59, 80, 81, 56, 55]
  });

  // Chart Toggle Demo
  const ChartToggleDemo = () => (
    <Card title="Chart Visibility Toggles" className="demo-card">
      <div className="demo-section">
        <h4>Toggle Controls</h4>
        <div className="toggle-buttons">
          <Button
            label="Line Chart"
            icon={isChartVisible('line_chart') ? 'pi pi-eye' : 'pi pi-eye-slash'}
            onClick={() => toggleChart('line_chart', !isChartVisible('line_chart'))}
            className={isChartVisible('line_chart') ? 'p-button-success' : 'p-button-secondary'}
          />
          <Button
            label="Bar Chart"
            icon={isChartVisible('bar_chart') ? 'pi pi-eye' : 'pi pi-eye-slash'}
            onClick={() => toggleChart('bar_chart', !isChartVisible('bar_chart'))}
            className={isChartVisible('bar_chart') ? 'p-button-success' : 'p-button-secondary'}
          />
          <Button
            label="Pie Chart"
            icon={isChartVisible('pie_chart') ? 'pi pi-eye' : 'pi pi-eye-slash'}
            onClick={() => toggleChart('pie_chart', !isChartVisible('pie_chart'))}
            className={isChartVisible('pie_chart') ? 'p-button-success' : 'p-button-secondary'}
          />
          <Button
            label="Area Chart"
            icon={isChartVisible('area_chart') ? 'pi pi-eye' : 'pi pi-eye-slash'}
            onClick={() => toggleChart('area_chart', !isChartVisible('area_chart'))}
            className={isChartVisible('area_chart') ? 'p-button-success' : 'p-button-secondary'}
          />
        </div>
      </div>

      <Divider />

      <div className="demo-section">
        <h4>Visible Charts</h4>
        <div className="charts-grid">
          {isChartVisible('line_chart') && (
            <div className="chart-container">
              <h5>Line Chart</h5>
              <LineChart data={demoData} />
            </div>
          )}
          {isChartVisible('bar_chart') && (
            <div className="chart-container">
              <h5>Bar Chart</h5>
              <BarChart data={demoData} />
            </div>
          )}
          {isChartVisible('pie_chart') && (
            <div className="chart-container">
              <h5>Pie Chart</h5>
              <PieChart data={demoData} />
            </div>
          )}
          {isChartVisible('area_chart') && (
            <div className="chart-container">
              <h5>Area Chart</h5>
              <AreaChart data={demoData} />
            </div>
          )}
        </div>
        {visibleCharts.length === 0 && (
          <Message severity="info" text="No charts are currently visible. Enable charts using the toggle buttons above." />
        )}
      </div>
    </Card>
  );

  // Export Format Toggle Demo
  const ExportFormatToggleDemo = () => (
    <Card title="Export Format Toggles" className="demo-card">
      <div className="demo-section">
        <h4>Toggle Controls</h4>
        <div className="toggle-buttons">
          <Button
            label="PDF"
            icon={isExportFormatAvailable('pdf') ? 'pi pi-check' : 'pi pi-times'}
            onClick={() => toggleExportFormat('pdf', !isExportFormatAvailable('pdf'))}
            className={isExportFormatAvailable('pdf') ? 'p-button-success' : 'p-button-secondary'}
          />
          <Button
            label="Excel"
            icon={isExportFormatAvailable('excel') ? 'pi pi-check' : 'pi pi-times'}
            onClick={() => toggleExportFormat('excel', !isExportFormatAvailable('excel'))}
            className={isExportFormatAvailable('excel') ? 'p-button-success' : 'p-button-secondary'}
          />
          <Button
            label="CSV"
            icon={isExportFormatAvailable('csv') ? 'pi pi-check' : 'pi pi-times'}
            onClick={() => toggleExportFormat('csv', !isExportFormatAvailable('csv'))}
            className={isExportFormatAvailable('csv') ? 'p-button-success' : 'p-button-secondary'}
          />
          <Button
            label="JSON"
            icon={isExportFormatAvailable('json') ? 'pi pi-check' : 'pi pi-times'}
            onClick={() => toggleExportFormat('json', !isExportFormatAvailable('json'))}
            className={isExportFormatAvailable('json') ? 'p-button-success' : 'p-button-secondary'}
          />
        </div>
      </div>

      <Divider />

      <div className="demo-section">
        <h4>Available Export Buttons</h4>
        <div className="export-buttons">
          {availableExportFormats.map(format => (
            <Button
              key={format}
              label={`Export as ${format.toUpperCase()}`}
              icon="pi pi-download"
              onClick={() => alert(`Exporting as ${format.toUpperCase()}`)}
              className="p-button-outlined"
            />
          ))}
        </div>
        {availableExportFormats.length === 0 && (
          <Message severity="info" text="No export formats are currently available. Enable formats using the toggle buttons above." />
        )}
      </div>
    </Card>
  );

  // Theme Toggle Demo
  const ThemeToggleDemo = () => (
    <Card title="UI Theme Toggles" className="demo-card">
      <div className="demo-section">
        <h4>Toggle Controls</h4>
        <div className="toggle-buttons">
          <Button
            label="Light Theme"
            icon={isThemeAvailable('light') ? 'pi pi-sun' : 'pi pi-times'}
            onClick={() => toggleTheme('light', !isThemeAvailable('light'))}
            className={isThemeAvailable('light') ? 'p-button-success' : 'p-button-secondary'}
          />
          <Button
            label="Dark Theme"
            icon={isThemeAvailable('dark') ? 'pi pi-moon' : 'pi pi-times'}
            onClick={() => toggleTheme('dark', !isThemeAvailable('dark'))}
            className={isThemeAvailable('dark') ? 'p-button-success' : 'p-button-secondary'}
          />
          <Button
            label="High Contrast"
            icon={isThemeAvailable('high_contrast') ? 'pi pi-eye' : 'pi pi-times'}
            onClick={() => toggleTheme('high_contrast', !isThemeAvailable('high_contrast'))}
            className={isThemeAvailable('high_contrast') ? 'p-button-success' : 'p-button-secondary'}
          />
        </div>
      </div>

      <Divider />

      <div className="demo-section">
        <h4>Available Themes</h4>
        <div className="theme-list">
          {availableThemes.map(theme => (
            <div key={theme} className="theme-item">
              <i className="pi pi-palette" />
              <span>{theme.replace('_', ' ').toUpperCase()}</span>
            </div>
          ))}
        </div>
        {availableThemes.length === 0 && (
          <Message severity="info" text="No themes are currently available. Enable themes using the toggle buttons above." />
        )}
      </div>
    </Card>
  );

  // Language Toggle Demo
  const LanguageToggleDemo = () => (
    <Card title="Language Toggles" className="demo-card">
      <div className="demo-section">
        <h4>Toggle Controls</h4>
        <div className="toggle-buttons">
          <Button
            label="Deutsch"
            icon={isLanguageAvailable('de') ? 'pi pi-check' : 'pi pi-times'}
            onClick={() => toggleLanguage('de', !isLanguageAvailable('de'))}
            className={isLanguageAvailable('de') ? 'p-button-success' : 'p-button-secondary'}
          />
          <Button
            label="English"
            icon={isLanguageAvailable('en') ? 'pi pi-check' : 'pi pi-times'}
            onClick={() => toggleLanguage('en', !isLanguageAvailable('en'))}
            className={isLanguageAvailable('en') ? 'p-button-success' : 'p-button-secondary'}
          />
          <Button
            label="Français"
            icon={isLanguageAvailable('fr') ? 'pi pi-check' : 'pi pi-times'}
            onClick={() => toggleLanguage('fr', !isLanguageAvailable('fr'))}
            className={isLanguageAvailable('fr') ? 'p-button-success' : 'p-button-secondary'}
          />
          <Button
            label="Español"
            icon={isLanguageAvailable('es') ? 'pi pi-check' : 'pi pi-times'}
            onClick={() => toggleLanguage('es', !isLanguageAvailable('es'))}
            className={isLanguageAvailable('es') ? 'p-button-success' : 'p-button-secondary'}
          />
        </div>
      </div>

      <Divider />

      <div className="demo-section">
        <h4>Available Languages</h4>
        <div className="language-list">
          {availableLanguages.map(lang => (
            <div key={lang} className="language-item">
              <i className="pi pi-globe" />
              <span>{lang.toUpperCase()}</span>
            </div>
          ))}
        </div>
        {availableLanguages.length === 0 && (
          <Message severity="info" text="No languages are currently available. Enable languages using the toggle buttons above." />
        )}
      </div>
    </Card>
  );

  if (loading) {
    return (
      <div className="demo-loading">
        <i className="pi pi-spin pi-spinner" style={{ fontSize: '3rem' }} />
        <p>Loading component toggles...</p>
      </div>
    );
  }

  return (
    <div className="component-toggles-demo">
      <h1>Component Toggles Demo</h1>
      <p className="demo-description">
        This demo showcases the component-level feature toggle system. Use the toggle buttons
        to enable or disable different components and see the changes in real-time.
      </p>

      {error && (
        <Message severity="error" text={error} className="demo-error" />
      )}

      <div className="demo-grid">
        <ChartToggleDemo />
        <ExportFormatToggleDemo />
        <ThemeToggleDemo />
        <LanguageToggleDemo />
      </div>

      <style>{`
        .component-toggles-demo {
          padding: 2rem;
          max-width: 1400px;
          margin: 0 auto;
        }

        .component-toggles-demo h1 {
          color: var(--text-color);
          margin-bottom: 0.5rem;
        }

        .demo-description {
          color: var(--text-color-secondary);
          margin-bottom: 2rem;
          font-size: 1.1rem;
        }

        .demo-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
          gap: 2rem;
        }

        .demo-card {
          height: 100%;
        }

        .demo-section {
          margin-bottom: 1.5rem;
        }

        .demo-section h4 {
          color: var(--text-color);
          margin-bottom: 1rem;
        }

        .toggle-buttons {
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
        }

        .charts-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
        }

        .chart-container {
          padding: 1rem;
          border: 1px solid var(--surface-border);
          border-radius: 6px;
          background: var(--surface-card);
        }

        .chart-container h5 {
          margin: 0 0 1rem 0;
          color: var(--text-color);
        }

        .export-buttons {
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
        }

        .theme-list,
        .language-list {
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .theme-item,
        .language-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1rem;
          background: var(--surface-100);
          border-radius: 6px;
          color: var(--text-color);
        }

        .demo-loading {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 4rem;
          gap: 1rem;
        }

        .demo-loading p {
          color: var(--text-color-secondary);
          font-size: 1.1rem;
        }

        .demo-error {
          margin-bottom: 2rem;
        }

        @media (max-width: 768px) {
          .demo-grid {
            grid-template-columns: 1fr;
          }

          .toggle-buttons {
            flex-direction: column;
          }

          .toggle-buttons button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};
