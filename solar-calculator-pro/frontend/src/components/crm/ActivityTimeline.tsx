/**
 * Activity Timeline Component
 * 
 * Displays a timeline of activities/notes for a customer
 */

import React, { useState, useEffect } from 'react';
import { Timeline } from 'primereact/timeline';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { Tag } from 'primereact/tag';
import { Toast } from 'primereact/toast';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Dropdown } from 'primereact/dropdown';
import api from '../../services/api';
import './ActivityTimeline.css';

interface Activity {
  id: number;
  customer_id: number;
  activity_type: 'note' | 'email' | 'call' | 'appointment' | 'meeting' | 'task' | 'other';
  title: string;
  content?: string;
  created_by?: string;
  created_at: string;
  is_important?: boolean;
  is_archived?: boolean;
}

interface ActivityTimelineProps {
  customerId: number;
  onActivityEdit?: (activity: Activity) => void;
  refreshTrigger?: number;
}

const ActivityTimeline: React.FC<ActivityTimelineProps> = ({
  customerId,
  onActivityEdit,
  refreshTrigger
}) => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(false);
  const [typeFilter, setTypeFilter] = useState<string | null>(null);
  const toast = React.useRef<Toast>(null);

  const activityTypeOptions = [
    { label: 'All Types', value: null },
    { label: 'Note', value: 'note' },
    { label: 'Email', value: 'email' },
    { label: 'Call', value: 'call' },
    { label: 'Appointment', value: 'appointment' },
    { label: 'Meeting', value: 'meeting' },
    { label: 'Task', value: 'task' },
    { label: 'Other', value: 'other' }
  ];

  // Load activities
  const loadActivities = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (typeFilter) params.activity_type = typeFilter;

      const response = await api.get(`/crm/activities/customer/${customerId}`, { params });
      setActivities(response.data.activities);
    } catch (error: any) {
      console.error('Error loading activities:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.error?.message || 'Failed to load activities',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (customerId) {
      loadActivities();
    }
  }, [customerId, typeFilter, refreshTrigger]);

  // Handle delete activity
  const handleDelete = async (activity: Activity) => {
    confirmDialog({
      message: `Are you sure you want to delete this activity?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await api.delete(`/crm/activities/${activity.id}`);
          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'Activity deleted successfully',
            life: 3000
          });
          loadActivities();
        } catch (error: any) {
          console.error('Error deleting activity:', error);
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.error?.message || 'Failed to delete activity',
            life: 3000
          });
        }
      }
    });
  };

  // Get icon for activity type
  const getActivityIcon = (type: string) => {
    const iconMap: Record<string, string> = {
      note: 'pi-file',
      email: 'pi-envelope',
      call: 'pi-phone',
      appointment: 'pi-calendar',
      meeting: 'pi-users',
      task: 'pi-check-square',
      other: 'pi-info-circle'
    };
    return iconMap[type] || 'pi-info-circle';
  };

  // Get color for activity type
  const getActivityColor = (type: string) => {
    const colorMap: Record<string, string> = {
      note: '#3B82F6',
      email: '#10B981',
      call: '#F59E0B',
      appointment: '#8B5CF6',
      meeting: '#EC4899',
      task: '#6366F1',
      other: '#6B7280'
    };
    return colorMap[type] || '#6B7280';
  };

  // Custom marker for timeline
  const customMarker = (item: Activity) => {
    return (
      <span
        className="custom-marker shadow-2"
        style={{ backgroundColor: getActivityColor(item.activity_type) }}
      >
        <i className={`pi ${getActivityIcon(item.activity_type)}`}></i>
      </span>
    );
  };

  // Custom content for timeline
  const customContent = (item: Activity) => {
    return (
      <Card className="activity-card">
        <div className="activity-header">
          <div className="flex justify-content-between align-items-start">
            <div className="flex-1">
              <div className="flex align-items-center gap-2 mb-2">
                <h4 className="m-0">{item.title}</h4>
                {item.is_important && (
                  <Tag severity="danger" value="Important" icon="pi pi-star-fill" />
                )}
              </div>
              <div className="text-sm text-gray-600 mb-2">
                <i className="pi pi-clock mr-2"></i>
                {new Date(item.created_at).toLocaleString()}
                {item.created_by && (
                  <>
                    <i className="pi pi-user ml-3 mr-2"></i>
                    {item.created_by}
                  </>
                )}
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                icon="pi pi-pencil"
                className="p-button-rounded p-button-text p-button-sm"
                onClick={() => onActivityEdit && onActivityEdit(item)}
                tooltip="Edit"
              />
              <Button
                icon="pi pi-trash"
                className="p-button-rounded p-button-text p-button-danger p-button-sm"
                onClick={() => handleDelete(item)}
                tooltip="Delete"
              />
            </div>
          </div>
        </div>
        {item.content && (
          <div className="activity-content mt-3">
            <p className="m-0 text-gray-700">{item.content}</p>
          </div>
        )}
      </Card>
    );
  };

  return (
    <div className="activity-timeline">
      <Toast ref={toast} />
      <ConfirmDialog />

      {/* Filter Bar */}
      <div className="filter-bar mb-4">
        <Dropdown
          value={typeFilter}
          options={activityTypeOptions}
          onChange={(e) => setTypeFilter(e.value)}
          placeholder="Filter by Type"
          className="w-full md:w-auto"
        />
      </div>

      {/* Timeline */}
      {loading ? (
        <div className="text-center p-4">
          <i className="pi pi-spin pi-spinner" style={{ fontSize: '2rem' }}></i>
        </div>
      ) : activities.length === 0 ? (
        <div className="text-center p-4 text-gray-600">
          <i className="pi pi-inbox" style={{ fontSize: '3rem' }}></i>
          <p className="mt-3">No activities found</p>
        </div>
      ) : (
        <Timeline
          value={activities}
          align="alternate"
          className="customized-timeline"
          marker={customMarker}
          content={customContent}
        />
      )}
    </div>
  );
};

export default ActivityTimeline;
