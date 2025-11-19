/**
 * PDF Downloader Component
 * 
 * Handles PDF download functionality with various options
 */

import React, { useState } from 'react';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Dialog } from 'primereact/dialog';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import './PDFDownloader.css';

interface PDFDownloaderProps {
  pdfData?: string; // Base64 encoded PDF
  filename?: string;
  storedFilename?: string; // For downloading from server
  className?: string;
  buttonLabel?: string;
  buttonIcon?: string;
  buttonClassName?: string;
}

export const PDFDownloader: React.FC<PDFDownloaderProps> = ({
  pdfData,
  filename = 'document.pdf',
  storedFilename,
  className = '',
  buttonLabel = 'Download PDF',
  buttonIcon = 'pi pi-download',
  buttonClassName = '',
}) => {
  const [showDialog, setShowDialog] = useState(false);
  const [customFilename, setCustomFilename] = useState(filename);
  const [downloading, setDownloading] = useState(false);
  const toastRef = React.useRef<Toast>(null);

  const downloadFromBase64 = (data: string, name: string) => {
    try {
      // Convert base64 to blob
      const binaryString = atob(data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: 'application/pdf' });

      // Create download link
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = name.endsWith('.pdf') ? name : `${name}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toastRef.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'PDF downloaded successfully',
        life: 3000,
      });
    } catch (error) {
      console.error('Download error:', error);
      toastRef.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to download PDF',
        life: 3000,
      });
    }
  };

  const downloadFromServer = async (serverFilename: string, localFilename: string) => {
    try {
      setDownloading(true);

      const response = await api.get(`/api/v1/pdf/download/${serverFilename}`, {
        responseType: 'blob',
      });

      // Create download link from blob
      const url = URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.download = localFilename.endsWith('.pdf') ? localFilename : `${localFilename}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toastRef.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'PDF downloaded successfully',
        life: 3000,
      });
    } catch (error: any) {
      console.error('Download error:', error);
      toastRef.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.detail || 'Failed to download PDF',
        life: 3000,
      });
    } finally {
      setDownloading(false);
    }
  };

  const handleDownload = () => {
    if (pdfData) {
      downloadFromBase64(pdfData, customFilename);
      setShowDialog(false);
    } else if (storedFilename) {
      downloadFromServer(storedFilename, customFilename);
      setShowDialog(false);
    } else {
      toastRef.current?.show({
        severity: 'warn',
        summary: 'Warning',
        detail: 'No PDF data available',
        life: 3000,
      });
    }
  };

  const handleQuickDownload = () => {
    if (pdfData) {
      downloadFromBase64(pdfData, filename);
    } else if (storedFilename) {
      downloadFromServer(storedFilename, filename);
    } else {
      toastRef.current?.show({
        severity: 'warn',
        summary: 'Warning',
        detail: 'No PDF data available',
        life: 3000,
      });
    }
  };

  const dialogFooter = (
    <div className="download-dialog-footer">
      <Button
        label="Cancel"
        icon="pi pi-times"
        onClick={() => setShowDialog(false)}
        className="p-button-text"
        disabled={downloading}
      />
      <Button
        label="Download"
        icon="pi pi-download"
        onClick={handleDownload}
        loading={downloading}
        className="p-button-success"
      />
    </div>
  );

  return (
    <div className={`pdf-downloader ${className}`}>
      <Toast ref={toastRef} />

      <div className="downloader-buttons">
        <Button
          label={buttonLabel}
          icon={buttonIcon}
          onClick={handleQuickDownload}
          className={buttonClassName}
          disabled={!pdfData && !storedFilename}
          loading={downloading}
        />
        <Button
          icon="pi pi-cog"
          onClick={() => setShowDialog(true)}
          className="p-button-text"
          tooltip="Download Options"
          disabled={!pdfData && !storedFilename}
        />
      </div>

      <Dialog
        visible={showDialog}
        onHide={() => setShowDialog(false)}
        header="Download PDF"
        footer={dialogFooter}
        className="download-dialog"
        style={{ width: '450px' }}
        modal
      >
        <div className="download-dialog-content">
          <div className="dialog-section">
            <label htmlFor="filename" className="dialog-label">
              Filename
            </label>
            <InputText
              id="filename"
              value={customFilename}
              onChange={(e) => setCustomFilename(e.target.value)}
              placeholder="Enter filename"
              className="w-full"
            />
            <small className="dialog-hint">
              The .pdf extension will be added automatically
            </small>
          </div>

          <div className="dialog-section">
            <div className="info-box">
              <i className="pi pi-info-circle"></i>
              <div className="info-content">
                <p className="info-title">Download Information</p>
                <ul className="info-list">
                  <li>PDF will be saved to your default downloads folder</li>
                  <li>You can rename the file before downloading</li>
                  <li>The download will start immediately</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </Dialog>
    </div>
  );
};
