/**
 * Email Integration Display Component
 * 
 * Displays email communications and provides email composition interface
 */

import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { FileUpload } from 'primereact/fileupload';
import { Toast } from 'primereact/toast';
import { Tag } from 'primereact/tag';
import { Chip } from 'primereact/chip';
import api from '../../services/api';
import './EmailIntegration.css';

interface Email {
  id: number;
  customer_id: number;
  title: string;
  content: string;
  created_at: string;
  created_by?: string;
  attachments?: string[];
  is_important: boolean;
}

interface EmailIntegrationProps {
  customerId: number;
  customerEmail?: string;
}

export const EmailIntegration: React.FC<EmailIntegrationProps> = ({ 
  customerId, 
  customerEmail 
}) => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(false);
  const [showComposeDialog, setShowComposeDialog] = useState(false);
  const [showViewDialog, setShowViewDialog] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [newEmail, setNewEmail] = useState({
    to: customerEmail || '',
    subject: '',
    body: '',
    attachments: [] as File[]
  });
  const toast = React.useRef<Toast>(null);

  useEffect(() => {
    loadEmails();
  }, [customerId]);

  useEffect(() => {
    if (customerEmail) {
      setNewEmail(prev => ({ ...prev, to: customerEmail }));
    }
  }, [customerEmail]);

  const loadEmails = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/crm/activities/customer/${customerId}`, {
        params: { activity_type: 'email' }
      });
      setEmails(response.data.activities || []);
    } catch (error) {
      console.error('Error loading emails:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load emails',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCompose = () => {
    setNewEmail({
      to: customerEmail || '',
      subject: '',
      body: '',
      attachments: []
    });
    setShowComposeDialog(true);
  };

  const handleSendEmail = async () => {
    if (!newEmail.to || !newEmail.subject || !newEmail.body) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Validation Error',
        detail: 'Please fill in all required fields',
        life: 3000
      });
      return;
    }

    try {
      // Create activity record for the email
      const activityData = {
        customer_id: customerId,
        activity_type: 'email',
        title: `Email: ${newEmail.subject}`,
        content: `To: ${newEmail.to}\n\n${newEmail.body}`,
        created_by: 'Current User', // TODO: Get from auth context
        is_important: false,
        attachments: newEmail.attachments.map(f => f.name)
      };

      await api.post('/api/v1/crm/activities', activityData);

      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Email sent and logged successfully',
        life: 3000
      });

      setShowComposeDialog(false);
      loadEmails();
    } catch (error) {
      console.error('Error sending email:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to send email',
        life: 3000
      });
    }
  };

  const viewEmail = (email: Email) => {
    setSelectedEmail(email);
    setShowViewDialog(true);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('de-DE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const subjectBodyTemplate = (rowData: Email) => {
    return (
      <div className="email-subject">
        {rowData.is_important && (
          <i className="pi pi-star-fill important-icon"></i>
        )}
        <span>{rowData.title.replace('Email: ', '')}</span>
      </div>
    );
  };

  const dateBodyTemplate = (rowData: Email) => {
    return <span>{formatDate(rowData.created_at)}</span>;
  };

  const attachmentBodyTemplate = (rowData: Email) => {
    if (!rowData.attachments || rowData.attachments.length === 0) {
      return null;
    }
    return (
      <Tag 
        value={`${rowData.attachments.length} attachment${rowData.attachments.length > 1 ? 's' : ''}`}
        icon="pi pi-paperclip"
        severity="info"
      />
    );
  };

  const actionsBodyTemplate = (rowData: Email) => {
    return (
      <div className="action-buttons">
        <Button
          icon="pi pi-eye"
          className="p-button-rounded p-button-text p-button-info"
          onClick={() => viewEmail(rowData)}
          tooltip="View Email"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-reply"
          className="p-button-rounded p-button-text p-button-success"
          onClick={() => {
            setNewEmail({
              to: customerEmail || '',
              subject: `Re: ${rowData.title.replace('Email: ', '')}`,
              body: `\n\n--- Original Message ---\n${rowData.content}`,
              attachments: []
            });
            setShowComposeDialog(true);
          }}
          tooltip="Reply"
          tooltipOptions={{ position: 'top' }}
        />
      </div>
    );
  };

  const composeDialogFooter = (
    <div>
      <Button
        label="Cancel"
        icon="pi pi-times"
        onClick={() => setShowComposeDialog(false)}
        className="p-button-text"
      />
      <Button
        label="Send"
        icon="pi pi-send"
        onClick={handleSendEmail}
        autoFocus
      />
    </div>
  );

  return (
    <div className="email-integration">
      <Toast ref={toast} />

      <div className="email-header">
        <h3>📧 Email Communications</h3>
        <Button
          label="Compose Email"
          icon="pi pi-plus"
          onClick={handleCompose}
          className="p-button-success"
        />
      </div>

      <DataTable
        value={emails}
        loading={loading}
        paginator
        rows={10}
        rowsPerPageOptions={[5, 10, 20]}
        emptyMessage="No emails found"
        className="email-table"
        sortField="created_at"
        sortOrder={-1}
      >
        <Column
          field="title"
          header="Subject"
          body={subjectBodyTemplate}
          sortable
          style={{ minWidth: '15rem' }}
        />
        <Column
          field="created_by"
          header="From"
          sortable
          style={{ width: '12rem' }}
        />
        <Column
          field="created_at"
          header="Date"
          body={dateBodyTemplate}
          sortable
          style={{ width: '12rem' }}
        />
        <Column
          header="Attachments"
          body={attachmentBodyTemplate}
          style={{ width: '10rem' }}
        />
        <Column
          header="Actions"
          body={actionsBodyTemplate}
          style={{ width: '10rem' }}
        />
      </DataTable>

      {/* Compose Email Dialog */}
      <Dialog
        header="Compose Email"
        visible={showComposeDialog}
        style={{ width: '60vw' }}
        onHide={() => setShowComposeDialog(false)}
        footer={composeDialogFooter}
        modal
      >
        <div className="compose-form">
          <div className="form-field">
            <label htmlFor="to">To *</label>
            <InputText
              id="to"
              value={newEmail.to}
              onChange={(e) => setNewEmail({ ...newEmail, to: e.target.value })}
              placeholder="recipient@example.com"
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="subject">Subject *</label>
            <InputText
              id="subject"
              value={newEmail.subject}
              onChange={(e) => setNewEmail({ ...newEmail, subject: e.target.value })}
              placeholder="Email subject"
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="body">Message *</label>
            <InputTextarea
              id="body"
              value={newEmail.body}
              onChange={(e) => setNewEmail({ ...newEmail, body: e.target.value })}
              rows={10}
              placeholder="Type your message here..."
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label>Attachments</label>
            <FileUpload
              mode="basic"
              multiple
              accept="*/*"
              maxFileSize={10000000}
              onSelect={(e) => setNewEmail({ ...newEmail, attachments: e.files })}
              chooseLabel="Add Attachments"
              className="w-full"
            />
            {newEmail.attachments.length > 0 && (
              <div className="attachment-chips">
                {newEmail.attachments.map((file, index) => (
                  <Chip
                    key={index}
                    label={file.name}
                    removable
                    onRemove={() => {
                      const newAttachments = [...newEmail.attachments];
                      newAttachments.splice(index, 1);
                      setNewEmail({ ...newEmail, attachments: newAttachments });
                    }}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </Dialog>

      {/* View Email Dialog */}
      <Dialog
        header="Email Details"
        visible={showViewDialog}
        style={{ width: '60vw' }}
        onHide={() => setShowViewDialog(false)}
        modal
      >
        {selectedEmail && (
          <div className="email-details">
            <div className="detail-row">
              <strong>Subject:</strong>
              <span>{selectedEmail.title.replace('Email: ', '')}</span>
            </div>
            <div className="detail-row">
              <strong>From:</strong>
              <span>{selectedEmail.created_by || 'Unknown'}</span>
            </div>
            <div className="detail-row">
              <strong>Date:</strong>
              <span>{formatDate(selectedEmail.created_at)}</span>
            </div>
            {selectedEmail.attachments && selectedEmail.attachments.length > 0 && (
              <div className="detail-row">
                <strong>Attachments:</strong>
                <div className="attachments-list">
                  {selectedEmail.attachments.map((attachment, index) => (
                    <Chip key={index} label={attachment} icon="pi pi-paperclip" />
                  ))}
                </div>
              </div>
            )}
            <div className="detail-row">
              <strong>Message:</strong>
              <div className="email-content">{selectedEmail.content}</div>
            </div>
          </div>
        )}
      </Dialog>
    </div>
  );
};
