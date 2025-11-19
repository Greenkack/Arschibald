/**
 * CRM Page
 * 
 * Customer relationship management with customer list, creation, editing, and detail view
 */

import React, { useState } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { TabView, TabPanel } from 'primereact/tabview';
import CustomerList from '../components/crm/CustomerList';
import CustomerForm from '../components/crm/CustomerForm';
import CustomerDetail from '../components/crm/CustomerDetail';
import './CRM.css';

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

const CRM: React.FC = () => {
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDetailDialog, setShowDetailDialog] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Handle create customer
  const handleCreateClick = () => {
    setSelectedCustomer(null);
    setShowCreateDialog(true);
  };

  // Handle edit customer
  const handleEditCustomer = (customer: Customer) => {
    setSelectedCustomer(customer);
    setShowEditDialog(true);
  };

  // Handle view customer details
  const handleViewCustomer = (customer: Customer) => {
    setSelectedCustomer(customer);
    setShowDetailDialog(true);
  };

  // Handle save (create or update)
  const handleSave = () => {
    setShowCreateDialog(false);
    setShowEditDialog(false);
    setShowDetailDialog(false);
    setRefreshTrigger(prev => prev + 1);
  };

  // Handle cancel
  const handleCancel = () => {
    setShowCreateDialog(false);
    setShowEditDialog(false);
    setSelectedCustomer(null);
  };

  // Handle edit from detail view
  const handleEditFromDetail = () => {
    setShowDetailDialog(false);
    setShowEditDialog(true);
  };

  return (
    <div className="crm-page">
      <div className="page-header">
        <h1>Customer Management</h1>
        <Button
          label="New Customer"
          icon="pi pi-plus"
          onClick={handleCreateClick}
          className="p-button-success"
        />
      </div>

      <Card>
        <TabView>
          <TabPanel header="Customers" leftIcon="pi pi-users">
            <CustomerList
              onCustomerSelect={handleViewCustomer}
              onCustomerEdit={handleEditCustomer}
              refreshTrigger={refreshTrigger}
            />
          </TabPanel>
          
          <TabPanel header="Offers" leftIcon="pi pi-file" disabled>
            <p>Offer management coming soon...</p>
          </TabPanel>
          
          <TabPanel header="Tasks" leftIcon="pi pi-check-square" disabled>
            <p>Task management coming soon...</p>
          </TabPanel>
          
          <TabPanel header="Activities" leftIcon="pi pi-calendar" disabled>
            <p>Activity tracking coming soon...</p>
          </TabPanel>
        </TabView>
      </Card>

      {/* Create Customer Dialog */}
      <Dialog
        header="Create New Customer"
        visible={showCreateDialog}
        style={{ width: '800px' }}
        onHide={handleCancel}
        maximizable
      >
        <CustomerForm
          onSave={handleSave}
          onCancel={handleCancel}
        />
      </Dialog>

      {/* Edit Customer Dialog */}
      <Dialog
        header="Edit Customer"
        visible={showEditDialog}
        style={{ width: '800px' }}
        onHide={handleCancel}
        maximizable
      >
        <CustomerForm
          customer={selectedCustomer}
          onSave={handleSave}
          onCancel={handleCancel}
        />
      </Dialog>

      {/* Customer Detail Dialog */}
      <Dialog
        visible={showDetailDialog}
        style={{ width: '800px' }}
        onHide={() => setShowDetailDialog(false)}
        maximizable
      >
        {selectedCustomer && (
          <CustomerDetail
            customer={selectedCustomer}
            onEdit={handleEditFromDetail}
            onClose={() => setShowDetailDialog(false)}
          />
        )}
      </Dialog>
    </div>
  );
};

export default CRM;
