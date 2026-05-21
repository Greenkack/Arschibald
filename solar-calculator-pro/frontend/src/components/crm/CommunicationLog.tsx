/**
 * Communication Log Component
 * 
 * Displays a comprehensive log of all communications with a customer
 * including emails, calls, meetings, and notes.
 */

import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Tag } from 'primereact/tag';
import { Dialog } from 'primereact/dialog';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import './CommunicationLog.css';

interface Activity {
  id: number;
  customer_id: number;
  activity_type: string;
  title: string;
  content?: string;
  created_at: string;
  created_by?: string;
  is_important: boolean;
  is_archived: boolean;
  attachments?: string[];
}

interface CommunicationLogProps {
  customerId: number;
}

export const CommunicationLog: React.FC<CommunicationLogProps> = ({ customerId }) => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string | null>(null);
  const [includeArchived, setIncludeArchived] = useState(false);
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

  useEffect(() => {
    loadActivities();
  }, [customerId, typeFilter, includeArchived]);

  const loadActivities = async () => {
    setLoading(true);
    try {
      const params: any = {
        include_archived: includeArchived
      };
      if (typeFilter) {
        params.activity_type = typeFilter;
      }

      const response = await api.get(`/api/v1/crm/activities/customer/${customerId}`, { params });
      setActivities(response.data.activities || []);
    } catch (error) {
      console.error('Error loading activities:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load communication history',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      loadActivities();
      return;
    }

    setLoading(true);
    try {
      const params: any = {
        search_term: searchTerm,
        customer_id: customerId
      };
      if (typeFilter) {
        params.activity_type = typeFilter;
      }

      const response = await api.get('/api/v1/crm/activities/search', { params });
      setActivities(response.data.activities || []);
    } catch (error) {
      console.error('Error searching activities:', error);
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

  const viewDetails = (activity: Activity) => {
    setSelectedActivity(activity);
    setShowDetailDialog(true);
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

  const typeBodyTemplate = (rowData: Activity) => {
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

  const dateBodyTemplate = (rowData: Activity) => {
    return <span>{formatDate(rowData.created_at)}</span>;
  };

  const importantBodyTemplate = (rowData: Activity) => {
    return rowData.is_important ? (
      <i className="pi pi-star-fill" style={{ color: '#ffc107' }}></i>
    ) : null;
  };

  const actionsBodyTemplate = (rowData: Activity) => {
    return (
      <div className="action-buttons">
        <Button
          icon="pi pi-eye"
          className="p-button-rounded p-button-text p-button-info"
          onClick={() => viewDetails(rowData)}
          tooltip="View Details"
          tooltipOptions={{ position: 'top' }}
        />
      </div>
    );
  };

  const filteredActivities = activities.filter(activity => {
    if (searchTerm && !activity.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !activity.content?.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    return true;
  });

  return (
    <div className="communication-log">
      <Toast ref={toast} />

      <div className="log-header">
        <h3>📞 Communication History</h3>
        <div className="log-controls">
          <span className="p-input-icon-left">
            <i className="pi pi-search" />
            <InputText
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search communications..."
              className="search-input"
            />
          </span>
          <Button
            icon="pi pi-search"
            onClick={handleSearch}
            className="p-button-outlined"
            tooltip="Search"
          />
          <Dropdown
            value={typeFilter}
            options={activityTypes}
            onChange={(e) => setTypeFilter(e.value)}
            placeholder="Filter by Type"
            className="type-filter"
          />
          <Button
            icon={includeArchived ? 'pi pi-eye-slash' : 'pi pi-eye'}
            onClick={() => setIncludeArchived(!includeArchived)}
            className="p-button-outlined"
            tooltip={includeArchived ? 'Hide Archived' : 'Show Archived'}
          />
          <Button
            icon="pi pi-refresh"
            onClick={loadActivities}
            className="p-button-outlined"
            tooltip="Refresh"
          />
        </div>
      </div>

      <DataTable
        value={filteredActivities}
        loading={loading}
        paginator
        rows={20}
        rowsPerPageOptions={[10, 20, 50]}
        emptyMessage="No communications found"
        className="communication-table"
        sortField="created_at"
        sortOrder={-1}
      >
        <Column
          field="is_important"
          header=""
          body={importantBodyTemplate}
          style={{ width: '3rem' }}
        />
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
        <Column
          header="Actions"
          body={actionsBodyTemplate}
          style={{ width: '8rem' }}
        />
      </DataTable>

      <Dialog
        header="Communication Details"
        visible={showDetailDialog}
        style={{ width: '50vw' }}
        onHide={() => setShowDetailDialog(false)}
        modal
      >
        {selectedActivity && (
          <div className="activity-details">
            <div className="detail-row">
              <strong>Type:</strong>
              {typeBodyTemplate(selectedActivity)}
            </div>
            <div className="detail-row">
              <strong>Subject:</strong>
              <span>{selectedActivity.title}</span>
            </div>
            <div className="detail-row">
              <strong>Date:</strong>
              <span>{formatDate(selectedActivity.created_at)}</span>
            </div>
            {selectedActivity.created_by && (
              <div className="detail-row">
                <strong>Created By:</strong>
                <span>{selectedActivity.created_by}</span>
              </div>
            )}
            {selectedActivity.content && (
              <div className="detail-row">
                <strong>Content:</strong>
                <div className="content-box">{selectedActivity.content}</div>
              </div>
            )}
            {selectedActivity.attachments && selectedActivity.attachments.length > 0 && (
              <div className="detail-row">
                <strong>Attachments:</strong>
                <div className="attachments-list">
                  {selectedActivity.attachments.map((attachment, index) => (
                    <div key={index} className="attachment-item">
                      <i className="pi pi-paperclip"></i>
                      <span>{attachment}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {selectedActivity.is_important && (
              <div className="detail-row">
                <Tag value="IMPORTANT" severity="warning" icon="pi pi-star-fill" />
              </div>
            )}
          </div>
        )}
      </Dialog>
    </div>
  );
};
