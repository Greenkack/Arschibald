/**
 * PDF Configuration Component
 * 
 * Comprehensive PDF configuration interface with:
 * - PDF options form
 * - Logo upload and positioning
 * - Color scheme selection
 * - Content section toggles
 * - Custom text fields
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dropdown } from 'primereact/dropdown';
import { ColorPicker } from 'primereact/colorpicker';
import { Checkbox } from 'primereact/checkbox';
import { Slider } from 'primereact/slider';
import { FileUpload, FileUploadHandlerEvent } from 'primereact/fileupload';
import { TabView, TabPanel } from 'primereact/tabview';
import { Message } from 'primereact/message';
import { ProgressSpinner } from 'primereact/progressspinner';
import { PDFTemplate } from './TemplateGallery';
import './PDFConfiguration.css';

export interface LogoPosition {
  x: number;
  y: number;
  width: number;
  height: number;
  alignment: 'left' | 'center' | 'right';
}

export interface ColorScheme {
  primary: string;
  secondary: string;
  accent: string;
  text: string;
  background: string;
}

export interface ContentSection {
  id: string;
  name: string;
  enabled: boolean;
  order: number;
}

export interface CustomTextField {
  id: string;
  label: string;
  value: string;
  placeholder: string;
}

export interface PDFConfiguration {
  template_id: number;
  logo_url?: string;
  logo_position: LogoPosition;
  color_scheme: ColorScheme;
  content_sections: ContentSection[];
  custom_fields: CustomTextField[];
  page_size: 'A4' | 'Letter' | 'Legal';
  orientation: 'portrait' | 'landscape';
  margins: {
    top: number;
    right: number;
    bottom: number;
    left: number;
  };
  header_text?: string;
  footer_text?: string;
  show_page_numbers: boolean;
  show_date: boolean;
  show_logo: boolean;
}

interface PDFConfigurationProps {
  template: PDFTemplate;
  initialConfig?: Partial<PDFConfiguration>;
  onConfigChange?: (config: PDFConfiguration) => void;
  onGenerate?: (config: PDFConfiguration) => void;
  onCancel?: () => void;
}

export const PDFConfigurationComponent: React.FC<PDFConfigurationProps> = ({
  template,
  initialConfig,
  onConfigChange,
  onGenerate,
  onCancel,
}) => {
  const [config, setConfig] = useState<PDFConfiguration>({
    template_id: template.id,
    logo_position: {
      x: 50,
      y: 20,
      width: 100,
      height: 50,
      alignment: 'left',
    },
    color_scheme: {
      primary: '#2196F3',
      secondary: '#FFC107',
      accent: '#4CAF50',
      text: '#333333',
      background: '#FFFFFF',
    },
    content_sections: [
      { id: 'summary', name: 'Executive Summary', enabled: true, order: 1 },
      { id: 'calculations', name: 'Calculations & Results', enabled: true, order: 2 },
      { id: 'charts', name: 'Charts & Visualizations', enabled: true, order: 3 },
      { id: 'technical', name: 'Technical Details', enabled: true, order: 4 },
      { id: 'financial', name: 'Financial Analysis', enabled: true, order: 5 },
      { id: 'recommendations', name: 'Recommendations', enabled: true, order: 6 },
    ],
    custom_fields: [
      { id: 'company_name', label: 'Company Name', value: '', placeholder: 'Enter company name' },
      { id: 'project_name', label: 'Project Name', value: '', placeholder: 'Enter project name' },
      { id: 'customer_name', label: 'Customer Name', value: '', placeholder: 'Enter customer name' },
      { id: 'notes', label: 'Additional Notes', value: '', placeholder: 'Enter any additional notes' },
    ],
    page_size: 'A4',
    orientation: 'portrait',
    margins: {
      top: 20,
      right: 20,
      bottom: 20,
      left: 20,
    },
    show_page_numbers: true,
    show_date: true,
    show_logo: true,
    ...initialConfig,
  });

  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (onConfigChange) {
      onConfigChange(config);
    }
  }, [config, onConfigChange]);

  const updateConfig = (updates: Partial<PDFConfiguration>) => {
    setConfig(prev => ({ ...prev, ...updates }));
  };

  const updateLogoPosition = (updates: Partial<LogoPosition>) => {
    setConfig(prev => ({
      ...prev,
      logo_position: { ...prev.logo_position, ...updates },
    }));
  };

  const updateColorScheme = (updates: Partial<ColorScheme>) => {
    setConfig(prev => ({
      ...prev,
      color_scheme: { ...prev.color_scheme, ...updates },
    }));
  };

  const updateMargins = (updates: Partial<PDFConfiguration['margins']>) => {
    setConfig(prev => ({
      ...prev,
      margins: { ...prev.margins, ...updates },
    }));
  };

  const toggleSection = (sectionId: string) => {
    setConfig(prev => ({
      ...prev,
      content_sections: prev.content_sections.map(section =>
        section.id === sectionId
          ? { ...section, enabled: !section.enabled }
          : section
      ),
    }));
  };

  const updateCustomField = (fieldId: string, value: string) => {
    setConfig(prev => ({
      ...prev,
      custom_fields: prev.custom_fields.map(field =>
        field.id === fieldId ? { ...field, value } : field
      ),
    }));
  };

  const handleLogoUpload = (event: FileUploadHandlerEvent) => {
    const file = event.files[0];
    if (file) {
      setLogoFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        setLogoPreview(result);
        updateConfig({ logo_url: result });
      };
      reader.readAsDataURL(file);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      if (onGenerate) {
        await onGenerate(config);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const pageSizeOptions = [
    { label: 'A4 (210 × 297 mm)', value: 'A4' },
    { label: 'Letter (8.5 × 11 in)', value: 'Letter' },
    { label: 'Legal (8.5 × 14 in)', value: 'Legal' },
  ];

  const orientationOptions = [
    { label: 'Portrait', value: 'portrait', icon: 'pi pi-mobile' },
    { label: 'Landscape', value: 'landscape', icon: 'pi pi-tablet' },
  ];

  const alignmentOptions = [
    { label: 'Left', value: 'left', icon: 'pi pi-align-left' },
    { label: 'Center', value: 'center', icon: 'pi pi-align-center' },
    { label: 'Right', value: 'right', icon: 'pi pi-align-right' },
  ];

  return (
    <div className="pdf-configuration">
      <div className="configuration-header">
        <div className="header-info">
          <h2>📝 Configure PDF</h2>
          <p className="template-name">Template: {template.display_name}</p>
        </div>
        <div className="header-actions">
          <Button
            label="Cancel"
            icon="pi pi-times"
            onClick={onCancel}
            className="p-button-text"
            disabled={isGenerating}
          />
          <Button
            label={isGenerating ? 'Generating...' : 'Generate PDF'}
            icon={isGenerating ? 'pi pi-spin pi-spinner' : 'pi pi-file-pdf'}
            onClick={handleGenerate}
            className="p-button-success"
            disabled={isGenerating}
          />
        </div>
      </div>

      <TabView className="configuration-tabs">
        {/* General Options Tab */}
        <TabPanel header="⚙️ General Options" leftIcon="pi pi-cog">
          <Card className="config-card">
            <h3>📄 Page Settings</h3>
            <div className="form-grid">
              <div className="form-field">
                <label htmlFor="page-size">Page Size</label>
                <Dropdown
                  id="page-size"
                  value={config.page_size}
                  options={pageSizeOptions}
                  onChange={(e) => updateConfig({ page_size: e.value })}
                  className="w-full"
                />
              </div>

              <div className="form-field">
                <label htmlFor="orientation">Orientation</label>
                <div className="orientation-buttons">
                  {orientationOptions.map(option => (
                    <Button
                      key={option.value}
                      label={option.label}
                      icon={option.icon}
                      onClick={() => updateConfig({ orientation: option.value as any })}
                      className={config.orientation === option.value ? 'p-button-primary' : 'p-button-outlined'}
                    />
                  ))}
                </div>
              </div>
            </div>

            <h3>📏 Margins (mm)</h3>
            <div className="margins-grid">
              <div className="form-field">
                <label htmlFor="margin-top">Top</label>
                <InputText
                  id="margin-top"
                  type="number"
                  value={config.margins.top.toString()}
                  onChange={(e) => updateMargins({ top: parseInt(e.target.value) || 0 })}
                />
              </div>
              <div className="form-field">
                <label htmlFor="margin-right">Right</label>
                <InputText
                  id="margin-right"
                  type="number"
                  value={config.margins.right.toString()}
                  onChange={(e) => updateMargins({ right: parseInt(e.target.value) || 0 })}
                />
              </div>
              <div className="form-field">
                <label htmlFor="margin-bottom">Bottom</label>
                <InputText
                  id="margin-bottom"
                  type="number"
                  value={config.margins.bottom.toString()}
                  onChange={(e) => updateMargins({ bottom: parseInt(e.target.value) || 0 })}
                />
              </div>
              <div className="form-field">
                <label htmlFor="margin-left">Left</label>
                <InputText
                  id="margin-left"
                  type="number"
                  value={config.margins.left.toString()}
                  onChange={(e) => updateMargins({ left: parseInt(e.target.value) || 0 })}
                />
              </div>
            </div>

            <h3>🔢 Display Options</h3>
            <div className="checkbox-group">
              <div className="checkbox-item">
                <Checkbox
                  inputId="show-page-numbers"
                  checked={config.show_page_numbers}
                  onChange={(e) => updateConfig({ show_page_numbers: e.checked || false })}
                />
                <label htmlFor="show-page-numbers">Show Page Numbers</label>
              </div>
              <div className="checkbox-item">
                <Checkbox
                  inputId="show-date"
                  checked={config.show_date}
                  onChange={(e) => updateConfig({ show_date: e.checked || false })}
                />
                <label htmlFor="show-date">Show Generation Date</label>
              </div>
              <div className="checkbox-item">
                <Checkbox
                  inputId="show-logo"
                  checked={config.show_logo}
                  onChange={(e) => updateConfig({ show_logo: e.checked || false })}
                />
                <label htmlFor="show-logo">Show Logo</label>
              </div>
            </div>
          </Card>
        </TabPanel>

        {/* Logo & Branding Tab */}
        <TabPanel header="🎨 Logo & Branding" leftIcon="pi pi-image">
          <Card className="config-card">
            <h3>📷 Logo Upload</h3>
            <div className="logo-upload-section">
              <FileUpload
                mode="basic"
                name="logo"
                accept="image/*"
                maxFileSize={5000000}
                customUpload
                uploadHandler={handleLogoUpload}
                chooseLabel="Choose Logo"
                className="logo-upload-button"
              />
              {logoPreview && (
                <div className="logo-preview">
                  <img src={logoPreview} alt="Logo Preview" />
                  <Button
                    icon="pi pi-times"
                    className="p-button-rounded p-button-danger p-button-text remove-logo"
                    onClick={() => {
                      setLogoFile(null);
                      setLogoPreview(null);
                      updateConfig({ logo_url: undefined });
                    }}
                  />
                </div>
              )}
            </div>

            {config.show_logo && (
              <>
                <h3>📍 Logo Position</h3>
                <div className="form-grid">
                  <div className="form-field">
                    <label htmlFor="logo-x">X Position (mm)</label>
                    <Slider
                      id="logo-x"
                      value={config.logo_position.x}
                      onChange={(e) => updateLogoPosition({ x: e.value as number })}
                      min={0}
                      max={200}
                    />
                    <span className="slider-value">{config.logo_position.x} mm</span>
                  </div>

                  <div className="form-field">
                    <label htmlFor="logo-y">Y Position (mm)</label>
                    <Slider
                      id="logo-y"
                      value={config.logo_position.y}
                      onChange={(e) => updateLogoPosition({ y: e.value as number })}
                      min={0}
                      max={200}
                    />
                    <span className="slider-value">{config.logo_position.y} mm</span>
                  </div>

                  <div className="form-field">
                    <label htmlFor="logo-width">Width (mm)</label>
                    <Slider
                      id="logo-width"
                      value={config.logo_position.width}
                      onChange={(e) => updateLogoPosition({ width: e.value as number })}
                      min={20}
                      max={200}
                    />
                    <span className="slider-value">{config.logo_position.width} mm</span>
                  </div>

                  <div className="form-field">
                    <label htmlFor="logo-height">Height (mm)</label>
                    <Slider
                      id="logo-height"
                      value={config.logo_position.height}
                      onChange={(e) => updateLogoPosition({ height: e.value as number })}
                      min={20}
                      max={200}
                    />
                    <span className="slider-value">{config.logo_position.height} mm</span>
                  </div>
                </div>

                <div className="form-field">
                  <label>Alignment</label>
                  <div className="alignment-buttons">
                    {alignmentOptions.map(option => (
                      <Button
                        key={option.value}
                        icon={option.icon}
                        tooltip={option.label}
                        onClick={() => updateLogoPosition({ alignment: option.value as any })}
                        className={config.logo_position.alignment === option.value ? 'p-button-primary' : 'p-button-outlined'}
                      />
                    ))}
                  </div>
                </div>
              </>
            )}
          </Card>
        </TabPanel>

        {/* Color Scheme Tab */}
        <TabPanel header="🎨 Color Scheme" leftIcon="pi pi-palette">
          <Card className="config-card">
            <h3>🌈 Color Palette</h3>
            <Message
              severity="info"
              text="Choose colors that match your brand identity. These colors will be used throughout the PDF."
              className="color-info-message"
            />

            <div className="color-grid">
              <div className="color-field">
                <label htmlFor="color-primary">Primary Color</label>
                <div className="color-picker-wrapper">
                  <ColorPicker
                    id="color-primary"
                    value={config.color_scheme.primary}
                    onChange={(e) => updateColorScheme({ primary: `#${e.value}` })}
                  />
                  <InputText
                    value={config.color_scheme.primary}
                    onChange={(e) => updateColorScheme({ primary: e.target.value })}
                    className="color-input"
                  />
                  <div
                    className="color-preview"
                    style={{ backgroundColor: config.color_scheme.primary }}
                  />
                </div>
              </div>

              <div className="color-field">
                <label htmlFor="color-secondary">Secondary Color</label>
                <div className="color-picker-wrapper">
                  <ColorPicker
                    id="color-secondary"
                    value={config.color_scheme.secondary}
                    onChange={(e) => updateColorScheme({ secondary: `#${e.value}` })}
                  />
                  <InputText
                    value={config.color_scheme.secondary}
                    onChange={(e) => updateColorScheme({ secondary: e.target.value })}
                    className="color-input"
                  />
                  <div
                    className="color-preview"
                    style={{ backgroundColor: config.color_scheme.secondary }}
                  />
                </div>
              </div>

              <div className="color-field">
                <label htmlFor="color-accent">Accent Color</label>
                <div className="color-picker-wrapper">
                  <ColorPicker
                    id="color-accent"
                    value={config.color_scheme.accent}
                    onChange={(e) => updateColorScheme({ accent: `#${e.value}` })}
                  />
                  <InputText
                    value={config.color_scheme.accent}
                    onChange={(e) => updateColorScheme({ accent: e.target.value })}
                    className="color-input"
                  />
                  <div
                    className="color-preview"
                    style={{ backgroundColor: config.color_scheme.accent }}
                  />
                </div>
              </div>

              <div className="color-field">
                <label htmlFor="color-text">Text Color</label>
                <div className="color-picker-wrapper">
                  <ColorPicker
                    id="color-text"
                    value={config.color_scheme.text}
                    onChange={(e) => updateColorScheme({ text: `#${e.value}` })}
                  />
                  <InputText
                    value={config.color_scheme.text}
                    onChange={(e) => updateColorScheme({ text: e.target.value })}
                    className="color-input"
                  />
                  <div
                    className="color-preview"
                    style={{ backgroundColor: config.color_scheme.text }}
                  />
                </div>
              </div>

              <div className="color-field">
                <label htmlFor="color-background">Background Color</label>
                <div className="color-picker-wrapper">
                  <ColorPicker
                    id="color-background"
                    value={config.color_scheme.background}
                    onChange={(e) => updateColorScheme({ background: `#${e.value}` })}
                  />
                  <InputText
                    value={config.color_scheme.background}
                    onChange={(e) => updateColorScheme({ background: e.target.value })}
                    className="color-input"
                  />
                  <div
                    className="color-preview"
                    style={{ backgroundColor: config.color_scheme.background }}
                  />
                </div>
              </div>
            </div>
          </Card>
        </TabPanel>

        {/* Content Sections Tab */}
        <TabPanel header="📑 Content Sections" leftIcon="pi pi-list">
          <Card className="config-card">
            <h3>📋 Select Sections to Include</h3>
            <Message
              severity="info"
              text="Toggle sections on/off to customize what appears in your PDF. Drag to reorder sections."
              className="sections-info-message"
            />

            <div className="sections-list">
              {config.content_sections.map((section) => (
                <div key={section.id} className="section-item">
                  <div className="section-checkbox">
                    <Checkbox
                      inputId={`section-${section.id}`}
                      checked={section.enabled}
                      onChange={() => toggleSection(section.id)}
                    />
                  </div>
                  <div className="section-info">
                    <label htmlFor={`section-${section.id}`} className="section-name">
                      {section.name}
                    </label>
                    <span className="section-order">Order: {section.order}</span>
                  </div>
                  <div className="section-actions">
                    <Button
                      icon="pi pi-bars"
                      className="p-button-text p-button-sm drag-handle"
                      tooltip="Drag to reorder"
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabPanel>

        {/* Custom Fields Tab */}
        <TabPanel header="✏️ Custom Fields" leftIcon="pi pi-pencil">
          <Card className="config-card">
            <h3>📝 Custom Text Fields</h3>
            <Message
              severity="info"
              text="Add custom information that will appear in your PDF document."
              className="fields-info-message"
            />

            <div className="custom-fields-list">
              {config.custom_fields.map((field) => (
                <div key={field.id} className="custom-field">
                  <label htmlFor={`field-${field.id}`}>{field.label}</label>
                  {field.id === 'notes' ? (
                    <InputTextarea
                      id={`field-${field.id}`}
                      value={field.value}
                      onChange={(e) => updateCustomField(field.id, e.target.value)}
                      placeholder={field.placeholder}
                      rows={4}
                      className="w-full"
                    />
                  ) : (
                    <InputText
                      id={`field-${field.id}`}
                      value={field.value}
                      onChange={(e) => updateCustomField(field.id, e.target.value)}
                      placeholder={field.placeholder}
                      className="w-full"
                    />
                  )}
                </div>
              ))}
            </div>

            <h3>📄 Header & Footer</h3>
            <div className="header-footer-fields">
              <div className="form-field">
                <label htmlFor="header-text">Header Text</label>
                <InputText
                  id="header-text"
                  value={config.header_text || ''}
                  onChange={(e) => updateConfig({ header_text: e.target.value })}
                  placeholder="Enter header text (optional)"
                  className="w-full"
                />
              </div>

              <div className="form-field">
                <label htmlFor="footer-text">Footer Text</label>
                <InputText
                  id="footer-text"
                  value={config.footer_text || ''}
                  onChange={(e) => updateConfig({ footer_text: e.target.value })}
                  placeholder="Enter footer text (optional)"
                  className="w-full"
                />
              </div>
            </div>
          </Card>
        </TabPanel>
      </TabView>

      {isGenerating && (
        <div className="generating-overlay">
          <Card className="generating-card">
            <ProgressSpinner />
            <h3>Generating PDF...</h3>
            <p>Please wait while we create your document</p>
          </Card>
        </div>
      )}
    </div>
  );
};
