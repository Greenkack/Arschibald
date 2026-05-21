/**
 * Matrix Preview Component
 * 
 * Displays preview of price matrix data in table format
 * Task 37: Price Matrix Management
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Toast } from 'primereact/toast';
import { Tag } from 'primereact/tag';
import api from '../../services/api';
import './MatrixPreview.css';

interface MatrixPreviewProps {
  matrixId: number;
  onClose?: () => void;
}

interface MatrixData {
  meta: {
    id: number;
    name: string;
    description: string;
    is_active: boolean;
    pricing_mode: string;
    include_accessories: boolean;
    include_misc: boolean;
    created_at: string;
    updated_at: string;
  };
  rows: Array<{ id: number; position: number; label: string }>;
  columns: Array<{ id: number; position: number; label: string }>;
  cells: Record<string, { value: number | null; raw_input: string | null; data_type: string }>;
}

const MatrixPreview: React.FC<MatrixPreviewProps> = ({ matrixId, onClose }) => {
  const [matrixData, setMatrixData] = useState<MatrixData | null>(null);
  const [loading, setLoading] = useState(false);
  const [tableData, setTableData] = useState<any[]>([]);
  const toastRef = React.useRef<Toast>(null);

  useEffect(() => {
    loadMatrixData();
  }, [matrixId]);

  const loadMatrixData = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/pricing/matrix/${matrixId}`);
      if (response.data.success) {
        const data = response.data.matrix;
        setMatrixData(data);
        buildTableData(data);
      }
    } catch (error: any) {
      toastRef.current?.show({
        severity: 'error',
        summary: 'Fehler',
        detail: 'Matrix-Daten konnten nicht geladen werden',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const buildTableData = (data: MatrixData) => {
    const rows = data.rows.sort((a, b) => a.position - b.position);
    const cols = data.columns.sort((a, b) => a.position - b.position);

    const tableRows = rows.map(row => {
      const rowData: any = {
        rowLabel: row.label,
        rowId: row.id
      };

      cols.forEach(col => {
        const cellKey = `${row.id},${col.id}`;
        const cellData = data.cells[cellKey];
        
        if (cellData) {
          if (cellData.value !== null) {
            // Format number with German locale
            rowData[`col_${col.id}`] = new Intl.NumberFormat('de-DE', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            }).format(cellData.value);
          } else if (cellData.raw_input) {
            rowData[`col_${col.id}`] = cellData.raw_input;
          } else {
            rowData[`col_${col.id}`] = '-';
          }
        } else {
          rowData[`col_${col.id}`] = '-';
        }
      });

      return rowData;
    });

    setTableData(tableRows);
  };

  const formatGermanNumber = (value: number): string => {
    return new Intl.NumberFormat('de-DE', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  if (loading) {
    return (
      <div className="matrix-preview-loading">
        <ProgressSpinner />
        <p>Matrix wird geladen...</p>
      </div>
    );
  }

  if (!matrixData) {
    return (
      <Card title="Matrix-Vorschau">
        <p>Keine Matrix-Daten verfügbar.</p>
      </Card>
    );
  }

  const { meta, columns } = matrixData;

  return (
    <div className="matrix-preview">
      <Toast ref={toastRef} />

      <Card className="matrix-preview-card">
        <div className="matrix-preview-header">
          <div className="matrix-info">
            <h2>🔍 {meta.name}</h2>
            {meta.description && <p className="matrix-description">{meta.description}</p>}
            
            <div className="matrix-meta-tags">
              {meta.is_active && (
                <Tag value="Aktiv" severity="success" icon="pi pi-check" />
              )}
              <Tag 
                value={meta.pricing_mode === 'pauschal' ? 'Pauschal' : 'Additiv'} 
                severity={meta.pricing_mode === 'pauschal' ? 'info' : 'warning'} 
              />
              {meta.include_accessories && (
                <Tag value="Mit Zubehör" severity="info" />
              )}
              {meta.include_misc && (
                <Tag value="Mit Extras" severity="info" />
              )}
            </div>

            <div className="matrix-meta-dates">
              <small>
                <strong>Erstellt:</strong> {new Date(meta.created_at).toLocaleString('de-DE')}
              </small>
              <small>
                <strong>Aktualisiert:</strong> {new Date(meta.updated_at).toLocaleString('de-DE')}
              </small>
            </div>
          </div>

          {onClose && (
            <Button
              icon="pi pi-times"
              className="p-button-rounded p-button-text"
              onClick={onClose}
              tooltip="Schließen"
            />
          )}
        </div>

        <div className="matrix-preview-stats">
          <div className="stat-item">
            <i className="pi pi-list"></i>
            <span>{matrixData.rows.length} Zeilen</span>
          </div>
          <div className="stat-item">
            <i className="pi pi-table"></i>
            <span>{matrixData.columns.length} Spalten</span>
          </div>
          <div className="stat-item">
            <i className="pi pi-th-large"></i>
            <span>{Object.keys(matrixData.cells).length} Zellen</span>
          </div>
        </div>

        <div className="matrix-preview-table">
          <DataTable
            value={tableData}
            scrollable
            scrollHeight="500px"
            className="matrix-data-table"
            emptyMessage="Keine Daten vorhanden"
          >
            <Column
              field="rowLabel"
              header="Modulanzahl"
              frozen
              style={{ minWidth: '150px', fontWeight: 'bold' }}
            />
            {columns.sort((a, b) => a.position - b.position).map(col => (
              <Column
                key={col.id}
                field={`col_${col.id}`}
                header={col.label}
                style={{ minWidth: '150px', textAlign: 'right' }}
              />
            ))}
          </DataTable>
        </div>

        <div className="matrix-preview-footer">
          <p className="matrix-note">
            <i className="pi pi-info-circle"></i>
            Alle Preise sind in Euro (€) angegeben. Zahlen werden im deutschen Format angezeigt (1.234,56).
          </p>
        </div>
      </Card>
    </div>
  );
};

export default MatrixPreview;
