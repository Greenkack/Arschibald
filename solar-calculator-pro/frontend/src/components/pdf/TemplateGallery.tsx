/**
 * PDF Template Gallery Component
 * 
 * Displays available PDF templates in a gallery view with preview cards.
 * Allows users to browse and select templates for PDF generation.
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { Badge } from 'primereact/badge';
import { Skeleton } from 'primereact/skeleton';
import { Message } from 'primereact/message';
import api from '../../services/api';
import './TemplateGallery.css';

export interface PDFTemplate {
  name: string;
  display_name: string;
  description: string;
  preview_image?: string;
  is_custom?: boolean;
  created_at?: string;
  file_size?: number;
}

interface TemplateGalleryProps {
  onSelectTemplate: (template: PDFTemplate) => void;
  selectedTemplate?: PDFTemplate;
  onPreviewTemplate?: (template: PDFTemplate) => void;
}

export const TemplateGallery: React.FC<TemplateGalleryProps> = ({
  onSelectTemplate,
  selectedTemplate,
  onPreviewTemplate
}) => {
  const [templates, setTemplates] = useState<PDFTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/api/v1/pdf/templates');
      setTemplates(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTemplate = (template: PDFTemplate) => {
    onSelectTemplate(template);
  };

  const handlePreviewTemplate = (template: PDFTemplate, e: React.MouseEvent) => {
    e.stopPropagation();
    if (onPreviewTemplate) {
      onPreviewTemplate(template);
    }
  };

  const renderTemplateCard = (template: PDFTemplate) => {
    const isSelected = selectedTemplate?.name === template.name;

    const header = (
      <div className="template-card-header">
        {template.preview_image ? (
          <img 
            src={template.preview_image} 
            alt={template.display_name}
            className="template-preview-image"
          />
        ) : (
          <div className="template-preview-placeholder">
            <i className="pi pi-file-pdf" style={{ fontSize: '3rem' }}></i>
          </div>
        )}
        {template.is_custom && (
          <Badge 
            value="Custom" 
            severity="info" 
            className="template-badge"
          />
        )}
        {isSelected && (
          <Badge 
            value="Selected" 
            severity="success" 
            className="template-badge-selected"
          />
        )}
      </div>
    );

    const footer = (
      <div className="template-card-footer">
        <Button
          label={isSelected ? "Selected" : "Select"}
          icon={isSelected ? "pi pi-check" : "pi pi-arrow-right"}
          onClick={() => handleSelectTemplate(template)}
          className={isSelected ? "p-button-success" : "p-button-primary"}
          disabled={isSelected}
        />
        {onPreviewTemplate && (
          <Button
            label="Preview"
            icon="pi pi-eye"
            onClick={(e) => handlePreviewTemplate(template, e)}
            className="p-button-outlined"
          />
        )}
      </div>
    );

    return (
      <Card
        key={template.name}
        title={template.display_name}
        subTitle={template.description}
        header={header}
        footer={footer}
        className={`template-card ${isSelected ? 'template-card-selected' : ''}`}
      >
        <div className="template-card-content">
          {template.created_at && (
            <div className="template-meta">
              <i className="pi pi-calendar"></i>
              <span>{new Date(template.created_at).toLocaleDateString('de-DE')}</span>
            </div>
          )}
          {template.file_size && (
            <div className="template-meta">
              <i className="pi pi-file"></i>
              <span>{(template.file_size / 1024).toFixed(2)} KB</span>
            </div>
          )}
        </div>
      </Card>
    );
  };

  const renderSkeleton = () => (
    <div className="template-gallery-grid">
      {[1, 2, 3].map((i) => (
        <Card key={i} className="template-card">
          <Skeleton width="100%" height="200px" className="mb-3" />
          <Skeleton width="80%" height="1.5rem" className="mb-2" />
          <Skeleton width="100%" height="1rem" className="mb-3" />
          <Skeleton width="100%" height="2.5rem" />
        </Card>
      ))}
    </div>
  );

  if (loading) {
    return renderSkeleton();
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

  if (templates.length === 0) {
    return (
      <Message 
        severity="info" 
        text="No templates available. Upload a custom template to get started."
        className="w-full"
      />
    );
  }

  return (
    <div className="template-gallery">
      <div className="template-gallery-header">
        <h3>📄 PDF Templates</h3>
        <p className="text-muted">Select a template for your PDF generation</p>
      </div>
      
      <div className="template-gallery-grid">
        {templates.map(renderTemplateCard)}
      </div>
    </div>
  );
};
