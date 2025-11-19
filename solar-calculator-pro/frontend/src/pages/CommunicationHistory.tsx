import React, { useState } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { Card } from 'primereact/card';
import { Dropdown } from 'primereact/dropdown';
import {
  CommunicationLog,
  EmailIntegration,
  CallLogging,
  DocumentAttachments,
  CommunicationSearch
} from '../components/crm';
import './CommunicationHistory.css';

interface Customer {
  id: number;
  first_name: string;
  last_name: string;
  email?: string;
  phone_mobile?: string;
}

export const CommunicationHistory: React.FC = () => {
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);

  React.useEffect(() => {
    // Load customers - in a real app, this would fetch from API
    // For now, using mock data
    const mockCustomers: Customer[] = [
      { id: 1, first_name: 'Max', last_name: 'Mustermann', email: 'max@example.com', phone_mobile: '+49 123 456789' },
      { id: 2, first_name: 'Anna', last_name: 'Schmidt', email: 'anna@example.com', phone_mobile: '+49 987 654321' }
    ];
    setCustomers(mockCustomers);
    if (mockCustomers.length > 0) {
      setSelectedCustomer(mockCustomers[0]);
    }
  }, []);

  const customerOptions = customers.map(c => ({
    label: `${c.first_name} ${c.last_name}`,
    value: c.id
  }));

  const handleCustomerChange = (customerId: number) => {
    const customer = customers.find(c => c.id === customerId);
    if (customer) {
      setSelectedCustomer(customer);
    }
  };

  return (
    <div className="communication-history-page">
      <div className="page-header">
        <h1>📞 Communication History</h1>
        <p>Manage all customer communications in one place</p>
      </div>

      <Card className="customer-selector-card">
        <div className="customer-selector">
          <label htmlFor="customer">Select Customer:</label>
          <Dropdown
            id="customer"
            value={selectedCustomer?.id}
            options={customerOptions}
            onChange={(e) => handleCustomerChange(e.value)}
            placeholder="Select a customer"
            className="customer-dropdown"
          />
          {selectedCustomer && (
            <div className="customer-info">
              <span>📧 {selectedCustomer.email || 'No email'}</span>
              <span>📱 {selectedCustomer.phone_mobile || 'No phone'}</span>
            </div>
          )}
        </div>
      </Card>

      {selectedCustomer ? (
        <TabView activeIndex={activeIndex} onTabChange={(e) => setActiveIndex(e.index)}>
          <TabPanel header="All Communications" leftIcon="pi pi-list">
            <Card>
              <CommunicationLog customerId={selectedCustomer.id} />
            </Card>
          </TabPanel>

          <TabPanel header="Emails" leftIcon="pi pi-envelope">
            <Card>
              <EmailIntegration 
                customerId={selectedCustomer.id}
                customerEmail={selectedCustomer.email}
              />
            </Card>
          </TabPanel>

          <TabPanel header="Calls" leftIcon="pi pi-phone">
            <Card>
              <CallLogging 
                customerId={selectedCustomer.id}
                customerPhone={selectedCustomer.phone_mobile}
              />
            </Card>
          </TabPanel>

          <TabPanel header="Documents" leftIcon="pi pi-paperclip">
            <Card>
              <DocumentAttachments customerId={selectedCustomer.id} />
            </Card>
          </TabPanel>

          <TabPanel header="Search" leftIcon="pi pi-search">
            <Card>
              <CommunicationSearch customerId={selectedCustomer.id} />
            </Card>
          </TabPanel>
        </TabView>
      ) : (
        <Card>
          <div className="no-customer-selected">
            <i className="pi pi-users" style={{ fontSize: '3rem', color: 'var(--text-color-secondary)' }}></i>
            <h3>No Customer Selected</h3>
            <p>Please select a customer to view their communication history</p>
          </div>
        </Card>
      )}
    </div>
  );
};

export default CommunicationHistory;
