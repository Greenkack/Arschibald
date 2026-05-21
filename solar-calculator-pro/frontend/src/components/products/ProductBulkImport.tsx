/**
 * ProductBulkImport Component - Task 50
 * 
 * Bulk import products from Excel/CSV files with:
 * - File upload
 * - Data preview
 * - Validation
 * - Import progress
 */

import React, { useState, useRef } from 'react';
import { FileUpload, FileUploadHandlerEvent } from 'primereact/fileupload';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { ProgressBar } from 'primereact/progressbar';
import { Message } from 'primereact/message';
import { Panel } from 'primereact/panel';
import { Tag } from 'primereact/tag';
import * as XLSX from 'xlsx';
import './ProductBulkImport.css';

interface ImportRow {
  row: number;
  data: Record<string, any>;
  status: 'pending' | 'valid' | 'invalid' | 'imported' | 'error';
  errors?: string[];
}

interface ProductBulkImportProps {
  onImport: (products: any[]) => Promise<void>;
  onCancel: () => void;
}

const ProductBulkImport: React.FC<ProductBulkImportProps> = ({
  onImport,
  onCancel
}) => {
  const [importData, setImportData] = useState<ImportRow[]>([]);
  const [importing, setImporting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [importResults, setImportResults] = useState<{
    success: number;
    failed: number;
    total: number;
  } | null>(null);
  const fileUploadRef = useRef<FileUpload>(null);

  const handleFileSelect = async (event: FileUploadHandlerEvent) => {
    const file = event.files[0];
    if (!file) return;

    try {
      const data = await readFile(file);
      const rows = parseData(data);
      const validatedRows = validateRows(rows);
      setImportData(validatedRows);
    } catch (error) {
      console.error('Error reading file:', error);
    }
  };

  const readFile = (file: File): Promise<any[][]> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const data = e.target?.result;
          const workbook = XLSX.read(data, { type: 'binary' });
          const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
          const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });
          resolve(jsonData as any[][]);
        } catch (error) {
          reject(error);
        }
      };
      
      reader.onerror = reject;
      reader.readAsBinaryString(file);
    });
  };

  const parseData = (data: any[][]): ImportRow[] => {
    if (data.length < 2) return [];

    const headers = data[0].map(h => String(h).toLowerCase().trim());
    const rows: ImportRow[] = [];

    for (let i = 1; i < data.length; i++) {
      const rowData: Record<string, any> = {};
      
      headers.forEach((header, index) => {
        rowData[header] = data[i][index];
      });

      rows.push({
        row: i,
        data: rowData,
        status: 'pending'
      });
    }

    return rows;
  };

  const validateRows = (rows: ImportRow[]): ImportRow[] => {
    return rows.map(row => {
      const errors: string[] = [];

      // Required fields
      if (!row.data.category) {
        errors.push('Category is required');
      }
      if (!row.data.model_name && !row.data['model name']) {
        errors.push('Model name is required');
      }

      // Price validation
      const price = row.data.price_euro || row.data.price;
      if (price !== undefined && price !== null) {
        const numPrice = Number(price);
        if (isNaN(numPrice) || numPrice < 0) {
          errors.push('Price must be a positive number');
        }
      }

      return {
        ...row,
        status: errors.length > 0 ? 'invalid' : 'valid',
        errors: errors.length > 0 ? errors : undefined
      };
    });
  };

  const handleImport = async () => {
    const validRows = importData.filter(row => row.status === 'valid');
    
    if (validRows.length === 0) {
      return;
    }

    setImporting(true);
    setProgress(0);

    const results = {
      success: 0,
      failed: 0,
      total: validRows.length
    };

    const products = validRows.map(row => ({
      category: row.data.category,
      model_name: row.data.model_name || row.data['model name'],
      brand: row.data.brand,
      price_euro: row.data.price_euro || row.data.price,
      description: row.data.description,
      specifications: row.data.specifications ? 
        (typeof row.data.specifications === 'string' ? 
          JSON.parse(row.data.specifications) : 
          row.data.specifications) : 
        {}
    }));

    try {
      await onImport(products);
      results.success = products.length;
      
      // Update row statuses
      setImportData(prev => prev.map(row => 
        row.status === 'valid' ? { ...row, status: 'imported' } : row
      ));
    } catch (error) {
      console.error('Import error:', error);
      results.failed = products.length;
      
      // Update row statuses
      setImportData(prev => prev.map(row => 
        row.status === 'valid' ? { ...row, status: 'error', errors: ['Import failed'] } : row
      ));
    }

    setImportResults(results);
    setImporting(false);
    setProgress(100);
  };

  const handleClear = () => {
    setImportData([]);
    setImportResults(null);
    setProgress(0);
    if (fileUploadRef.current) {
      fileUploadRef.current.clear();
    }
  };

  const statusBodyTemplate = (rowData: ImportRow) => {
    const statusConfig = {
      pending: { severity: 'info', label: 'Pending' },
      valid: { severity: 'success', label: 'Valid' },
      invalid: { severity: 'danger', label: 'Invalid' },
      imported: { severity: 'success', label: 'Imported' },
      error: { severity: 'danger', label: 'Error' }
    };

    const config = statusConfig[rowData.status];
    return <Tag severity={config.severity as any} value={config.label} />;
  };

  const errorsBodyTemplate = (rowData: ImportRow) => {
    if (!rowData.errors || rowData.errors.length === 0) {
      return null;
    }

    return (
      <ul className="error-list">
        {rowData.errors.map((error, index) => (
          <li key={index}>{error}</li>
        ))}
      </ul>
    );
  };

  const validCount = importData.filter(row => row.status === 'valid').length;
  const invalidCount = importData.filter(row => row.status === 'invalid').length;

  return (
    <div className="product-bulk-import">
      <div className="import-header">
        <h2>Bulk Import Products</h2>
        <p>Upload an Excel or CSV file to import multiple products at once</p>
      </div>

      <Panel header="Upload File" className="upload-section">
        <FileUpload
          ref={fileUploadRef}
          mode="basic"
          name="file"
          accept=".xlsx,.xls,.csv"
          maxFileSize={10000000}
          customUpload
          uploadHandler={handleFileSelect}
          auto
          chooseLabel="Choose File"
          disabled={importing}
        />
        
        <Message 
          severity="info" 
          text="Supported formats: Excel (.xlsx, .xls) and CSV (.csv). Maximum file size: 10MB" 
        />

        <div className="template-download">
          <p>Don't have a template? Download our sample template:</p>
          <Button
            label="Download Template"
            icon="pi pi-download"
            className="p-button-outlined"
            onClick={() => {
              // Create sample template
              const template = [
                ['category', 'model_name', 'brand', 'price_euro', 'description'],
                ['Solar Module', 'Example Module 400W', 'Example Brand', '250.00', 'High efficiency solar module'],
              ];
              const ws = XLSX.utils.aoa_to_sheet(template);
              const wb = XLSX.utils.book_new();
              XLSX.utils.book_append_sheet(wb, ws, 'Products');
              XLSX.writeFile(wb, 'product_import_template.xlsx');
            }}
          />
        </div>
      </Panel>

      {importData.length > 0 && (
        <>
          <Panel header="Import Preview" className="preview-section">
            <div className="import-stats">
              <div className="stat-item">
                <span className="stat-label">Total Rows:</span>
                <span className="stat-value">{importData.length}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Valid:</span>
                <span className="stat-value valid">{validCount}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Invalid:</span>
                <span className="stat-value invalid">{invalidCount}</span>
              </div>
            </div>

            <DataTable
              value={importData}
              paginator
              rows={10}
              className="import-table"
              emptyMessage="No data to import"
            >
              <Column field="row" header="Row" style={{ width: '80px' }} />
              <Column 
                field="data.category" 
                header="Category" 
                style={{ width: '150px' }} 
              />
              <Column 
                field="data.model_name" 
                header="Model Name" 
                body={(row) => row.data.model_name || row.data['model name']}
              />
              <Column 
                field="data.brand" 
                header="Brand" 
                style={{ width: '150px' }} 
              />
              <Column 
                field="data.price_euro" 
                header="Price" 
                style={{ width: '120px' }}
                body={(row) => {
                  const price = row.data.price_euro || row.data.price;
                  return price ? `€${Number(price).toFixed(2)}` : '-';
                }}
              />
              <Column 
                header="Status" 
                body={statusBodyTemplate} 
                style={{ width: '120px' }} 
              />
              <Column 
                header="Errors" 
                body={errorsBodyTemplate} 
                style={{ width: '200px' }} 
              />
            </DataTable>
          </Panel>

          {importing && (
            <div className="import-progress">
              <ProgressBar value={progress} />
              <p>Importing products...</p>
            </div>
          )}

          {importResults && (
            <Message
              severity={importResults.failed === 0 ? 'success' : 'warn'}
              text={`Import completed: ${importResults.success} successful, ${importResults.failed} failed`}
            />
          )}

          <div className="import-actions">
            <Button
              label="Clear"
              icon="pi pi-times"
              className="p-button-secondary"
              onClick={handleClear}
              disabled={importing}
            />
            <Button
              label="Cancel"
              icon="pi pi-ban"
              className="p-button-secondary"
              onClick={onCancel}
              disabled={importing}
            />
            <Button
              label={`Import ${validCount} Products`}
              icon="pi pi-upload"
              onClick={handleImport}
              disabled={validCount === 0 || importing}
              loading={importing}
            />
          </div>
        </>
      )}
    </div>
  );
};

export default ProductBulkImport;
