/**
 * PDF Configuration Manager Component
 * Comprehensive UI for configuring all PDF options
 */

import React, { useState, useEffect } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { Button } from 'primereact/button';
import { Dropdown } from 'primereact/dropdown';
import { InputSwitch } from 'primereact/inputswitch';
import { InputNumber } from 'primereact/inputnumber';
import { InputText } from 'primereact/inputtext';
import { Slider } from 'primereact/slider';
import { ColorPicker } from 'primereact/colorpicker';
import { MultiSelect } from 'primereact/multiselect';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Panel } from 'primereact/panel';
import { Message } from 'primereact/message';
import { ProgressBar } from 'primereact/progressbar';
import { Dialog } from 'primereact/dialog';
import './PDFConfigurationManager.css';

interface PDFConfigurationManagerProps {
  projectId?: number;
  onConfigurationSaved?: (configId: string) => void;
  onPDFGenerated?: (pdfUrl: string) => void;
}

type PDFType = 'standard_pv' | 'extended_pv' | 'standard_wp' | 'extended_wp' | 'multi_pdf';
type ComponentType = 'diagram' | 'calculation' | 'document' | 'image' | 'datasheet' | 'table' | 'chart' | 'text';
type ColorScheme = 'default' | 'blue' | 'green' | 'orange' | 'purple' | 'custom';
type FontFamily = 'Helvetica' | 'Times-Roman' | 'Courier' | 'Arial' | 'Verdana';

interface PageConfig {
  page_number: number;
  enabled: boolean;
  components: string[];
  custom_header?: string;
  custom_footer?: string;
}

interface ComponentConfig {
  component_id: string;
  component_type: ComponentType;
  enabled: boolean;
  page: number;
  position: { x: number; y: number };
  size?: { width: number; height: number };
  data_source?: string;
  options: Record<string, any>;
}

interface CompanySelection {
  company_id: number;
  company_name: string;
  logo_path?: string;
  logo_position?: any;
  color_scheme?: ColorScheme;
  custom_colors?: Record<string, string>;
}

interface PDFConfiguration {
  pdf_type: PDFType;
  project_id?: number;
  pages: PageConfig[];
  components: ComponentConfig[];
  color_scheme: ColorScheme;
  custom_colors?: Record<string, string>;
  font_family: FontFamily;
  font_size_base: number;
  logo_positions: Record<number, any>;
  watermark?: {
    enabled: boolean;
    text: string;
    opacity: number;
    rotation: number;
    font_size: number;
    color: string;
  };
  companies: CompanySelection[];
  product_rotation?: {
    enabled: boolean;
    avoid_duplicate_brands: boolean;
    avoid_duplicate_products: boolean;
    rotation_strategy: string;
    product_categories: string[];
  };
  price_increase?: {
    enabled: boolean;
    increase_percentage: number;
    apply_to_base_price: boolean;
    compound_increases: boolean;
    min_price?: number;
    max_price?: number;
  };
  include_3d_visualization: boolean;
  include_charts: boolean;
  include_calculations: boolean;
  include_datasheets: boolean;
  include_documents: boolean;
  compress_pdf: boolean;
  pdf_version: string;
}

