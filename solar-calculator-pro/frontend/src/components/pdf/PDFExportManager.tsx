/**
 * PDF Export Manager Component
 * Handles single and batch PDF downloads, email sending, and export management
 */

import React, { useState } from 'react';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Checkbox } from 'primereact/checkbox';
import { Toast } from 'primereact/toast';
import { ProgressBar } from 'primereact/progressbar';
import './PDFExportManager.css';

interface PDFExportManagerProps {
  pdfId?: number;
  pdfIds?: number[];
  onExportComplete?: (result: any) => void;
}

export const PDFExportManager: React.FC<PDFExportManagerProps> = ({
  pdfId,
  pdfIds,
  onExportComplete
}) => {
  const [showEmailDialog, setShowEmailDialog] = useState(false);
  const [emailData, setEmailData] = useState({
    recipient: '',
    subject: 'Your Solar Calculator PDF',
    body: 'Please find attached your solar calculator PDF document.',
    asZip: true
  });
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const toast = React.useRef<Toast>(null);

  const isBatch = pdfIds && pdfIds.length > 1;

  const handleDownload = async () => {
    setIsExporting(true);
    setExportProgress(0);

    try {
      const endpoint = isBatch ? '/api/v1/pdf-export/download/batch' : '/api/v1/pdf-export/download/single';
      const payload = isBatch 
        ? { pdf_ids: pdfIds }
        : { pdf_id: pdfId };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Download failed');
      }

      // Get filename from Content-Disposition header
      const contentDisposition = response.headers.get('Content-Disposition');
      const filenameMatch = contentDisposition?.match(/filename="(.+)"/);
      const filename = filenameMatch ? filenameMatch[1] : 'download.pdf';

      // Download file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setExportProgress(100);
      toast.current?.show({
        severity: 'success',
        summary: 'Download Complete',
        detail: `${filename} has been downloaded successfully`,
        life: 3000
      });

      if (onExportComplete) {
        onExportComplete({ success: true, filename });
      }

    } catch (error) {
      console.error('Download error:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Download Failed',
        detail: 'Failed to download PDF. Please try again.',
        life: 5000
      });
    } finally {
      setIsExporting(false);
      setExportProgress(0);
    }
  };

  const handleEmailSend = async () => {
    if (!emailData.recipient) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Email Required',
        detail: 'Please enter a recipient email address',
        life: 3000
      });
      return;
    }

    setIsExporting(true);

    try {
      const endpoint = isBatch ? '/api/v1/pdf-export/email/batch' : '/api/v1/pdf-export/email/single';
      const payload = isBatch
        ? {
            pdf_ids: pdfIds,
            recipient_email: emailData.recipient,
            subject: emailData.subject,
            body: emailData.body,
            as_zip: emailData.asZip
          }
        : {
            pdf_id: pdfId,
            recipient_email: emailData.recipient,
            subject: emailData.subject,
            body: emailData.body
          };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Email send failed');
      }

      const result = await response.json();

      toast.current?.show({
        severity: 'success',
        summary: 'Email Queued',
        detail: `Email to ${emailData.recipient} is being sent`,
        life: 3000
      });

      setShowEmailDialog(false);
      setEmailData({
        recipient: '',
        subject: 'Your Solar Calculator PDF',
        body: 'Please find attached your solar calculator PDF document.',
        asZip: true
      });

      if (onExportComplete) {
        onExportComplete({ success: true, ...result });
      }

    } catch (error) {
      console.error('Email send error:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Email Failed',
        detail: 'Failed to send email. Please try again.',
        life: 5000
      });
    } finally {
      setIsExporting(false);
    }
  };

  const handlePrint = async () => {
    setIsExporting(true);

    try {
      const response = await fetch('/api/v1/pdf-export/preview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ pdf_id: pdfId })
      });

      if (!response.ok) {
        throw new Error('Preview failed');
      }

      const result = await response.json();
      
      // Create blob from base64
      const byteCharacters = atob(result.preview_data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);

      // Open print dialog
      const printWindow = window.open(url, '_blank');
      if (printWindow) {
        printWindow.onload = () => {
          printWindow.print();
        };
      }

      toast.current?.show({
        severity: 'success',
        summary: 'Print Ready',
        detail: 'PDF opened for printing',
        life: 3000
      });

    } catch (error) {
      console.error('Print error:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Print Failed',
        detail: 'Failed to open PDF for printing',
        life: 5000
      });
    } finally {
      setIsExporting(false);
    }
  };

  const emailDialogFooter = (
    <div>
      <Button
        label="Cancel"
        icon="pi pi-times"
        onClick={() => setShowEmailDialog(false)}
        className="p-button-text"
        disabled={isExporting}
      />
      <Button
        label="Send Email"
        icon="pi pi-send"
        onClick={handleEmailSend}
        disabled={isExporting}
        loading={isExporting}
      />
    </div>
  );

  return (
    <div className="pdf-export-manager">
      <Toast ref={toast} />

      <div className="export-actions">
        <Button
          label={isBatch ? "Download ZIP" : "Download PDF"}
          icon="pi pi-download"
          onClick={handleDownload}
          disabled={isExporting}
          loading={isExporting}
          className="p-button-success"
        />

        <Button
          label="Send Email"
          icon="pi pi-envelope"
          onClick={() => setShowEmailDialog(true)}
          disabled={isExporting}
          className="p-button-info"
        />

        {!isBatch && (
          <Button
            label="Print"
            icon="pi pi-print"
            onClick={handlePrint}
            disabled={isExporting}
            className="p-button-secondary"
          />
        )}
      </div>

      {isExporting && exportProgress > 0 && (
        <div className="export-progress">
          <ProgressBar value={exportProgress} />
        </div>
      )}

      <Dialog
        header="Send PDF via Email"
        visible={showEmailDialog}
        style={{ width: '500px' }}
        footer={emailDialogFooter}
        onHide={() => setShowEmailDialog(false)}
      >
        <div className="email-form">
          <div className="p-field">
            <label htmlFor="recipient">Recipient Email *</label>
            <InputText
              id="recipient"
              value={emailData.recipient}
              onChange={(e) => setEmailData({ ...emailData, recipient: e.target.value })}
              placeholder="recipient@example.com"
              className="w-full"
              disabled={isExporting}
            />
          </div>

          <div className="p-field">
            <label htmlFor="subject">Subject</label>
            <InputText
              id="subject"
              value={emailData.subject}
              onChange={(e) => setEmailData({ ...emailData, subject: e.target.value })}
              className="w-full"
              disabled={isExporting}
            />
          </div>

          <div className="p-field">
            <label htmlFor="body">Message</label>
            <InputTextarea
              id="body"
              value={emailData.body}
              onChange={(e) => setEmailData({ ...emailData, body: e.target.value })}
              rows={5}
              className="w-full"
              disabled={isExporting}
            />
          </div>

          {isBatch && (
            <div className="p-field-checkbox">
              <Checkbox
                inputId="asZip"
                checked={emailData.asZip}
                onChange={(e) => setEmailData({ ...emailData, asZip: e.checked || false })}
                disabled={isExporting}
              />
              <label htmlFor="asZip">Send as ZIP file</label>
            </div>
          )}
        </div>
      </Dialog>
    </div>
  );
};
