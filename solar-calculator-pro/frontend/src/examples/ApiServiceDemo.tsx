/**
 * API Service Demo
 * 
 * This file demonstrates all features of the API Service Layer including:
 * - Basic HTTP requests
 * - File upload/download
 * - Retry logic
 * - Batch requests
 * - Polling
 * - Request cancellation
 * - Token management
 * - Error handling
 */

import React, { useState, useEffect } from 'react';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { ProgressBar } from 'primereact/progressbar';
import { Toast } from 'primereact/toast';
import { FileUpload } from 'primereact/fileupload';
import api, {
  apiService,
  uploadFile,
  downloadFile,
  retryRequest,
  batchRequest,
  sequentialRequest,
  pollEndpoint,
  createCancelToken,
  isCancelError,
  requestQueue,
  APIError,
} from '../services/api';

export const ApiServiceDemo: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [pollingStatus, setPollingStatus] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const toast = React.useRef<Toast>(null);

  // Demo 1: Basic GET Request
  const handleBasicGet = async () => {
    setLoading(true);
    try {
      const response = await api.get('/projects');
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: `Fetched ${response.data.length} projects`,
      });
      setResults(response.data);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  // Demo 2: POST Request with Data
  const handlePost = async () => {
    setLoading(true);
    try {
      const response = await api.post('/projects', {
        name: 'New Project',
        type: 'solar',
        data: { roofArea: 50, moduleType: 'standard' },
      });
      toast.current?.show({
        severity: 'success',
        summary: 'Created',
        detail: `Project created with ID: ${response.data.id}`,
      });
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  // Demo 3: File Upload with Progress
  const handleFileUpload = async (event: any) => {
    const file = event.files[0];
    if (!file) return;

    try {
      const response = await uploadFile(
        '/upload/matrix',
        file,
        (progress) => {
          setUploadProgress(progress);
        }
      );
      toast.current?.show({
        severity: 'success',
        summary: 'Uploaded',
        detail: 'File uploaded successfully',
      });
      setUploadProgress(0);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Upload Failed',
        detail: error.message,
      });
      setUploadProgress(0);
    }
  };

  // Demo 4: File Download
  const handleFileDownload = async () => {
    setLoading(true);
    try {
      await downloadFile('/download/report/123', 'solar-report.pdf');
      toast.current?.show({
        severity: 'success',
        summary: 'Downloaded',
        detail: 'File downloaded successfully',
      });
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Download Failed',
        detail: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  // Demo 5: Retry Logic
  const handleRetry = async () => {
    setLoading(true);
    try {
      const data = await retryRequest(
        () => api.get('/unstable-endpoint'),
        3,
        1000
      );
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Request succeeded after retries',
      });
      setResults([data]);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Failed',
        detail: 'All retry attempts failed',
      });
    } finally {
      setLoading(false);
    }
  };

  // Demo 6: Batch Requests (Parallel)
  const handleBatchRequests = async () => {
    setLoading(true);
    try {
      const results = await batchRequest([
        () => api.get('/projects/1'),
        () => api.get('/projects/2'),
        () => api.get('/projects/3'),
      ]);
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: `Fetched ${results.length} projects in parallel`,
      });
      setResults(results);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  // Demo 7: Sequential Requests
  const handleSequentialRequests = async () => {
    setLoading(true);
    try {
      const results = await sequentialRequest([
        () => api.post('/workflow/step1', { data: 'step1' }),
        () => api.post('/workflow/step2', { data: 'step2' }),
        () => api.post('/workflow/step3', { data: 'step3' }),
      ]);
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: `Completed ${results.length} steps sequentially`,
      });
      setResults(results);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  // Demo 8: Polling
  const handlePolling = async () => {
    setLoading(true);
    setPollingStatus('Polling...');
    try {
      const result = await pollEndpoint(
        () => api.get('/job/status/123'),
        (data) => data.status === 'completed',
        {
          interval: 2000,
          maxAttempts: 10,
          timeout: 30000,
        }
      );
      setPollingStatus('Completed');
      toast.current?.show({
        severity: 'success',
        summary: 'Job Completed',
        detail: 'Polling completed successfully',
      });
      setResults([result]);
    } catch (error: any) {
      setPollingStatus('Failed');
      toast.current?.show({
        severity: 'error',
        summary: 'Polling Failed',
        detail: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  // Demo 9: Request Cancellation
  const handleCancellableRequest = () => {
    const cancelToken = createCancelToken();
    setLoading(true);

    // Start long-running request
    api
      .get('/long-running-task', {
        cancelToken: cancelToken.token,
      })
      .then((response) => {
        toast.current?.show({
          severity: 'success',
          summary: 'Completed',
          detail: 'Long-running task completed',
        });
        setResults([response.data]);
      })
      .catch((error) => {
        if (isCancelError(error)) {
          toast.current?.show({
            severity: 'info',
            summary: 'Cancelled',
            detail: 'Request was cancelled',
          });
        } else {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: error.message,
          });
        }
      })
      .finally(() => {
        setLoading(false);
      });

    // Cancel after 2 seconds
    setTimeout(() => {
      cancelToken.cancel('User cancelled the request');
    }, 2000);
  };

  // Demo 10: Rate-Limited Requests
  const handleRateLimitedRequests = async () => {
    setLoading(true);
    try {
      const promises = [];
      for (let i = 1; i <= 20; i++) {
        promises.push(
          requestQueue.add(() => api.get(`/projects/${i}`))
        );
      }
      const results = await Promise.all(promises);
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: `Completed ${results.length} rate-limited requests`,
      });
      setResults(results);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  // Demo 11: Token Management
  const handleTokenManagement = () => {
    const isAuth = apiService.isAuthenticated();
    const token = apiService.getAccessToken();

    toast.current?.show({
      severity: 'info',
      summary: 'Token Status',
      detail: `Authenticated: ${isAuth}, Token: ${token ? 'Present' : 'None'}`,
    });
  };

  // Demo 12: Error Handling
  const handleErrorDemo = async () => {
    setLoading(true);
    try {
      await api.get('/non-existent-endpoint');
    } catch (error: any) {
      const apiError = error as APIError;
      toast.current?.show({
        severity: 'error',
        summary: `Error ${apiError.status}`,
        detail: apiError.message,
      });
      console.error('Error details:', apiError.details);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="api-service-demo p-4">
      <Toast ref={toast} />
      
      <h1 className="text-3xl font-bold mb-4">API Service Layer Demo</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Basic Requests */}
        <Card title="Basic Requests" className="mb-4">
          <div className="flex flex-col gap-2">
            <Button
              label="GET Request"
              icon="pi pi-download"
              onClick={handleBasicGet}
              loading={loading}
            />
            <Button
              label="POST Request"
              icon="pi pi-upload"
              onClick={handlePost}
              loading={loading}
            />
          </div>
        </Card>

        {/* File Operations */}
        <Card title="File Operations" className="mb-4">
          <div className="flex flex-col gap-2">
            <FileUpload
              mode="basic"
              name="file"
              accept=".xlsx,.csv"
              maxFileSize={10000000}
              customUpload
              uploadHandler={handleFileUpload}
              auto
              chooseLabel="Upload File"
            />
            {uploadProgress > 0 && (
              <ProgressBar value={uploadProgress} />
            )}
            <Button
              label="Download File"
              icon="pi pi-download"
              onClick={handleFileDownload}
              loading={loading}
            />
          </div>
        </Card>

        {/* Retry Logic */}
        <Card title="Retry Logic" className="mb-4">
          <Button
            label="Retry Request"
            icon="pi pi-refresh"
            onClick={handleRetry}
            loading={loading}
            className="w-full"
          />
        </Card>

        {/* Batch Requests */}
        <Card title="Batch Requests" className="mb-4">
          <div className="flex flex-col gap-2">
            <Button
              label="Parallel Requests"
              icon="pi pi-clone"
              onClick={handleBatchRequests}
              loading={loading}
            />
            <Button
              label="Sequential Requests"
              icon="pi pi-list"
              onClick={handleSequentialRequests}
              loading={loading}
            />
          </div>
        </Card>

        {/* Polling */}
        <Card title="Polling" className="mb-4">
          <Button
            label="Start Polling"
            icon="pi pi-sync"
            onClick={handlePolling}
            loading={loading}
            className="w-full"
          />
          {pollingStatus && (
            <p className="mt-2 text-sm">Status: {pollingStatus}</p>
          )}
        </Card>

        {/* Cancellation */}
        <Card title="Request Cancellation" className="mb-4">
          <Button
            label="Cancellable Request"
            icon="pi pi-times"
            onClick={handleCancellableRequest}
            loading={loading}
            className="w-full"
          />
          <p className="mt-2 text-xs text-gray-500">
            Request will be cancelled after 2 seconds
          </p>
        </Card>

        {/* Rate Limiting */}
        <Card title="Rate Limiting" className="mb-4">
          <Button
            label="20 Rate-Limited Requests"
            icon="pi pi-clock"
            onClick={handleRateLimitedRequests}
            loading={loading}
            className="w-full"
          />
        </Card>

        {/* Token Management */}
        <Card title="Token Management" className="mb-4">
          <Button
            label="Check Token Status"
            icon="pi pi-key"
            onClick={handleTokenManagement}
            className="w-full"
          />
        </Card>

        {/* Error Handling */}
        <Card title="Error Handling" className="mb-4">
          <Button
            label="Trigger Error"
            icon="pi pi-exclamation-triangle"
            onClick={handleErrorDemo}
            loading={loading}
            className="w-full"
            severity="danger"
          />
        </Card>
      </div>

      {/* Results Display */}
      {results.length > 0 && (
        <Card title="Results" className="mt-4">
          <pre className="bg-gray-100 p-4 rounded overflow-auto max-h-96">
            {JSON.stringify(results, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  );
};

export default ApiServiceDemo;
