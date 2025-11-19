/**
 * User List Component
 * 
 * Display and manage list of users
 */

import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Dropdown } from 'primereact/dropdown';
import { Tag } from 'primereact/tag';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import { Toast } from 'primereact/toast';
import api from '../../services/api';
import './UserList.css';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  status: string;
  phone?: string;
  department?: string;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

interface UserListProps {
  onEdit: (user: User) => void;
  onView: (user: User) => void;
  refreshTrigger?: number;
}

const UserList: React.FC<UserListProps> = ({ onEdit, onView, refreshTrigger }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalRecords, setTotalRecords] = useState(0);
  const [first, setFirst] = useState(0);
  const [rows, setRows] = useState(10);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const toast = React.useRef<Toast>(null);

  const roles = [
    { label: 'All Roles', value: null },
    { label: 'Super Admin', value: 'super_admin' },
    { label: 'Admin', value: 'admin' },
    { label: 'Manager', value: 'manager' },
    { label: 'User', value: 'user' },
    { label: 'Viewer', value: 'viewer' }
  ];

  const statuses = [
    { label: 'All Statuses', value: null },
    { label: 'Active', value: 'active' },
    { label: 'Inactive', value: 'inactive' },
    { label: 'Suspended', value: 'suspended' },
    { label: 'Pending', value: 'pending' }
  ];

  useEffect(() => {
    loadUsers();
  }, [first, rows, search, roleFilter, statusFilter, refreshTrigger]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const params: any = {
        skip: first,
        limit: rows
      };

      if (search) params.search = search;
      if (roleFilter) params.role = roleFilter;
      if (statusFilter) params.status = statusFilter;

      const response = await api.get('/api/v1/users/', { params });
      setUsers(response.data.users);
      setTotalRecords(response.data.total);
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.detail || 'Failed to load users',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (user: User) => {
    confirmDialog({
      message: `Are you sure you want to delete user "${user.username}"?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await api.delete(`/api/v1/users/${user.id}`);
          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'User deleted successfully',
            life: 3000
          });
          loadUsers();
        } catch (error: any) {
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.detail || 'Failed to delete user',
            life: 3000
          });
        }
      }
    });
  };

  const roleBodyTemplate = (rowData: User) => {
    const roleColors: Record<string, string> = {
      super_admin: 'danger',
      admin: 'warning',
      manager: 'info',
      user: 'success',
      viewer: 'secondary'
    };

    const roleLabels: Record<string, string> = {
      super_admin: 'Super Admin',
      admin: 'Admin',
      manager: 'Manager',
      user: 'User',
      viewer: 'Viewer'
    };

    return (
      <Tag
        value={roleLabels[rowData.role] || rowData.role}
        severity={roleColors[rowData.role] as any}
      />
    );
  };

  const statusBodyTemplate = (rowData: User) => {
    const statusColors: Record<string, string> = {
      active: 'success',
      inactive: 'secondary',
      suspended: 'danger',
      pending: 'warning'
    };

    return (
      <Tag
        value={rowData.status.charAt(0).toUpperCase() + rowData.status.slice(1)}
        severity={statusColors[rowData.status] as any}
      />
    );
  };

  const actionsBodyTemplate = (rowData: User) => {
    return (
      <div className="action-buttons">
        <Button
          icon="pi pi-eye"
          className="p-button-rounded p-button-info p-button-sm"
          onClick={() => onView(rowData)}
          tooltip="View Details"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-pencil"
          className="p-button-rounded p-button-success p-button-sm"
          onClick={() => onEdit(rowData)}
          tooltip="Edit User"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-trash"
          className="p-button-rounded p-button-danger p-button-sm"
          onClick={() => handleDelete(rowData)}
          tooltip="Delete User"
          tooltipOptions={{ position: 'top' }}
          disabled={rowData.role === 'super_admin'}
        />
      </div>
    );
  };

  const dateBodyTemplate = (rowData: User, field: keyof User) => {
    const date = rowData[field];
    if (!date) return '-';
    return new Date(date as string).toLocaleString('de-DE');
  };

  const header = (
    <div className="table-header">
      <div className="search-container">
        <span className="p-input-icon-left">
          <i className="pi pi-search" />
          <InputText
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search users..."
          />
        </span>
      </div>
      <div className="filter-container">
        <Dropdown
          value={roleFilter}
          options={roles}
          onChange={(e) => setRoleFilter(e.value)}
          placeholder="Filter by Role"
          className="filter-dropdown"
        />
        <Dropdown
          value={statusFilter}
          options={statuses}
          onChange={(e) => setStatusFilter(e.value)}
          placeholder="Filter by Status"
          className="filter-dropdown"
        />
      </div>
    </div>
  );

  return (
    <div className="user-list">
      <Toast ref={toast} />
      <ConfirmDialog />
      
      <DataTable
        value={users}
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
        emptyMessage="No users found"
        className="user-table"
      >
        <Column field="username" header="Username" sortable />
        <Column field="email" header="Email" sortable />
        <Column
          field="first_name"
          header="Name"
          body={(rowData) => `${rowData.first_name} ${rowData.last_name}`}
          sortable
        />
        <Column field="role" header="Role" body={roleBodyTemplate} sortable />
        <Column field="status" header="Status" body={statusBodyTemplate} sortable />
        <Column field="department" header="Department" sortable />
        <Column
          field="last_login"
          header="Last Login"
          body={(rowData) => dateBodyTemplate(rowData, 'last_login')}
          sortable
        />
        <Column
          field="created_at"
          header="Created"
          body={(rowData) => dateBodyTemplate(rowData, 'created_at')}
          sortable
        />
        <Column
          body={actionsBodyTemplate}
          header="Actions"
          style={{ width: '150px' }}
        />
      </DataTable>
    </div>
  );
};

export default UserList;
