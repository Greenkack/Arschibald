/**
 * Matrix Version History Component
 * 
 * Displays version history and allows comparison between versions
 * Task 37: Price Matrix Management
 */

import React, { useState, useEffect } from 'react';
import { Card } from 'primereact/card';
import { Timeline } from 'primereact/timeline';
import { Button } from 'primereact/button';
import { Tag } from 'primereact/tag';
import { Dialog } from 'primereact/dialog';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import './MatrixVersionHistory.css';

interface MatrixVersion {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  pricing_mode: string;
  row_count?: number;
  column_count?: number;
  cell_count?: number;
}

interface MatrixVersionHistoryProps {
  matrixId?: number;
}

const MatrixVersionHistory: React.FC<MatrixVersionHistoryProps> = ({ matrixId }) => {
  const [versions, setVersions] = useState<MatrixVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState<MatrixVersion | null>(null);
  const [showCompareDialog, setShowCompareDialog] = useState(false);
  const toastRef = React.useRef<Toast>(null);

  useEffect(() => {
    loadVersionHistory();
  }, [matrixId]);

  const loadVersionHistory = async () => {
    setLoading(true);
    try {
      const response = await api.get('/pricing/matrix');
      if (response.data.success) {
        let matrices = response.data.matrices || [];
        
        // If matrixId is provided, filter related versions
        // For now, we show all matrices as "versions"
        // In a real implementation, you'd have a proper versioning system
        
        // Sort by updated_at descending (newest first)
        matrices.sort((a: MatrixVersion, b: MatrixVersion) => {
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
        });
        
        setVersions(matrices);
      }
    } catch (error: any) {
      toastRef.current?.show({
        severity: 'error',
        summary: 'Fehler',
        detail: 'Versionshistorie konnte nicht geladen werden',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async (version: MatrixVersion) => {
    try {
      // In a real implementation, this would restore a specific version
      // For now, we just activate the matrix
      const response = await api.put(`/pricing/matrix/${version.id}/activate`);
      if (response.data.success) {
        toastRef.current?.show({
          severity: 'success',
          summary: 'Erfolg',
          detail: `Version "${version.name}" wurde wiederhergestellt`,
          life: 3000
        });
        await loadVersionHistory();
      }
    } catch (error: any) {
      toastRef.current?.show({
        severity: 'error',
        summary: 'Fehler',
        detail: 'Version konnte nicht wiederhergestellt werden',
        life: 3000
      });
    }
  };

  const handleCompare = (version: MatrixVersion) => {
    setSelectedVersion(version);
    setShowCompareDialog(true);
  };

  const customizedMarker = (item: MatrixVersion) => {
    return (
      <span className={`custom-marker ${item.is_active ? 'active' : ''}`}>
        <i className={item.is_active ? 'pi pi-check' : 'pi pi-circle'}></i>
      </span>
    );
  };

  const customizedContent = (item: MatrixVersion) => {
    const updatedDate = new Date(item.updated_at);
    const createdDate = new Date(item.created_at);
    const isNew = (Date.now() - createdDate.getTime()) < 24 * 60 * 60 * 1000; // Less than 24 hours

    return (
      <Card className="version-card">
        <div className="version-header">
          <div className="version-title">
            <h4>{item.name}</h4>
            {item.is_active && (
              <Tag value="Aktiv" severity="success" icon="pi pi-check" />
            )}
            {isNew && (
              <Tag value="Neu" severity="info" icon="pi pi-star" />
            )}
          </div>
          <div className="version-actions">
            {!item.is_active && (
              <Button
                icon="pi pi-replay"
                label="Wiederherstellen"
                className="p-button-sm p-button-outlined"
                onClick={() => handleRestore(item)}
                tooltip="Diese Version aktivieren"
              />
            )}
            <Button
              icon="pi pi-eye"
              className="p-button-sm p-button-outlined p-button-secondary"
              onClick={() => handleCompare(item)}
              tooltip="Details anzeigen"
            />
          </div>
        </div>

        {item.description && (
          <p className="version-description">{item.description}</p>
        )}

        <div className="version-meta">
          <div className="meta-item">
            <i className="pi pi-calendar"></i>
            <span>{updatedDate.toLocaleString('de-DE')}</span>
          </div>
          <div className="meta-item">
            <i className="pi pi-tag"></i>
            <span>{item.pricing_mode === 'pauschal' ? 'Pauschal' : 'Additiv'}</span>
          </div>
        </div>

        {(item.row_count || item.column_count || item.cell_count) && (
          <div className="version-stats">
            {item.row_count && (
              <span className="stat-badge">
                <i className="pi pi-list"></i> {item.row_count} Zeilen
              </span>
            )}
            {item.column_count && (
              <span className="stat-badge">
                <i className="pi pi-table"></i> {item.column_count} Spalten
              </span>
            )}
            {item.cell_count && (
              <span className="stat-badge">
                <i className="pi pi-th-large"></i> {item.cell_count} Zellen
              </span>
            )}
          </div>
        )}
      </Card>
    );
  };

  return (
    <div className="matrix-version-history">
      <Toast ref={toastRef} />

      <Card title="📜 Versionshistorie" className="history-card">
        {loading ? (
          <div className="loading-state">
            <i className="pi pi-spin pi-spinner" style={{ fontSize: '2rem' }}></i>
            <p>Lade Versionshistorie...</p>
          </div>
        ) : versions.length === 0 ? (
          <div className="empty-state">
            <i className="pi pi-inbox" style={{ fontSize: '3rem', color: 'var(--text-color-secondary)' }}></i>
            <p>Keine Versionen vorhanden</p>
          </div>
        ) : (
          <Timeline
            value={versions}
            align="alternate"
            className="version-timeline"
            marker={customizedMarker}
            content={customizedContent}
          />
        )}
      </Card>

      <Dialog
        header={selectedVersion ? `Details: ${selectedVersion.name}` : 'Version Details'}
        visible={showCompareDialog}
        style={{ width: '50vw' }}
        onHide={() => setShowCompareDialog(false)}
        breakpoints={{ '960px': '75vw', '641px': '90vw' }}
      >
        {selectedVersion && (
          <div className="version-details">
            <div className="detail-row">
              <strong>Name:</strong>
              <span>{selectedVersion.name}</span>
            </div>
            <div className="detail-row">
              <strong>Beschreibung:</strong>
              <span>{selectedVersion.description || 'Keine Beschreibung'}</span>
            </div>
            <div className="detail-row">
              <strong>Status:</strong>
              <span>
                {selectedVersion.is_active ? (
                  <Tag value="Aktiv" severity="success" />
                ) : (
                  <Tag value="Inaktiv" severity="secondary" />
                )}
              </span>
            </div>
            <div className="detail-row">
              <strong>Preismodus:</strong>
              <span>
                <Tag 
                  value={selectedVersion.pricing_mode === 'pauschal' ? 'Pauschal' : 'Additiv'} 
                  severity={selectedVersion.pricing_mode === 'pauschal' ? 'info' : 'warning'} 
                />
              </span>
            </div>
            <div className="detail-row">
              <strong>Erstellt:</strong>
              <span>{new Date(selectedVersion.created_at).toLocaleString('de-DE')}</span>
            </div>
            <div className="detail-row">
              <strong>Aktualisiert:</strong>
              <span>{new Date(selectedVersion.updated_at).toLocaleString('de-DE')}</span>
            </div>
          </div>
        )}
      </Dialog>
    </div>
  );
};

export default MatrixVersionHistory;
