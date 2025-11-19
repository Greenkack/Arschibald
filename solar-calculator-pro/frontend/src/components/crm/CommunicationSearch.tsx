import React, { useState } from 'react';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Dropdown } from 'primereact/dropdown';
import { Calendar } from 'primereact/calendar';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Tag } from 'primereact/tag';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import './CommunicationSearch.css';

interface SearchResult {
  id: number;
  customer_id: number;
  activity_type: string;
  title: string;
  content: string;
  created_at: string;
  created_by?: string;
  is_important: boolean;
}

interface CommunicationSearchProps {
  customerId?: number;
}

export const CommunicationSearch: React.FC<CommunicationSearchProps> = ({ customerId }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activityType, setActivityType] = useState<string | null>(null);
  const [dateFrom, setDateFrom] = useState<Date | null>(null);
  const [dateTo, setDateTo] = useState<Date | null>(null);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const toast = React.useRef<Toast>(null);

  const activityTypes = [
    { label: 'All Types', value: null },
    { label: 'Email', value: 'email' },
    { label: 'Call', value: 'call' },
    { label: 'Meeting', value: 'meeting' },
    { label: 'Note', value: 'note' },
    { label: 'Appointment', value: 'appointment' },
    { label: 'Task', value: 'task' },
    { label: 'Other', value: 'other' }
  ];

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Validation',
        detail: 'Please enter a search term',
        life: 3000
      });
      return;
    }

    setLoading(true);
    try {
      const params: any = {
        search_term: searchTerm
      };

      if (customerId) {
        params.customer_id = customerId;
      }

      if (activityType) {
        params.activity_type = activityType;
      }

      const response = await api.get('/api/v1/crm/activities/search', { params });
      let searchResults = response.data.activities || [];

      if (dateFrom || dateTo) {
        searchResults = searchResults.filter((result: SearchResult) => {
          const resultDate = new Date(result.created_at);
          if (dateFrom && resultDate < dateFrom) return false;
          if (dateTo && resultDate > dateTo) return false;
          return true;
        });
      }

      setResults(searchResults);

      if (searchResults.length === 0) {
        toast.current?.show({
          severity: 'info',
          summary: 'No Results',
          detail: 'No communications found matching your search',
          life: 3000
        });
      }
    } catch (error) {
      console.error('Error searching communications:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to search communications',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSearchTerm('');
    setActivityType(null);
    setDateFrom(null);
    setDateTo(null);
    setResults([]);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('de-DE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const typeBodyTemplate = (rowData: SearchResult) => {
    const typeConfig: Record<string, { icon: string; severity: any }> = {
      email: { icon: 'pi-envelope', severity: 'info' },
      call: { icon: 'pi-phone', severity: 'success' },
      meeting: { icon: 'pi-users', severity: 'warning' },
      note: { icon: 'pi-file', severity: null },
      appointment: { icon: 'pi-calendar', severity: 'help' },
      task: { icon: 'pi-check-square', severity: 'secondary' },
      other: { icon: 'pi-circle', severity: null }
    };

    const config = typeConfig[rowData.activity_type] || typeConfig.other;
    
    return (
      <Tag 
        value={rowData.activity_type.toUpperCase()} 
        severity={config.severity}
        icon={`pi ${config.icon}`}
      />
    );
  };

  const dateBodyTemplate = (rowData: SearchResult) => {
    return <span>{formatDate(rowData.created_at)}</span>;
  };

  const contentBodyTemplate = (rowData: SearchResult) => {
    const maxLength = 100;
    const content = rowData.content || '';
    return (
      <span title={content}>
        {content.length > maxLength ? `${content.substring(0, maxLength)}...` : content}
      </span>
    );
  };

  return (
    <div className="communication-search">
      <Toast ref={toast} />

      <div className="search-header">
        <h3>🔍 Search Communications</h3>
      </div>

      <div className="search-filters">
        <div className="filter-row">
          <span className="p-input-icon-left flex-1">
            <i className="pi pi-search" />
            <InputText
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search in subject and content..."
              className="w-full"
            />
          </span>
          <Dropdown
            value={activityType}
            options={activityTypes}
            onChange={(e) => setActivityType(e.value)}
            placeholder="Type"
            className="type-dropdown"
          />
        </div>

        <div className="filter-row">
          <Calendar
            value={dateFrom}
            onChange={(e) => setDateFrom(e.value as Date)}
            placeholder="From Date"
            showIcon
            dateFormat="dd.mm.yy"
            className="date-picker"
          />
          <Calendar
            value={dateTo}
            onChange={(e) => setDateTo(e.value as Date)}
            placeholder="To Date"
            showIcon
            dateFormat="dd.mm.yy"
            className="date-picker"
          />
          <Button
            label="Search"
            icon="pi pi-search"
            onClick={handleSearch}
            loading={loading}
            className="search-button"
          />
          <Button
            label="Clear"
            icon="pi pi-times"
            onClick={handleClear}
            className="p-button-outlined"
          />
        </div>
      </div>

      {results.length > 0 && (
        <div className="search-results">
          <div className="results-header">
            <h4>Search Results ({results.length})</h4>
          </div>

          <DataTable
            value={results}
            paginator
            rows={20}
            rowsPerPageOptions={[10, 20, 50]}
            className="results-table"
            sortField="created_at"
            sortOrder={-1}
          >
            <Column
              field="activity_type"
              header="Type"
              body={typeBodyTemplate}
              sortable
              style={{ width: '10rem' }}
            />
            <Column
              field="title"
              header="Subject"
              sortable
              style={{ minWidth: '15rem' }}
            />
            <Column
              field="content"
              header="Content"
              body={contentBodyTemplate}
              style={{ minWidth: '20rem' }}
            />
            <Column
              field="created_by"
              header="Created By"
              sortable
              style={{ width: '12rem' }}
            />
            <Column
              field="created_at"
              header="Date"
              body={dateBodyTemplate}
              sortable
              style={{ width: '12rem' }}
            />
          </DataTable>
        </div>
      )}
    </div>
  );
};
