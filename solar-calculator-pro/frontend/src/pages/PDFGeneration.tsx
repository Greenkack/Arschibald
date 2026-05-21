/**
 * PDF Generation Page
 * 
 * Main page for PDF template selection and generation.
 * Integrates all PDF-related components.
 */

import React, { useState } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { TemplateGallery, PDFTemplate } from '../components/pdf/TemplateGallery';
import { TemplatePreview } from '../components/pdf/TemplatePreview';
import { TemplateUpload } from '../components/pdf/TemplateUpload';
import { TemplateManagement } from '../components/pdf/TemplateManagement';
import { PDFConfigurationComponent, PDFConfiguration } from '../components/pdf/PDFConfiguration';
import { PDFPreviewViewer } from '../components/pdf/PDFPreviewViewer';
import { PDFGenerator } from '../components/pdf/PDFGenerator';
import { PDFDownloader } from '../components/pdf/PDFDownloader';
import { PDFEmailer } from '../components/pdf/PDFEmailer';
import { PDFHistory } from '../components/pdf/PDFHistory';
import './PDFGeneration.css';

export const PDFGeneration: React.FC = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<PDFTemplate | null>(null);
  const [previewTemplate, setPreviewTemplate] = useState<PDFTemplate | null>(null);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [uploadVisible, setUploadVisible] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [refreshKey, setRefreshKey] = useState(0);
  const [showConfiguration, setShowConfiguration] = useState(false);
  const [pdfConfig, setPdfConfig] = useState<PDFConfiguration | null>(null);
  const [generatedPDF, setGeneratedPDF] = useState<string | null>(null);
  const [pdfPreviewVisible, setPdfPreviewVisible] = useState(false);
  const [showGenerator, setShowGenerator] = useState(false);
  const [projectData, setProjectData] = useState<any>(null);

  const handleSelectTemplate = (template: PDFTemplate) => {
    setSelectedTemplate(template);
  };

  const handlePreviewTemplate = (template: PDFTemplate) => {
    setPreviewTemplate(template);
    setPreviewVisible(true);
  };

  const handleUploadSuccess = () => {
    setRefreshKey(prev => prev + 1);
  };

  const handleTemplateChange = () => {
    setRefreshKey(prev => prev + 1);
  };

  const handleConfigureTemplate = () => {
    if (selectedTemplate) {
      setShowConfiguration(true);
    }
  };

  const handleConfigChange = (config: PDFConfiguration) => {
    setPdfConfig(config);
  };

  const handleGeneratePDF = async (config: PDFConfiguration) => {
    console.log('Generating PDF with config:', config);
    setPdfConfig(config);
    setShowConfiguration(false);
    setShowGenerator(true);
    
    // Set project data from config
    setProjectData({
      customer_name: config.customerName || 'Customer',
      ...config,
    });
  };

  const handleCancelConfiguration = () => {
    setShowConfiguration(false);
  };

  const handlePDFGenerated = (pdfData: string) => {
    setGeneratedPDF(pdfData);
    setPdfPreviewVisible(true);
  };

  const handlePDFError = (error: string) => {
    console.error('PDF generation error:', error);
  };

  const handlePreviewFromHistory = (filename: string) => {
    // Load PDF from server and show preview
    // This would require an API call to get the PDF data
    console.log('Preview PDF from history:', filename);
  };

  const renderHeader = () => (
    <div className="pdf-page-header">
      <div className="header-content">
        <h1>📄 PDF Generation</h1>
        <p className="header-subtitle">
          Select a template, customize your PDF, and generate professional documents
        </p>
      </div>
      <div className="header-actions">
        <Button
          label="Upload Template"
          icon="pi pi-upload"
          onClick={() => setUploadVisible(true)}
          className="p-button-outlined"
        />
      </div>
    </div>
  );

  const renderSelectionSummary = () => {
    if (!selectedTemplate) return null;

    return (
      <Card className="selection-summary">
        <div className="summary-content">
          <div className="summary-icon">
            <i className="pi pi-check-circle"></i>
          </div>
          <div className="summary-details">
            <h4>Selected Template</h4>
            <p className="template-name">{selectedTemplate.display_name}</p>
            <p className="template-description">{selectedTemplate.description}</p>
          </div>
          <div className="summary-actions">
            <Button
              label="Preview"
              icon="pi pi-eye"
              onClick={() => handlePreviewTemplate(selectedTemplate)}
              className="p-button-outlined"
            />
            <Button
              label="Configure & Generate"
              icon="pi pi-cog"
              onClick={handleConfigureTemplate}
              className="p-button-success"
            />
          </div>
        </div>
      </Card>
    );
  };

  return (
    <div className="pdf-generation-page">
      {!showConfiguration && renderHeader()}

      {!showConfiguration && renderSelectionSummary()}

      {showConfiguration && selectedTemplate ? (
        <PDFConfigurationComponent
          template={selectedTemplate}
          onConfigChange={handleConfigChange}
          onGenerate={handleGeneratePDF}
          onCancel={handleCancelConfiguration}
        />
      ) : showGenerator && selectedTemplate ? (
        <div className="pdf-generator-view">
          <div className="generator-header">
            <Button
              label="Back to Templates"
              icon="pi pi-arrow-left"
              onClick={() => setShowGenerator(false)}
              className="p-button-text"
            />
          </div>
          
          <div className="generator-content-wrapper">
            <PDFGenerator
              projectData={projectData}
              template={selectedTemplate.name}
              onSuccess={handlePDFGenerated}
              onError={handlePDFError}
            />

            {generatedPDF && (
              <Card className="pdf-actions-card">
                <h4>📄 PDF Generated Successfully!</h4>
                <p>Your PDF is ready. What would you like to do?</p>
                <div className="pdf-action-buttons">
                  <Button
                    label="Preview PDF"
                    icon="pi pi-eye"
                    onClick={() => setPdfPreviewVisible(true)}
                    className="p-button-lg"
                  />
                  <PDFDownloader
                    pdfData={generatedPDF}
                    filename={`${projectData?.customer_name || 'document'}.pdf`}
                    buttonLabel="Download PDF"
                    buttonClassName="p-button-lg p-button-success"
                  />
                  <PDFEmailer
                    pdfData={generatedPDF}
                    defaultRecipient={projectData?.customer_email}
                    defaultSubject={`PDF Document for ${projectData?.customer_name}`}
                    buttonLabel="Email PDF"
                    buttonClassName="p-button-lg p-button-info"
                  />
                </div>
              </Card>
            )}
          </div>
        </div>
      ) : (
        <div className="pdf-content">
        <TabView 
          activeIndex={activeTab} 
          onTabChange={(e) => setActiveTab(e.index)}
          className="pdf-tabs"
        >
          <TabPanel header="📚 Template Gallery" leftIcon="pi pi-th-large">
            <div className="tab-content">
              <TemplateGallery
                key={`gallery-${refreshKey}`}
                onSelectTemplate={handleSelectTemplate}
                selectedTemplate={selectedTemplate || undefined}
                onPreviewTemplate={handlePreviewTemplate}
              />
            </div>
          </TabPanel>

          <TabPanel header="⚙️ Template Management" leftIcon="pi pi-cog">
            <div className="tab-content">
              <TemplateManagement
                key={`management-${refreshKey}`}
                onTemplateChange={handleTemplateChange}
              />
            </div>
          </TabPanel>

          <TabPanel header="📚 PDF History" leftIcon="pi pi-history">
            <div className="tab-content">
              <PDFHistory onPreview={handlePreviewFromHistory} />
            </div>
          </TabPanel>

          <TabPanel header="📖 Help & Documentation" leftIcon="pi pi-question-circle">
            <div className="tab-content">
              <Card className="help-card">
                <h3>🎯 Getting Started</h3>
                <ol className="help-list">
                  <li>
                    <strong>Select a Template:</strong> Browse the template gallery and choose a template that fits your needs.
                  </li>
                  <li>
                    <strong>Preview Template:</strong> Click the "Preview" button to see how the template looks with sample data.
                  </li>
                  <li>
                    <strong>Generate PDF:</strong> Once you've selected a template, click "Generate PDF" to create your document.
                  </li>
                  <li>
                    <strong>Upload Custom Templates:</strong> Click "Upload Template" to add your own custom PDF templates.
                  </li>
                </ol>

                <h3>📝 Template Types</h3>
                <div className="template-types">
                  <div className="type-card">
                    <i className="pi pi-file-pdf"></i>
                    <h4>Main Template</h4>
                    <p>Full-featured PDF with all sections and visualizations</p>
                  </div>
                  <div className="type-card">
                    <i className="pi pi-file"></i>
                    <h4>Simple Template</h4>
                    <p>Simplified PDF with essential information only</p>
                  </div>
                  <div className="type-card">
                    <i className="pi pi-file-excel"></i>
                    <h4>Extended Template</h4>
                    <p>Extended PDF with detailed analysis and charts</p>
                  </div>
                </div>

                <h3>🔧 Custom Templates</h3>
                <p>
                  You can upload custom templates in the following formats:
                </p>
                <ul className="help-list">
                  <li><strong>PDF:</strong> Static PDF templates that will be used as-is</li>
                  <li><strong>HTML:</strong> Dynamic HTML templates with placeholder support</li>
                  <li><strong>JSON:</strong> Template definitions with structure and styling</li>
                </ul>

                <h3>💡 Tips & Best Practices</h3>
                <ul className="help-list">
                  <li>Use placeholders like {`{{customer_name}}`} for dynamic content in HTML templates</li>
                  <li>Keep template file sizes under 10MB for optimal performance</li>
                  <li>Preview templates before generating final PDFs</li>
                  <li>Set a default template for quick access</li>
                  <li>Organize templates with clear names and descriptions</li>
                </ul>
              </Card>
            </div>
          </TabPanel>
        </TabView>
        </div>
      )}

      <TemplatePreview
        template={previewTemplate}
        visible={previewVisible}
        onHide={() => setPreviewVisible(false)}
      />

      <TemplateUpload
        visible={uploadVisible}
        onHide={() => setUploadVisible(false)}
        onUploadSuccess={handleUploadSuccess}
      />

      <PDFPreviewViewer
        pdfData={generatedPDF}
        visible={pdfPreviewVisible}
        onHide={() => setPdfPreviewVisible(false)}
        title="PDF Preview"
        onDownload={() => {
          // Download handled by PDFDownloader component
        }}
        onEmail={() => {
          // Email handled by PDFEmailer component
        }}
      />
    </div>
  );
};
