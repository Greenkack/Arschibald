/**
 * Activity Form Component
 * 
 * Form for creating and editing activities/notes
 */

import React, { useState, useEffect } from 'react';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dropdown } from 'primereact/dropdown';
import { Checkbox } from 'primereact/checkbox';
import { Button } from 'primereact/button';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import './ActivityForm.css';

interface Activity {
  id?: number;
  customer_id: number;
  activity_type: 'note' | 'email' | 'call' | 'appointment' | 'meeting' | 'task' | 'other';
  title: string;
  content?: string;
  created_by?: string;
  is_important?: boolean;
}

interface ActivityFormProps {
  visible: boolean;
  activity?: Activity | null;
  customerId: number;
  onHide: () => void;
  onSuccess: () => void;
}

const ActivityForm: React.FC<ActivityFormProps> = ({
  visible,
  activity,
  customerId,
  onHide,
  onSuccess
}) => {
  const [formData, setFormData] = useState<Activity>({
    customer_id: customerId,
    activity_type: 'note',
    title: '',
    content: '',
    created_by: '',
    is_important: false
  });
  const [loading, setLoading] = useState(false);
  const toast = React.useRef<Toast>(null);

  const activityTypeOptions = [
    { label: 'Note', value: 'note' },
    { label: 'Email', value: 'email' },
    { label: 'Call', value: 'call' },
    { label: 'Appointment', value: 'appointment' },
    { label: 'Meeting', value: 'meeting' },
    { label: 'Task', value: 'task' },
    { label: 'Other', value: 'other' }
  ];

  useEffect(() => {
    if (activity) {
      setFormData(activity);
    } else {
      setFormData({
        customer_id: customerId,
        activity_type: 'note',
        title: '',
        content: '',
        created_by: '',
        is_important: false
      });
    }
  }, [activity, customerId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim()) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Validation Error',
        detail: 'Activity title is required',
        life: 3000
      });
      return;
    }

    setLoading(true);
    try {
      const submitData = {
        ...formData,
        customer_id: customerId
      };

      if (activity?.id) {
        await api.put(`/crm/activities/${activity.id}`, submitData);
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'Activity updated successfully',
          life: 3000
        });
      } else {
        await api.post('/crm/activities', submitData);
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'Activity created successfully',
          life: 3000
        });
      }
      
      onSuccess();
      onHide();
    } catch (error: any) {
      console.error('Error saving activity:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.error?.message || 'Failed to save activity',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const footer = (
    <div>
      <Button
        label="Cancel"
        icon="pi pi-times"
        onClick={onHide}
        className="p-button-text"
        disabled={loading}
      />
      <Button
        label={activity?.id ? 'Update' : 'Create'}
        icon="pi pi-check"
        onClick={handleSubmit}
        loading={loading}
      />
    </div>
  );

  return (
    <>
      <Toast ref={toast} />
      <Dialog
        visible={visible}
        style={{ width: '600px' }}
        header={activity?.id ? 'Edit Activity' : 'Create New Activity'}
        modal
        className="p-fluid"
        footer={footer}
        onHide={onHide}
      >
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="activity_type">Activity Type *</label>
            <Dropdown
              id="activity_type"
              value={formData.activity_type}
              options={activityTypeOptions}
              onChange={(e) => setFormData({ ...formData, activity_type: e.value })}
              required
            />
          </div>

          <div className="field">
            <label htmlFor="title">Title *</label>
            <InputText
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
              autoFocus
            />
          </div>

          <div className="field">
            <label htmlFor="content">Content</label>
            <InputTextarea
              id="content"
              value={formData.content || ''}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              rows={6}
              placeholder="Enter activity details..."
            />
          </div>

          <div className="field">
            <label htmlFor="created_by">Created By</label>
            <InputText
              id="created_by"
              value={formData.created_by || ''}
              onChange={(e) => setFormData({ ...formData, created_by: e.target.value })}
              placeholder="Enter your name"
            />
          </div>

          <div className="field-checkbox">
            <Checkbox
              inputId="is_important"
              checked={formData.is_important || false}
  