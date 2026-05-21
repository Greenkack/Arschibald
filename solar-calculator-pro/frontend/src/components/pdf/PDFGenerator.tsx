/**
 * PDF Generator Component
 * 
 * Handles PDF generation with loading states, progress tracking,
 * and error handling
 */

import React, { useState } from 'react';
import { Button } from 'primereact/button';
import { ProgressBar } from 'primereact/progressbar';
import { Message } from 'primereact/message';
import { Toast } from 'primereact/toast';
import { Card } from 'primereact/card';
import { Checkbox } from 'primereact/checkbox';
import api from '../../services/api';
import './PDFGenerator.css';

interface PDFGeneratorProps {
  projectData: any;
  template: string;
  onSuccess?: (pdfData: string) => void;
  onError?: (error: string) => void;
  className?: string;
}

interface GenerationState {
  loading: boolean;
  progress: number;
  status: string;
  error: string | null;
}

export const PDFGenerator: React.FC<PDFGeneratorProps> = ({
  projectData,
  template,
  onSuccess,
  onError,
  className = '',
}) => {
  const [state, setState] = useState<GenerationState>({
    loading: false,
    progress: 0,
    status: '',
    error: null,
  });
  const [useCache, setUseCache] = useState(true);
  const [storePDF, setStorePDF] = useState(true);
  const toastRef = React.useRef<Toast>(null);

  const updateProgress = (progress: number, status: string) => {
    setState(prev => ({ ...prev, progress, status }));
  };

  const handleGenerate = async () => {
    setState({
      loading: true,
      progress: 0,
      status: 'Initializing PDF generation...',
      error: null,
    });

    try {
      // Step 1: Validate data
      updateProgress(10, 'Validating project data...');
      await new Promise(resolve => setTimeout(resolve, 300));

      if (!projectData || Object.keys(projectData).length === 0) {
        throw new Error('No project data available');
      }

      // Step 2: Prepare request
      updateProgress(20, 'Preparing PDF request...');
      await new Promise(resolve => setTimeout(resolve, 300));

      const requestData = {
        offer_data: projectData,
        template: template,
        use_cache: useCache,
        store_pdf: storePDF,
        filename: `${projectData.customer_name || 'project'}_${Date.now()}.pdf`,
        metadata: {
          generated_at: new Date().toISOString(),
          template: template,
          customer: projectData.customer_name,
        },
      };

      // Step 3: Generate PDF
      updateProgress(40, 'Generating PDF document...');
      
      const response = await api.post('/api/v1/pdf/generate', requestData);

      updateProgress(80, 'Processing PDF data...');
      await new Promise(resolve => setTimeout(resolve, 300));

      const { pdf_base64, size_bytes, cached, stored_path } = response.data;

      // Step 4: Complete
      updateProgress(100, 'PDF generated successfully!');

      toastRef.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: `PDF generated successfully (${(size_bytes / 1024).toFixed(2)} KB)${cached ? ' - from cache' : ''}`,
        life: 5000,
      });

      if (onSuccess) {
        onSuccess(pdf_base64);
      }

      // Reset after delay
      setTimeout(() => {
        setState({
          loading: false,
          progress: 0,
          status: '',
          error: null,
        });
      }, 2000);

    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'PDF generation failed';
      
      setState({
        loading: false,
        progress: 0,
        status: '',
        error: errorMessage,
      });

      toastRef.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: errorMessage,
        life: 5000,
      });

      if (onError) {
        onError(errorMessage);
      }
    }
  };

  const renderGenerateButton = () => {
    if (state.loading) {
      return (
        <Button
          label={state.status}
          icon="pi pi-spin pi-spinner"
          disabled
          className="p-button-lg generate-button"
        />
      );
    }

    return (
      <Button
        label="Generate PDF"
        icon="pi pi-file-pdf"
        onClick={handleGenerate}
        className="p-button-lg p-button-success generate-button"
        disabled={!projectData}
      />
    );
  };

  return (
    <div className={`pdf-generator ${className}`}>
      <Toast ref={toastRef} />

      <Card className="generator-card">
        <div className="generator-content">
          <div className="generator-header">
            <h3>📄 Generate PDF</h3>
            <p className="generator-subtitle">
              Create a professional PDF document from your project data
            </p>
          </div>

          {state.error && (
            <Message
              severity="error"
              text={state.error}
              className="generator-error"
            />
          )}

          <div className="generator-options">
            <div className="option-item">
              <Checkbox
                inputId="use-cache"
                checked={useCache}
                onChange={(e) => setUseCache(e.checked || false)}
              />
              <label htmlFor="use-cache" className="option-label">
                <span className="option-title">Use Cache</span>
                <span className="option-description">
                  Use cached PDF if available for faster generation
                </span>
              </label>
            </div>

            <div className="option-item">
              <Checkbox
                inputId="store-pdf"
                checked={storePDF}
                onChange={(e) => setStorePDF(e.checked || false)}
              />
              <label htmlFor="store-pdf" className="option-label">
                <span className="option-title">Store PDF</span>
                <span className="option-description">
                  Save generated PDF to history for later access
                </span>
              </label>
            </div>
          </div>

          {state.loading && (
            <div className="generator-progress">
              <ProgressBar value={state.progress} showValue={false} />
              <p className="progress-status">{state.status}</p>
            </div>
          )}

          <div className="generator-actions">
            {renderGenerateButton()}
          </div>

          <div className="generator-info">
            <div className="info-item">
              <i className="pi pi-info-circle"></i>
              <span>Template: <strong>{template}</strong></span>
            </div>
            {projectData && (
              <div className="info-item">
                <i className="pi pi-check-circle"></i>
                <span>Project data ready</span>
              </div>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};
