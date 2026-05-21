/**
 * PDF Template Upload Component
 * 
 * Allows users to upload custom PDF templates.
 * Supports drag-and-drop and file validation.
 */

import React, { useState, useRef } from 'react';
import { FileUpload, FileUploadHandlerEvent } from 'primereact/fileupload';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dialog } from 'primereact/dialog';
import { Message } from 'primereact/message';
import { ProgressBar } from 'primereact/progressbar';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import './TemplateUpload.css';

interface TemplateUploadProps {
  visible: boolean;
  onHide: () => void;
  onUploadSuccess: () => void;
}

export const TemplateUpload: React.FC<TemplateUploadProps> = ({
  visible,
  onHide,
  onUploadSuccess
}) => {
  const [templateName, setTemplateName] = useState('');
  const [templateDescription, setTemplateDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const toast = useRef<Toast>(null);
  const fileUploadRef = useRef<FileUpload>(null);

  const handleFileSelect = (event: FileUploadHandlerEvent) => {
    const file = event.files[0];
    
    // Validate file
    if (!file) return;
    
    // Check file type
    const validTypes = ['application/pdf', 'text/html', 'application/json'];
    if (!validTypes.includes(file.type)) {
      setError('Invalid file type. Please upload PDF, HTML, or JSON files.');
      return;
    }
    
    // Check file size (max 10MB)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('File size exceeds 10MB limit.');
      return;
    }
    
    setSelectedFile(file);
    setError(null);
    
    // Auto-fill template name from filename if empty
    if (!templateName) {
      const name = file.name.replace(/\.[^/.]+$/, '');
      setTemplateName(name);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !templateName) {
      setError('Please provide a template name and select a file.');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      setUploadProgress(0);

      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('name', templateName);
      formData.append('description', templateDescription);

      const response = await api.post('/api/v1/pdf/templates/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(progress);
          }
        }
      });

      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Template uploaded successfully',
        life: 3000
      });

      // Reset form
      setTemplateName('');
      setTemplateDescription('');
      setSelectedFile(null);
      setUploadProgress(0);
      fileUploadRef.current?.clear();

      // Notify parent
      onUploadSuccess();
      onHide();
    } catch (err: any) {
      const errorMessage = err.response?.data?.error?.message || 'Failed to upload template';
      setError(errorMessage);
      toast.current?.show({
        severity: 'error',
        summary: 'Upload Failed',
        detail: errorMessage,
        life: 5000
      });
    } finally {
      setUploading(false);
    }
  };

  const handleCancel = () => {
    setTemplateName('');
    setTemplateDescription('');
    setSelectedFile(null);
    setError(null);
    setUploadProgress(0);
    fileUploadRef.current?.clear();
    onHide();
  };

  const renderFooter = () => (
    <div className="template-upload-footer">
      <Button
        label="Cancel"
        icon="pi pi-times"
        onClick={handleCancel}
        className="p-button-text"
        disabled={uploading}
      />
      <Button
        label="Upload"
        icon="pi pi-upload"
        onClick={handleUpload}
        disabled={!selectedFile || !templateName || uploading}
        loading={uploading}
      />
    </div>
  );

  return (
    <>
      <Toast ref={toast} />
      <Dialog
        visible={visible}
        onHide={handleCancel}
        header="📤 Upload Custom Template"
        footer={renderFooter()}
        className="template-upload-dialog"
        style={{ width: '600px' }}
      >
        <div className="template-upload-content">
          {error && (
            <Message 
              severity="error" 
              text={error}
              className="w-full mb-3"
            />
          )}

          <div className="form-field">
            <label htmlFor="template-name">
              Template Name <span className="required">*</span>
            </label>
            <InputText
              id="template-name"
              value={templateName}
              onChange={(e) => setTemplateName(e.target.value)}
              placeholder="Enter template name"
              className="w-full"
              disabled={uploading}
            />
          </div>

          <div className="form-field">
            <label htmlFor="template-description">Description</label>
            <InputTextarea
              id="template-description"
              value={templateDescription}
              onChange={(e) => setTemplateDescription(e.target.value)}
              placeholder="Enter template description (optional)"
              rows={3}
              className="w-full"
              disabled={uploading}
            />
          </div>

          <div className="form-field">
            <label>
              Template File <span className="required">*</span>
            </label>
            <FileUpload
              ref={fileUploadRef}
              mode="basic"
              name="template"
              accept=".pdf,.html,.json"
              maxFileSize={10485760}
              customUpload
              uploadHandler={handleFileSelect}
              auto={false}
              chooseLabel="Choose File"
              className="w-full"
              disabled={uploading}
            />
            <small className="text-muted">
              Supported formats: PDF, HTML, JSON (Max 10MB)
            </small>
          </div>

          {selectedFile && (
            <div className="selected-file-info">
              <i className="pi pi-file"></i>
              <div className="file-details">
                <span className="file-name">{selectedFile.name}</span>
                <span className="file-size">
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </span>
              </div>
              {!uploading && (
                <Button
                  icon="pi pi-times"
                  className="p-button-text p-button-sm"
                  onClick={() => {
                    setSelectedFile(null);
                    fileUploadRef.current?.clear();
                  }}
                />
              )}
            </div>
          )}

          {uploading && (
            <div className="upload-progress">
              <ProgressBar value={uploadProgress} />
              <span className="progress-text">Uploading... {uploadProgress}%</span>
            </div>
          )}

          <div className="upload-info">
            <i className="pi pi-info-circle"></i>
            <div>
              <p><strong>Template Guidelines:</strong></p>
              <ul>
                <li>PDF templates will be used as-is for generation</li>
                <li>HTML templates support dynamic placeholders</li>
                <li>JSON templates define structure and styling</li>
                <li>Use placeholders like {`{{customer_name}}`} for dynamic content</li>
              </ul>
            </div>
          </div>
        </div>
      </Dialog>
    </>
  );
};
