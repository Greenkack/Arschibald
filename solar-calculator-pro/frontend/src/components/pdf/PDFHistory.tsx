/**
 * PDF History Component
 * 
 * Displays archive of generated PDFs with search, filter, and management
 */

import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Calendar } from 'primereact/calendar';
import { Dropdown } from 'primereact/dropdown';
import { Toast } from 'primereact/toast';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Card } from 'primereact/card';
import { Tag } from 'primereact/tag';
import { ProgressSpinner } from 'primereact/progressspinner';
import api from '../../services/api';
import { PDFDownloader } from './PDFDownloader';
import { PDFEmailer } from './PDFEmailer';
import './PDFHistory.css';

interface PDFRecord {
  filename: string;
  size_bytes: number;
  created_at: string;
  customer?: string;
  template?: string;
  [key: string]: any;
}

interface PDFHistoryProps {
  onPreview?: (filename: string) => void;
  className?: string;
}

export const PDFHistory: React.FC<PDFHistoryProps> = ({
  onPreview,
  className = '',
}) => {
  const [pdfs, setPdfs] = useState<PDFRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [globalFilter, setGlobalFilter] = useState('');
  const [dateFilter, setDateFilter] = useState<Date | null>(null);
  const [templateFilter, setTemplateFilter] = useState<string | null>(null);
  const [selectedPdfs, setSelectedPdfs] = useState<PDFRecord[]>([]);
  const [totalSize, setTotalSize] = useState(0);
  const toastRef = React.useRef<Toast>(null);

  const templateOptions = [
    { label: 'All Templates', value: null },
    { label: 'Main Template', value: 'main' },
    { label: 'Simple Template', value: 'simple' },
    { label: 'Extended Template', value: 'extended' },
  ];

  useEffect(() => {
    loadPDFs();
  }, []);

  const loadPDFs = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/pdf/list');
      setPdfs(response.data.pdfs);
      setTotalSize(response.data.total_size_bytes);
    } catch (error: any) {
      console.error('Failed to load PDFs:', error);
      toastRef.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load PDF history',
        life: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (filename: string) => {
    confirmDialog({
      message: `Are you sure you want to delete ${filename}?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await api.delete(`/api/v1/pdf/${filename}`);
          toastRef.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'PDF deleted successfully',
            life: 3000,
          });
          loadPDFs();
        } catch (error: any) {
          toastRef.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'Failed to delete PDF',
            life: 3000,
          });
        }
      },
    });
  };

  const handleBulkDelete = () => {
    if (selectedPdfs.length === 0) return;

    confirmDialog({
      message: `Are you sure you want to delete ${selectedPdfs.length} PDF(s)?`,
      header: 'Confirm Bulk Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await Promise.all(
            selectedPdfs.map(pdf => api.delete(`/api/v1/pdf/${pdf.filename}`))
          );
          toastRef.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: `${selectedPdfs.length} PDF(s) deleted successfully`,
            life: 3000,
          });
          setSelectedPdfs([]);
          loadPDFs();
        } catch (error: any) {
          toastRef.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to delete some PDFs',
            life: 3000,
          });
        }
      },
    });
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleString('de-DE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const filenameBodyTemplate = (rowData: PDFRecord) => {
    return (
      <div className="filename-cell">
        <i className="pi pi-file-pdf" style={{ color: '#d32f2f', marginRight: '0.5rem' }}></i>
        <span className="filename-text">{rowData.filename}</span>
      </div>
    );
  };

  const sizeBodyTemplate = (rowData: PDFRecord) => {
    return <span>{formatFileSize(rowData.size_bytes)}</span>;
  };

  const dateBodyTemplate = (rowData: PDFRecord) => {
    return <span>{formatDate(rowData.created_at)}</span>;
  };

  const templateBodyTemplate = (rowData: PDFRecord) => {
    if (!rowData.template) return <span>-</span>;
    
    const severityMap: Record<string, any> = {
      main: 'success',
      simple: 'info',
      extended: 'warning',
    };

    return (
      <Tag
        value={rowData.template}
        severity={severityMap[rowData.template] || 'info'}
      />
    );
  };

  const actionsBodyTemplate = (rowData: PDFRecord) => {
    return (
      <div className="actions-cell">
        {onPreview && (
          <Button
            icon="pi pi-eye"
            className="p-button-rounded p-button-text"
            tooltip="Preview"
            onClick={() => onPreview(rowData.filename)}
          />
        )}
        <PDFDownloader
          storedFilename={rowData.filename}
          filename={rowData.filename}
          buttonLabel=""
          buttonIcon="pi pi-download"
          buttonClassName="p-button-rounded p-button-text"
        />
        <PDFEmailer
          storedFilename={rowData.filename}
          defaultRecipient={rowData.customer}
          defaultSubject={`PDF: ${rowData.filename}`}
          buttonLabel=""
          buttonIcon="pi pi-envelope"
          buttonClassName="p-button-rounded p-button-text"
        />
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-text p-button-danger"
          tooltip="Delete"
          onClick={() => handleDelete(rowData.filename)}
        />
      </div>
    );
  };

  const renderHeader = () => {
    return (
      <div className="history-header">
        <div className="header-left">
          <h3>📚 PDF History</h3>
          <div className="header-stats">
            <span className="stat-item">
              <i className="pi pi-file"></i>
              {pdfs.length} PDFs
            </span>
            <span className="stat-item">
              <i className="pi pi-database"></i>
              {formatFileSize(totalSize)}
            </span>
          </div>
        </div>
        <div className="header-right">
          <Button
            icon="pi pi-refresh"
            onClick={loadPDFs}
            className="p-button-text"
            tooltip="Refresh"
            loading={loading}
          />
          {selectedPdfs.length > 0 && (
            <Button
              label={`Delete ${selectedPdfs.length} Selected`}
              icon="pi pi-trash"
              onClick={handleBulkDelete}
              className="p-button-danger"
            />
          )}
        </div>
      </div>
    );
  };

  const renderFilters = () => {
    return (
      <div className="history-filters">
        <span className="p-input-icon-left">
          <i className="pi pi-search" />
          <InputText
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            placeholder="Search PDFs..."
            className="filter-input"
          />
        </span>

        <Calendar
          value={dateFilter}
          onChange={(e) => setDateFilter(e.value as Date)}
          placeholder="Filter by date"
          showIcon
          dateFormat="dd.mm.yy"
          className="filter-calendar"
        />

        <Dropdown
          value={templateFilter}
          options={templateOptions}
          onChange={(e) => setTemplateFilter(e.value)}
          placeholder="Filter by template"
          className="filter-dropdown"
        />

        {(globalFilter || dateFilter || templateFilter) && (
          <Button
            label="Clear Filters"
            icon="pi pi-filter-slash"
            onClick={() => {
              setGlobalFilter('');
              setDateFilter(null);
              setTemplateFilter(null);
            }}
            className="p-button-text"
          />
        )}
      </div>
    );
  };

  const filteredPdfs = pdfs.filter(pdf => {
    // Global filter
    if (globalFilter) {
      const searchLower = globalFilter.toLowerCase();
      if (
        !pdf.filename.toLowerCase().includes(searchLower) &&
        !pdf.customer?.toLowerCase().includes(searchLower)
      ) {
        return false;
      }
    }

    // Date filter
    if (dateFilter) {
      const pdfDate = new Date(pdf.created_at);
      const filterDate = new Date(dateFilter);
      if (
        pdfDate.getDate() !== filterDate.getDate() ||
        pdfDate.getMonth() !== filterDate.getMonth() ||
        pdfDate.getFullYear() !== filterDate.getFullYear()
      ) {
        return false;
      }
    }

    // Template filter
    if (templateFilter && pdf.template !== templateFilter) {
      return false;
    }

    return true;
  });

  if (loading && pdfs.length === 0) {
    return (
      <div className="history-loading">
        <ProgressSpinner />
        <p>Loading PDF history...</p>
      </div>
    );
  }

  return (
    <div className={`pdf-history ${className}`}>
      <Toast ref={toastRef} />
      <ConfirmDialog />

      <Card className="history-card">
        {renderHeader()}
        {renderFilters()}

        <DataTable
          value={filteredPdfs}
          selection={selectedPdfs}
          onSelectionChange={(e) => setSelectedPdfs(e.value)}
          dataKey="filename"
          paginator
          rows={10}
          rowsPerPageOptions={[5, 10, 25, 50]}
          emptyMessage="No PDFs found"
          className="history-table"
          responsiveLayout="scroll"
        >
          <Column selectionMode="multiple" headerStyle={{ width: '3rem' }} />
          <Column
            field="filename"
            header="Filename"
            body={filenameBodyTemplate}
            sortable
          />
          <Column
            field="customer"
            header="Customer"
            sortable
          />
          <Column
            field="template"
            header="Template"
            body={templateBodyTemplate}
            sortable
          />
          <Column
            field="size_bytes"
            header="Size"
            body={sizeBodyTemplate}
            sortable
          />
          <Column
            field="created_at"
            header="Created"
            body={dateBodyTemplate}
            sortable
          />
          <Column
            header="Actions"
            body={actionsBodyTemplate}
            headerStyle={{ width: '12rem', textAlign: 'center' }}
            bodyStyle={{ textAlign: 'center' }}
          />
        </DataTable>
      </Card>
    </div>
  );
};
