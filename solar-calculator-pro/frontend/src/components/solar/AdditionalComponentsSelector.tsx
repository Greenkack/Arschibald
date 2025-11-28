/**
 * Additional Components Selector Component
 * 
 * UI component for selecting additional PV system components:
 * - Wallbox (EV charging stations)
 * - Energy Management System (EMS)
 * - Power Optimizers
 * - Emergency Power Systems (Notstrom)
 * - Animal Protection (Tierabwehr)
 * 
 * Requirements: funktionen.txt - "Zusatzkomponenten"
 * Task: 251. Additional Components (Wallbox, EMS, Optimizer)
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card } from 'primereact/card';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Tag } from 'primereact/tag';
import { Accordion, AccordionTab } from 'primereact/accordion';
import { Message } from 'primereact/message';
import { Skeleton } from 'primereact/skeleton';
import { Divider } from 'primereact/divider';

import additionalComponentsService, {
  AnyComponent,
  WallboxComponent,
  EMSComponent,
  OptimizerComponent,
  EmergencyPowerComponent,
  AnimalProtectionComponent,
  ComponentCostCalculation
} from '../../services/additionalComponentsService';

import './AdditionalComponentsSelector.css';

// ==================== Interfaces ====================

interface AdditionalComponentsSelectorProps {
  moduleCount?: number;
  inverterManufacturer?: string;
  batteryManufacturer?: string;
  onSelectionChange?: (selectedComponents: AnyComponent[], totalCost: ComponentCostCalculation | null) => void;
  className?: string;
}

interface SelectedComponents {
  wallbox: WallboxComponent | null;
  ems: EMSComponent | null;
  optimizer: OptimizerComponent | null;
  emergency_power: EmergencyPowerComponent | null;
  animal_protection: AnimalProtectionComponent | null;
}

// ==================== Component ====================

export const AdditionalComponentsSelector: React.FC<AdditionalComponentsSelectorProps> = ({
  moduleCount = 0,
  inverterManufacturer,
  batteryManufacturer: _batteryManufacturer,
  onSelectionChange,
  className = ''
}) => {
  // State
  const [wallboxes, setWallboxes] = useState<WallboxComponent[]>([]);
  const [emsSystems, setEmsSystems] = useState<EMSComponent[]>([]);
  const [optimizers, setOptimizers] = useState<OptimizerComponent[]>([]);
  const [emergencyPower, setEmergencyPower] = useState<EmergencyPowerComponent[]>([]);
  const [animalProtection, setAnimalProtection] = useState<AnimalProtectionComponent[]>([]);
  
  const [selected, setSelected] = useState<SelectedComponents>({
    wallbox: null,
    ems: null,
    optimizer: null,
    emergency_power: null,
    animal_protection: null
  });
  
  const [totalCost, setTotalCost] = useState<ComponentCostCalculation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeIndex, setActiveIndex] = useState<number | number[]>([0]);

  // ==================== Data Loading ====================

  const loadComponents = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [wb, ems, opt, ep, ap] = await Promise.all([
        additionalComponentsService.getWallboxes(),
        additionalComponentsService.getEMSSystems(inverterManufacturer),
        additionalComponentsService.getOptimizers(),
        additionalComponentsService.getEmergencyPowerSystems(inverterManufacturer),
        additionalComponentsService.getAnimalProtection()
      ]);
      
      setWallboxes(wb);
      setEmsSystems(ems);
      setOptimizers(opt);
      setEmergencyPower(ep);
      setAnimalProtection(ap);
    } catch (err) {
      setError('Fehler beim Laden der Komponenten');
      console.error('Error loading components:', err);
    } finally {
      setLoading(false);
    }
  }, [inverterManufacturer]);

  const calculateTotalCost = useCallback(async () => {
    const selectedIds: number[] = [];
    
    if (selected.wallbox) selectedIds.push(selected.wallbox.id);
    if (selected.ems) selectedIds.push(selected.ems.id);
    if (selected.optimizer) selectedIds.push(selected.optimizer.id);
    if (selected.emergency_power) selectedIds.push(selected.emergency_power.id);
    if (selected.animal_protection) selectedIds.push(selected.animal_protection.id);
    
    if (selectedIds.length === 0) {
      setTotalCost(null);
      return;
    }
    
    try {
      const cost = await additionalComponentsService.calculateTotalCost(selectedIds, moduleCount);
      setTotalCost(cost);
    } catch (err) {
      console.error('Error calculating cost:', err);
    }
  }, [selected, moduleCount]);

  // ==================== Effects ====================

  useEffect(() => {
    loadComponents();
  }, [loadComponents]);

  useEffect(() => {
    calculateTotalCost();
  }, [calculateTotalCost]);

  useEffect(() => {
    const selectedArray: AnyComponent[] = [];
    if (selected.wallbox) selectedArray.push(selected.wallbox);
    if (selected.ems) selectedArray.push(selected.ems);
    if (selected.optimizer) selectedArray.push(selected.optimizer);
    if (selected.emergency_power) selectedArray.push(selected.emergency_power);
    if (selected.animal_protection) selectedArray.push(selected.animal_protection);
    
    onSelectionChange?.(selectedArray, totalCost);
  }, [selected, totalCost, onSelectionChange]);

  // ==================== Handlers ====================

  const handleSelect = (category: keyof SelectedComponents, component: AnyComponent | null) => {
    setSelected(prev => ({
      ...prev,
      [category]: component
    }));
  };

  const handleToggle = (category: keyof SelectedComponents, component: AnyComponent) => {
    const currentSelected = selected[category];
    if (currentSelected?.id === component.id) {
      handleSelect(category, null);
    } else {
      handleSelect(category, component as any);
    }
  };

  // ==================== Render Helpers ====================

  const renderPrice = (component: AnyComponent) => (
    <span className="component-price">
      {additionalComponentsService.formatPrice(component.price_gross)}
    </span>
  );

  const renderFeatures = (component: AnyComponent) => (
    <div className="features-list">
      {component.features.slice(0, 3).map((feature, idx) => (
        <Tag key={idx} severity="info" value={feature} className="feature-tag" />
      ))}
    </div>
  );

  const renderSelectButton = (category: keyof SelectedComponents, component: AnyComponent) => {
    const isSelected = selected[category]?.id === component.id;
    return (
      <Button
        icon={isSelected ? 'pi pi-check' : 'pi pi-plus'}
        className={`p-button-sm ${isSelected ? 'p-button-success' : 'p-button-outlined'}`}
        onClick={() => handleToggle(category, component)}
        tooltip={isSelected ? 'Ausgewählt' : 'Auswählen'}
      />
    );
  };

  // ==================== Wallbox Table ====================

  const renderWallboxTable = () => (
    <DataTable
      value={wallboxes}
      selection={selected.wallbox}
      onSelectionChange={(e) => handleSelect('wallbox', e.value as WallboxComponent)}
      selectionMode="single"
      dataKey="id"
      className="component-table"
      emptyMessage="Keine Wallboxen gefunden"
    >
      <Column 
        field="model_name" 
        header="Modell"
        body={(wb: WallboxComponent) => (
          <div className="component-name">
            <span className="manufacturer">{wb.manufacturer}</span>
            <span className="model">{wb.model_name}</span>
          </div>
        )}
      />
      <Column 
        field="power_kw" 
        header="Leistung"
        body={(wb: WallboxComponent) => (
          <Tag severity={wb.power_kw >= 22 ? 'success' : 'info'} value={`${wb.power_kw} kW`} />
        )}
      />
      <Column 
        field="phase" 
        header="Phasen"
        body={(wb: WallboxComponent) => wb.phase}
      />
      <Column 
        field="has_solar_charging" 
        header="Solar-Laden"
        body={(wb: WallboxComponent) => (
          <i className={`pi ${wb.has_solar_charging ? 'pi-check text-green-500' : 'pi-times text-red-500'}`} />
        )}
      />
      <Column field="price_gross" header="Preis" body={renderPrice} />
      <Column body={(wb: WallboxComponent) => renderSelectButton('wallbox', wb)} />
    </DataTable>
  );

  // ==================== EMS Table ====================

  const renderEMSTable = () => (
    <DataTable
      value={emsSystems}
      selection={selected.ems}
      onSelectionChange={(e) => handleSelect('ems', e.value as EMSComponent)}
      selectionMode="single"
      dataKey="id"
      className="component-table"
      emptyMessage="Keine EMS-Systeme gefunden"
    >
      <Column 
        field="model_name" 
        header="Modell"
        body={(ems: EMSComponent) => (
          <div className="component-name">
            <span className="manufacturer">{ems.manufacturer}</span>
            <span className="model">{ems.model_name}</span>
          </div>
        )}
      />
      <Column 
        field="supported_inverters" 
        header="Kompatibel mit"
        body={(ems: EMSComponent) => ems.supported_inverters.join(', ')}
      />
      <Column field="features" header="Features" body={renderFeatures} />
      <Column field="price_gross" header="Preis" body={renderPrice} />
      <Column body={(ems: EMSComponent) => renderSelectButton('ems', ems)} />
    </DataTable>
  );

  // ==================== Optimizer Table ====================

  const renderOptimizerTable = () => (
    <DataTable
      value={optimizers}
      selection={selected.optimizer}
      onSelectionChange={(e) => handleSelect('optimizer', e.value as OptimizerComponent)}
      selectionMode="single"
      dataKey="id"
      className="component-table"
      emptyMessage="Keine Optimierer gefunden"
    >
      <Column 
        field="model_name" 
        header="Modell"
        body={(opt: OptimizerComponent) => (
          <div className="component-name">
            <span className="manufacturer">{opt.manufacturer}</span>
            <span className="model">{opt.model_name}</span>
          </div>
        )}
      />
      <Column 
        field="max_power_w" 
        header="Max. Leistung"
        body={(opt: OptimizerComponent) => `${opt.max_power_w} W`}
      />
      <Column 
        field="price_per_module" 
        header="Preis/Modul"
        body={(opt: OptimizerComponent) => additionalComponentsService.formatPrice(opt.price_per_module)}
      />
      <Column 
        header="Gesamt"
        body={(opt: OptimizerComponent) => (
          <span className="total-price">
            {additionalComponentsService.formatPrice(opt.price_per_module * moduleCount)}
            <small> ({moduleCount} Module)</small>
          </span>
        )}
      />
      <Column body={(opt: OptimizerComponent) => renderSelectButton('optimizer', opt)} />
    </DataTable>
  );

  // ==================== Emergency Power Table ====================

  const renderEmergencyPowerTable = () => (
    <DataTable
      value={emergencyPower}
      selection={selected.emergency_power}
      onSelectionChange={(e) => handleSelect('emergency_power', e.value as EmergencyPowerComponent)}
      selectionMode="single"
      dataKey="id"
      className="component-table"
      emptyMessage="Keine Notstrom-Systeme gefunden"
    >
      <Column 
        field="model_name" 
        header="Modell"
        body={(ep: EmergencyPowerComponent) => (
          <div className="component-name">
            <span className="manufacturer">{ep.manufacturer}</span>
            <span className="model">{ep.model_name}</span>
          </div>
        )}
      />
      <Column 
        field="power_kw" 
        header="Leistung"
        body={(ep: EmergencyPowerComponent) => `${ep.power_kw} kW`}
      />
      <Column 
        field="supported_inverters" 
        header="Kompatibel mit"
        body={(ep: EmergencyPowerComponent) => ep.supported_inverters.join(', ')}
      />
      <Column field="price_gross" header="Preis" body={renderPrice} />
      <Column body={(ep: EmergencyPowerComponent) => renderSelectButton('emergency_power', ep)} />
    </DataTable>
  );

  // ==================== Animal Protection Table ====================

  const renderAnimalProtectionTable = () => (
    <DataTable
      value={animalProtection}
      selection={selected.animal_protection}
      onSelectionChange={(e) => handleSelect('animal_protection', e.value as AnimalProtectionComponent)}
      selectionMode="single"
      dataKey="id"
      className="component-table"
      emptyMessage="Keine Tierabwehr-Optionen gefunden"
    >
      <Column 
        field="model_name" 
        header="Modell"
        body={(ap: AnimalProtectionComponent) => (
          <div className="component-name">
            <span className="manufacturer">{ap.manufacturer}</span>
            <span className="model">{ap.model_name}</span>
          </div>
        )}
      />
      <Column 
        field="protection_type" 
        header="Typ"
        body={(ap: AnimalProtectionComponent) => (
          <Tag severity="warning" value={ap.protection_type} />
        )}
      />
      <Column 
        field="coverage_area_m2" 
        header="Abdeckung"
        body={(ap: AnimalProtectionComponent) => `${ap.coverage_area_m2} m²`}
      />
      <Column field="price_gross" header="Preis" body={renderPrice} />
      <Column body={(ap: AnimalProtectionComponent) => renderSelectButton('animal_protection', ap)} />
    </DataTable>
  );

  // ==================== Cost Summary ====================

  const renderCostSummary = () => {
    if (!totalCost) return null;
    
    return (
      <Card className="cost-summary-card">
        <h4>Kostenübersicht Zusatzkomponenten</h4>
        <div className="cost-items">
          {totalCost.components.map((item, idx) => (
            <div key={idx} className="cost-item">
              <span className="item-name">
                {additionalComponentsService.formatComponentName(item.component)}
                {item.quantity > 1 && <small> (×{item.quantity})</small>}
              </span>
              <span className="item-price">
                {additionalComponentsService.formatPrice(item.cost_gross)}
              </span>
            </div>
          ))}
        </div>
        <Divider />
        <div className="cost-totals">
          <div className="cost-row">
            <span>Zwischensumme (netto)</span>
            <span>{additionalComponentsService.formatPrice(totalCost.subtotal_net)}</span>
          </div>
          <div className="cost-row">
            <span>Installation (geschätzt)</span>
            <span>{additionalComponentsService.formatPrice(totalCost.installation_cost)}</span>
          </div>
          <div className="cost-row total">
            <span>Gesamt (brutto)</span>
            <span>{additionalComponentsService.formatPrice(totalCost.total_gross)}</span>
          </div>
        </div>
      </Card>
    );
  };

  // ==================== Main Render ====================

  if (loading) {
    return (
      <div className={`additional-components-selector ${className}`}>
        <Card>
          <Skeleton height="2rem" className="mb-3" />
          <Skeleton height="15rem" />
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`additional-components-selector ${className}`}>
        <Message severity="error" text={error} />
      </div>
    );
  }

  return (
    <div className={`additional-components-selector ${className}`}>
      <div className="selector-content">
        <Accordion 
          multiple 
          activeIndex={activeIndex as number[]} 
          onTabChange={(e) => setActiveIndex(e.index as number[])}
        >
          <AccordionTab 
            header={
              <span className="accordion-header">
                <i className="pi pi-car" />
                Wallbox (E-Auto Ladestation)
                {selected.wallbox && <Tag severity="success" value="Ausgewählt" className="ml-2" />}
              </span>
            }
          >
            {renderWallboxTable()}
          </AccordionTab>
          
          <AccordionTab 
            header={
              <span className="accordion-header">
                <i className="pi pi-chart-line" />
                Energiemanagement (EMS)
                {selected.ems && <Tag severity="success" value="Ausgewählt" className="ml-2" />}
              </span>
            }
          >
            {renderEMSTable()}
          </AccordionTab>
          
          <AccordionTab 
            header={
              <span className="accordion-header">
                <i className="pi pi-bolt" />
                Leistungsoptimierer
                {selected.optimizer && <Tag severity="success" value="Ausgewählt" className="ml-2" />}
              </span>
            }
          >
            <Message 
              severity="info" 
              text={`Optimierer werden pro Modul berechnet. Aktuell: ${moduleCount} Module`}
              className="mb-3"
            />
            {renderOptimizerTable()}
          </AccordionTab>
          
          <AccordionTab 
            header={
              <span className="accordion-header">
                <i className="pi pi-shield" />
                Notstrom
                {selected.emergency_power && <Tag severity="success" value="Ausgewählt" className="ml-2" />}
              </span>
            }
          >
            {renderEmergencyPowerTable()}
          </AccordionTab>
          
          <AccordionTab 
            header={
              <span className="accordion-header">
                <i className="pi pi-heart" />
                Tierabwehr (Marderschutz)
                {selected.animal_protection && <Tag severity="success" value="Ausgewählt" className="ml-2" />}
              </span>
            }
          >
            {renderAnimalProtectionTable()}
          </AccordionTab>
        </Accordion>
      </div>
      
      {renderCostSummary()}
    </div>
  );
};

export default AdditionalComponentsSelector;