export const PDFConfigurationManager: React.FC<PDFConfigurationManagerProps> = ({
  projectId,
  onConfigurationSaved,
  onPDFGenerated
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [configuration, setConfiguration] = useState<PDFConfiguration>({
    pdf_type: 'standard_pv',
    project_id: projectId,
    pages: [],
    components: [],
    color_scheme: 'default',
    font_family: 'Helvetica',
    font_size_base: 10,
    logo_positions: {},
    companies: [],
    include_3d_visualization: true,
    include_charts: true,
    include_calculations: true,
    include_datasheets: false,
    include_documents: false,
    compress_pdf: true,
    pdf_version: '1.7'
  });
  
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [validationWarnings, setValidationWarnings] = useState<string[]>([]);
  const [estimatedSize, setEstimatedSize] = useState<number>(0);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [previewImage, setPreviewImage] = useState<string>('');
  const [generating, setGenerating] = useState(false);
  const [configId, setConfigId] = useState<string>('');

  const pdfTypeOptions = [
    { label: 'Standard PV PDF (8 Seiten)', value: 'standard_pv' },
    { label: 'Erweiterte PV PDF (8+ Seiten)', value: 'extended_pv' },
    { label: 'Standard WP PDF (8 Seiten)', value: 'standard_wp' },
    { label: 'Erweiterte WP PDF (8+ Seiten)', value: 'extended_wp' },
    { label: 'Multi-PDF (Mehrere Firmen)', value: 'multi_pdf' }
  ];

  const colorSchemeOptions = [
    { label: 'Standard', value: 'default' },
    { label: 'Blau', value: 'blue' },
    { label: 'Grün', value: 'green' },
    { label: 'Orange', value: 'orange' },
    { label: 'Lila', value: 'purple' },
    { label: 'Benutzerdefiniert', value: 'custom' }
  ];

  const fontFamilyOptions = [
    { label: 'Helvetica', value: 'Helvetica' },
    { label: 'Times Roman', value: 'Times-Roman' },
    { label: 'Courier', value: 'Courier' },
    { label: 'Arial', value: 'Arial' },
    { label: 'Verdana', value: 'Verdana' }
  ];

  useEffect(() => {
    // Load default configuration when PDF type changes
    loadDefaultConfiguration();
  }, [configuration.pdf_type]);

  const loadDefaultConfiguration = async () => {
    try {
      const response = await fetch(`/api/v1/pdf-configuration/defaults/${configuration.pdf_type}`);
      if (response.ok) {
        const defaultConfig = await response.json();
        setConfiguration(prev => ({
          ...prev,
          pages: defaultConfig.pages,
          components: defaultConfig.components
        }));
      }
    } catch (error) {
      console.error('Error loading default configuration:', error);
    }
  };

  const validateConfiguration = async () => {
    try {
      const response = await fetch('/api/v1/pdf-configuration/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(configuration)
      });
      
      if (response.ok) {
        const result = await response.json();
        setConfigId(result.config_id);
        setValidationErrors(result.validation_errors || []);
        setValidationWarnings(result.validation_warnings || []);
        setEstimatedSize(result.estimated_size_mb || 0);
        
        if (onConfigurationSaved && result.validation_errors.length === 0) {
          onConfigurationSaved(result.config_id);
        }
        
        return result.validation_errors.length === 0;
      }
    } catch (error) {
      console.error('Error validating configuration:', error);
      return false;
    }
  };

  const generatePreview = async (pageNumber: number) => {
    if (!configId) {
      await validateConfiguration();
    }
    
    try {
      const response = await fetch('/api/v1/pdf-configuration/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          config_id: configId,
          page_number: pageNumber,
          resolution: 150
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setPreviewImage(`data:image/png;base64,${result.preview_image_base64}`);
        setPreviewVisible(true);
      }
    } catch (error) {
      console.error('Error generating preview:', error);
    }
  };

  const generatePDF = async () => {
    const isValid = await validateConfiguration();
    if (!isValid) {
      return;
    }
    
    setGenerating(true);
    try {
      const response = await fetch('/api/v1/pdf-configuration/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          config_id: configId,
          output_format: 'pdf',
          filename: `angebot_${Date.now()}.pdf`
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        if (onPDFGenerated && result.pdf_url) {
          onPDFGenerated(result.pdf_url);
        }
      }
    } catch (error) {
      console.error('Error generating PDF:', error);
    } finally {
      setGenerating(false);
    }
  };

  const renderBasicSettings = () => (
    <div className="pdf-config-section">
      <h3>Grundeinstellungen</h3>
      
      <div className="p-field">
        <label htmlFor="pdf-type">PDF-Typ</label>
        <Dropdown
          id="pdf-type"
          value={configuration.pdf_type}
          options={pdfTypeOptions}
          onChange={(e) => setConfiguration({ ...configuration, pdf_type: e.value })}
          placeholder="PDF-Typ auswählen"
        />
      </div>

      <div className="p-field">
        <label htmlFor="color-scheme">Farbschema</label>
        <Dropdown
          id="color-scheme"
          value={configuration.color_scheme}
          options={colorSchemeOptions}
          onChange={(e) => setConfiguration({ ...configuration, color_scheme: e.value })}
        />
      </div>

      <div className="p-field">
        <label htmlFor="font-family">Schriftart</label>
        <Dropdown
          id="font-family"
          value={configuration.font_family}
          options={fontFamilyOptions}
          onChange={(e) => setConfiguration({ ...configuration, font_family: e.value })}
        />
      </div>

      <div className="p-field">
        <label htmlFor="font-size">Basis-Schriftgröße: {configuration.font_size_base}pt</label>
        <Slider
          id="font-size"
          value={configuration.font_size_base}
          onChange={(e) => setConfiguration({ ...configuration, font_size_base: e.value as number })}
          min={6}
          max={20}
        />
      </div>
    </div>
  );

  const renderPageConfiguration = () => (
    <div className="pdf-config-section">
      <h3>Seiten-Konfiguration</h3>
      
      <DataTable value={configuration.pages} responsiveLayout="scroll">
        <Column field="page_number" header="Seite" />
        <Column
          field="enabled"
          header="Aktiviert"
          body={(rowData) => (
            <InputSwitch
              checked={rowData.enabled}
              onChange={(e) => {
                const updatedPages = configuration.pages.map(p =>
                  p.page_number === rowData.page_number ? { ...p, enabled: e.value } : p
                );
                setConfiguration({ ...configuration, pages: updatedPages });
              }}
            />
          )}
        />
        <Column
          header="Vorschau"
          body={(rowData) => (
            <Button
              icon="pi pi-eye"
              className="p-button-sm p-button-text"
              onClick={() => generatePreview(rowData.page_number)}
              disabled={!rowData.enabled}
            />
          )}
        />
      </DataTable>
    </div>
  );

  const renderComponentSelection = () => (
    <div className="pdf-config-section">
      <h3>Komponenten-Auswahl</h3>
      
      <div className="p-field-checkbox">
        <InputSwitch
          id="include-3d"
          checked={configuration.include_3d_visualization}
          onChange={(e) => setConfiguration({ ...configuration, include_3d_visualization: e.value })}
        />
        <label htmlFor="include-3d">3D-Visualisierung einschließen</label>
      </div>

      <div className="p-field-checkbox">
        <InputSwitch
          id="include-charts"
          checked={configuration.include_charts}
          onChange={(e) => setConfiguration({ ...configuration, include_charts: e.value })}
        />
        <label htmlFor="include-charts">Diagramme einschließen</label>
      </div>

      <div className="p-field-checkbox">
        <InputSwitch
          id="include-calculations"
          checked={configuration.include_calculations}
          onChange={(e) => setConfiguration({ ...configuration, include_calculations: e.value })}
        />
        <label htmlFor="include-calculations">Detaillierte Berechnungen einschließen</label>
      </div>

      <div className="p-field-checkbox">
        <InputSwitch
          id="include-datasheets"
          checked={configuration.include_datasheets}
          onChange={(e) => setConfiguration({ ...configuration, include_datasheets: e.value })}
        />
        <label htmlFor="include-datasheets">Produktdatenblätter einschließen</label>
      </div>

      <div className="p-field-checkbox">
        <InputSwitch
          id="include-documents"
          checked={configuration.include_documents}
          onChange={(e) => setConfiguration({ ...configuration, include_documents: e.value })}
        />
        <label htmlFor="include-documents">Zusätzliche Dokumente einschließen</label>
      </div>
    </div>
  );

  const renderMultiPDFSettings = () => {
    if (configuration.pdf_type !== 'multi_pdf') {
      return null;
    }

    return (
      <div className="pdf-config-section">
        <h3>Multi-PDF Einstellungen</h3>
        
        <Panel header="Firmen-Auswahl" toggleable>
          <p>Wählen Sie die Firmen aus, für die Angebote erstellt werden sollen.</p>
          {/* Company selection would go here */}
        </Panel>

        <Panel header="Produktrotation" toggleable collapsed>
          <div className="p-field-checkbox">
            <InputSwitch
              id="product-rotation"
              checked={configuration.product_rotation?.enabled || false}
              onChange={(e) => setConfiguration({
                ...configuration,
                product_rotation: {
                  ...configuration.product_rotation,
                  enabled: e.value,
                  avoid_duplicate_brands: true,
                  avoid_duplicate_products: true,
                  rotation_strategy: 'sequential',
                  product_categories: []
                }
              })}
            />
            <label htmlFor="product-rotation">Produktrotation aktivieren</label>
          </div>

          {configuration.product_rotation?.enabled && (
            <>
              <div className="p-field-checkbox">
                <InputSwitch
                  id="avoid-brands"
                  checked={configuration.product_rotation.avoid_duplicate_brands}
                  onChange={(e) => setConfiguration({
                    ...configuration,
                    product_rotation: {
                      ...configuration.product_rotation!,
                      avoid_duplicate_brands: e.value
                    }
                  })}
                />
                <label htmlFor="avoid-brands">Marken-Duplikate vermeiden</label>
              </div>

              <div className="p-field-checkbox">
                <InputSwitch
                  id="avoid-products"
                  checked={configuration.product_rotation.avoid_duplicate_products}
                  onChange={(e) => setConfiguration({
                    ...configuration,
                    product_rotation: {
                      ...configuration.product_rotation!,
                      avoid_duplicate_products: e.value
                    }
                  })}
                />
                <label htmlFor="avoid-products">Produkt-Duplikate vermeiden</label>
              </div>
            </>
          )}
        </Panel>

        <Panel header="Preiserhöhung" toggleable collapsed>
          <div className="p-field-checkbox">
            <InputSwitch
              id="price-increase"
              checked={configuration.price_increase?.enabled || false}
              onChange={(e) => setConfiguration({
                ...configuration,
                price_increase: {
                  ...configuration.price_increase,
                  enabled: e.value,
                  increase_percentage: 7.0,
                  apply_to_base_price: true,
                  compound_increases: true
                }
              })}
            />
            <label htmlFor="price-increase">Preiserhöhung aktivieren</label>
          </div>

          {configuration.price_increase?.enabled && (
            <div className="p-field">
              <label htmlFor="increase-percentage">
                Erhöhung: {configuration.price_increase.increase_percentage}%
              </label>
              <Slider
                id="increase-percentage"
                value={configuration.price_increase.increase_percentage}
                onChange={(e) => setConfiguration({
                  ...configuration,
                  price_increase: {
                    ...configuration.price_increase!,
                    increase_percentage: e.value as number
                  }
                })}
                min={0}
                max={50}
                step={0.5}
              />
            </div>
          )}
        </Panel>
      </div>
    );
  };

  const renderWatermarkSettings = () => (
    <div className="pdf-config-section">
      <h3>Wasserzeichen</h3>
      
      <div className="p-field-checkbox">
        <InputSwitch
          id="watermark-enabled"
          checked={configuration.watermark?.enabled || false}
          onChange={(e) => setConfiguration({
            ...configuration,
            watermark: {
              ...configuration.watermark,
              enabled: e.value,
              text: configuration.watermark?.text || 'ENTWURF',
              opacity: configuration.watermark?.opacity || 0.1,
              rotation: configuration.watermark?.rotation || 45,
              font_size: configuration.watermark?.font_size || 60,
              color: configuration.watermark?.color || '#CCCCCC'
            }
          })}
        />
        <label htmlFor="watermark-enabled">Wasserzeichen aktivieren</label>
      </div>

      {configuration.watermark?.enabled && (
        <>
          <div className="p-field">
            <label htmlFor="watermark-text">Text</label>
            <InputText
              id="watermark-text"
              value={configuration.watermark.text}
              onChange={(e) => setConfiguration({
                ...configuration,
                watermark: { ...configuration.watermark!, text: e.target.value }
              })}
            />
          </div>

          <div className="p-field">
            <label htmlFor="watermark-opacity">Deckkraft: {configuration.watermark.opacity}</label>
            <Slider
              id="watermark-opacity"
              value={configuration.watermark.opacity}
              onChange={(e) => setConfiguration({
                ...configuration,
                watermark: { ...configuration.watermark!, opacity: e.value as number }
              })}
              min={0}
              max={1}
              step={0.05}
            />
          </div>
        </>
      )}
    </div>
  );

  const renderValidationResults = () => {
    if (validationErrors.length === 0 && validationWarnings.length === 0) {
      return null;
    }

    return (
      <div className="pdf-config-validation">
        {validationErrors.map((error, index) => (
          <Message key={`error-${index}`} severity="error" text={error} />
        ))}
        {validationWarnings.map((warning, index) => (
          <Message key={`warning-${index}`} severity="warn" text={warning} />
        ))}
      </div>
    );
  };

  return (
    <div className="pdf-configuration-manager">
      <div className="pdf-config-header">
        <h2>PDF-Konfiguration</h2>
        <div className="pdf-config-actions">
          <Button
            label="Validieren"
            icon="pi pi-check"
            onClick={validateConfiguration}
            className="p-button-secondary"
          />
          <Button
            label="PDF Generieren"
            icon="pi pi-file-pdf"
            onClick={generatePDF}
            loading={generating}
            disabled={validationErrors.length > 0}
          />
        </div>
      </div>

      {renderValidationResults()}

      {estimatedSize > 0 && (
        <div className="pdf-config-info">
          <Message
            severity="info"
            text={`Geschätzte PDF-Größe: ${estimatedSize.toFixed(2)} MB`}
          />
        </div>
      )}

      <TabView activeIndex={activeTab} onTabChange={(e) => setActiveTab(e.index)}>
        <TabPanel header="Grundeinstellungen">
          {renderBasicSettings()}
        </TabPanel>

        <TabPanel header="Seiten">
          {renderPageConfiguration()}
        </TabPanel>

        <TabPanel header="Komponenten">
          {renderComponentSelection()}
        </TabPanel>

        <TabPanel header="Multi-PDF">
          {renderMultiPDFSettings()}
        </TabPanel>

        <TabPanel header="Wasserzeichen">
          {renderWatermarkSettings()}
        </TabPanel>
      </TabView>

      <Dialog
        header="PDF-Vorschau"
        visible={previewVisible}
        style={{ width: '80vw' }}
        onHide={() => setPreviewVisible(false)}
      >
        {previewImage && (
          <img src={previewImage} alt="PDF Preview" style={{ width: '100%' }} />
        )}
      </Dialog>
    </div>
  );
};
