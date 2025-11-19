/**
 * Customer Detail Component
 * 
 * Displays detailed information about a customer
 */

import React from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { Divider } from 'primereact/divider';
import './CustomerDetail.css';

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

interface CustomerDetailProps {
  customer: Customer;
  onEdit?: () => void;
  onClose?: () => void;
}

const CustomerDetail: React.FC<CustomerDetailProps> = ({
  customer,
  onEdit,
  onClose
}) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('de-DE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const header = (
    <div className="customer-detail-header">
      <div className="customer-name">
        <h2>{customer.first_name} {customer.last_name}</h2>
        {customer.company_name && (
          <p className="company-name">{customer.company_name}</p>
        )}
      </div>
      <div className="header-actions">
        <Button
          icon="pi pi-pencil"
          label="Edit"
          className="p-button-warning"
          onClick={onEdit}
        />
        <Button
          icon="pi pi-times"
          className="p-button-text"
          onClick={onClose}
        />
      </div>
    </div>
  );

  return (
    <div className="customer-detail">
      <Card header={header}>
        {/* Contact Information */}
        <div className="detail-section">
          <h3>
            <i className="pi pi-phone mr-2"></i>
            Contact Information
          </h3>
          <div className="detail-grid">
            <div className="detail-item">
              <label>Email</label>
              <div className="detail-value">
                {customer.email ? (
                  <a href={`mailto:${customer.email}`}>{customer.email}</a>
                ) : (
                  <span className="text-muted">-</span>
                )}
              </div>
            </div>
            <div className="detail-item">
              <label>Mobile Phone</label>
              <div className="detail-value">
                {customer.phone_mobile ? (
                  <a href={`tel:${customer.phone_mobile}`}>{customer.phone_mobile}</a>
                ) : (
                  <span className="text-muted">-</span>
                )}
              </div>
            </div>
            <div className="detail-item">
              <label>Landline Phone</label>
              <div className="detail-value">
                {customer.phone_landline ? (
                  <a href={`tel:${customer.phone_landline}`}>{customer.phone_landline}</a>
                ) : (
                  <span className="text-muted">-</span>
                )}
              </div>
            </div>
          </div>
        </div>

        <Divider />

        {/* Address Information */}
        <div className="detail-section">
          <h3>
            <i className="pi pi-map-marker mr-2"></i>
            Address
          </h3>
          <div className="detail-grid">
            <div className="detail-item">
              <label>Street</label>
              <div className="detail-value">
                {customer.street || <span className="text-muted">-</span>}
              </div>
            </div>
            <div className="detail-item">
              <label>City</label>
              <div className="detail-value">
                {customer.city || <span className="text-muted">-</span>}
              </div>
            </div>
            <div className="detail-item">
              <label>Postal Code</label>
              <div className="detail-value">
                {customer.postal_code || <span className="text-muted">-</span>}
              </div>
            </div>
            <div className="detail-item">
              <label>Country</label>
              <div className="detail-value">
                {customer.country || <span className="text-muted">-</span>}
              </div>
            </div>
          </div>
        </div>

        <Divider />

        {/* Notes */}
        {customer.notes && (
          <>
            <div className="detail-section">
              <h3>
                <i className="pi pi-file-edit mr-2"></i>
                Notes
              </h3>
              <div className="notes-content">
                {customer.notes}
              </div>
            </div>
            <Divider />
          </>
        )}

        {/* Metadata */}
        <div className="detail-section">
          <h3>
            <i className="pi pi-info-circle mr-2"></i>
            Information
          </h3>
          <div className="detail-grid">
            <div className="detail-item">
              <label>Customer ID</label>
              <div className="detail-value">{customer.id}</div>
            </div>
            <div className="detail-item">
              <label>Created</label>
              <div className="detail-value">{formatDate(customer.created_at)}</div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default CustomerDetail;
