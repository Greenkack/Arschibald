/**
 * Notification History Component
 * 
 * Displays a list of recent notifications with filtering and search capabilities.
 */

import React, { useEffect, useState } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Tag } from 'primereact/tag';
import { Message } from 'primereact/message';
import { useNotifications } from '../../hooks/useNotifications';
import './NotificationHistory.css';

interface NotificationHistoryItem {
  title: string;
  body: string;
  type: string;
  timestamp: string;
  data?: any;
}

export const NotificationHistory: React.FC = () => {
  const { isSupported, history, loadHistory, clearHistory } = useNotifications();
  const [filteredHistory, setFilteredHistory] = useState<NotificationHistoryItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string | null>(null);

  useEffect(() => {
    if (isSupported) {
      loadHistory(50);
    }
  }, [isSupported, loadHistory]);

  useEffect(() => {
    let filtered = history;

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.body.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply type filter
    if (typeFilter) {
      filtered = filtered.filter(item => item.type === typeFilter);
    }

    setFilteredHistory(filtered);
  }, [history, searchTerm, typeFilter]);

  if (!isSupported) {
    return (
      <Card title="Benachrichtigungsverlauf">
        <Message 
          severity="warn" 
          text="Benachrichtigungen werden in dieser Umgebung nicht unterstützt." 
        />
      </Card>
    );
  }

  const typeOptions = [
    { label: 'Alle', value: null },
    { label: 'Berechnung', value: 'calculation' },
    { label: 'Update', value: 'update' },
    { label: 'Fehler', value: 'error' },
    { label: 'Warnung', value: 'warning' },
    { label: 'Info', value: 'info' },
    { label: 'PDF', value: 'pdf' },
    { label: 'Export', value: 'export' },
    { label: 'Backup', value: 'backup' },
    { label: 'Sync', value: 'sync' },
    { label: 'Benutzerdefiniert', value: 'custom' }
  ];

  const getTypeSeverity = (type: string): 'success' | 'info' | 'warning' | 'danger' => {
    switch (type) {
      case 'error':
        return 'danger';
      case 'warning':
        return 'warning';
      case 'calculation':
      case 'pdf':
      case 'export':
      case 'backup':
      case 'sync':
        return 'success';
      default:
        return 'info';
    }
  };

  const getTypeLabel = (type: string): string => {
    const option = typeOptions.find(opt => opt.value === type);
    return option ? option.label : type;
  };

  const typeBodyTemplate = (rowData: NotificationHistoryItem) => {
    return (
      <Tag 
        value={getTypeLabel(rowData.type)} 
        severity={getTypeSeverity(rowData.type)}
      />
    );
  };

  const timestampBodyTemplate = (rowData: NotificationHistoryItem) => {
    const date = new Date(rowData.timestamp);
    return (
      <span>
        {date.toLocaleDateString('de-DE')} {date.toLocaleTimeString('de-DE')}
      </span>
    );
  };

  const handleClearHistory = async () => {
    if (window.confirm('Möchten Sie den gesamten Benachrichtigungsverlauf löschen?')) {
      await clearHistory();
    }
  };

  const header = (
    <div className="history-header">
      <div className="search-section">
        <span className="p-input-icon-left">
          <i className="pi pi-search" />
          <InputText
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Suchen..."
          />
        </span>
        <Dropdown
          value={typeFilter}
          options={typeOptions}
          onChange={(e) => setTypeFilter(e.value)}
          placeholder="Typ filtern"
          className="type-filter"
        />
      </div>
      <div className="action-section">
        <Button
          label="Verlauf löschen"
          icon="pi pi-trash"
          onClick={handleClearHistory}
          className="p-button-danger p-button-outlined"
          disabled={history.length === 0}
        />
        <Button
          label="Aktualisieren"
          icon="pi pi-refresh"
          onClick={() => loadHistory(50)}
          className="p-button-outlined"
        />
      </div>
    </div>
  );

  return (
    <div className="notification-history">
      <Card title="Benachrichtigungsverlauf">
        {history.length === 0 ? (
          <Message 
            severity="info" 
            text="Keine Benachrichtigungen im Verlauf." 
          />
        ) : (
          <DataTable
            value={filteredHistory}
            paginator
            rows={10}
            rowsPerPageOptions={[10, 25, 50]}
            header={header}
            emptyMessage="Keine Benachrichtigungen gefunden."
            className="notification-table"
          >
            <Column
              field="type"
              header="Typ"
              body={typeBodyTemplate}
              sortable
              style={{ width: '120px' }}
            />
            <Column
              field="title"
              header="Titel"
              sortable
              style={{ width: '200px' }}
            />
            <Column
              field="body"
              header="Nachricht"
              sortable
            />
            <Column
              field="timestamp"
              header="Zeitstempel"
              body={timestampBodyTemplate}
              sortable
              style={{ width: '180px' }}
            />
          </DataTable>
        )}
      </Card>
    </div>
  );
};
