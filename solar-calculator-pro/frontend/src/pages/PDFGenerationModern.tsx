/**
 * Modern PDF Generation Page with shadcn/ui
 * 
 * Main page for PDF template selection and generation
 */

import React, { useState } from 'react';
import { FileText, Upload, Settings2, History, HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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

export const PDFGenerationModern: React.FC = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<PDFTemplate | null>(null);
  const [previewTemplate, setPreviewTemplate] = useState<PDFTemplate | null>(null);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [uploadVisible, setUploadVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('gallery');
  const [refreshKey, setRefreshKey] = useState(0);
  const [showConfiguration, setShowConfiguration] = useState(false);
  const [generatedPDF, setGeneratedPDF] = useState<string | null>(null);
  const [pdfPreviewVisible, setPdfPreviewVisible] = useState(false);
  const [showGenerator, setShowGenerator] = useState(false);
  const [projectData, setProjectData] = useState<Record<string, unknown> | null>(null);

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

  const handleGeneratePDF = async (config: PDFConfiguration) => {
    setShowConfiguration(false);
    setShowGenerator(true);
    
    setProjectData({
      customer_name: (config as Record<string, unknown>).customer_name || 'Customer',
      ...config,
    });
  };

  const handlePDFGenerated = (pdfData: string) => {
    setGeneratedPDF(pdfData);
    setPdfPreviewVisible(true);
  };

  const handlePDFError = (error: string) => {
    console.error('PDF generation error:', error);
  };

  const handlePreviewFromHistory = (filename: string) => {
    console.log('Preview PDF from history:', filename);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        {!showConfiguration && (
          <div className="mb-8 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight">PDF Generation</h1>
                <p className="text-muted-foreground">
                  Select a template, customize your PDF, and generate professional documents
                </p>
              </div>
            </div>
            <Button onClick={() => setUploadVisible(true)} size="lg">
              <Upload className="mr-2 h-5 w-5" />
              Upload Template
            </Button>
          </div>
        )}

        {/* Selection Summary */}
        {!showConfiguration && selectedTemplate && (
          <Card className="mb-6">
            <CardContent className="flex items-center justify-between p-6">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
                  <FileText className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <h4 className="font-semibold">Selected Template</h4>
                  <p className="text-lg font-bold">{selectedTemplate.display_name}</p>
                  <p className="text-sm text-muted-foreground">{selectedTemplate.description}</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => handlePreviewTemplate(selectedTemplate)}>
                  Preview
                </Button>
                <Button onClick={handleConfigureTemplate}>
                  <Settings2 className="mr-2 h-4 w-4" />
                  Configure & Generate
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Configuration View */}
        {showConfiguration && selectedTemplate ? (
          <PDFConfigurationComponent
            template={selectedTemplate}
            onConfigChange={setPdfConfig}
            onGenerate={handleGeneratePDF}
            onCancel={() => setShowConfiguration(false)}
          />
        ) : showGenerator && selectedTemplate ? (
          <div className="space-y-6">
            <Button variant="ghost" onClick={() => setShowGenerator(false)}>
              ← Back to Templates
            </Button>
            
            <PDFGenerator
              projectData={projectData}
              template={selectedTemplate.name}
              onSuccess={handlePDFGenerated}
              onError={handlePDFError}
            />

            {generatedPDF && (
              <Card>
                <CardHeader>
                  <CardTitle>PDF Generated Successfully!</CardTitle>
                  <CardDescription>Your PDF is ready. What would you like to do?</CardDescription>
                </CardHeader>
                <CardContent className="flex gap-4">
                  <Button onClick={() => setPdfPreviewVisible(true)} size="lg">
                    Preview PDF
                  </Button>
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
                </CardContent>
              </Card>
            )}
          </div>
        ) : (
          <Card>
            <CardContent className="p-6">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="gallery" className="gap-2">
                    <FileText className="h-4 w-4" />
                    Template Gallery
                  </TabsTrigger>
                  <TabsTrigger value="management" className="gap-2">
                    <Settings2 className="h-4 w-4" />
                    Management
                  </TabsTrigger>
                  <TabsTrigger value="history" className="gap-2">
                    <History className="h-4 w-4" />
                    PDF History
                  </TabsTrigger>
                  <TabsTrigger value="help" className="gap-2">
                    <HelpCircle className="h-4 w-4" />
                    Help
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="gallery" className="space-y-4">
                  <TemplateGallery
                    key={`gallery-${refreshKey}`}
                    onSelectTemplate={handleSelectTemplate}
                    selectedTemplate={selectedTemplate || undefined}
                    onPreviewTemplate={handlePreviewTemplate}
                  />
                </TabsContent>

                <TabsContent value="management" className="space-y-4">
                  <TemplateManagement
                    key={`management-${refreshKey}`}
                    onTemplateChange={handleTemplateChange}
                  />
                </TabsContent>

                <TabsContent value="history" className="space-y-4">
                  <PDFHistory onPreview={handlePreviewFromHistory} />
                </TabsContent>

                <TabsContent value="help" className="space-y-4">
                  <div className="grid gap-6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Getting Started</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <ol className="list-decimal list-inside space-y-2">
                          <li><strong>Select a Template:</strong> Browse the template gallery and choose a template that fits your needs.</li>
                          <li><strong>Preview Template:</strong> Click the "Preview" button to see how the template looks with sample data.</li>
                          <li><strong>Generate PDF:</strong> Once you've selected a template, click "Generate PDF" to create your document.</li>
                          <li><strong>Upload Custom Templates:</strong> Click "Upload Template" to add your own custom PDF templates.</li>
                        </ol>
                      </CardContent>
                    </Card>

                    <div className="grid gap-4 md:grid-cols-3">
                      <Card>
                        <CardHeader>
                          <FileText className="h-8 w-8 text-primary" />
                          <CardTitle>Main Template</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-sm text-muted-foreground">Full-featured PDF with all sections and visualizations</p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardHeader>
                          <FileText className="h-8 w-8 text-primary" />
                          <CardTitle>Simple Template</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-sm text-muted-foreground">Simplified PDF with essential information only</p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardHeader>
                          <FileText className="h-8 w-8 text-primary" />
                          <CardTitle>Extended Template</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p className="text-sm text-muted-foreground">Extended PDF with detailed analysis and charts</p>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
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
          onDownload={() => {}}
          onEmail={() => {}}
        />
      </div>
    </div>
  );
};
