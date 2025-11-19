import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { FileUpload } from 'primereact/fileupload';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Toast } from 'primereact/toast';
import { Tag } from 'primereact/tag';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import api from '../../services/api';
import './DocumentAttachments.css';

interface Document {
  id: number;
  customer_id: number;
  title: string;
  content: string;
  created_at: string;
  created_by?: string;
  attachments?: string[];
}

interface DocumentAttachmentsProps {
  customerId: number;
}

export const DocumentAttachments: React.FC<DocumentAttachmentsProps> = ({ customerId }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [showViewDialog, setShowViewDialog] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [newDocument, setNewDocument] = useState({
    title: '',
    description: '',
    files: [] as File[]
  });
  const toast = React.useRef<Toast>(null);

  useEffect(() => {
    loadDocuments();
  }, [customerId]);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/crm/activities/customer/${customerId}`);
      const allActivities = response.data.activities || [];
      const docsWithAttachments = allActivities.filter(
        (activity: Document) => activity.attachments && activity.attachments.length > 0
      );
      setDocuments(docsWithAttachments);
    } catch (error) {
      console.error('Error loading documents:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load documents',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = () => {
    setNewDocument({
      title: '',
      description: '',
      files: []
    });
    setShowUploadDialog(true);
  };

  const handleSaveDocument = async () => {
    if (!newDocument.title || newDocument.files.length === 0) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Validation Error',
        detail: 'Please provide a title and at least one file',
        life: 3000
      });
      return;
    }

    try {
      const activityData = {
        customer_id: customerId,
        activity_type: 'other',
        title: newDocument.title,
        content: newDocument.description,
        created_by: 'Current User',
        is_important: false,
        attachments: newDocument.files.map(f => f.name)
      };

      await api.post('/api/v1/crm/activities', activityData);

      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Document uploaded successfully',
        life: 3000
      });

      setShowUploadDialog(false);
      loadDocuments();
    } catch (error) {
      console.error('Error uploading document:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to upload document',
        life: 3000
      });
    }
  };

  const viewDocument = (document: Document) => {
    setSelectedDocument(document);
    setShowViewDialog(true);
  };

  const deleteDocument = (document: Document) => {
    confirmDialog({
      message: 'Are you sure you want to delete this document?',
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await api.delete(`/api/v1/crm/activities/${document.id}`);
          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'Document deleted successfully',
            life: 3000
          });
          loadDocuments();
        } catch (error) {
          console.error('Error deleting document:', error);
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete document',
            life: 3000
          });
        }
      }
    });
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

  const attachmentBodyTemplate = (rowData: Document) => {
    if (!rowData.attachments || rowData.attachments.length === 0) {
      return null;
    }
    return (
      <Tag 
        value={`${rowData.attachments.length} file${rowData.attachments.length > 1 ? 's' : ''}`}
        icon="pi pi-paperclip"
        severity="info"
      />
    );
  };

  const dateBodyTemplate = (rowData: Document) => {
    return <span>{formatDate(rowData.created_at)}</span>;
  };

  const actionsBodyTemplate = (rowData: Document) => {
    return (
      <div className="action-buttons">
        <Button
          icon="pi pi-eye"
          className="p-button-rounded p-button-text p-button-info"
          onClick={() => viewDocument(rowData)}
          tooltip="View"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-text p-button-danger"
          onClick={() => deleteDocument(rowData)}
          tooltip="Delete"
          tooltipOptions={{ position: 'top' }}
        />
      </div>
    );
  };

  const uploadDialogFooter = (
    <div>
      <Button
        label="Cancel"
        icon="pi pi-times"
        onClick={() => setShowUploadDialog(false)}
        className="p-button-text"
      />
      <Button
        label="Upload"
        icon="pi pi-upload"
        onClick={handleSaveDocument}
        autoFocus
      />
    </div>
  );

  return (
    <div className="document-attachments">
      <Toast ref={toast} />
      <ConfirmDialog />

      <div className="document-header">
        <h3>📎 Document Attachments</h3>
        <Button
          label="Upload Document"
          icon="pi pi-upload"
          onClick={handleUpload}
          className="p-button-success"
        />
      </div>

      <DataTable
        value={documents}
        loading={loading}
        paginator
        rows={10}
        rowsPerPageOptions={[5, 10, 20]}
        emptyMessage="No documents attached"
        className="document-table"
        sortField="created_at"
        sortOrder={-1}
      >
        <Column
          field="title"
          header="Title"
          sortable
          style={{ minWidth: '15rem' }}
        />
        <Column
          header="Attachments"
          body={attachmentBodyTemplate}
          style={{ width: '10rem' }}
        />
        <Column
          field="created_by"
          header="Uploaded By"
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
          header="Actions"
          body={actionsBodyTemplate}
          style={{ width: '10rem' }}
        />
      </DataTable>

      <Dialog
        header="Upload Document"
        visible={showUploadDialog}
        style={{ width: '50vw' }}
        onHide={() => setShowUploadDialog(false)}
        footer={uploadDialogFooter}
        modal
      >
        <div className="upload-form">
          <div className="form-field">
            <label htmlFor="title">Title *</label>
            <InputText
              id="title"
              value={newDocument.title}
              onChange={(e) => setNewDocument({ ...newDocument, title: e.target.value })}
              placeholder="Document title"
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="description">Description</label>
            <InputTextarea
              id="description"
              value={newDocument.description}
              onChange={(e) => setNewDocument({ ...newDocument, description: e.target.value })}
              rows={4}
              placeholder="Document description..."
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label>Files *</label>
            <FileUpload
              mode="basic"
              multiple
              accept="*/*"
              maxFileSize={50000000}
              onSelect={(e) => setNewDocument({ ...newDocument, files: e.files })}
              chooseLabel="Select Files"
              className="w-full"
            />
            {newDocument.files.length > 0 && (
              <div className="file-list">
                {newDocument.files.map((file, index) => (
                  <div key={index} className="file-item">
                    <i className="pi pi-file"></i>
                    <span>{file.name}</span>
                    <span className="file-size">({(file.size / 1024).toFixed(2)} KB)</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </Dialog>

      <Dialog
        header="Document Details"
        visible={showViewDialog}
        style={{ width: '50vw' }}
        onHide={() => setShowViewDialog(false)}
        modal
      >
        {selectedDocument && (
          <div className="document-details">
            <div className="detail-row">
              <strong>Title:</strong>
              <span>{selectedDocument.title}</span>
            </div>
            <div className="detail-row">
              <strong>Date:</strong>
              <span>{formatDate(selectedDocument.created_at)}</span>
            </div>
            <div className="detail-row">
              <strong>Uploaded By:</strong>
              <span>{selectedDocument.created_by || 'Unknown'}</span>
            </div>
            {selectedDocument.content && (
              <div className="detail-row">
                <strong>Description:</strong>
                <div className="document-content">{selectedDocument.content}</div>
              </div>
            )}
            {selectedDocument.attachments && selectedDocument.attachments.length > 0 && (
              <div className="detail-row">
                <strong>Attachments:</strong>
                <div className="attachments-list">
                  {selectedDocument.attachments.map((attachment, index) => (
                    <div key={index} className="attachment-item">
                      <i className="pi pi-file"></i>
                      <span>{attachment}</span>
                      <Button
                        icon="pi pi-download"
                        className="p-button-rounded p-button-text p-button-sm"
                        tooltip="Download"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Dialog>
    </div>
  );
};
