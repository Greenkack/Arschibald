/**
 * Inverter Selector Component
 * 
 * Provides inverter selection with sizing calculation,
 * compatibility check, and multi-inverter configuration.
 * 
 * Requirements: funktionen.txt - "Wechselrichter"
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Dropdown } from 'primereact/dropdown';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Tag } from 'primereact/tag';
import { ProgressBar } from 'primereact/progressbar';
import { Checkbox } from 'primereact/checkbox';
import { Message } from 'primereact/message';
import { Dialog } from 'primereact/dialog';
import { 
  inverterService, 
  Inverter, 
  InverterSelectionResult,
  InverterSizingResult,
  CompatibilityResult 
} from '../../services/inverterService';
import './InverterSelector.css';

// ==================== Props Interface ====================

export interface InverterSelectorProps {
  pvPowerKwp: number;
  moduleVoltageVmp?: number;
  moduleCurrentImp?: number;
  modulesPerString?: number;
  numberOfStrings?: number;
  onChange?: (inverter: Inverter, sizing: InverterSizingResult) => void;
  disabled?: boolean;
}

// ==================== Component ====================

const InverterSelector: React.FC<InverterSelectorProps> = ({
  pvPowerKwp,
  moduleVoltageVmp = 40,
  moduleCurrentImp = 10,
  modulesPerString = 10,
  numberOfStrings = 2,
  onChange,
  disabled = false
}) => {
  // State
  const [manufacturers, setManufacturers] = useState<string[]>([]);
  const [inverters, setInverters] = useState<Inverter[]>([]);
  const [selectedManufacturer, setSelectedManufacturer] = useState<string>('');
  const [selectedInverter, setSelectedInverter] = useState<Inverter | null>(null);
  const [sizing, setSizing] = useState<InverterSizingResult | null>(null);
  const [selection, setSelection] = useState<InverterSelectionResult | null>(null);
  const [compatibility, setCompatibility] = useState<CompatibilityResult | null>(null);
  const [hybridOnly, setHybridOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showDetailsDialog, setShowDetailsDialog] = useState(false);

  // Load manufacturers on mount
  useEffect(() => {
    loadManufacturers();
    loadInverters();
  }, []);

  // Calculate sizing when PV power changes
  useEffect(() => {
    if (pvPowerKwp > 0) {
      calculateSizing();
      autoSelectInverter();
    }
  }, [pvPowerKwp, hybridOnly]);

  // Check compatibility when inverter is selected
  useEffect(() => {
    if (selectedInverter && pvPowerKwp > 0) {
      checkCompatibility();
    }
  }, [selectedInverter, pvPowerKwp]);

  // Notify parent of changes
  useEffect(() => {
    if (selectedInverter && sizing && onChange) {
      onChange(selectedInverter, sizing);
    }
  }, [selectedInverter, sizing]);

  // ==================== Data Loading ====================

  const loadManufacturers = async () => {
    try {
      const data = await inverterService.getManufacturers();
      setManufacturers(data);
    } catch (error) {
      console.error('Error loading manufacturers:', error);
    }
  };

  const loadInverters = async () => {
    setLoading(true);
    try {
      const data = await inverterService.getAllInverters({
        activeOnly: true,
        hybridOnly: hybridOnly,
        manufacturer: selectedManufacturer || undefined
      });
      setInverters(data);
    } catch (error) {
      console.error('Error loading inverters:', error);
    } finally {
      setLoading(false);
    }
  };

  // ==================== Calculations ====================

  const calculateSizing = async () => {
    try {
      const result = await inverterService.calculateSizing({
        pv_power_kwp: pvPowerKwp,
        module_voltage_vmp: moduleVoltageVmp,
        module_current_imp: moduleCurrentImp,
        modules_per_string: modulesPerString,
        number_of_strings: numberOfStrings
      });
      setSizing(result);
    } catch (error) {
      console.error('Error calculating sizing:', error);
    }
  };

  const autoSelectInverter = async () => {
    try {
      const result = await inverterService.selectInverter({
        pv_power_kwp: pvPowerKwp,
        is_hybrid_required: hybridOnly
      });
      setSelection(result);
      setSelectedInverter(result.selected_inverter);
    } catch (error) {
      console.error('Error auto-selecting inverter:', error);
    }
  };

  const checkCompatibility = async () => {
    if (!selectedInverter) return;
    
    try {
      const stringVoltage = moduleVoltageVmp * modulesPerString;
      const totalCurrent = moduleCurrentImp * numberOfStrings;
      
      const result = await inverterService.checkCompatibility({
        inverter_id: selectedInverter.id,
        pv_power_kwp: pvPowerKwp,
        string_voltage: stringVoltage,
        total_current: totalCurrent,
        number_of_strings: numberOfStrings
      });
      setCompatibility(result);
    } catch (error) {
      console.error('Error checking compatibility:', error);
    }
  };

  // ==================== Event Handlers ====================

  const handleManufacturerChange = (manufacturer: string) => {
    setSelectedManufacturer(manufacturer);
    setSelectedInverter(null);
  };

  const handleInverterSelect = (inverter: Inverter) => {
    setSelectedInverter(inverter);
  };

  const handleHybridChange = (checked: boolean) => {
    setHybridOnly(checked);
    setSelectedInverter(null);
  };

  // ==================== Render Helpers ====================

  const getDcAcRatioSeverity = (ratio: number): 'success' | 'warning' | 'danger' => {
    if (ratio >= 0.9 && ratio <= 1.1) return 'success';
    if (ratio >= 0.8 && ratio <= 1.2) return 'warning';
    return 'danger';
  };

  const manufacturerOptions = [
    { label: 'Alle Hersteller', value: '' },
    ...manufacturers.map(m => ({ label: m, value: m }))
  ];

  // ==================== Render ====================

  return (
    <div className="inverter-selector">
      {/* Sizing Info */}
      {sizing && (
        <Card className="sizing-card">
          <h4>Wechselrichter-Dimensionierung</h4>
          <div className="sizing-info">
            <div className="sizing-item">
              <span className="label">PV-Leistung</span>
              <span className="value">{pvPowerKwp.toFixed(1)} kWp</span>
            </div>
            <div className="sizing-item highlight">
              <span className="label">Empfohlene WR-Leistung</span>
              <span className="value">{sizing.recommended_power_range.optimal_kw.toFixed(1)} kW</span>
            </div>
            <div className="sizing-item">
              <span className="label">Bereich</span>
              <span className="value">
                {sizing.recommended_power_range.min_kw.toFixed(1)} - {sizing.recommended_power_range.max_kw.toFixed(1)} kW
              </span>
            </div>
            <div className="sizing-item">
              <span className="label">DC/AC-Verhältnis</span>
              <span className="value">{sizing.sizing_ratio.dc_ac_ratio.toFixed(2)}</span>
            </div>
          </div>
        </Card>
      )}

      {/* Selection Controls */}
      <Card className="selection-card">
        <h4>Wechselrichter-Auswahl</h4>
        
        <div className="selection-controls">
          <div className="field">
            <label>Hersteller</label>
            <Dropdown
              value={selectedManufacturer}
              options={manufacturerOptions}
              onChange={(e) => handleManufacturerChange(e.value)}
              placeholder="Hersteller wählen"
              disabled={disabled}
              className="w-full"
            />
          </div>
          
          <div className="field checkbox-field">
            <Checkbox
              inputId="hybridOnly"
              checked={hybridOnly}
              onChange={(e) => handleHybridChange(e.checked || false)}
              disabled={disabled}
            />
            <label htmlFor="hybridOnly">Nur Hybrid-Wechselrichter</label>
          </div>
        </div>

        {/* Auto-Selection Result */}
        {selection && (
          <div className="auto-selection">
            <Message 
              severity="info" 
              text={`Empfehlung: ${selection.selected_inverter.manufacturer} ${selection.selected_inverter.model_name} (Score: ${selection.selection_score})`}
            />
          </div>
        )}
      </Card>

      {/* Selected Inverter Details */}
      {selectedInverter && (
        <Card className="details-card">
          <div className="details-header">
            <h4>{selectedInverter.manufacturer} {selectedInverter.model_name}</h4>
            <Button 
              icon="pi pi-info-circle" 
              className="p-button-text"
              onClick={() => setShowDetailsDialog(true)}
              tooltip="Details anzeigen"
            />
          </div>
          
          <div className="specs-grid">
            <div className="spec-item">
              <span className="spec-label">AC-Leistung</span>
              <span className="spec-value">{selectedInverter.power_kw} kW</span>
            </div>
            <div className="spec-item">
              <span className="spec-label">Wirkungsgrad</span>
              <span className="spec-value">{selectedInverter.efficiency_percent}%</span>
            </div>
            <div className="spec-item">
              <span className="spec-label">Max. DC-Spannung</span>
              <span className="spec-value">{selectedInverter.max_dc_voltage} V</span>
            </div>
            <div className="spec-item">
              <span className="spec-label">MPPT-Tracker</span>
              <span className="spec-value">{selectedInverter.mppt_count}</span>
            </div>
            <div className="spec-item">
              <span className="spec-label">Max. DC-Strom</span>
              <span className="spec-value">{selectedInverter.max_dc_current} A</span>
            </div>
            <div className="spec-item">
              <span className="spec-label">Garantie</span>
              <span className="spec-value">{selectedInverter.warranty_years} Jahre</span>
            </div>
            <div className="spec-item highlight">
              <span className="spec-label">Preis (brutto)</span>
              <span className="spec-value">{inverterService.formatPrice(selectedInverter.price_gross)}</span>
            </div>
            <div className="spec-item">
              <span className="spec-label">Typ</span>
              <Tag value={selectedInverter.is_hybrid ? 'Hybrid' : 'Standard'} 
                   severity={selectedInverter.is_hybrid ? 'success' : 'info'} />
            </div>
          </div>

          {/* Features */}
          {selectedInverter.features.length > 0 && (
            <div className="features">
              <span className="features-label">Features:</span>
              {selectedInverter.features.map((feature, idx) => (
                <Tag key={idx} value={feature} className="feature-tag" />
              ))}
            </div>
          )}
        </Card>
      )}

      {/* Compatibility Check */}
      {compatibility && (
        <Card className="compatibility-card">
          <h4>Kompatibilitätsprüfung</h4>
          
          <div className="compatibility-score">
            <ProgressBar 
              value={compatibility.compatibility_score} 
              showValue={true}
              color={compatibility.is_compatible ? 'var(--green-500)' : 'var(--red-500)'}
            />
          </div>
          
          <div className="compatibility-checks">
            {compatibility.checks.map((check, idx) => (
              <div key={idx} className={`check-item ${check.status.toLowerCase()}`}>
                <i className={`pi ${check.status === 'OK' ? 'pi-check-circle' : 'pi-times-circle'}`}></i>
                <span className="check-name">{check.check}</span>
                <span className="check-details">{check.details}</span>
              </div>
            ))}
          </div>
          
          {!compatibility.is_compatible && (
            <Message severity="error" text="Wechselrichter ist nicht kompatibel mit dem PV-System!" />
          )}
        </Card>
      )}

      {/* Inverter List */}
      <Card className="inverter-list-card">
        <h4>Verfügbare Wechselrichter</h4>
        
        <DataTable 
          value={inverters} 
          size="small" 
          stripedRows
          loading={loading}
          selectionMode="single"
          selection={selectedInverter}
          onSelectionChange={(e) => handleInverterSelect(e.value)}
          dataKey="id"
        >
          <Column field="manufacturer" header="Hersteller" sortable />
          <Column field="model_name" header="Modell" sortable />
          <Column 
            field="power_kw" 
            header="Leistung" 
            body={(row: Inverter) => `${row.power_kw} kW`}
            sortable 
          />
          <Column 
            field="efficiency_percent" 
            header="Wirkungsgrad" 
            body={(row: Inverter) => `${row.efficiency_percent}%`}
            sortable 
          />
          <Column 
            field="is_hybrid" 
            header="Typ" 
            body={(row: Inverter) => (
              <Tag value={row.is_hybrid ? 'Hybrid' : 'Standard'} 
                   severity={row.is_hybrid ? 'success' : 'info'} />
            )}
          />
          <Column 
            field="price_gross" 
            header="Preis" 
            body={(row: Inverter) => inverterService.formatPrice(row.price_gross)}
            sortable 
          />
        </DataTable>
      </Card>

      {/* Details Dialog */}
      <Dialog
        header={selectedInverter ? `${selectedInverter.manufacturer} ${selectedInverter.model_name}` : ''}
        visible={showDetailsDialog}
        onHide={() => setShowDetailsDialog(false)}
        style={{ width: '600px' }}
      >
        {selectedInverter && (
          <div className="inverter-details-dialog">
            <table className="details-table">
              <tbody>
                <tr><td>Hersteller</td><td>{selectedInverter.manufacturer}</td></tr>
                <tr><td>Modell</td><td>{selectedInverter.model_name}</td></tr>
                <tr><td>AC-Leistung</td><td>{selectedInverter.power_kw} kW</td></tr>
                <tr><td>Wirkungsgrad</td><td>{selectedInverter.efficiency_percent}%</td></tr>
                <tr><td>Max. DC-Spannung</td><td>{selectedInverter.max_dc_voltage} V</td></tr>
                <tr><td>MPPT-Tracker</td><td>{selectedInverter.mppt_count}</td></tr>
                <tr><td>Max. DC-Strom/MPPT</td><td>{selectedInverter.max_dc_current} A</td></tr>
                <tr><td>Gewicht</td><td>{selectedInverter.weight_kg} kg</td></tr>
                <tr><td>Garantie</td><td>{selectedInverter.warranty_years} Jahre</td></tr>
                <tr><td>Preis (netto)</td><td>{inverterService.formatPrice(selectedInverter.price_net)}</td></tr>
                <tr><td>Preis (brutto)</td><td>{inverterService.formatPrice(selectedInverter.price_gross)}</td></tr>
                <tr><td>Typ</td><td>{selectedInverter.is_hybrid ? 'Hybrid' : 'Standard'}</td></tr>
                <tr><td>Features</td><td>{selectedInverter.features.join(', ')}</td></tr>
              </tbody>
            </table>
          </div>
        )}
      </Dialog>
    </div>
  );
};

export default InverterSelector;
