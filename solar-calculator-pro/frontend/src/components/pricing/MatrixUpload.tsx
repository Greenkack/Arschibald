/**
 * Matrix Upload Component
 * 
 * Handles Excel file upload with drag-and-drop, validation, and progress tracking
 */

import React, { useState, useRef, useCallback } from 'react';
import { FileUpload, FileUploadHandlerEvent } from 'primereact/fileupload';
import { ProgressBar } from 'primereact/progressbar';
import { Message } from 'primereact/message';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import './MatrixUpload.css';

interface MatrixUploadProps {
  onUploadSuccess?: (data: any) => void;
  onUploadError?: (error: string) => void;
}

interface UploadState {
  uploading: boolean;
  progress: number;
  error: string | null;
  success: boolean;
  fileName: string | null;
}

const MatrixUpload: React.FC<MatrixUploadProps> = ({ 
  onUploadSuccess, 
  onUploadError 
}) => {
  const [uploadState, setUploadState] = useState<UploadState>({
    uploading: false,
    progress: 0,
    error: null,
    success: false,
    fileName: null,
  });

  const toast = useRef<Toast>(null);
  const fileUploadRef = useRef<FileUpload>(null);

  // Allowed file types
  const allowedTypes = [
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv',
    'application/json',
  ];

  // Max file size: 10MB
  const maxFileSize = 10 * 1024 * 1024;

  /**
   * Validate file before upload
   */
  const validateFile = (file: File): { valid: boolean; error?: string } => {
    // Check file type
    if (!allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: 'Ungültiger Dateityp. Bitte laden Sie eine Excel (.xlsx, .xls), CSV oder JSON Datei hoch.',
      };
    }

    // Check file size
    if (file.size > maxFileSize) {
      return {
        valid: false,
        error: `Datei ist zu groß. Maximale Größe: ${(maxFileSize / 1024 / 1024).toFixed(0)}MB`,
      };
    }

    // Check file extension
    const extension = file.name.split('.').pop()?.toLowerCase();
    const validExtensions = ['xlsx', 'xls', 'csv', 'json'];
    if (!extension || !validExtensions.includes(extension)) {
      return {
        valid: false,
        error: 'Ungültige Dateierweiterung. Erlaubt: .xlsx, .xls, .csv, .json',
      };
    }

    return { valid: true };
  };

  /**
   * Handle file upload
   */
  const handleUpload = useCallback(async (event: FileUploadHandlerEvent) => {
    const file = event.files[0];

    // Validate file
    const validation = validateFile(file);
    if (!validation.valid) {
      setUploadState({
        uploading: false,
        progress: 0,
        error: validation.error || 'Validierungsfehler',
        success: false,
        fileName: null,
      });
      
      toast.current?.show({
        severity: 'error',
        summary: 'Validierungsfehler',
        detail: validation.error,
        life: 5000,
      });

      if (onUploadError) {
        onUploadError(validation.error || 'Validierungsfehler');
      }

      return;
    }

    // Start upload
    setUploadState({
      uploading: true,
      progress: 0,
      error: null,
      success: false,
      fileName: file.name,
    });

    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', file);
      formData.append('matrix_type', 'price_matrix');

      // Upload with progress tracking
      const response = await api.post('/api/v1/pricing/matrix/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;
          
          setUploadState(prev => ({
            ...prev,
            progress: percentCompleted,
          }));
        },
      });

      // Success
      setUploadState({
        uploading: false,
        progress: 100,
        error: null,
        success: true,
        fileName: file.name,
      });

      toast.current?.show({
        severity: 'success',
        summary: 'Upload erfolgreich',
        detail: `Datei "${file.name}" wurde erfolgreich hochgeladen.`,
        life: 5000,
      });

      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }

      // Clear file upload after 2 seconds
      setTimeout(() => {
        fileUploadRef.current?.clear();
        setUploadState({
          uploading: false,
          progress: 0,
          error: null,
          success: false,
          fileName: null,
        });
      }, 2000);

    } catch (error: any) {
      const errorMessage = error.response?.data?.error?.message || 
                          error.message || 
                          'Upload fehlgeschlagen';

      setUploadState({
        uploading: false,
        progress: 0,
        error: errorMessage,
        success: false,
        fileName: file.name,
      });

      toast.current?.show({
        severity: 'error',
        summary: 'Upload fehlgeschlagen',
        detail: errorMessage,
        life: 5000,
      });

      if (onUploadError) {
        onUploadError(errorMessage);
      }
    }
  }, [onUploadSuccess, onUploadError]);

  /**
   * Handle file select (before upload)
   */
  const handleSelect = (event: any) => {
    const file = event.files[0];
    
    if (file) {
      const validation = validateFile(file);
      if (!validation.valid) {
        toast.current?.show({
          severity: 'warn',
          summary: 'Validierungswarnung',
          detail: validation.error,
          life: 5000,
        });
        
        // Clear invalid file
        fileUploadRef.current?.clear();
      }
    }
  };

  /**
   * Handle file remove
   */
  const handleRemove = () => {
    setUploadState({
      uploading: false,
      progress: 0,
      error: null,
      success: false,
      fileName: null,
    });
  };

  /**
   * Custom upload button template
   */
  const chooseOptions = {
    icon: 'pi pi-fw pi-file-excel',
    iconOnly: false,
    className: 'custom-choose-btn p-button-rounded',
    label: 'Datei auswählen',
  };

  const uploadOptions = {
    icon: 'pi pi-fw pi-cloud-upload',
    iconOnly: false,
    className: 'custom-upload-btn p-button-success p-button-rounded',
    label: 'Hochladen',
  };

  const cancelOptions = {
    icon: 'pi pi-fw pi-times',
    iconOnly: false,
    className: 'custom-cancel-btn p-button-danger p-button-rounded',
    label: 'Abbrechen',
  };

  return (
    <div className="matrix-upload">
      <Toast ref={toast} />

      <Card title="📤 Preismatrix hochladen" className="upload-card">
        <div className="upload-instructions">
          <Message 
            severity="info" 
            text="Laden Sie eine Excel-Datei (.xlsx, .xls), CSV oder JSON mit Ihrer Preismatrix hoch. Die Datei sollte die Modulanzahl in Spalte A und Batteriespeichermodelle in Zeile 1 enthalten."
          />
        </div>

        <div className="upload-area">
          <FileUpload
            ref={fileUploadRef}
            name="file"
            customUpload
            uploadHandler={handleUpload}
            onSelect={handleSelect}
            onRemove={handleRemove}
            accept=".xlsx,.xls,.csv,.json"
            maxFileSize={maxFileSize}
            emptyTemplate={
              <div className="empty-template">
                <i className="pi pi-cloud-upload" style={{ fontSize: '3em', color: '#6366f1' }}></i>
                <p className="drag-drop-text">
                  Ziehen Sie eine Datei hierher oder klicken Sie zum Auswählen
                </p>
                <p className="file-info">
                  Erlaubte Formate: Excel (.xlsx, .xls), CSV, JSON
                  <br />
                  Maximale Größe: 10MB
                </p>
              </div>
            }
            chooseOptions={chooseOptions}
            uploadOptions={uploadOptions}
            cancelOptions={cancelOptions}
            disabled={uploadState.uploading}
          />
        </div>

        {/* Upload Progress */}
        {uploadState.uploading && (
          <div className="upload-progress">
            <div className="progress-info">
              <span className="progress-label">
                <i className="pi pi-spin pi-spinner" style={{ marginRight: '0.5rem' }}></i>
                Hochladen: {uploadState.fileName}
              </span>
              <span className="progress-percentage">{uploadState.progress}%</span>
            </div>
            <ProgressBar 
              value={uploadState.progress} 
              showValue={false}
              className="upload-progress-bar"
            />
          </div>
        )}

        {/* Success Message */}
        {uploadState.success && !uploadState.uploading && (
          <Message 
            severity="success" 
            text={`✅ Datei "${uploadState.fileName}" wurde erfolgreich hochgeladen und verarbeitet.`}
            className="upload-message"
          />
        )}

        {/* Error Message */}
        {uploadState.error && !uploadState.uploading && (
          <Message 
            severity="error" 
            text={`❌ ${uploadState.error}`}
            className="upload-message"
          />
        )}

        {/* File Format Help */}
        <div className="format-help">
          <h4>📋 Erwartetes Dateiformat:</h4>
          <ul>
            <li><strong>Spalte A (A2:A200):</strong> Anzahl der PV-Module (z.B. 10, 15, 20, ...)</li>
            <li><strong>Zeile 1 (B1:XX1):</strong> Batteriespeichermodelle (z.B. "Tesla Powerwall", "BYD HVS", ...)</li>
            <li><strong>Letzte Spalte:</strong> "kein Speicher" Option</li>
            <li><strong>Zellen:</strong> Schlüsselfertige Systempreise in Euro</li>
          </ul>
          
          <Button 
            label="📥 Beispiel-Vorlage herunterladen" 
            icon="pi pi-download"
            className="p-button-outlined p-button-sm"
            onClick={() => {
              // Download template
              window.open('/api/v1/pricing/matrix/template', '_blank');
            }}
          />
        </div>
      </Card>
    </div>
  );
};

export default MatrixUpload;
