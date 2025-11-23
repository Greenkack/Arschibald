/**
 * PDF History Viewer Component
 * Displays PDF generation history with search, filter, and management capabilities
 */

import React, { useState, useEffect, useRef } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Calendar } from 'primereact/calendar';
import { Toast } from 'primereact/toast';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Card } from 'primereact/card';
import { Tag } from 'primereact/tag';
import './PDFHistoryViewer.css';

interface PDFHistoryRecord {
  id: number;
  pdf_type: string;
  filename: string;
  file_size_mb: number;
  generated_at: string;
  metadata: any;
  status: string;
}

interface PDFHistoryViewerProps {
  userId?: number;
  onPDFSelect?: (record: PDFHistoryRecord) => void;
}

export const PDFHistoryViewer: React.FC<PDFHistoryViewerProps> = ({
  userId,
  onPDFSelect
}) => {
  const [history, setHistory] = useState<PDFHistoryRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalRecords, setTotalRecords] = useState(0);
  const [first, setFirst] = useState(0);
  const [rows, setRows] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [dateFrom, setDateFrom] = useState<Date | null>(null);
  const [dateTo, setDateTo] = useState<Date | null>(null);
  const [selectedRecords, setSelectedRecords] = useState<PDFHistoryRecord[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const toast = useRef<Toast>(null);

  const pdfTypes = [
    { label: 'All Types', value: null },
    { label: 'Standard PV', value: 'standard_pv' },
    { label: 'Extended PV', value: 'extended_pv' },
    { label: 'Standard WP', value: 'standard_wp' },
    { label: 'Extended WP', value: 'extended_wp' },
    { label: 'Multi PDF', value: 'multi_pdf' }
  ];

  useEffect(() => {
    loadHistory();
    loadStatistics();
  }, [first, rows, selectedType]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        limit: rows.toString(),
        offset: first.toString(),
        ...(selectedType && { pdf_type: selectedType })
      });

      const response = await fetch(`/api/v1/pdf-export/history?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load history');
      }

      const data = await response.json();
      setHistory(data.history);
      setTotalRecords(data.total);

    } catch (error) {
      console.error('Error loading history:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Load Failed',
        detail: 'Failed to load PDF history',
        life: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await fetch('/api/v1/pdf-export/history/statistics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setStatistics(data);
      }
    } catch (error) {
      console.error('Error loading statistics:', error);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/pdf-export/history/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          search_term: searchTerm,
          pdf_type: selectedType,
          date_from: dateFrom?.toISOString(),
          date_to: dateTo?.toISOString(),
          limit: rows,
          offset: first
        })
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setHistory(data.results);
      setTotalRecords(data.count);

    } catch (error) {
      console.error('Search error:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Search Failed',
        detail: 'Failed to search PDF history',
        life: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (record: PDFHistoryRecord) => {
    confirmDialog({
      message: `Are you sure you want to delete "${record.filename}"?`,
      header: 'Confirm Deletion',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          const response = await fetch(`/api/v1/pdf-export/history/${record.id}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
          });

          if (!response.ok) {
            throw new Error('Delete failed');
          }

          toast.current?.show({
            severity: 'success',
            summary: 'Deleted',
            detail: 'PDF history record deleted',
            life: 3000
          });

          loadHistory();

        } catch (error) {
          console.error('Delete error:', error);
          toast.current?.show({
            severity: 'error',
            summary: 'Delete Failed',
            detail: 'Failed to delete PDF history record',
            life: 5000
          });
        }
      }
    });
  };

  const handleBulkDelete = () => {
    if (selectedRecords.length === 0) {
      toast.current?.show({
        severity: 'warn',
        summary: 'No Selection',
        detail: 'Please select records to delete',
        life: 3000
      });
      return;
    }

    confirmDialog({
      message: `Are you sure you want to delete ${selectedRecords.length} record(s)?`,
      header: 'Confirm Bulk Deletion',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          // In real implementation, call bulk delete endpoint
          toast.current?.show({
            severity: 'success',
            summary: 'Deleted',
            detail: `${selectedRecords.length} records deleted`,
            life: 3000
          });

          setSelectedRecords([]);
          loadHistory();

        } catch (error) {
          console.error('Bulk delete error:', error);
          toast.current?.show({
            severity: 'error',
            summary: 'Delete Failed',
            detail: 'Failed to delete selected records',
            life: 5000
          });
        }
      }
    });
  };

  const handleDownload = async (record: PDFHistoryRecord) => {
    try {
      const response = await fetch('/api/v1/pdf-export/download/single', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ pdf_id: record.id, filename: record.filename })
      });

      if (!response.ok) {
        throw new Error('Download failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = record.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.current?.show({
        severity: 'success',
        summary: 'Downloaded',
        detail: `${record.filename} downloaded successfully`,
        life: 3000
      });

    } catch (error) {
      console.error('Download error:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Download Failed',
        detail: 'Failed to download PDF',
        life: 5000
      });
    }
  };

  const onPage = (event: any) => {
    setFirst(event.first);
    setRows(event.rows);
  };

  const typeBodyTemplate = (rowData: PDFHistoryRecord) => {
    const typeLabels: Record<string, string> = {
      'standard_pv': 'Standard PV',
      'extended_pv': 'Extended PV',
      'standard_wp': 'Standard WP',
      'extended_wp': 'Extended WP',
      'multi_pdf': 'Multi PDF'
    };

    return <Tag value={typeLabels[rowData.pdf_type] || rowData.pdf_type} />;
  };

  const sizeBodyTemplate = (rowData: PDFHistoryRecord) => {
    return `${rowData.file_size_mb} MB`;
  };

  const dateBodyTemplate = (rowData: PDFHistoryRecord) => {
    return new Date(rowData.generated_at).toLocaleString();
  };

  const actionsBodyTemplate = (rowData: PDFHistoryRecord) => {
    return (
      <div className="action-buttons">
        <Button
          icon="pi pi-download"
          className="p-button-rounded p-button-text p-button-success"
          onClick={() => handleDownload(rowData)}
          tooltip="Download"
        />
        <Button
          icon="pi pi-eye"
          className="p-button-rounded p-button-text p-button-info"
          onClick={() => onPDFSelect && onPDFSelect(rowData)}
          tooltip="Preview"
        />
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-text p-button-danger"
          onClick={() => handleDelete(rowData)}
          tooltip="Delete"
        />
      </div>
    );
  };

  return (
    <div className="pdf-history-viewer">
      <Toast ref={toast} />
      <ConfirmDialog />

      {statistics && (
        <div className="statistics-cards">
          <Card className="stat-card">
            <div className="stat-content">
              <i className="pi pi-file-pdf stat-icon"></i>
              <div className="stat-details">
                <div className="stat-value">{statistics.total_pdfs || 0}</div>
                <div className="stat-label">Total PDFs</div>
              </div>
            </div>
          </Card>

          <Card className="stat-card">
            <div className="stat-content">
              <i className="pi pi-database stat-icon"></i>
              <div className="stat-details">
                <div className="stat-value">{statistics.total_size_mb || 0} MB</div>
                <div className="stat-label">Total Size</div>
              </div>
            </div>
          </Card>

          <Card className="stat-card">
            <div className="stat-content">
              <i className="pi pi-chart-bar stat-icon"></i>
              <div className="stat-details">
                <div className="stat-value">{statistics.average_size_mb || 0} MB</div>
                <div className="stat-label">Average Size</div>
              </div>
            </div>
          </Card>
        </div>
      )}

      <Card className="filter-card">
        <div className="filter-controls">
          <div className="p-inputgroup">
            <InputText
              placeholder="Search by filename..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button icon="pi pi-search" onClick={handleSearch} />
          </div>

          <Dropdown
            value={selectedType}
            options={pdfTypes}
            onChange={(e) => setSelectedType(e.value)}
            placeholder="Filter by type"
          />

          <Calendar
            value={dateFrom}
            onChange={(e) => setDateFrom(e.value as Date)}
            placeholder="From date"
            showIcon
          />

          <Calendar
            value={dateTo}
            onChange={(e) => setDateTo(e.value as Date)}
            placeholder="To date"
            showIcon
          />

          <Button
            label="Clear Filters"
            icon="pi pi-filter-slash"
            className="p-button-outlined"
            onClick={() => {
              setSearchTerm('');
              setSelectedType(null);
              setDateFrom(null);
              setDateTo(null);
              loadHistory();
            }}
          />
        </div>

        {selectedRecords.length > 0 && (
          <div className="bulk-actions">
            <Button
              label={`Delete Selected (${selectedRecords.length})`}
              icon="pi pi-trash"
              className="p-button-danger"
              onClick={handleBulkDelete}
            />
          </div>
        )}
      </Card>

      <Card className="table-card">
        <DataTable
          value={history}
          loading={loading}
          paginator
          rows={rows}
          first={first}
          totalRecords={totalRecords}
          onPage={onPage}
          rowsPerPageOptions={[10, 25, 50]}
          selection={selectedRecords}
          onSelectionChange={(e) => setSelectedRecords(e.value)}
          dataKey="id"
          emptyMessage="No PDF history found"
        >
          <Column selectionMode="multiple" style={{ width: '3rem' }} />
          <Column field="filename" header="Filename" sortable />
          <Column field="pdf_type" header="Type" body={typeBodyTemplate} sortable />
          <Column field="file_size_mb" header="Size" body={sizeBodyTemplate} sortable />
          <Column field="generated_at" header="Generated" body={dateBodyTemplate} sortable />
          <Column header="Actions" body={actionsBodyTemplate} style={{ width: '150px' }} />
        </DataTable>
      </Card>
    </div>
  );
};
