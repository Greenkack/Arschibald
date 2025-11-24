/**
 * Opportunity Dialog Component
 * Create and edit opportunities
 */

import React, { useState, useEffect } from 'react';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { InputNumber } from 'primereact/inputnumber';
import { Dropdown } from 'primereact/dropdown';
import { Calendar } from 'primereact/calendar';
import { Button } from 'primereact/button';
import { TabView, TabPanel } from 'primereact/tabview';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import './OpportunityDialog.css';

interface OpportunityDialogProps {
  visible: boolean;
  opportunity?: any;
  onHide: () => void;
  onSave: () => void;
}

export const OpportunityDialog: React.FC<OpportunityDialogProps> = ({
  visible,
  opportunity,
  onHide,
  onSave
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    contact_name: '',
    contact_email: '',
    contact_phone: '',
    stage_id: null,
    estimated_value: 0,
    probability: null,
    expected_close_date: null,
    owner_id: null,
    source: '',
    tags: []
  });
  
  const [stages, setStages] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const toast = React.useRef<Toast>(null);

  useEffect(() => {
    if (visible) {
      loadFormData();
    }
  }, [visible, opportunity]);

  const loadFormData = async () => {
    try {
      setLoading(true);
      
      // Load stages
      const stagesResponse = await api.get('/api/v1/pipeline/stages');
      setStages(stagesResponse.data.stages);
      
      // Load users (owners)
      const usersResponse = await api.get('/api/v1/users');
      setUsers(usersResponse.data.users || []);
      
      // Set form data if editing
      if (opportunity) {
        setFormData({
          name: opportunity.name || '',
          description: opportunity.description || '',
          contact_name: opportunity.contact_name || '',
          contact_email: opportunity.contact_email || '',
          contact_phone: opportunity.contact_phone || '',
          stage_id: opportunity.stage_id,
          estimated_value: opportunity.estimated_value || 0,
          probability: opportunity.probability,
          expected_close_date: opportunity.expected_close_date 
            ? new Date(opportunity.expected_close_date) 
            : null,
          owner_id: opportunity.owner_id,
          source: opportunity.source || '',
          tags: opportunity.tags || []
        });
      }
      
    } catch (error) {
      console.error('Error loading form data:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load form data'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // Validate required fields
      if (!formData.name || !formData.stage_id || !formData.estimated_value || !formData.owner_id) {
        toast.current?.show({
          severity: 'warn',
          summary: 'Validation Error',
          detail: 'Please fill in all required fields'
        });
        return;
      }
      
      const payload = {
        ...formData,
        expected_close_date: formData.expected_close_date 
          ? formData.expected_close_date.toISOString() 
          : null
      };
      
      if (opportunity) {
        // Update existing
        await api.put(`/api/v1/pipeline/opportunities/${opportunity.id}`, payload);
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'Opportunity updated successfully'
        });
      } else {
        // Create new
        await api.post('/api/v1/pipeline/opportunities', payload);
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'Opportunity created successfully'
        });
      }
      
      onSave();
      
    } catch (error) {
      console.error('Error saving opportunity:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to save opportunity'
      });
    } finally {
      setSaving(false);
    }
  };

  const handleWin = async () => {
    if (!opportunity) return;
    
    try {
      await api.post(`/api/v1/pipeline/opportunities/${opportunity.id}/win`, {
        actual_value: formData.estimated_value,
        actual_close_date: new Date().toISOString(),
        win_reason: 'Won via dialog'
      });
      
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Opportunity marked as won'
      });
      
      onSave();
      
    } catch (error) {
      console.error('Error marking as won:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to mark as won'
      });
    }
  };

  const handleLose = async () => {
    if (!opportunity) return;
    
    try {
      await api.post(`/api/v1/pipeline/opportunities/${opportunity.id}/lose`, {
        loss_reason: 'Lost via dialog',
        actual_close_date: new Date().toISOString()
      });
      
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Opportunity marked as lost'
      });
      
      onSave();
      
    } catch (error) {
      console.error('Error marking as lost:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to mark as lost'
      });
    }
  };

  const footer = (
    <div className="dialog-footer">
      <div className="footer-left">
        {opportunity && (
          <>
            <Button
              label="Mark as Won"
              icon="pi pi-check"
              className="p-button-success"
              onClick={handleWin}
            />
            <Button
              label="Mark as Lost"
              icon="pi pi-times"
              className="p-button-danger"
              onClick={handleLose}
            />
          </>
        )}
      </div>
      <div className="footer-right">
        <Button
          label="Cancel"
          icon="pi pi-times"
          className="p-button-text"
          onClick={onHide}
        />
        <Button
          label="Save"
          icon="pi pi-check"
          loading={saving}
          onClick={handleSave}
        />
      </div>
    </div>
  );

  return (
    <>
      <Toast ref={toast} />
      <Dialog
        visible={visible}
        onHide={onHide}
        header={opportunity ? 'Edit Opportunity' : 'New Opportunity'}
        footer={footer}
        className="opportunity-dialog"
        style={{ width: '800px' }}
      >
        {loading ? (
          <div className="dialog-loading">Loading...</div>
        ) : (
          <TabView>
            <TabPanel header="Details">
              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="name">Name *</label>
                  <InputText
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Opportunity name"
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="stage">Stage *</label>
                  <Dropdown
                    id="stage"
                    value={formData.stage_id}
                    options={stages}
                    onChange={(e) => setFormData({ ...formData, stage_id: e.value })}
                    optionLabel="name"
                    optionValue="id"
                    placeholder="Select stage"
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="value">Estimated Value * (€)</label>
                  <InputNumber
                    id="value"
                    value={formData.estimated_value}
                    onValueChange={(e) => setFormData({ ...formData, estimated_value: e.value || 0 })}
                    mode="currency"
                    currency="EUR"
                    locale="de-DE"
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="probability">Probability (%)</label>
                  <InputNumber
                    id="probability"
                    value={formData.probability}
                    onValueChange={(e) => setFormData({ ...formData, probability: e.value })}
                    min={0}
                    max={100}
                    suffix="%"
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="owner">Owner *</label>
                  <Dropdown
                    id="owner"
                    value={formData.owner_id}
                    options={users}
                    onChange={(e) => setFormData({ ...formData, owner_id: e.value })}
                    optionLabel="username"
                    optionValue="id"
                    placeholder="Select owner"
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="closeDate">Expected Close Date</label>
                  <Calendar
                    id="closeDate"
                    value={formData.expected_close_date}
                    onChange={(e) => setFormData({ ...formData, expected_close_date: e.value })}
                    dateFormat="dd.mm.yy"
                    showIcon
                  />
                </div>

                <div className="form-field full-width">
                  <label htmlFor="description">Description</label>
                  <InputTextarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                    placeholder="Opportunity description"
                  />
                </div>
              </div>
            </TabPanel>

            <TabPanel header="Contact">
              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="contactName">Contact Name</label>
                  <InputText
                    id="contactName"
                    value={formData.contact_name}
                    onChange={(e) => setFormData({ ...formData, contact_name: e.target.value })}
                    placeholder="Contact name"
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="contactEmail">Contact Email</label>
                  <InputText
                    id="contactEmail"
                    value={formData.contact_email}
                    onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                    placeholder="contact@example.com"
                    type="email"
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="contactPhone">Contact Phone</label>
                  <InputText
                    id="contactPhone"
                    value={formData.contact_phone}
                    onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                    placeholder="+49 123 456789"
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="source">Source</label>
                  <InputText
                    id="source"
                    value={formData.source}
                    onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                    placeholder="e.g., Website, Referral, Cold Call"
                  />
                </div>
              </div>
            </TabPanel>
          </TabView>
        )}
      </Dialog>
    </>
  );
};
