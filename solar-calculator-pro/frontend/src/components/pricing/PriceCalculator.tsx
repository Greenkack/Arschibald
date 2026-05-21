/**
 * Price Calculator Component
 * 
 * Task 38: Price Calculation Interface
 * 
 * Features:
 * - Product selection interface
 * - Quantity input with validation
 * - Options selection (extras, services)
 * - Real-time price calculation
 * - Price breakdown display
 * 
 * Requirements: 7.2
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card } from 'primereact/card';
import { InputNumber } from 'primereact/inputnumber';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import { Divider } from 'primereact/divider';
import { Message } from 'primereact/message';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Checkbox } from 'primereact/checkbox';
import { Panel } from 'primereact/panel';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Tag } from 'primereact/tag';
import api from '../../services/api';
import { germanFormatter } from '../../utils/germanNumberFormatter';
import './PriceCalculator.css';

interface Product {
  id: number;
  name: string;
  category: string;
  manufacturer: string;
  base_price?: number;
}

interface StorageOption {
  id: string;
  name: string;
  capacity: string;
  manufacturer: string;
}

interface Extra {
  id: string;
  name: string;
  price: number;
  category: string;
  description?: string;
}

interface Service {
  id: string;
  name: string;
  price: number;
  description?: string;
}

interface PriceBreakdown {
  base_price: number;
  extras_total: number;
  services_total: number;
  subtotal: number;
  discount: number;
  tax: number;
  total: number;
  items: Array<{
    name: string;
    quantity: number;
    unit_price: number;
    total: number;
    type: 'base' | 'extra' | 'service';
  }>;
}

interface CalculationResult {
  success: boolean;
  price?: number;
  breakdown?: PriceBreakdown;
  error?: string;
  user_message?: string;
  metadata?: {
    module_count: number;
    storage_model: string | null;
    matrix_id: number;
    calculation_time: number;
  };
}

const PriceCalculator: React.FC = () => {
  // State for product selection
  const [moduleCount, setModuleCount] = useState<number>(20);
  const [storageModel, setStorageModel] = useState<string | null>(null);
  const [storageOptions, setStorageOptions] = useState<StorageOption[]>([]);
  
  // State for extras and services
  const [selectedExtras, setSelectedExtras] = useState<string[]>([]);
  const [selectedServices, setSelectedServices] = useState<string[]>([]);
  const [availableExtras, setAvailableExtras] = useState<Extra[]>([]);
  const [availableServices, setAvailableServices] = useState<Service[]>([]);
  
  // State for calculation
  const [calculating, setCalculating] = useState(false);
  const [result, setResult] = useState<CalculationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // State for validation
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  // Load storage options on mount
  useEffect(() => {
    loadStorageOptions();
    loadExtras();
    loadServices();
  }, []);

  // Real-time calculation when inputs change
  useEffect(() => {
    if (moduleCount > 0) {
      calculatePrice();
    }
  }, [moduleCount, storageModel, selectedExtras, selectedServices]);

  const loadStorageOptions = async () => {
    try {
      // Mock data - replace with actual API call
      const mockOptions: StorageOption[] = [
        { id: 'none', name: 'kein Speicher', capacity: '0 kWh', manufacturer: '-' },
        { id: 'byd_5', name: 'BYD Battery-Box Premium HVS 5.1', capacity: '5,1 kWh', manufacturer: 'BYD' },
        { id: 'byd_10', name: 'BYD Battery-Box Premium HVS 10.2', capacity: '10,2 kWh', manufacturer: 'BYD' },
        { id: 'byd_15', name: 'BYD Battery-Box Premium HVS 15.4', capacity: '15,4 kWh', manufacturer: 'BYD' },
        { id: 'sonnen_10', name: 'sonnenBatterie 10', capacity: '10 kWh', manufacturer: 'sonnen' },
        { id: 'sonnen_15', name: 'sonnenBatterie 15', capacity: '15 kWh', manufacturer: 'sonnen' },
      ];
      setStorageOptions(mockOptions);
      setStorageModel('none'); // Default to no storage
    } catch (err) {
      console.error('Error loading storage options:', err);
    }
  };

  const loadExtras = async () => {
    try {
      // Mock data - replace with actual API call
      const mockExtras: Extra[] = [
        { id: 'optimizer', name: 'Leistungsoptimierer', price: 150, category: 'Optimierung', description: 'Pro Modul' },
        { id: 'monitoring', name: 'Monitoring-System', price: 500, category: 'Überwachung', description: 'Erweiterte Überwachung' },
        { id: 'wallbox', name: 'Wallbox 11kW', price: 1200, category: 'E-Mobilität', description: 'Ladestation für E-Auto' },
        { id: 'surge_protection', name: 'Überspannungsschutz', price: 300, category: 'Sicherheit', description: 'Typ 1+2' },
        { id: 'smart_meter', name: 'Smart Meter', price: 400, category: 'Messung', description: 'Intelligenter Stromzähler' },
      ];
      setAvailableExtras(mockExtras);
    } catch (err) {
      console.error('Error loading extras:', err);
    }
  };

  const loadServices = async () => {
    try {
      // Mock data - replace with actual API call
      const mockServices: Service[] = [
        { id: 'installation', name: 'Installation & Inbetriebnahme', price: 2500, description: 'Komplette Installation' },
        { id: 'planning', name: 'Detailplanung', price: 500, description: 'Technische Planung' },
        { id: 'permit', name: 'Genehmigungsservice', price: 300, description: 'Behördliche Genehmigungen' },
        { id: 'warranty_extended', name: 'Erweiterte Garantie (5 Jahre)', price: 800, description: 'Zusätzliche Garantie' },
        { id: 'maintenance', name: 'Wartungsvertrag (1 Jahr)', price: 400, description: 'Jährliche Wartung' },
      ];
      setAvailableServices(mockServices);
    } catch (err) {
      console.error('Error loading services:', err);
    }
  };

  const validateInputs = (): boolean => {
    const errors: Record<string, string> = {};

    if (!moduleCount || moduleCount < 1) {
      errors.moduleCount = 'Bitte geben Sie eine gültige Modulanzahl ein (mindestens 1)';
    }

    if (moduleCount > 200) {
      errors.moduleCount = 'Maximale Modulanzahl ist 200';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const calculatePrice = useCallback(async () => {
    if (!validateInputs()) {
      return;
    }

    setCalculating(true);
    setError(null);

    try {
      // Calculate base price from matrix
      const response = await api.post('/api/v1/pricing/calculate', {
        module_count: moduleCount,
        storage_model: storageModel === 'none' ? null : storageModel,
        enable_fallback: true
      });

      if (response.data.success) {
        // Calculate extras and services
        const extrasTotal = selectedExtras.reduce((sum, extraId) => {
          const extra = availableExtras.find(e => e.id === extraId);
          return sum + (extra?.price || 0);
        }, 0);

        const servicesTotal = selectedServices.reduce((sum, serviceId) => {
          const service = availableServices.find(s => s.id === serviceId);
          return sum + (service?.price || 0);
        }, 0);

        const basePrice = response.data.price || 0;
        const subtotal = basePrice + extrasTotal + servicesTotal;
        const discount = 0; // Could be calculated based on rules
        const tax = subtotal * 0.19; // 19% MwSt
        const total = subtotal - discount + tax;

        // Build breakdown items
        const items = [
          {
            name: `PV-Anlage (${moduleCount} Module${storageModel && storageModel !== 'none' ? ' + Speicher' : ''})`,
            quantity: 1,
            unit_price: basePrice,
            total: basePrice,
            type: 'base' as const
          },
          ...selectedExtras.map(extraId => {
            const extra = availableExtras.find(e => e.id === extraId)!;
            return {
              name: extra.name,
              quantity: 1,
              unit_price: extra.price,
              total: extra.price,
              type: 'extra' as const
            };
          }),
          ...selectedServices.map(serviceId => {
            const service = availableServices.find(s => s.id === serviceId)!;
            return {
              name: service.name,
              quantity: 1,
              unit_price: service.price,
              total: service.price,
              type: 'service' as const
            };
          })
        ];

        const breakdown: PriceBreakdown = {
          base_price: basePrice,
          extras_total: extrasTotal,
          services_total: servicesTotal,
          subtotal,
          discount,
          tax,
          total,
          items
        };

        setResult({
          success: true,
          price: total,
          breakdown,
          metadata: response.data.metadata
        });
      } else {
        setError(response.data.user_message || response.data.error || 'Fehler bei der Preisberechnung');
        setResult(null);
      }
    } catch (err: any) {
      console.error('Error calculating price:', err);
      setError(err.response?.data?.detail || 'Fehler bei der Preisberechnung');
      setResult(null);
    } finally {
      setCalculating(false);
    }
  }, [moduleCount, storageModel, selectedExtras, selectedServices, availableExtras, availableServices]);

  const handleExtraToggle = (extraId: string) => {
    setSelectedExtras(prev => 
      prev.includes(extraId) 
        ? prev.filter(id => id !== extraId)
        : [...prev, extraId]
    );
  };

  const handleServiceToggle = (serviceId: string) => {
    setSelectedServices(prev => 
      prev.includes(serviceId) 
        ? prev.filter(id => id !== serviceId)
        : [...prev, serviceId]
    );
  };

  const handleReset = () => {
    setModuleCount(20);
    setStorageModel('none');
    setSelectedExtras([]);
    setSelectedServices([]);
    setResult(null);
    setError(null);
    setValidationErrors({});
  };

  const renderPriceBreakdown = () => {
    if (!result?.breakdown) return null;

    const { breakdown } = result;

    return (
      <div className="price-breakdown">
        <h3>💰 Preisaufschlüsselung</h3>
        
        <DataTable value={breakdown.items} className="breakdown-table">
          <Column 
            field="name" 
            header="Position" 
            body={(rowData) => (
              <div className="item-name">
                <span className={`item-type-badge ${rowData.type}`}>
                  {rowData.type === 'base' ? '🏠' : rowData.type === 'extra' ? '➕' : '🔧'}
                </span>
                {rowData.name}
              </div>
            )}
          />
          <Column 
            field="quantity" 
            header="Menge" 
            style={{ width: '100px', textAlign: 'center' }}
          />
          <Column 
            field="unit_price" 
            header="Einzelpreis" 
            body={(rowData) => germanFormatter.formatCurrency(rowData.unit_price)}
            style={{ width: '150px', textAlign: 'right' }}
          />
          <Column 
            field="total" 
            header="Gesamt" 
            body={(rowData) => germanFormatter.formatCurrency(rowData.total)}
            style={{ width: '150px', textAlign: 'right' }}
          />
        </DataTable>

        <Divider />

        <div className="price-summary">
          <div className="summary-row">
            <span>Zwischensumme:</span>
            <span className="amount">{germanFormatter.formatCurrency(breakdown.subtotal)}</span>
          </div>
          
          {breakdown.discount > 0 && (
            <div className="summary-row discount">
              <span>Rabatt:</span>
              <span className="amount">-{germanFormatter.formatCurrency(breakdown.discount)}</span>
            </div>
          )}
          
          <div className="summary-row tax">
            <span>MwSt. (19%):</span>
            <span className="amount">{germanFormatter.formatCurrency(breakdown.tax)}</span>
          </div>
          
          <Divider />
          
          <div className="summary-row total">
            <span>Gesamtpreis:</span>
            <span className="amount">{germanFormatter.formatCurrency(breakdown.total)}</span>
          </div>
        </div>

        {result.metadata && (
          <div className="calculation-metadata">
            <small>
              <i className="pi pi-info-circle"></i>
              {' '}Berechnung basiert auf {result.metadata.module_count} Modulen
              {result.metadata.storage_model && ` mit ${result.metadata.storage_model}`}
              {' '}(Matrix ID: {result.metadata.matrix_id})
            </small>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="price-calculator">
      <Card title="🧮 Preisberechnung" className="calculator-card">
        {error && (
          <Message severity="error" text={error} className="mb-3" />
        )}

        {/* Product Selection */}
        <Panel header="1️⃣ Produktauswahl" toggleable className="mb-3">
          <div className="form-grid">
            <div className="form-field">
              <label htmlFor="moduleCount">
                Anzahl PV-Module <span className="required">*</span>
              </label>
              <InputNumber
                id="moduleCount"
                value={moduleCount}
                onValueChange={(e) => setModuleCount(e.value || 0)}
                min={1}
                max={200}
                showButtons
                buttonLayout="horizontal"
                decrementButtonClassName="p-button-secondary"
                incrementButtonClassName="p-button-secondary"
                incrementButtonIcon="pi pi-plus"
                decrementButtonIcon="pi pi-minus"
                className={validationErrors.moduleCount ? 'p-invalid' : ''}
                suffix=" Module"
              />
              {validationErrors.moduleCount && (
                <small className="p-error">{validationErrors.moduleCount}</small>
              )}
              <small className="field-hint">
                Geben Sie die gewünschte Anzahl an PV-Modulen ein (1-200)
              </small>
            </div>

            <div className="form-field">
              <label htmlFor="storageModel">
                Batteriespeicher
              </label>
              <Dropdown
                id="storageModel"
                value={storageModel}
                options={storageOptions}
                onChange={(e) => setStorageModel(e.value)}
                optionLabel="name"
                optionValue="id"
                placeholder="Speicher auswählen"
                className="w-full"
                itemTemplate={(option) => (
                  <div className="storage-option">
                    <div className="option-name">{option.name}</div>
                    <div className="option-details">
                      <small>{option.capacity} • {option.manufacturer}</small>
                    </div>
                  </div>
                )}
              />
              <small className="field-hint">
                Optional: Wählen Sie einen Batteriespeicher aus
              </small>
            </div>
          </div>
        </Panel>

        {/* Extras Selection */}
        <Panel header="2️⃣ Extras & Zubehör" toggleable collapsed className="mb-3">
          <div className="extras-grid">
            {availableExtras.map(extra => (
              <div key={extra.id} className="extra-item">
                <Checkbox
                  inputId={`extra-${extra.id}`}
                  checked={selectedExtras.includes(extra.id)}
                  onChange={() => handleExtraToggle(extra.id)}
                />
                <label htmlFor={`extra-${extra.id}`} className="extra-label">
                  <div className="extra-name">{extra.name}</div>
                  <div className="extra-price">{germanFormatter.formatCurrency(extra.price)}</div>
                  {extra.description && (
                    <div className="extra-description">{extra.description}</div>
                  )}
                  <Tag value={extra.category} severity="info" className="extra-category" />
                </label>
              </div>
            ))}
          </div>
        </Panel>

        {/* Services Selection */}
        <Panel header="3️⃣ Dienstleistungen" toggleable collapsed className="mb-3">
          <div className="services-grid">
            {availableServices.map(service => (
              <div key={service.id} className="service-item">
                <Checkbox
                  inputId={`service-${service.id}`}
                  checked={selectedServices.includes(service.id)}
                  onChange={() => handleServiceToggle(service.id)}
                />
                <label htmlFor={`service-${service.id}`} className="service-label">
                  <div className="service-name">{service.name}</div>
                  <div className="service-price">{germanFormatter.formatCurrency(service.price)}</div>
                  {service.description && (
                    <div className="service-description">{service.description}</div>
                  )}
                </label>
              </div>
            ))}
          </div>
        </Panel>

        {/* Action Buttons */}
        <div className="calculator-actions">
          <Button
            label="Neu berechnen"
            icon="pi pi-refresh"
            onClick={calculatePrice}
            loading={calculating}
            className="p-button-primary"
          />
          <Button
            label="Zurücksetzen"
            icon="pi pi-times"
            onClick={handleReset}
            className="p-button-secondary"
            disabled={calculating}
          />
        </div>

        {/* Loading State */}
        {calculating && (
          <div className="calculating-overlay">
            <ProgressSpinner />
            <p>Preis wird berechnet...</p>
          </div>
        )}

        {/* Price Breakdown */}
        {result && !calculating && renderPriceBreakdown()}
      </Card>
    </div>
  );
};

export default PriceCalculator;
