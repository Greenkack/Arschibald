/**
 * Customer Data Service
 * 
 * Frontend service for customer data management with CRM integration
 */

import api from './api';

export interface Customer {
  id?: number;
  salutation: string;
  title: string;
  first_name: string;
  last_name: string;
  company: string;
  street: string;
  house_number: string;
  postal_code: string;
  city: string;
  bundesland: string;
  email: string;
  phone: string;
  mobile: string;
  notes: string;
  tags: string[];
  source?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CustomerCreate {
  salutation?: string;
  title?: string;
  first_name: string;
  last_name: string;
  company?: string;
  street?: string;
  house_number?: string;
  postal_code?: string;
  city?: string;
  bundesland?: string;
  email?: string;
  phone?: string;
  mobile?: string;
  notes?: string;
  tags?: string[];
  source?: string;
}

export interface CustomerSearchFilters {
  postal_code?: string;
  city?: string;
  bundesland?: string;
}

export interface PlaceholderInfo {
  key: string;
  placeholder: string;
  description: string;
}

export interface ImportResult {
  imported: number;
  errors: string[];
}

class CustomerDataService {
  private baseUrl = '/api/v1/customer-data';

  // ==================== CRUD Operations ====================

  async createCustomer(customer: CustomerCreate): Promise<{ id: number }> {
    const response = await api.post(`${this.baseUrl}/`, customer);
    return response.data;
  }

  async getCustomer(customerId: number): Promise<Customer> {
    const response = await api.get(`${this.baseUrl}/${customerId}`);
    return response.data;
  }

  async updateCustomer(customerId: number, updates: Partial<Customer>): Promise<{ success: boolean }> {
    const response = await api.put(`${this.baseUrl}/${customerId}`, updates);
    return response.data;
  }

  async deleteCustomer(customerId: number): Promise<{ success: boolean }> {
    const response = await api.delete(`${this.baseUrl}/${customerId}`);
    return response.data;
  }

  // ==================== Search & List ====================

  async listCustomers(limit: number = 100, offset: number = 0): Promise<Customer[]> {
    const response = await api.get(`${this.baseUrl}/`, {
      params: { limit, offset }
    });
    return response.data;
  }

  async searchCustomers(query: string, filters?: CustomerSearchFilters): Promise<Customer[]> {
    const response = await api.get(`${this.baseUrl}/search/`, {
      params: { q: query, ...filters }
    });
    return response.data;
  }

  // ==================== PDF Placeholders ====================

  async getCustomerPlaceholders(customerId: number): Promise<Record<string, string>> {
    const response = await api.get(`${this.baseUrl}/${customerId}/placeholders`);
    return response.data;
  }

  async listPlaceholders(): Promise<PlaceholderInfo[]> {
    const response = await api.get(`${this.baseUrl}/placeholders/list`);
    return response.data;
  }

  // ==================== Export ====================

  async exportCustomersCSV(customerIds?: number[]): Promise<Blob> {
    const params = customerIds ? { customer_ids: customerIds.join(',') } : {};
    const response = await api.get(`${this.baseUrl}/export/csv`, {
      params,
      responseType: 'blob'
    });
    return response.data;
  }

  async exportCustomersJSON(customerIds?: number[]): Promise<Blob> {
    const params = customerIds ? { customer_ids: customerIds.join(',') } : {};
    const response = await api.get(`${this.baseUrl}/export/json`, {
      params,
      responseType: 'blob'
    });
    return response.data;
  }

  downloadBlob(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  // ==================== Import ====================

  async importCustomersCSV(file: File): Promise<ImportResult> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`${this.baseUrl}/import/csv`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }

  async importCustomersJSON(file: File): Promise<ImportResult> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`${this.baseUrl}/import/json`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  }

  // ==================== Health Check ====================

  async healthCheck(): Promise<{ status: string; customer_count?: number }> {
    const response = await api.get(`${this.baseUrl}/health/check`);
    return response.data;
  }

  // ==================== Utility Methods ====================

  formatCustomerName(customer: Customer): string {
    const parts = [];
    if (customer.salutation) parts.push(customer.salutation);
    if (customer.title) parts.push(customer.title);
    if (customer.first_name) parts.push(customer.first_name);
    if (customer.last_name) parts.push(customer.last_name);
    return parts.join(' ');
  }

  formatCustomerAddress(customer: Customer): string {
    const parts = [];
    let streetLine = customer.street || '';
    if (customer.house_number) streetLine += ` ${customer.house_number}`;
    if (streetLine) parts.push(streetLine);
    
    let cityLine = '';
    if (customer.postal_code) cityLine = customer.postal_code;
    if (customer.city) cityLine += cityLine ? ` ${customer.city}` : customer.city;
    if (cityLine) parts.push(cityLine);
    
    return parts.join(', ');
  }
}

export const customerDataService = new CustomerDataService();
export default customerDataService;
