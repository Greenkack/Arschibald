/**
 * Customer List Component
 * 
 * Displays a list of customers with search, filtering, and pagination
 */

import React, { useState, useEffect } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import { Dialog } from 'primereact/dialog';
import { Toast } from 'primereact/toast';
import { ConfirmDialog, confirmDialog } from 'primereact/confirmdialog';
import api from '../../services/api';
import './CustomerList.css';

interface Customer {
  id: number;
  first_name: string;
  last_name: string;
  company_name?: string;
  email?: string;
  phone_mobile?: string;
  phone_landline?: string;
  street?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  notes?: string;
  created_at?: string;
}

interface CustomerListProps {
  onCustomerSelect?: (customer: Customer) => void;
  onCustomerEdit?: (customer: Customer) => void;
  refreshTrigger?: number;
}

const CustomerList: React.FC<CustomerListProps> = ({
  onCustomerSelect,
  onCustomerEdit,
  refreshTrigger
}) => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [totalRecords, setTotalRecords] = useState(0);
  const [first, setFirst] = useState(0);
  const [rows, setRows] = useState(10);
  const toast = React.useRef<Toast>(null);

  // Load customers
  const loadCustomers = async () => {
    setLoading(true);
    try {
      const params: any = {
        limit: rows,
        offset: first
      };
      
      if (searchTerm) {
        params.search = searchTerm;
      }

      const response = await api.get('/crm/customers', { params });
      setCustomers(response.data.customers);
      setTotalRecords(response.data.total);
    } catch (error: any) {
      console.error('Error loading customers:', error);
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.response?.data?.error?.message || 'Failed to load customers',
        life: 3000
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCustomers();
  }, [first, rows, refreshTrigger]);

  // Handle search
  const handleSearch = () => {
    setFirst(0); // Reset to first page
    loadCustomers();
  };

  // Handle search on Enter key
  const handleSearchKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Handle delete customer
  const handleDelete = async (customer: Customer) => {
    confirmDialog({
      message: `Are you sure you want to delete ${customer.first_name} ${customer.last_name}?`,
      header: 'Confirm Delete',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        try {
          await api.delete(`/crm/customers/${customer.id}`);
          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: 'Customer deleted successfully',
            life: 3000
          });
          loadCustomers();
        } catch (error: any) {
          console.error('Error deleting customer:', error);
          toast.current?.show({
            severity: 'error',
            summary: 'Error',
            detail: error.response?.data?.error?.message || 'Failed to delete customer',
            life: 3000
          });
        }
      }
    });
  };

  // Template for name column
  const nameBodyTemplate = (rowData: Customer) => {
    return (
      <div>
        <div className="font-bold">{rowData.first_name} {rowData.last_name}</div>
        {rowData.company_name && (
          <div className="text-sm text-gray-600">{rowData.company_name}</div>
        )}
      </div>
    );
  };

  // Template for contact column
  const contactBodyTemplate = (rowData: Customer) => {
    return (
      <div>
        {rowData.email && (
          <div className="flex align-items-center mb-1">
            <i className="pi pi-envelope mr-2 text-sm"></i>
            <span className="text-sm">{rowData.email}</span>
          </div>
        )}
        {rowData.phone_mobile && (
          <div className="flex align-items-center">
            <i className="pi pi-phone mr-2 text-sm"></i>
            <span className="text-sm">{rowData.phone_mobile}</span>
          </div>
        )}
      </div>
    );
  };

  // Template for location column
  const locationBodyTemplate = (rowData: Customer) => {
    if (!rowData.city && !rowData.postal_code) return '-';
    return (
      <div>
        {rowData.postal_code && rowData.city && (
          <span>{rowData.postal_code} {rowData.city}</span>
        )}
        {!rowData.postal_code && rowData.city && <span>{rowData.city}</span>}
        {rowData.postal_code && !rowData.city && <span>{rowData.postal_code}</span>}
      </div>
    );
  };

  // Template for actions column
  const actionsBodyTemplate = (rowData: Customer) => {
    return (
      <div className="flex gap-2">
        <Button
          icon="pi pi-eye"
          className="p-button-rounded p-button-text p-button-info"
          onClick={() => onCustomerSelect && onCustomerSelect(rowData)}
          tooltip="View Details"
          tooltipOptions={{ position: 'top' }}
        />
        <Button
          icon="pi pi-pencil"
          className="p-button-rounded p-button-text p-button-warning"
          onClick={() => onCustomerEdit && onCustomerEdit(rowData)}
          tooltip="Edit"
          tooltipOptions={{ position: 'top' }}
        />
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

  // Pagination event handler
  const onPage = (event: any) => {
    setFirst(event.first);
    setRows(event.rows);
  };

  return (
    <div className="customer-list">
      <Toast ref={toast} />
      <ConfirmDialog />

      {/* Search Bar */}
      <div className="search-bar mb-3">
        <div className="p-inputgroup">
          <InputText
            placeholder="Search customers by name, company, or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={handleSearchKeyPress}
          />
          <Button
            icon="pi pi-search"
            onClick={handleSearch}
            label="Search"
          />
          {searchTerm && (
            <Button
              icon="pi pi-times"
              className="p-button-secondary"
              onClick={() => {
                setSearchTerm('');
                setFirst(0);
                loadCustomers();
              }}
              tooltip="Clear Search"
            />
          )}
        </div>
      </div>

      {/* Data Table */}
      <DataTable
        value={customers}
        loading={loading}
        paginator
        rows={rows}
        first={first}
        totalRecords={totalRecords}
        onPage={onPage}
        rowsPerPageOptions={[5, 10, 25, 50]}
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} customers"
        emptyMessage="No customers found"
        className="customer-datatable"
        responsiveLayout="scroll"
      >
        <Column
          field="name"
          header="Name"
          body={nameBodyTemplate}
          sortable
          style={{ minWidth: '200px' }}
        />
        <Column
          field="contact"
          header="Contact"
          body={contactBodyTemplate}
          style={{ minWidth: '200px' }}
        />
        <Column
          field="location"
          header="Location"
          body={locationBodyTemplate}
          sortable
          style={{ minWidth: '150px' }}
        />
        <Column
          field="created_at"
          header="Created"
          sortable
          style={{ minWidth: '120px' }}
          body={(rowData) => rowData.created_at ? new Date(rowData.created_at).toLocaleDateString() : '-'}
        />
        <Column
          header="Actions"
          body={actionsBodyTemplate}
          style={{ width: '150px' }}
        />
      </DataTable>
    </div>
  );
};

export default CustomerList;
