/**
 * Task Form Component
 * 
 * Form for creating and editing tasks
 */

import React, { useState, useEffect } from 'react';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { Dropdown } from 'primereact/dropdown';
import { Calendar } from 'primereact/calendar';
import { Button } from 'primereact/button';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import './TaskForm.css';

interface Task {
  id?: number;
  title: string;
  description?: string;
  status: 'open' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  due_date?: string;
  customer_id?: number;
  project_id?: number;
  assigned_to?: string;
}

interface TaskFormProps {
  visible: boolean;
  task?: Task | null;
  customerId?: number;
  projectId?: number;
  onHide: () => void;
  onSuccess: () => void;
}

const TaskForm: React.FC<TaskFormProps> = ({
  visible,
  task,
  customerId,
  projectId,
  onHide,
  onSuccess
}) => {
  const [formData, setFormData] = useState<Task>({
    title: '',
    description: '',
    status: 'open',
    priority: 'medium',
    due_date: undefined,
    customer_id: customerId,
    project_id: projectId,
    assigned_to: ''
  });
  const [loading, setLoading] = useState(false);
  const toast = React.useRef<Toast>(null);

  const statusOptions = [
    { label: 'Open', value: 'open' },
    { label: 'In Progress', value: 'in_progress' },
    { label: 'Completed', value: 'completed' }
  ];

  const priorityOptions = [
    { label: 'Low', value: 'low' },
    { label: 'Medium', value: 'medium' },
    { label: 'High', value: 'high' }
  ];

  useEffect(() => {
    if (task) {
      setFormData({
        ...task,
        due_date: task.due_date ? task.due_date : undefined
      });
    } else {
      setFormData({
        title: '',
        description: '',
        status: 'open',
        priority: 'medium',
        due_date: undefined,
        customer_id: customerId,
        project_id: projectId,
        assigned_to: ''
      });
    }
  }, [task, customerId, projectId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim()) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Validation Error',
        detail: 'Task title is required',
        life: 3000
      });
      return;
    }

    setLoading(true);
    try {
      const submitData = {
        ...formData,
        customer_id: customerId || formData.customer_id,
        project_id: projectId || formData.project_id
      };

      if (task?.id) {
        await api.put(`/crm/tasks/${task.id}`, submitData);
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'Task updated successfully',
          life: 3000
        });
      } else {
        await api.post('/crm/tasks', submitData);
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'Task created successfully',
          life: 3000
        });
      }
      
      onSuccess();
      onHide();
    } catch (error: any) {
      console.error('Error saving task:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.error?.message || 'Failed to save task',
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
        label={task?.id ? 'Update' : 'Create'}
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
        header={task?.id ? 'Edit Task' : 'Create New Task'}
        modal
        className="p-fluid"
        footer={footer}
        onHide={onHide}
      >
        <form onSubmit={handleSubmit}>
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
            <label htmlFor="description">Description</label>
            <InputTextarea
              id="description"
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={4}
            />
          </div>

          <div className="formgrid grid">
            <div className="field col-6">
              <label htmlFor="status">Status</label>
              <Dropdown
                id="status"
                value={formData.status}
                options={statusOptions}
                onChange={(e) => setFormData({ ...formData, status: e.value })}
              />
            </div>

            <div className="field col-6">
              <label htmlFor="priority">Priority</label>
              <Dropdown
                id="priority"
                value={formData.priority}
                options={priorityOptions}
                onChange={(e) => setFormData({ ...formData, priority: e.value })}
              />
            </div>
          </div>

          <div className="formgrid grid">
            <div className="field col-6">
              <label htmlFor="due_date">Due Date</label>
              <Calendar
                id="due_date"
                value={formData.due_date ? new Date(formData.due_date) : null}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  due_date: e.value ? e.value.toISOString().split('T')[0] : undefined 
                })}
                dateFormat="yy-mm-dd"
                showIcon
              />
            </div>

            <div className="field col-6">
              <label htmlFor="assigned_to">Assigned To</label>
              <InputText
                id="assigned_to"
                value={formData.assigned_to || ''}
                onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
                placeholder="Enter name"
              />
            </div>
          </div>
        </form>
      </Dialog>
    </>
  );
};

export default TaskForm;
