/**
 * PV Module Selector Component
 * 
 * Provides module selection with manufacturer/model dropdown,
 * specifications display, and system power calculation.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Tag } from 'primereact/tag';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Dialog } from 'primereact/dialog';
import { pvModuleService, PVModule, SystemPowerResult, ModuleComparison } from '../../services/pvModuleService';
import './PVModuleSelector.css';

export interface PVModuleSelectorProps {
  value?: { moduleId: number; moduleCount: number };
  onChange?: (value: { moduleId: number; moduleCount: number; systemPower: SystemPowerResult }) => void;
  roofAreaM2?: number;
  disabled?: boolean;
  showRecommendations?: boolean;
  showComparison?: boolean;
}

const PVModuleSelector: React.FC<PVModuleSelectorProps> = ({
  value,
  onChange,
  roofAreaM2,
  disabled = false,
  showRecommendations = true,
  showComparison = true
}) => {
  const [manufacturers, setManufacturers] = useState<string[]>([]);
  const [modules, setModules] = useState<PVModule[]>([]);
  const [selectedManufacturer, setSelectedManufacturer] = useState<string>('');
  const [selectedModule, setSelectedModule] = useState<PVModule | null>(null);
  const [moduleCount, setModuleCount] = useState<number>(20);
  const [systemPower, setSystemPower] = useState<SystemPowerResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [compareModules, setCompareModules] = useState<number[]>([]);
  const [comparison, setComparison] = useState<ModuleComparison | null>(null);
  const [showCompareDialog, setShowCompareDialog] = useState(false);

  // Load manufacturers on mount
  useEffect(() => {
    loadManufacturers();
  }, []);

  // Load modules when manufacturer changes
  useEffect(() => {
    if (selectedManufacturer) {
      loadModulesByManufacturer(selectedManufacturer);
    }
  }, [selectedManufacturer]);

  // Calculate system power when module or count changes
  useEffect(() => {
    if (selectedModule && moduleCount > 0) {
      calculateSystem();
    }
  }, [selectedModule, moduleCount]);

  // Initialize from value prop
  useEffect(() => {
    if (value?.moduleId && !selectedModule) {
      loadModuleById(value.moduleId);
      setModuleCount(value.moduleCount || 20);
    }
  }, [value]);

  const loadManufacturers = async () => {
    try {
      const data = await pvModuleService.getManufacturers();
      setManufacturers(data);
    } catch (error) {
      console.error('Error loading manufacturers:', error);
    }
  };

  const loadModulesByManufacturer = async (manufacturer: string) => {
    setLoading(true);
    try {
      const data = await pvModuleService.getModulesByManufacturer(manufacturer);
      setModules(data);
    } catch (error) {
      console.error('Error loading modules:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadModuleById = async (moduleId: number) => {
    try {
      const module = await pvModuleService.getModule(moduleId);
      setSelectedManufacturer(module.manufacturer);
      setSelectedModule(module);
    } catch (error) {
      console.error('Error loading module:', error);
    }
  };

  const calculateSystem = useCallback(async () => {
    if (!selectedModule) return;
    
    try {
      const result = await pvModuleService.calculateSystemPower(selectedModule.id, moduleCount);
      setSystemPower(result);
      
      if (onChange) {
        onChange({
          moduleId: selectedModule.id,
          moduleCount,
          systemPower: result
        });
      }
    } catch (error) {
      console.error('Error calculating system:', error);
    }
  }, [selectedModule, moduleCount, onChange]);

  const handleCompare = async () => {
    if (compareModules.length < 2) return;
    
    try {
      const result = await pvModuleService.compareModules(compareModules);
      setComparison(result);
      setShowCompareDialog(true);
    } catch (error) {
      console.error('Error comparing modules:', error);
    }
  };

  const toggleCompareModule = (moduleId: number) => {
    setCompareModules(prev => {
      if (prev.includes(moduleId)) {
        return prev.filter(id => id !== moduleId);
      }
      if (prev.length >= 5) return prev;
      return [...prev, moduleId];
    });
  };

  const manufacturerOptions = manufacturers.map(m => ({ label: m, value: m }));
  const moduleOptions = modules.map(m => ({
    label: `${m.model} (${m.power_wp} Wp)`,
    value: m
  }));

  return (
    <div className="pv-module-selector">
      {/* Selection Section */}
      <Card className="selection-card">
        <h4>PV-Modul Auswahl</h4>
        
        <div className="selection-grid">
          <div className="field">
            <label>Hersteller</label>
            <Dropdown
              value={selectedManufacturer}
              options={manufacturerOptions}
              onChange={(e) => {
                setSelectedManufacturer(e.value);
                setSelectedModule(null);
              }}
              placeholder="Hersteller wählen"
              disabled={disabled}
              filter
              className="w-full"
            />
          </div>
          
          <div className="field">
            <label>Modul</label>
            <Dropdown
              value={selectedModule}
              options={moduleOptions}
              onChange={(e) => setSelectedModule(e.value)}
              placeholder="Modul wählen"
              disabled={disabled || !selectedManufacturer}
              filter
              className="w-full"
            />
            {loading && <ProgressSpinner style={{ width: '20px', height: '20px' }} />}
          </div>
          
          <div className="field">
            <label>Anzahl Module</label>
            <InputNumber
              value={moduleCount}
              onValueChange={(e) => setModuleCount(e.value || 1)}
              min={1}
              max={500}
              disabled={disabled}
              showButtons
              className="w-full"
            />
          </div>
        </div>
      </Card>

      {/* Module Specifications */}
      {selectedModule && (
        <Card className="specs-card">
          <h4>Modul-Spezifikationen</h4>
          <div className="specs-grid">
            <div className="spec-item">
              <span className="spec-label">Leistung</span>
              <span className="spec-value">{selectedModule.power_wp} Wp</span>
            </div>
            <div className="spec-item">
              <span className="spec-label">Wirkungsgrad</span>
              <span className="spec-value">{selectedModule.efficiency.toFixed(1)}%</span>
            </div>
            <div className="spec-item">
              <span className="spec-label">Abmessungen</span>
              <span className="spec-value">{selectedModule.width_mm} × {selectedModule.height_mm} mm</span>
            </div>
            <div className="spec-item">
              <span className="spec-label">Gewicht</span>
              <span className="spec-value">{selectedModule.weight_kg} kg</span>
            </div>
            <div className="spec-item">
              <span className="spec-label">Zelltyp</span>
              <Tag value={selectedModule.cell_type} />
            </div>
            <div className="spec-item">
              <span className="spec-label">Garantie</span>
              <span className="spec-value">{selectedModule.warranty_years} Jahre</span>
            </div>
            <div className="spec-item">
              <span className="spec-label">Preis (netto)</span>
              <span className="spec-value">{pvModuleService.formatPrice(selectedModule.price_net)}</span>
            </div>
            <div className="spec-item">
              <span className="spec-label">Preis (brutto)</span>
              <span className="spec-value">{pvModuleService.formatPrice(selectedModule.price_gross)}</span>
            </div>
          </div>
        </Card>
      )}

      {/* System Power Calculation */}
      {systemPower && (
        <Card className="system-card">
          <h4>Anlagenleistung</h4>
          <div className="system-grid">
            <div className="system-item highlight">
              <span className="system-label">Gesamtleistung</span>
              <span className="system-value">{systemPower.total_power_kwp} kWp</span>
            </div>
            <div className="system-item">
              <span className="system-label">Anzahl Module</span>
              <span className="system-value">{systemPower.module_count}</span>
            </div>
            <div className="system-item">
              <span className="system-label">Gesamtfläche</span>
              <span className="system-value">{systemPower.total_area_m2} m²</span>
            </div>
            <div className="system-item">
              <span className="system-label">Gesamtgewicht</span>
              <span className="system-value">{systemPower.total_weight_kg} kg</span>
            </div>
            <div className="system-item highlight">
              <span className="system-label">Modulpreis (brutto)</span>
              <span className="system-value">{pvModuleService.formatPrice(systemPower.price_gross)}</span>
            </div>
            <div className="system-item">
              <span className="system-label">Preis pro kWp</span>
              <span className="system-value">{pvModuleService.formatPrice(systemPower.price_per_kwp_net)}</span>
            </div>
          </div>
        </Card>
      )}

      {/* Module List with Compare */}
      {showComparison && modules.length > 0 && (
        <Card className="modules-list-card">
          <div className="modules-header">
            <h4>Verfügbare Module</h4>
            {compareModules.length >= 2 && (
              <Button 
                label={`Vergleichen (${compareModules.length})`}
                icon="pi pi-chart-bar"
                onClick={handleCompare}
                className="p-button-sm"
              />
            )}
          </div>
          
          <DataTable value={modules} size="small" stripedRows>
            <Column 
              header="" 
              body={(rowData: PVModule) => (
                <input
                  type="checkbox"
                  checked={compareModules.includes(rowData.id)}
                  onChange={() => toggleCompareModule(rowData.id)}
                  disabled={!compareModules.includes(rowData.id) && compareModules.length >= 5}
                />
              )}
              style={{ width: '40px' }}
            />
            <Column field="model" header="Modell" />
            <Column field="power_wp" header="Leistung" body={(row: PVModule) => `${row.power_wp} Wp`} />
            <Column field="efficiency" header="Wirkungsgrad" body={(row: PVModule) => `${row.efficiency.toFixed(1)}%`} />
            <Column field="cell_type" header="Zelltyp" body={(row: PVModule) => <Tag value={row.cell_type} />} />
            <Column field="price_gross" header="Preis" body={(row: PVModule) => pvModuleService.formatPrice(row.price_gross)} />
            <Column 
              header="" 
              body={(rowData: PVModule) => (
                <Button
                  icon="pi pi-check"
                  className="p-button-sm p-button-text"
                  onClick={() => setSelectedModule(rowData)}
                  tooltip="Auswählen"
                />
              )}
              style={{ width: '60px' }}
            />
          </DataTable>
        </Card>
      )}

      {/* Comparison Dialog */}
      <Dialog
        header="Modulvergleich"
        visible={showCompareDialog}
        onHide={() => setShowCompareDialog(false)}
        style={{ width: '90vw', maxWidth: '1200px' }}
      >
        {comparison && (
          <DataTable value={comparison.modules} size="small">
            <Column field="manufacturer" header="Hersteller" />
            <Column field="model" header="Modell" />
            <Column 
              field="power_wp" 
              header="Leistung" 
              body={(row) => (
                <span className={comparison.best.highest_power === row.id ? 'best-value' : ''}>
                  {row.power_wp} Wp
                </span>
              )}
            />
            <Column 
              field="efficiency" 
              header="Wirkungsgrad"
              body={(row) => (
                <span className={comparison.best.highest_efficiency === row.id ? 'best-value' : ''}>
                  {row.efficiency.toFixed(1)}%
                </span>
              )}
            />
            <Column field="dimensions" header="Abmessungen" />
            <Column 
              field="weight_kg" 
              header="Gewicht"
              body={(row) => (
                <span className={comparison.best.lightest === row.id ? 'best-value' : ''}>
                  {row.weight_kg} kg
                </span>
              )}
            />
            <Column 
              field="warranty_years" 
              header="Garantie"
              body={(row) => (
                <span className={comparison.best.longest_warranty === row.id ? 'best-value' : ''}>
                  {row.warranty_years} Jahre
                </span>
              )}
            />
            <Column 
              field="price_gross" 
              header="Preis"
              body={(row) => (
                <span className={comparison.best.lowest_price === row.id ? 'best-value' : ''}>
                  {pvModuleService.formatPrice(row.price_gross)}
                </span>
              )}
            />
            <Column 
              field="price_per_wp" 
              header="€/Wp"
              body={(row) => (
                <span className={comparison.best.best_value === row.id ? 'best-value' : ''}>
                  {row.price_per_wp.toFixed(3)} €
                </span>
              )}
            />
          </DataTable>
        )}
      </Dialog>
    </div>
  );
};

export default PVModuleSelector;
