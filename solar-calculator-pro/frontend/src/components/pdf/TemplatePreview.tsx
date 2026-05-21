/**
 * PDF Template Preview Component
 * 
 * Displays a preview of a PDF template with zoom and navigation controls.
 * Supports both image previews and actual PDF rendering.
 */

import React, { useState, useEffect } from 'react';
import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import { Slider } from 'primereact/slider';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Message } from 'primereact/message';
import api from '../../services/api';
import { PDFTemplate } from './TemplateGallery';
import './TemplatePreview.css';

interface TemplatePreviewProps {
  template: PDFTemplate | null;
  visible: boolean;
  onHide: () => void;
  projectData?: any;
}

export const TemplatePreview: React.FC<TemplatePreviewProps> = ({
  template,
  visible,
  onHide,
  projectData
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [zoom, setZoom] = useState(100);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    if (visible && template) {
      loadPreview();
    }
    
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [visible, template]);

  const loadPreview = async () => {
    if (!template) return;

    try {
      setLoading(true);
      setError(null);

      // Generate preview PDF with sample data or provided project data
      const response = await api.post(
        '/api/v1/pdf/preview',
        {
          template: template.name,
          project_data: projectData || getSampleProjectData(),
          page_limit: 3 // Preview first 3 pages only
        },
        {
          responseType: 'blob'
        }
      );

      // Create object URL for PDF blob
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      setPreviewUrl(url);
      setTotalPages(3); // Preview is limited to 3 pages
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load preview');
    } finally {
      setLoading(false);
    }
  };

  const getSampleProjectData = () => {
    return {
      customer_name: 'Max Mustermann',
      project_name: 'Solar Installation Preview',
      system_size: 10.5,
      module_count: 30,
      annual_production: 12000,
      total_cost: 25000,
      payback_period: 8.5
    };
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 25, 200));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 25, 50));
  };

  const handleResetZoom = () => {
    setZoom(100);
  };

  const handlePreviousPage = () => {
    setCurrentPage(prev => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages));
  };

  const renderHeader = () => (
    <div className="template-preview-header">
      <div className="template-preview-title">
        <i className="pi pi-file-pdf"></i>
        <span>{template?.display_name} - Preview</span>
      </div>
      <div className="template-preview-controls">
        <Button
          icon="pi pi-minus"
          onClick={handleZoomOut}
          className="p-button-text p-button-sm"
          tooltip="Zoom Out"
          tooltipOptions={{ position: 'bottom' }}
          disabled={zoom <= 50}
        />
        <span className="zoom-level">{zoom}%</span>
        <Button
          icon="pi pi-plus"
          onClick={handleZoomIn}
          className="p-button-text p-button-sm"
          tooltip="Zoom In"
          tooltipOptions={{ position: 'bottom' }}
          disabled={zoom >= 200}
        />
        <Button
          icon="pi pi-refresh"
          onClick={handleResetZoom}
          className="p-button-text p-button-sm"
          tooltip="Reset Zoom"
          tooltipOptions={{ position: 'bottom' }}
        />
      </div>
    </div>
  );

  const renderFooter = () => (
    <div className="template-preview-footer">
      <div className="page-navigation">
        <Button
          icon="pi pi-chevron-left"
          onClick={handlePreviousPage}
          className="p-button-text"
          disabled={currentPage === 1}
        />
        <span className="page-info">
          Page {currentPage} of {totalPages}
        </span>
        <Button
          icon="pi pi-chevron-right"
          onClick={handleNextPage}
          className="p-button-text"
          disabled={currentPage === totalPages}
        />
      </div>
      <div className="preview-actions">
        <Button
          label="Refresh Preview"
          icon="pi pi-refresh"
          onClick={loadPreview}
          className="p-button-outlined"
        />
        <Button
          label="Close"
          icon="pi pi-times"
          onClick={onHide}
          className="p-button-secondary"
        />
      </div>
    </div>
  );

  const renderContent = () => {
    if (loading) {
      return (
        <div className="preview-loading">
          <ProgressSpinner />
          <p>Generating preview...</p>
        </div>
      );
    }

    if (error) {
      return (
        <Message 
          severity="error" 
          text={error}
          className="w-full"
        />
      );
    }

    if (!previewUrl) {
      return (
        <Message 
          severity="info" 
          text="No preview available"
          className="w-full"
        />
      );
    }

    return (
      <div className="preview-container">
        <div 
          className="preview-content"
          style={{ transform: `scale(${zoom / 100})` }}
        >
          <iframe
            src={`${previewUrl}#page=${currentPage}`}
            className="pdf-preview-iframe"
            title="PDF Preview"
          />
        </div>
      </div>
    );
  };

  return (
    <Dialog
      visible={visible}
      onHide={onHide}
      header={renderHeader()}
      footer={renderFooter()}
      className="template-preview-dialog"
      maximizable
      style={{ width: '90vw', height: '90vh' }}
    >
      {renderContent()}
    </Dialog>
  );
};
