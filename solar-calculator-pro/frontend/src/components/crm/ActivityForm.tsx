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
