import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dropdown } from 'primereact/dropdown';
import { Toast } from 'primereact/toast';
import { Tag } from 'primereact/tag';
import api from '../../services/api';
import './CallLogging.css';

interface Call {
  id: number;
  customer_id: number;
  title: string;
  content: string;
  created_at: string;
  created_by?: string;
  is_important: boolean;
}

interface CallLoggingProps {
  customerId: number;
  customerPhone?: string;
}

export const CallLogging: React.FC<CallLoggingProps> = ({ customerId, customerPhone }) => {
  const [calls, setCalls] = useState<Call[]>([]);
  const [loading, setLoading] = useState(false);
  const [showLogDialog, setShowLogDialog] = useState(false);
  const [showViewDialog, setShowViewDialog] = useState(false);
  const [selectedCall, setSelectedCall] = useState<Call | null>(null);
  const [newCall, setNewCall] = useState({
    phone: customerPhone || '',
    subject: '',
    notes: '',
    callType: 'outbound',
    duration: '',
    outcome: ''
  });
  const toast = React.useRef<Toast>(null);

  const callTypes = [
    { label: 'Outbound', value: 'outbound' },
    { label: 'Inbound', value: 'inbound' },
    { label: 'Missed', value: 'missed' }
  ];

  const outcomes = [
    { label: 'Successful', value: 'successful' },
    { label: 'No Answer', value: 'no_answer' },
    { label: 'Voicemail', value: 'voicemail' },
    { label: 'Busy', value: 'busy' },
    { label: 'Follow-up Required', value: 'follow_up' }
  ];

  useEffect(() => {
    loadCalls();
  }, [customerId]);

  const loadCalls = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/crm/activities/customer/${customerId}`, {
        params: { activity_type: 'call' }
      });
      setCalls(response.data.activities || []);
    } catch (error) {
      console.error('Error loading calls:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load call history',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogCall = () => {
    setNewCall({
      phone: customerPhone || '',
      subject: '',
      notes: '',
      callType: 'outbound',
      duration: '',
      outcome: ''
    });
    setShowLogDialog(true);
  };

  const handleSaveCall = async () => {
    if (!newCall.subject || !newCall.notes) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Validation Error',
        detail: 'Please fill in all required fields',
        life: 3000
      });
      return;
    }

    try {
      const activityData = {
        customer_id: customerId,
        activity_type: 'call',
        title: `Call: ${newCall.subject}`,
        content: `Type: ${newCall.callType}\nPhone: ${newCall.phone}\nDuration: ${newCall.duration}\nOutcome: ${newCall.outcome}\n\nNotes:\n${newCall.notes}`,
        created_by: 'Current User',
        is_important: newCall.outcome === 'follow_up'
      };

      await api.post('/api/v1/crm/activities', activityData);

      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Call logged successfully',
        life: 3000
      });

      setShowLogDialog(false);
      loadCalls();
    } catch (error) {
      console.error('Error logging call:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to log call',
        life: 3000
      });
    }
  };

  const viewCall = (call: Call) => {
    setSelectedCall(call);
    setShowViewDialog(true);
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

  const subjectBodyTemplate = (rowData: Call) => {
    return (
      <div className="call-subject">
        {rowData.is_important && (
          <i className="pi pi-star-fill important-icon"></i>
        )}
        <span>{rowData.title.replace('Call: ', '')}</span>
      </div>
    );
  };

  const dateBodyTemplate = (rowData: Call) => {
    return <span>{formatDate(rowData.created_at)}</span>;
  };

  const actionsBodyTemplate = (rowData: Call) => {
    return (
      <div className="action-buttons">
        <Button
          icon="pi pi-eye"
          className="p-button-rounded p-button-text p-button-info"
          onClick={() => viewCall(rowData)}
          tooltip="View Details"
          tooltipOptions={{ position: 'top' }}
        />
      </div>
    );
  };

  const logDialogFooter = (
    <div>
      <Button
        label="Cancel"
        icon="pi pi-times"
        onClick={() => setShowLogDialog(false)}
        className="p-button-text"
      />
      <Button
        label="Save"
        icon="pi pi-check"
        onClick={handleSaveCall}
        autoFocus
      />
    </div>
  );

  return (
    <div className="call-logging">
      <Toast ref={toast} />

      <div className="call-header">
        <h3>📞 Call History</h3>
        <Button
          label="Log Call"
          icon="pi pi-plus"
          onClick={handleLogCall}
          className="p-button-success"
        />
      </div>

      <DataTable
        value={calls}
        loading={loading}
        paginator
        rows={10}
        rowsPerPageOptions={[5, 10, 20]}
        emptyMessage="No calls logged"
        className="call-table"
        sortField="created_at"
        sortOrder={-1}
      >
        <Column
          field="title"
          header="Subject"
          body={subjectBodyTemplate}
          sortable
          style={{ minWidth: '15rem' }}
        />
        <Column
          field="created_by"
          header="Logged By"
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
        header="Log Call"
        visible={showLogDialog}
        style={{ width: '50vw' }}
        onHide={() => setShowLogDialog(false)}
        footer={logDialogFooter}
        modal
      >
        <div className="log-form">
          <div className="form-field">
            <label htmlFor="callType">Call Type *</label>
            <Dropdown
              id="callType"
              value={newCall.callType}
              options={callTypes}
              onChange={(e) => setNewCall({ ...newCall, callType: e.value })}
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="phone">Phone Number</label>
            <InputText
              id="phone"
              value={newCall.phone}
              onChange={(e) => setNewCall({ ...newCall, phone: e.target.value })}
              placeholder="+49 123 456789"
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="subject">Subject *</label>
            <InputText
              id="subject"
              value={newCall.subject}
              onChange={(e) => setNewCall({ ...newCall, subject: e.target.value })}
              placeholder="Call subject"
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="duration">Duration (minutes)</label>
            <InputText
              id="duration"
              value={newCall.duration}
              onChange={(e) => setNewCall({ ...newCall, duration: e.target.value })}
              placeholder="15"
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="outcome">Outcome</label>
            <Dropdown
              id="outcome"
              value={newCall.outcome}
              options={outcomes}
              onChange={(e) => setNewCall({ ...newCall, outcome: e.value })}
              placeholder="Select outcome"
              className="w-full"
            />
          </div>

          <div className="form-field">
            <label htmlFor="notes">Notes *</label>
            <InputTextarea
              id="notes"
              value={newCall.notes}
              onChange={(e) => setNewCall({ ...newCall, notes: e.target.value })}
              rows={6}
              placeholder="Call notes and details..."
              className="w-full"
            />
          </div>
        </div>
      </Dialog>

      <Dialog
        header="Call Details"
        visible={showViewDialog}
        style={{ width: '50vw' }}
        onHide={() => setShowViewDialog(false)}
        modal
      >
        {selectedCall && (
          <div className="call-details">
            <div className="detail-row">
              <strong>Subject:</strong>
              <span>{selectedCall.title.replace('Call: ', '')}</span>
            </div>
            <div className="detail-row">
              <strong>Date:</strong>
              <span>{formatDate(selectedCall.created_at)}</span>
            </div>
            <div className="detail-row">
              <strong>Logged By:</strong>
              <span>{selectedCall.created_by || 'Unknown'}</span>
            </div>
            <div className="detail-row">
              <strong>Details:</strong>
              <div className="call-content">{selectedCall.content}</div>
            </div>
            {selectedCall.is_important && (
              <div className="detail-row">
                <Tag value="FOLLOW-UP REQUIRED" severity="warning" icon="pi pi-star-fill" />
              </div>
            )}
          </div>
        )}
      </Dialog>
    </div>
  );
};
