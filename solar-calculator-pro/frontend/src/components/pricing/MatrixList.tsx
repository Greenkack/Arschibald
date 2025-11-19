/**
 * Matrix List Component
 * 
 * Displays list of all price matrices with management actions
 * Task 37: Price Matrix Management
 */

import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Tag } from 'primereact/tag';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import './MatrixList.css';

interface Matrix {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  pricing_mode: string;
  include_accessories: boolean;
  include_misc: boolean;
  created_at: string;
  updated_at: string;
}

interface MatrixListProps {
  onMatrixSelect?: (matrix: Matrix) => void;
  onMatrixActivate?: (matrix: Matrix) => void;
  onRefresh?: () => void;
}

const MatrixList: React.FC<MatrixListProps> = ({ 
  onMatrixSelect, 
  onMatrixActivate,
  onRefresh 
}) => {
  const [matrices, setMatrices] = useState<Matrix[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedMatrix, setSelectedMatrix] = useState<Matrix | null>(null);
  const toastRef = React.useRef<Toast>(null);

  useEffect(() => {
    loadMatrices();
  }, []);

  const loadMatrices = async () => {
    setLoading(true);
    try {
      const response = await api.get('/pricing/matrix');
      if (response.data.success) {
        setMatrices(response.data.matrices || []);
      }
    } catch (error: any) {
      toastRef.current?.show({
        severity: 'error',
        summary: 'Fehler',
        detail: 'Matrizen konnten nicht geladen werden',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async (matrix: Matrix) => {
    try {
      const response = await api.put(`/pricing/matrix/${matrix.id}/activate`);
      if (response.data.success) {
        toastRef.current?.show({
          severity: 'success',
          summary: 'Erfolg',
          detail: `Matrix "${matrix.name}" wurde aktiviert`,
          life: 3000
        });
        await loadMatrices();
        if (onMatrixActivate) {
          onMatrixActivate(matrix);
        }
        if (onRefresh) {
          onRefresh();
        }
      }
    } catch (error: any) {
      toastRef.current?.show({
        severity: 'error',
        summary: 'Fehler',
        detail: 'Matrix konnte nicht aktiviert werden',
        life: 3000
      });
    }
  };

  const handleDelete = (matrix: Matrix) => {
    confirmDialog({
      message: `Möchten Sie die Matrix "${matrix.name}" wirklich löschen?`,
      header: 'Löschen bestätigen',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Ja, löschen',
      rejectLabel: 'Abbrechen',
      accept: async () => {
        try {
          const response = await api.delete(`/pricing/matrix/${matrix.id}`);
          if (response.data.success) {
            toastRef.current?.show({
              severity: 'success',
              summary: 'Erfolg',
              detail: `Matrix "${matrix.name}" wurde gelöscht`,
              life: 3000
            });
            await loadMatrices();
            if (onRefresh) {
              onRefresh();
            }
          }
        } catch (error: any) {
          toastRef.current?.show({
            severity: 'error',
            summary: 'Fehler',
            detail: 'Matrix konnte nicht gelöscht werden',
            life: 3000
          });
        }
      }
    });
  };

  const handleView = (matrix: Matrix) => {
    setSelectedMatrix(matrix);
    if (onMatrixSelect) {
      onMatrixSelect(matrix);
    }
  };

  const handleExport = async (matrix: Matrix) => {
    try {
      const response = await api.post('/pricing/matrix/export/csv', {
        matrix_id: matrix.id,
        delimiter: ';'
      });
      
      if (response.data.success) {
        // Create download link
        const blob = new Blob([response.data.csv_content], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `matrix_${matrix.name}_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        toastRef.current?.show({
          severity: 'success',
          summary: 'Erfolg',
          detail: `Matrix "${matrix.name}" wurde exportiert`,
          life: 3000
        });
      }
    } catch (error: any) {
      toastRef.current?.show({
        severity: 'error',
        summary: 'Fehler',
        detail: 'Matrix konnte nicht exportiert werden',
        life: 3000
      });
    }
  };

  const statusBodyTemplate = (rowData: Matrix) => {
    return rowData.is_active ? (
      <Tag value="Aktiv" severity="success" icon="pi pi-check" />
    ) : (
      <Tag value="Inaktiv" severity="secondary" />
    );
  };

  const pricingModeBodyTemplate = (rowData: Matrix) => {
    const mode = rowData.pricing_mode === 'pauschal' ? 'Pauschal' : 'Additiv';
    const severity = rowData.pricing_mode === 'pauschal' ? 'info' : 'warning';
    return <Tag value={mode} severity={severity} />;
  };

  const dateBodyTemplate = (rowData: Matrix, field: 'created_at' | 'updated_at') => {
    const date = new Date(rowData[field]);
    return date.toLocaleString('de-DE');
  };

  const actionsBodyTemplate = (rowData: Matrix) => {
    return (
      <div className="matrix-actions">
        <Button
          icon="pi pi-eye"
          className="p-button-rounded p-button-text p-button-info"
          onClick={() => handleView(rowData)}
          tooltip="Vorschau"
          tooltipOptions={{ position: 'top' }}
        />
        {!rowData.is_active && (
          <Button
            icon="pi pi-check"
            className="p-button-rounded p-button-text p-button-success"
            onClick={() => handleActivate(rowData)}
            tooltip="Aktivieren"
            tooltipOptions={{ position: 'top' }}
          />
        )}
        <Button
          icon="pi pi-download"
          className="p-button-rounded p-button-text p-button-help"
          onClick={() => handleExport(rowData)}
          tooltip="Exportieren"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-text p-button-danger"
          onClick={() => handleDelete(rowData)}
          tooltip="Löschen"
          tooltipOptions={{ position: 'top' }}
          disabled={rowData.is_active}
        />
      </div>
    );
  };

  return (
    <div className="matrix-list">
      <Toast ref={toastRef} />
      <ConfirmDialog />
      
      <div className="matrix-list-header">
        <h3>📋 Preismatrizen</h3>
        <Button
          icon="pi pi-refresh"
          label="Aktualisieren"
          onClick={loadMatrices}
          loading={loading}
          className="p-button-outlined"
        />
      </div>

      <DataTable
        value={matrices}
        loading={loading}
        paginator
        rows={10}
        rowsPerPageOptions={[5, 10, 25, 50]}
        emptyMessage="Keine Matrizen vorhanden"
        selectionMode="single"
        selection={selectedMatrix}
        onSelectionChange={(e) => setSelectedMatrix(e.value)}
        dataKey="id"
        className="matrix-table"
      >
        <Column
          field="name"
          header="Name"
          sortable
          style={{ minWidth: '200px' }}
        />
        <Column
          field="description"
          header="Beschreibung"
          style={{ minWidth: '250px' }}
        />
        <Column
          header="Status"
          body={statusBodyTemplate}
          sortable
          sortField="is_active"
          style={{ width: '120px' }}
        />
        <Column
          header="Modus"
          body={pricingModeBodyTemplate}
          sortable
          sortField="pricing_mode"
          style={{ width: '120px' }}
        />
        <Column
          header="Erstellt"
          body={(rowData) => dateBodyTemplate(rowData, 'created_at')}
          sortable
          sortField="created_at"
          style={{ width: '180px' }}
        />
        <Column
          header="Aktualisiert"
          body={(rowData) => dateBodyTemplate(rowData, 'updated_at')}
          sortable
          sortField="updated_at"
          style={{ width: '180px' }}
        />
        <Column
          header="Aktionen"
          body={actionsBodyTemplate}
          style={{ width: '200px' }}
        />
      </DataTable>
    </div>
  );
};

export default MatrixList;
