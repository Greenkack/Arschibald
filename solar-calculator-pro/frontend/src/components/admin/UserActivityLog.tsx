/**
 * User Activity Log Component
 * 
 * Display user activity logs
 */

import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Tag } from 'primereact/tag';
import { Toast } from 'primereact/toast';
import { Dialog } from 'primereact/dialog';
import { Button } from 'primereact/button';
import api from '../../services/api';
import './UserActivityLog.css';

interface ActivityLog {
  id: number;
  user_id: number;
  username: string;
  action: string;
  resource: string;
  resource_id?: number;
  details?: any;
  ip_address?: string;
  user_agent?: string;
  timestamp: string;
}

interface UserActivityLogProps {
  userId?: number;
}

const UserActivityLog: React.FC<UserActivityLogProps> = ({ userId }) => {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalRecords, setTotalRecords] = useState(0);
  const [first, setFirst] = useState(0);
  const [rows, setRows] = useState(10);
  const [actionFilter, setActionFilter] = useState<string | null>(null);
  const [resourceFilter, setResourceFilter] = useState<string | null>(null);
  const [selectedLog, setSelectedLog] = useState<ActivityLog | null>(null);
  const [detailsVisible, setDetailsVisible] = useState(false);
  const toast = React.useRef<Toast>(null);

  const actions = [
    { label: 'All Actions', value: null },
    { label: 'Create User', value: 'create_user' },
    { label: 'Update User', value: 'update_user' },
    { label: 'Delete User', value: 'delete_user' },
    { label: 'Change Password', value: 'change_password' },
    { label: 'Update Settings', value: 'update_settings' },
    { label: 'Login', value: 'login' },
    { label: 'Logout', value: 'logout' }
  ];

  const resources = [
    { label: 'All Resources', value: null },
    { label: 'User', value: 'user' },
    { label: 'Role', value: 'role' },
    { label: 'Settings', value: 'user_settings' },
    { label: 'Project', value: 'project' },
    { label: 'Product', value: 'product' }
  ];

  useEffect(() => {
    loadLogs();
  }, [first, rows, actionFilter, resourceFilter, userId]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params: any = {
        skip: first,
        limit: rows
      };

      if (userId) params.user_id = userId;
      if (actionFilter) params.action = actionFilter;
      if (resourceFilter) params.resource = resourceFilter;

      const response = await api.get('/api/v1/users/activity/logs', { params });
      setLogs(response.data.logs);
      setTotalRecords(response.data.total);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.detail || 'Failed to load activity logs',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const actionBodyTemplate = (rowData: ActivityLog) => {
    const actionColors: Record<string, string> = {
      create_user: 'success',
      update_user: 'info',
      delete_user: 'danger',
      change_password: 'warning',
      update_settings: 'info',
      login: 'success',
      logout: 'secondary'
    };

    const actionLabels: Record<string, string> = {
      create_user: 'Create User',
      update_user: 'Update User',
      delete_user: 'Delete User',
      change_password: 'Change Password',
      update_settings: 'Update Settings',
      login: 'Login',
      logout: 'Logout'
    };

    return (
      <Tag
        value={actionLabels[rowData.action] || rowData.action}
        severity={actionColors[rowData.action] as any || 'info'}
      />
    );
  };

  const timestampBodyTemplate = (rowData: ActivityLog) => {
    return new Date(rowData.timestamp).toLocaleString('de-DE');
  };

  const detailsBodyTemplate = (rowData: ActivityLog) => {
    if (!rowData.details) return '-';
    
    return (
      <Button
        icon="pi pi-eye"
        className="p-button-rounded p-button-text p-button-sm"
        onClick={() => {
          setSelectedLog(rowData);
          setDetailsVisible(true);
        }}
        tooltip="View Details"
      />
    );
  };

  const header = (
    <div className="table-header">
      <h3>Activity Logs</h3>
      <div className="filter-container">
        <Dropdown
          value={actionFilter}
          options={actions}
          onChange={(e) => setActionFilter(e.value)}
          placeholder="Filter by Action"
          className="filter-dropdown"
        />
        <Dropdown
          value={resourceFilter}
          options={resources}
          onChange={(e) => setResourceFilter(e.value)}
          placeholder="Filter by Resource"
          className="filter-dropdown"
        />
      </div>
    </div>
  );

  return (
    <div className="user-activity-log">
      <Toast ref={toast} />
      
      <DataTable
        value={logs}
        loading={loading}
        paginator
        rows={rows}
        first={first}
        totalRecords={totalRecords}
        onPage={(e) => {
          setFirst(e.first);
          setRows(e.rows);
        }}
        rowsPerPageOptions={[5, 10, 25, 50]}
        header={header}
        emptyMessage="No activity logs found"
        className="activity-table"
      >
        <Column field="timestamp" header="Timestamp" body={timestampBodyTemplate} sortable />
        <Column field="username" header="User" sortable />
        <Column field="action" header="Action" body={actionBodyTemplate} sortable />
        <Column field="resource" header="Resource" sortable />
        <Column field="resource_id" header="Resource ID" sortable />
        <Column field="ip_address" header="IP Address" />
        <Column body={detailsBodyTemplate} header="Details" style={{ width: '80px' }} />
      </DataTable>

      <Dialog
        visible={detailsVisible}
        onHide={() => setDetailsVisible(false)}
        header="Activity Details"
        style={{ width: '600px' }}
        modal
      >
        {selectedLog && (
          <div className="activity-details">
            <div className="detail-row">
              <strong>User:</strong>
              <span>{selectedLog.username}</span>
            </div>
            <div className="detail-row">
              <strong>Action:</strong>
              <span>{selectedLog.action}</span>
            </div>
            <div className="detail-row">
              <strong>Resource:</strong>
              <span>{selectedLog.resource}</span>
            </div>
            {selectedLog.resource_id && (
              <div className="detail-row">
                <strong>Resource ID:</strong>
                <span>{selectedLog.resource_id}</span>
              </div>
            )}
            <div className="detail-row">
              <strong>Timestamp:</strong>
              <span>{new Date(selectedLog.timestamp).toLocaleString('de-DE')}</span>
            </div>
            {selectedLog.ip_address && (
              <div className="detail-row">
                <strong>IP Address:</strong>
                <span>{selectedLog.ip_address}</span>
              </div>
            )}
            {selectedLog.user_agent && (
              <div className="detail-row">
                <strong>User Agent:</strong>
                <span className="user-agent">{selectedLog.user_agent}</span>
              </div>
            )}
            {selectedLog.details && (
              <div className="detail-row">
                <strong>Details:</strong>
                <pre className="details-json">
                  {JSON.stringify(selectedLog.details, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </Dialog>
    </div>
  );
};

export default UserActivityLog;
