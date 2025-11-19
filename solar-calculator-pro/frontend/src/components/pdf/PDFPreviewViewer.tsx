/**
 * PDF Preview Viewer Component
 * 
 * Displays PDF preview in browser using PDF.js or iframe
 * Supports zoom, page navigation, and full-screen mode
 */

import React, { useState, useEffect } from 'react';
import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import { Slider } from 'primereact/slider';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Message } from 'primereact/message';
import './PDFPreviewViewer.css';

interface PDFPreviewViewerProps {
  pdfData: string | null; // Base64 encoded PDF
  visible: boolean;
  onHide: () => void;
  title?: string;
  onDownload?: () => void;
  onEmail?: () => void;
}

export const PDFPreviewViewer: React.FC<PDFPreviewViewerProps> = ({
  pdfData,
  visible,
  onHide,
  title = 'PDF Preview',
  onDownload,
  onEmail,
}) => {
  const [zoom, setZoom] = useState(100);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

  useEffect(() => {
    if (pdfData && visible) {
      try {
        // Convert base64 to blob URL
        const binaryString = atob(pdfData);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        const blob = new Blob([bytes], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);
        setPdfUrl(url);
        setError(null);
      } catch (err) {
        setError('Failed to load PDF preview');
        console.error('PDF loading error:', err);
      }
    }

    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [pdfData, visible]);

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 25, 200));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 25, 50));
  };

  const handleResetZoom = () => {
    setZoom(100);
  };

  const handleFullScreen = () => {
    if (pdfUrl) {
      window.open(pdfUrl, '_blank');
    }
  };

  const renderToolbar = () => (
    <div className="pdf-preview-toolbar">
      <div className="toolbar-section">
        <Button
          icon="pi pi-search-minus"
          onClick={handleZoomOut}
          className="p-button-text"
          tooltip="Zoom Out"
          disabled={zoom <= 50}
        />
        <span className="zoom-level">{zoom}%</span>
        <Button
          icon="pi pi-search-plus"
          onClick={handleZoomIn}
          className="p-button-text"
          tooltip="Zoom In"
          disabled={zoom >= 200}
        />
        <Button
          icon="pi pi-refresh"
          onClick={handleResetZoom}
          className="p-button-text"
          tooltip="Reset Zoom"
        />
      </div>

      <div className="toolbar-section">
        <Button
          icon="pi pi-window-maximize"
          onClick={handleFullScreen}
          className="p-button-text"
          tooltip="Full Screen"
          disabled={!pdfUrl}
        />
        {onDownload && (
          <Button
            icon="pi pi-download"
            onClick={onDownload}
            className="p-button-text"
            tooltip="Download PDF"
          />
        )}
        {onEmail && (
          <Button
            icon="pi pi-envelope"
            onClick={onEmail}
            className="p-button-text"
            tooltip="Email PDF"
          />
        )}
      </div>
    </div>
  );

  const renderContent = () => {
    if (loading) {
      return (
        <div className="pdf-preview-loading">
          <ProgressSpinner />
          <p>Loading PDF preview...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="pdf-preview-error">
          <Message severity="error" text={error} />
        </div>
      );
    }

    if (!pdfUrl) {
      return (
        <div className="pdf-preview-empty">
          <i className="pi pi-file-pdf" style={{ fontSize: '4rem', color: '#ccc' }}></i>
          <p>No PDF to preview</p>
        </div>
      );
    }

    return (
      <div className="pdf-preview-content" style={{ transform: `scale(${zoom / 100})` }}>
        <iframe
          src={pdfUrl}
          title="PDF Preview"
          className="pdf-iframe"
          style={{ width: '100%', height: '100%', border: 'none' }}
        />
      </div>
    );
  };

  const footer = (
    <div className="pdf-preview-footer">
      <Button
        label="Close"
        icon="pi pi-times"
        onClick={onHide}
        className="p-button-text"
      />
    </div>
  );

  return (
    <Dialog
      visible={visible}
      onHide={onHide}
      header={title}
      footer={footer}
      className="pdf-preview-dialog"
      style={{ width: '90vw', height: '90vh' }}
      maximizable
      modal
    >
      {renderToolbar()}
      {renderContent()}
    </Dialog>
  );
};
