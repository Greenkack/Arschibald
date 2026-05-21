/**
 * PDF Emailer Component
 * 
 * Handles sending PDF via email with customizable message
 */

import React, { useState } from 'react';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Toast } from 'primereact/toast';
import { Chips } from 'primereact/chips';
import { Message } from 'primereact/message';
import api from '../../services/api';
import './PDFEmailer.css';

interface PDFEmailerProps {
  pdfData?: string; // Base64 encoded PDF
  storedFilename?: string;
  defaultRecipient?: string;
  defaultSubject?: string;
  className?: string;
  buttonLabel?: string;
  buttonIcon?: string;
  buttonClassName?: string;
}

interface EmailForm {
  recipients: string[];
  subject: string;
  message: string;
  cc: string[];
  bcc: string[];
}

export const PDFEmailer: React.FC<PDFEmailerProps> = ({
  pdfData,
  storedFilename,
  defaultRecipient = '',
  defaultSubject = 'Your PDF Document',
  className = '',
  buttonLabel = 'Email PDF',
  buttonIcon = 'pi pi-envelope',
  buttonClassName = '',
}) => {
  const [showDialog, setShowDialog] = useState(false);
  const [sending, setSending] = useState(false);
  const [formData, setFormData] = useState<EmailForm>({
    recipients: defaultRecipient ? [defaultRecipient] : [],
    subject: defaultSubject,
    message: 'Please find the attached PDF document.',
    cc: [],
    bcc: [],
  });
  const [showAdvanced, setShowAdvanced] = useState(false);
  const toastRef = React.useRef<Toast>(null);

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validateForm = (): string | null => {
    if (formData.recipients.length === 0) {
      return 'Please add at least one recipient';
    }

    const invalidRecipients = formData.recipients.filter(email => !validateEmail(email));
    if (invalidRecipients.length > 0) {
      return `Invalid email addresses: ${invalidRecipients.join(', ')}`;
    }

    if (!formData.subject.trim()) {
      return 'Please enter a subject';
    }

    if (!formData.message.trim()) {
      return 'Please enter a message';
    }

    return null;
  };

  const handleSend = async () => {
    const validationError = validateForm();
    if (validationError) {
      toastRef.current?.show({
        severity: 'warn',
        summary: 'Validation Error',
        detail: validationError,
        life: 4000,
      });
      return;
    }

    setSending(true);

    try {
      // Prepare email data
      const emailData = {
        recipients: formData.recipients,
        subject: formData.subject,
        message: formData.message,
        cc: formData.cc,
        bcc: formData.bcc,
        pdf_data: pdfData,
        stored_filename: storedFilename,
      };

      // Send email via API
      await api.post('/api/v1/email/send-pdf', emailData);

      toastRef.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: `Email sent to ${formData.recipients.length} recipient(s)`,
        life: 4000,
      });

      setShowDialog(false);
      
      // Reset form
      setFormData({
        recipients: defaultRecipient ? [defaultRecipient] : [],
        subject: defaultSubject,
        message: 'Please find the attached PDF document.',
        cc: [],
        bcc: [],
      });
    } catch (error: any) {
      console.error('Email error:', error);
      toastRef.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.detail || 'Failed to send email',
        life: 4000,
      });
    } finally {
      setSending(false);
    }
  };

  const dialogFooter = (
    <div className="email-dialog-footer">
      <Button
        label="Cancel"
        icon="pi pi-times"
        onClick={() => setShowDialog(false)}
        className="p-button-text"
        disabled={sending}
      />
      <Button
        label="Send Email"
        icon="pi pi-send"
        onClick={handleSend}
        loading={sending}
        className="p-button-success"
      />
    </div>
  );

  return (
    <div className={`pdf-emailer ${className}`}>
      <Toast ref={toastRef} />

      <Button
        label={buttonLabel}
        icon={buttonIcon}
        onClick={() => setShowDialog(true)}
        className={buttonClassName}
        disabled={!pdfData && !storedFilename}
      />

      <Dialog
        visible={showDialog}
        onHide={() => setShowDialog(false)}
        header="📧 Email PDF"
        footer={dialogFooter}
        className="email-dialog"
        style={{ width: '600px' }}
        modal
      >
        <div className="email-dialog-content">
          <Message
            severity="info"
            text="The PDF will be attached to the email automatically"
            className="email-info-message"
          />

          <div className="form-section">
            <label htmlFor="recipients" className="form-label required">
              To
            </label>
            <Chips
              id="recipients"
              value={formData.recipients}
              onChange={(e) => setFormData({ ...formData, recipients: e.value || [] })}
              placeholder="Enter email addresses and press Enter"
              className="w-full"
              separator=","
            />
            <small className="form-hint">
              Press Enter or comma to add multiple recipients
            </small>
          </div>

          <div className="form-section">
            <label htmlFor="subject" className="form-label required">
              Subject
            </label>
            <InputText
              id="subject"
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              placeholder="Enter email subject"
              className="w-full"
            />
          </div>

          <div className="form-section">
            <label htmlFor="message" className="form-label required">
              Message
            </label>
            <InputTextarea
              id="message"
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              placeholder="Enter your message"
              rows={5}
              className="w-full"
            />
          </div>

          <div className="advanced-toggle">
            <Button
              label={showAdvanced ? 'Hide Advanced Options' : 'Show Advanced Options'}
              icon={showAdvanced ? 'pi pi-chevron-up' : 'pi pi-chevron-down'}
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="p-button-text p-button-sm"
            />
          </div>

          {showAdvanced && (
            <div className="advanced-options">
              <div className="form-section">
                <label htmlFor="cc" className="form-label">
                  CC
                </label>
                <Chips
                  id="cc"
                  value={formData.cc}
                  onChange={(e) => setFormData({ ...formData, cc: e.value || [] })}
                  placeholder="Enter CC email addresses"
                  className="w-full"
                  separator=","
                />
              </div>

              <div className="form-section">
                <label htmlFor="bcc" className="form-label">
                  BCC
                </label>
                <Chips
                  id="bcc"
                  value={formData.bcc}
                  onChange={(e) => setFormData({ ...formData, bcc: e.value || [] })}
                  placeholder="Enter BCC email addresses"
                  className="w-full"
                  separator=","
                />
              </div>
            </div>
          )}
        </div>
      </Dialog>
    </div>
  );
};
