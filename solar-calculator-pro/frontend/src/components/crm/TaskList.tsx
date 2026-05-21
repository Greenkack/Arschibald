/**
 * Task List Component
 * 
 * Displays a list of tasks with filtering, status updates, and management
 */

import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Tag } from 'primereact/tag';
import { Toast } from 'primereact/toast';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import api from '../../services/api';
import './TaskList.css';

interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'open' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  due_date?: string;
  customer_id?: number;
  project_id?: number;
  assigned_to?: string;
  created_at?: string;
  completed_at?: string;
}

interface TaskListProps {
  customerId?: number;
  projectId?: number;
  onTaskSelect?: (task: Task) => void;
  onTaskEdit?: (task: Task) => void;
  refreshTrigger?: number;
}

const TaskList: React.FC<TaskListProps> = ({
  customerId,
  projectId,
  onTaskSelect,
  onTaskEdit,
  refreshTrigger
}) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<string | null>(null);
  const [overdueOnly, setOverdueOnly] = useState(false);
  const toast = React.useRef<Toast>(null);

  const statusOptions = [
    { label: 'All Statuses', value: null },
    { label: 'Open', value: 'open' },
    { label: 'In Progress', value: 'in_progress' },
    { label: 'Completed', value: 'completed' }
  ];

  const priorityOptions = [
    { label: 'All Priorities', value: null },
    { label: 'Low', value: 'low' },
    { label: 'Medium', value: 'medium' },
    { label: 'High', value: 'high' }
  ];

  // Load tasks
  const loadTasks = async () => {
    setLoading(true);
    try {
      const params: any = {};
      
      if (statusFilter) params.status = statusFilter;
      if (priorityFilter) params.priority = priorityFilter;
      if (customerId) params.customer_id = customerId;
      if (projectId) params.project_id = projectId;
      if (overdueOnly) params.overdue_only = true;

      const response = await api.get('/crm/tasks', { params });
      setTasks(response.data.tasks);
    } catch (error: any) {
      console.error('Error loading tasks:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.error?.message || 'Failed to load tasks',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [statusFilter, priorityFilter, overdueOnly, customerId, projectId, refreshTrigger]);

  // Handle mark as completed
  const handleMarkCompleted = async (task: Task) => {
    try {
      await api.post(`/crm/tasks/${task.id}/complete`);
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'Task marked as completed',
        life: 3000
      });
      loadTasks();
    } catch (error: any) {
      console.error('Error marking task as completed:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.error?.message || 'Failed to mark task as completed',
        life: 3000
      });
    }
  };

  // Handle delete task
  const handleDelete = async (task: Task) => {
    confirmDialog({
      message: `Are you sure you want to delete task "${task.title}"?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await api.delete(`/crm/tasks/${task.id}`);
          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'Task deleted successfully',
            life: 3000
          });
          loadTasks();
        } catch (error: any) {
          console.error('Error deleting task:', error);
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.error?.message || 'Failed to delete task',
            life: 3000
          });
        }
      }
    });
  };

  // Template for status column
  const statusBodyTemplate = (rowData: Task) => {
    const statusMap = {
      open: { label: 'Open', severity: 'info' as const },
      in_progress: { label: 'In Progress', severity: 'warning' as const },
      completed: { label: 'Completed', severity: 'success' as const }
    };
    
    const status = statusMap[rowData.status];
    return <Tag value={status.label} severity={status.severity} />;
  };

  // Template for priority column
  const priorityBodyTemplate = (rowData: Task) => {
    const priorityMap = {
      low: { label: 'Low', severity: 'success' as const },
      medium: { label: 'Medium', severity: 'warning' as const },
      high: { label: 'High', severity: 'danger' as const }
    };
    
    const priority = priorityMap[rowData.priority];
    return <Tag value={priority.label} severity={priority.severity} />;
  };

  // Template for due date column
  const dueDateBodyTemplate = (rowData: Task) => {
    if (!rowData.due_date) return '-';
    
    const dueDate = new Date(rowData.due_date);
    const today = new Date();
    const isOverdue = dueDate < today && rowData.status !== 'completed';
    
    return (
      <div className={isOverdue ? 'text-red-600 font-bold' : ''}>
        {dueDate.toLocaleDateString()}
        {isOverdue && <i className="pi pi-exclamation-circle ml-2"></i>}
      </div>
    );
  };

  // Template for actions column
  const actionsBodyTemplate = (rowData: Task) => {
    return (
      <div className="flex gap-2">
        <Button
          icon="pi pi-eye"
          className="p-button-rounded p-button-text p-button-info"
          onClick={() => onTaskSelect && onTaskSelect(rowData)}
          tooltip="View Details"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-pencil"
          className="p-button-rounded p-button-text p-button-warning"
          onClick={() => onTaskEdit && onTaskEdit(rowData)}
          tooltip="Edit"
          tooltipOptions={{ position: 'top' }}
        />
        {rowData.status !== 'completed' && (
          <Button
            icon="pi pi-check"
            className="p-button-rounded p-button-text p-button-success"
            onClick={() => handleMarkCompleted(rowData)}
            tooltip="Mark as Completed"
            tooltipOptions={{ position: 'top' }}
          />
        )}
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-text p-button-danger"
          onClick={() => handleDelete(rowData)}
          tooltip="Delete"
          tooltipOptions={{ position: 'top' }}
        />
      </div>
    );
  };

  return (
    <div className="task-list">
      <Toast ref={toast} />
      <ConfirmDialog />

      {/* Filter Bar */}
      <div className="filter-bar mb-3 flex gap-3 flex-wrap">
        <Dropdown
          value={statusFilter}
          options={statusOptions}
          onChange={(e) => setStatusFilter(e.value)}
          placeholder="Filter by Status"
          className="w-full md:w-auto"
        />
        <Dropdown
          value={priorityFilter}
          options={priorityOptions}
          onChange={(e) => setPriorityFilter(e.value)}
          placeholder="Filter by Priority"
          className="w-full md:w-auto"
        />
        <Button
          label={overdueOnly ? 'Show All' : 'Show Overdue Only'}
          icon={overdueOnly ? 'pi pi-filter-slash' : 'pi pi-filter'}
          onClick={() => setOverdueOnly(!overdueOnly)}
          className={overdueOnly ? 'p-button-danger' : 'p-button-outlined'}
        />
      </div>

      {/* Data Table */}
      <DataTable
        value={tasks}
        loading={loading}
        emptyMessage="No tasks found"
        className="task-datatable"
        responsiveLayout="scroll"
        sortField="due_date"
        sortOrder={1}
      >
        <Column
          field="title"
          header="Title"
          sortable
          style={{ minWidth: '200px' }}
          body={(rowData) => (
            <div>
              <div className="font-bold">{rowData.title}</div>
              {rowData.description && (
                <div className="text-sm text-gray-600 mt-1">
                  {rowData.description.substring(0, 100)}
                  {rowData.description.length > 100 && '...'}
                </div>
              )}
            </div>
          )}
        />
        <Column
          field="status"
          header="Status"
          body={statusBodyTemplate}
          sortable
          style={{ width: '120px' }}
        />
        <Column
          field="priority"
          header="Priority"
          body={priorityBodyTemplate}
          sortable
          style={{ width: '120px' }}
        />
        <Column
          field="due_date"
          header="Due Date"
          body={dueDateBodyTemplate}
          sortable
          style={{ width: '150px' }}
        />
        {rowData.assigned_to && (
          <Column
            field="assigned_to"
            header="Assigned To"
            sortable
            style={{ width: '150px' }}
          />
        )}
        <Column
          header="Actions"
          body={actionsBodyTemplate}
          style={{ width: '200px' }}
        />
      </DataTable>
    </div>
  );
};

export default TaskList;
