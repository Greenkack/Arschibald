/**
 * Battery Storage Selector Component
 * 
 * UI component for selecting and configuring battery storage systems.
 * Includes product database selection, specifications display, sizing,
 * and ROI analysis.
 * 
 * Requirements: funktionen.txt - "Batteriespeicher"
 * Task: 250. Battery Storage Configuration
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Dropdown } from 'primereact/dropdown';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Tag } from 'primereact/tag';
import { InputNumber } from 'primereact/inputnumber';
import { Checkbox } from 'primereact/checkbox';
import { TabView, TabPanel } from 'primereact/tabview';
import { Chart } from 'primereact/chart';
import { Message } from 'primereact/message';
import { Skeleton } from 'primereact/skeleton';

import batteryStorageService, {
  BatteryStorage,
  BatterySizingResult,
  BatteryROIResult
} from '../../services/batteryStorageService';

import './BatteryStorageSelector.css';

// ==================== Interfaces ====================

interface BatteryStorageSelectorProps {
  pvSystemKwp?: number;
  annualConsumptionKwh?: number;
  /** Used for filtering compatible batteries */
  inverterManufacturer?: string;
  onBatterySelect?: (battery: BatteryStorage | null) => void;
  onSizingCalculated?: (sizing: BatterySizingResult) => void;
  onROICalculated?: (roi: BatteryROIResult) => void;
  showROIAnalysis?: boolean;
  showComparison?: boolean;
  className?: string;
}

// ==================== Component ====================

export const BatteryStorageSelector: React.FC<BatteryStorageSelectorProps> = ({
  pvSystemKwp = 10,
  annualConsumptionKwh = 4500,
  inverterManufacturer: _inverterManufacturer,
  onBatterySelect,
  onSizingCalculated,
  onROICalculated,
  showROIAnalysis = true,
  showComparison = true,
  className = ''
}) => {
  // State
  const [batteries, setBatteries] = useState<BatteryStorage[]>([]);
  const [manufacturers, setManufacturers] = useState<string[]>([]);
  const [selectedBattery, setSelectedBattery] = useState<BatteryStorage | null>(null);
  const [selectedManufacturer, setSelectedManufacturer] = useState<string | null>(null);
  const [sizingResult, setSizingResult] = useState<BatterySizingResult | null>(null);
  const [roiResult, setROIResult] = useState<BatteryROIResult | null>(null);
  const [comparisonBatteries, setComparisonBatteries] = useState<BatteryStorage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  
  // ROI Parameters
  const [electricityPrice, setElectricityPrice] = useState(0.35);
  const [feedInTariff, setFeedInTariff] = useState(0.082);
  const [analysisYears, setAnalysisYears] = useState(20);
  const [includeNoStorage, setIncludeNoStorage] = useState(true);

  // ==================== Data Loading ====================

  const loadBatteries = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [batteriesData, manufacturersData] = await Promise.all([
        batteryStorageService.getAllBatteries({
          activeOnly: true,
          includeNoStorage,
          manufacturer: selectedManufacturer || undefined
        }),
        batteryStorageService.getManufacturers()
      ]);
      
      setBatteries(batteriesData);
      setManufacturers(manufacturersData);
    } catch (err) {
      setError('Fehler beim Laden der Batteriespeicher');
      console.error('Error loading batteries:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedManufacturer, includeNoStorage]);

  const calculateSizing = useCallback(async () => {
    try {
      const result = await batteryStorageService.calculateSizing({
        annual_consumption_kwh: annualConsumptionKwh,
        pv_system_kwp: pvSystemKwp
      });
      setSizingResult(result);
      onSizingCalculated?.(result);
    } catch (err) {
      console.error('Error calculating sizing:', err);
    }
  }, [annualConsumptionKwh, pvSystemKwp, onSizingCalculated]);

  const calculateROI = useCallback(async () => {
    if (!selectedBattery || selectedBattery.id === 0) {
      setROIResult(null);
      return;
    }
    
    try {
      const result = await batteryStorageService.calculateROI({
        battery_id: selectedBattery.id,
        annual_consumption_kwh: annualConsumptionKwh,
        pv_production_kwh: pvSystemKwp * 1000,
        electricity_price: electricityPrice,
        feed_in_tariff: feedInTariff,
        analysis_years: analysisYears
      });
      setROIResult(result);
      onROICalculated?.(result);
    } catch (err) {
      console.error('Error calculating ROI:', err);
    }
  }, [selectedBattery, annualConsumptionKwh, pvSystemKwp, electricityPrice, feedInTariff, analysisYears, onROICalculated]);

  // ==================== Effects ====================

  useEffect(() => {
    loadBatteries();
  }, [loadBatteries]);

  useEffect(() => {
    calculateSizing();
  }, [calculateSizing]);

  useEffect(() => {
    if (selectedBattery && showROIAnalysis) {
      calculateROI();
    }
  }, [selectedBattery, calculateROI, showROIAnalysis]);

  // ==================== Handlers ====================

  const handleBatterySelect = (battery: BatteryStorage | null) => {
    if (!battery) return;
    setSelectedBattery(battery);
    onBatterySelect?.(battery.id === 0 ? null : battery);
  };

  const handleAddToComparison = (battery: BatteryStorage) => {
    if (battery.id === 0) return;
    if (!comparisonBatteries.find(b => b.id === battery.id)) {
      setComparisonBatteries([...comparisonBatteries, battery]);
    }
  };

  const handleRemoveFromComparison = (batteryId: number) => {
    setComparisonBatteries(comparisonBatteries.filter(b => b.id !== batteryId));
  };

  // ==================== Render Helpers ====================

  const renderBatteryName = (battery: BatteryStorage) => {
    if (battery.id === 0) {
      return <span className="no-storage-label">Kein Speicher</span>;
    }
    return (
      <div className="battery-name">
        <span className="manufacturer">{battery.manufacturer}</span>
        <span className="model">{battery.model_name}</span>
      </div>
    );
  };

  const renderCapacity = (battery: BatteryStorage) => {
    if (battery.id === 0) return '-';
    return (
      <div className="capacity-display">
        <span className="capacity-value">{battery.capacity_kwh.toFixed(1)}</span>
        <span className="capacity-unit">kWh</span>
      </div>
    );
  };

  const renderPrice = (battery: BatteryStorage) => {
    if (battery.id === 0) return '-';
    return (
      <div className="price-display">
        <span className="price-gross">
          {batteryStorageService.formatPrice(battery.price_gross)}
        </span>
        <span className="price-per-kwh">
          ({batteryStorageService.formatPricePerKwh(battery.price_per_kwh)})
        </span>
      </div>
    );
  };

  const renderEfficiency = (battery: BatteryStorage) => {
    if (battery.id === 0) return '-';
    const severity = battery.efficiency_percent >= 95 ? 'success' : 
                    battery.efficiency_percent >= 90 ? 'warning' : 'danger';
    return (
      <Tag severity={severity} value={`${battery.efficiency_percent}%`} />
    );
  };

  const renderWarranty = (battery: BatteryStorage) => {
    if (battery.id === 0) return '-';
    return batteryStorageService.formatWarranty(battery.warranty_years, battery.warranty_cycles);
  };

  const renderFeatures = (battery: BatteryStorage) => {
    if (battery.id === 0 || battery.features.length === 0) return '-';
    return (
      <div className="features-list">
        {battery.features.slice(0, 3).map((feature, index) => (
          <Tag key={index} severity="info" value={feature} className="feature-tag" />
        ))}
        {battery.features.length > 3 && (
          <Tag severity="secondary" value={`+${battery.features.length - 3}`} />
        )}
      </div>
    );
  };

  const renderActions = (battery: BatteryStorage) => {
    const isSelected = selectedBattery?.id === battery.id;
    const isInComparison = comparisonBatteries.some(b => b.id === battery.id);
    
    return (
      <div className="action-buttons">
        <Button
          icon={isSelected ? 'pi pi-check' : 'pi pi-plus'}
          className={`p-button-sm ${isSelected ? 'p-button-success' : 'p-button-outlined'}`}
          onClick={() => handleBatterySelect(battery)}
          tooltip={isSelected ? 'Ausgewählt' : 'Auswählen'}
          tooltipOptions={{ position: 'top' }}
        />
        {battery.id !== 0 && showComparison && (
          <Button
            icon={isInComparison ? 'pi pi-minus' : 'pi pi-copy'}
            className={`p-button-sm ${isInComparison ? 'p-button-warning' : 'p-button-outlined'}`}
            onClick={() => isInComparison ? 
              handleRemoveFromComparison(battery.id) : 
              handleAddToComparison(battery)}
            tooltip={isInComparison ? 'Aus Vergleich entfernen' : 'Zum Vergleich hinzufügen'}
            tooltipOptions={{ position: 'top' }}
          />
        )}
      </div>
    );
  };

  // ==================== ROI Chart ====================

  const renderROIChart = () => {
    if (!roiResult) return null;
    
    const chartData = {
      labels: roiResult.yearly_breakdown.map(y => `Jahr ${y.year}`),
      datasets: [
        {
          label: 'Kumulative Ersparnis (€)',
          data: roiResult.yearly_breakdown.map(y => y.cumulative_savings_eur),
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          fill: true
        },
        {
          label: 'Investition (€)',
          data: roiResult.yearly_breakdown.map(() => selectedBattery?.price_gross || 0),
          borderColor: '#ef4444',
          borderDash: [5, 5],
          fill: false
        }
      ]
    };
    
    const chartOptions = {
      responsive: true,
      plugins: {
        legend: { position: 'top' as const },
        title: { display: true, text: 'ROI-Analyse über Zeit' }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value: number) => `${value.toLocaleString('de-DE')} €`
          }
        }
      }
    };
    
    return <Chart type="line" data={chartData} options={chartOptions} />;
  };

  // ==================== Main Render ====================

  if (loading) {
    return (
      <div className={`battery-storage-selector ${className}`}>
        <Card>
          <Skeleton height="2rem" className="mb-3" />
          <Skeleton height="20rem" />
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`battery-storage-selector ${className}`}>
        <Message severity="error" text={error} />
      </div>
    );
  }

  return (
    <div className={`battery-storage-selector ${className}`}>
      <TabView activeIndex={activeTab} onTabChange={(e) => setActiveTab(e.index)}>
        {/* Tab 1: Battery Selection */}
        <TabPanel header="Batterieauswahl" leftIcon="pi pi-bolt">
          <div className="selection-header">
            <div className="filters">
              <Dropdown
                value={selectedManufacturer}
                options={[{ label: 'Alle Hersteller', value: null }, 
                         ...manufacturers.map(m => ({ label: m, value: m }))]}
                onChange={(e) => setSelectedManufacturer(e.value)}
                placeholder="Hersteller filtern"
                className="manufacturer-filter"
              />
              <div className="no-storage-toggle">
                <Checkbox
                  inputId="includeNoStorage"
                  checked={includeNoStorage}
                  onChange={(e) => setIncludeNoStorage(e.checked || false)}
                />
                <label htmlFor="includeNoStorage">"Kein Speicher" anzeigen</label>
              </div>
            </div>
            
            {sizingResult && (
              <div className="sizing-recommendation">
                <i className="pi pi-info-circle" />
                <span>
                  Empfohlene Kapazität: <strong>{sizingResult.recommended_capacity_kwh} kWh</strong>
                  {' '}(Bereich: {sizingResult.capacity_range.min_kwh} - {sizingResult.capacity_range.max_kwh} kWh)
                </span>
              </div>
            )}
          </div>

          <DataTable
            value={batteries}
            selection={selectedBattery}
            onSelectionChange={(e) => handleBatterySelect(e.value as BatteryStorage)}
            selectionMode="single"
            dataKey="id"
            paginator
            rows={10}
            rowsPerPageOptions={[5, 10, 20]}
            className="battery-table"
            emptyMessage="Keine Batteriespeicher gefunden"
            rowClassName={(data) => (data as BatteryStorage).id === 0 ? 'no-storage-row' : ''}
          >
            <Column 
              field="model_name" 
              header="Modell" 
              body={renderBatteryName}
              sortable
              filter
              filterPlaceholder="Suchen..."
            />
            <Column 
              field="capacity_kwh" 
              header="Kapazität" 
              body={renderCapacity}
              sortable
            />
            <Column 
              field="price_gross" 
              header="Preis" 
              body={renderPrice}
              sortable
            />
            <Column 
              field="efficiency_percent" 
              header="Effizienz" 
              body={renderEfficiency}
              sortable
            />
            <Column 
              field="warranty_years" 
              header="Garantie" 
              body={renderWarranty}
              sortable
            />
            <Column 
              field="features" 
              header="Features" 
              body={renderFeatures}
            />
            <Column 
              body={renderActions}
              header="Aktionen"
              style={{ width: '120px' }}
            />
          </DataTable>
        </TabPanel>

        {/* Tab 2: Selected Battery Details */}
        <TabPanel header="Details" leftIcon="pi pi-list" disabled={!selectedBattery}>
          {selectedBattery && selectedBattery.id !== 0 && (
            <div className="battery-details">
              <div className="details-header">
                <h3>{batteryStorageService.formatBatteryName(selectedBattery)}</h3>
                <Tag severity="success" value={selectedBattery.battery_type} />
              </div>
              
              <div className="details-grid">
                <Card className="spec-card">
                  <h4>Technische Daten</h4>
                  <div className="spec-list">
                    <div className="spec-item">
                      <span className="spec-label">Nutzbare Kapazität</span>
                      <span className="spec-value">{selectedBattery.capacity_kwh} kWh</span>
                    </div>
                    <div className="spec-item">
                      <span className="spec-label">Nominale Kapazität</span>
                      <span className="spec-value">{selectedBattery.nominal_capacity_kwh} kWh</span>
                    </div>
                    <div className="spec-item">
                      <span className="spec-label">Max. Leistung</span>
                      <span className="spec-value">{selectedBattery.max_power_kw} kW</span>
                    </div>
                    <div className="spec-item">
                      <span className="spec-label">Effizienz</span>
                      <span className="spec-value">{selectedBattery.efficiency_percent}%</span>
                    </div>
                    <div className="spec-item">
                      <span className="spec-label">Entladetiefe (DoD)</span>
                      <span className="spec-value">{selectedBattery.depth_of_discharge}%</span>
                    </div>
                    <div className="spec-item">
                      <span className="spec-label">Zyklenlebensdauer</span>
                      <span className="spec-value">{selectedBattery.cycle_life.toLocaleString('de-DE')}</span>
                    </div>
                  </div>
                </Card>

                <Card className="spec-card">
                  <h4>Preis & Garantie</h4>
                  <div className="spec-list">
                    <div className="spec-item">
                      <span className="spec-label">Preis (brutto)</span>
                      <span className="spec-value highlight">
                        {batteryStorageService.formatPrice(selectedBattery.price_gross)}
                      </span>
                    </div>
                    <div className="spec-item">
                      <span className="spec-label">Preis (netto)</span>
                      <span className="spec-value">
                        {batteryStorageService.formatPrice(selectedBattery.price_net)}
                      </span>
                    </div>
                    <div className="spec-item">
                      <span className="spec-label">Preis pro kWh</span>
                      <span className="spec-value">
                        {batteryStorageService.formatPricePerKwh(selectedBattery.price_per_kwh)}
                      </span>
                    </div>
                    <div className="spec-item">
                      <span className="spec-label">Garantie</span>
                      <span className="spec-value">
                        {batteryStorageService.formatWarranty(
                          selectedBattery.warranty_years, 
                          selectedBattery.warranty_cycles
                        )}
                      </span>
                    </div>
                  </div>
                </Card>

                <Card className="spec-card">
                  <h4>Physische Daten</h4>
                  <div className="spec-list">
                    <div className="spec-item">
                      <span className="spec-label">Gewicht</span>
                      <span className="spec-value">{selectedBattery.weight_kg} kg</span>
                    </div>
                    <div className="spec-item">
                      <span className="spec-label">Abmessungen</span>
                      <span className="spec-value">{selectedBattery.dimensions || '-'}</span>
                    </div>
                    <div className="spec-item">
                      <span className="spec-label">Modular</span>
                      <span className="spec-value">
                        {selectedBattery.is_modular ? 
                          `Ja (${selectedBattery.min_modules}-${selectedBattery.max_modules} Module)` : 
                          'Nein'}
                      </span>
                    </div>
                  </div>
                </Card>

                <Card className="spec-card">
                  <h4>Kompatibilität</h4>
                  <div className="compatible-inverters">
                    {selectedBattery.compatible_inverters.map((inv, idx) => (
                      <Tag key={idx} severity="info" value={inv} className="inverter-tag" />
                    ))}
                  </div>
                  <div className="features-section">
                    <h5>Features</h5>
                    <div className="features-grid">
                      {selectedBattery.features.map((feature, idx) => (
                        <Tag key={idx} severity="success" value={feature} />
                      ))}
                    </div>
                  </div>
                </Card>
              </div>
            </div>
          )}
          
          {selectedBattery && selectedBattery.id === 0 && (
            <Message 
              severity="info" 
              text="Sie haben 'Kein Speicher' ausgewählt. Die PV-Anlage wird ohne Batteriespeicher konfiguriert." 
            />
          )}
        </TabPanel>

        {/* Tab 3: ROI Analysis */}
        {showROIAnalysis && (
          <TabPanel header="ROI-Analyse" leftIcon="pi pi-chart-line" disabled={!selectedBattery || selectedBattery?.id === 0}>
            {selectedBattery && selectedBattery.id !== 0 && (
              <div className="roi-analysis">
                <div className="roi-parameters">
                  <h4>Parameter</h4>
                  <div className="parameter-grid">
                    <div className="parameter-item">
                      <label>Strompreis (€/kWh)</label>
                      <InputNumber
                        value={electricityPrice}
                        onValueChange={(e) => setElectricityPrice(e.value || 0.35)}
                        mode="decimal"
                        minFractionDigits={2}
                        maxFractionDigits={3}
                        min={0.1}
                        max={1.0}
                      />
                    </div>
                    <div className="parameter-item">
                      <label>Einspeisevergütung (€/kWh)</label>
                      <InputNumber
                        value={feedInTariff}
                        onValueChange={(e) => setFeedInTariff(e.value || 0.082)}
                        mode="decimal"
                        minFractionDigits={3}
                        maxFractionDigits={3}
                        min={0}
                        max={0.2}
                      />
                    </div>
                    <div className="parameter-item">
                      <label>Analysezeitraum (Jahre)</label>
                      <InputNumber
                        value={analysisYears}
                        onValueChange={(e) => setAnalysisYears(e.value || 20)}
                        min={5}
                        max={30}
                      />
                    </div>
                    <Button 
                      label="Neu berechnen" 
                      icon="pi pi-refresh" 
                      onClick={calculateROI}
                      className="recalculate-btn"
                    />
                  </div>
                </div>

                {roiResult && (
                  <div className="roi-results">
                    <div className="roi-summary">
                      <Card className="roi-card">
                        <div className="roi-metric">
                          <span className="metric-label">Amortisation</span>
                          <span className="metric-value">
                            {roiResult.payback_years.toFixed(1)} Jahre
                          </span>
                          <Tag 
                            severity={
                              roiResult.payback_years <= 10 ? 'success' : 
                              roiResult.payback_years <= 15 ? 'warning' : 'danger'
                            }
                            value={batteryStorageService.getROIStatusLabel(
                              batteryStorageService.getROIStatus(roiResult.payback_years)
                            )}
                          />
                        </div>
                      </Card>
                      <Card className="roi-card">
                        <div className="roi-metric">
                          <span className="metric-label">Gesamtersparnis</span>
                          <span className="metric-value">
                            {batteryStorageService.formatPrice(roiResult.total_savings_eur)}
                          </span>
                        </div>
                      </Card>
                      <Card className="roi-card">
                        <div className="roi-metric">
                          <span className="metric-label">Jährliche Ersparnis</span>
                          <span className="metric-value">
                            {batteryStorageService.formatPrice(roiResult.annual_savings_eur)}
                          </span>
                        </div>
                      </Card>
                      <Card className="roi-card">
                        <div className="roi-metric">
                          <span className="metric-label">ROI</span>
                          <span className="metric-value">
                            {roiResult.roi_percent.toFixed(1)}%
                          </span>
                        </div>
                      </Card>
                    </div>

                    <Card className="roi-chart-card">
                      {renderROIChart()}
                    </Card>
                  </div>
                )}
              </div>
            )}
          </TabPanel>
        )}

        {/* Tab 4: Comparison */}
        {showComparison && (
          <TabPanel 
            header={`Vergleich (${comparisonBatteries.length})`} 
            leftIcon="pi pi-copy"
            disabled={comparisonBatteries.length === 0}
          >
            {comparisonBatteries.length > 0 && (
              <div className="battery-comparison">
                <DataTable value={comparisonBatteries} className="comparison-table">
                  <Column field="manufacturer" header="Hersteller" />
                  <Column field="model_name" header="Modell" />
                  <Column 
                    field="capacity_kwh" 
                    header="Kapazität" 
                    body={(b) => `${b.capacity_kwh} kWh`}
                  />
                  <Column 
                    field="price_gross" 
                    header="Preis" 
                    body={(b) => batteryStorageService.formatPrice(b.price_gross)}
                  />
                  <Column 
                    field="price_per_kwh" 
                    header="€/kWh" 
                    body={(b) => batteryStorageService.formatPrice(b.price_per_kwh)}
                  />
                  <Column 
                    field="efficiency_percent" 
                    header="Effizienz" 
                    body={(b) => `${b.efficiency_percent}%`}
                  />
                  <Column 
                    field="cycle_life" 
                    header="Zyklen" 
                    body={(b) => b.cycle_life.toLocaleString('de-DE')}
                  />
                  <Column 
                    body={(b) => (
                      <Button 
                        icon="pi pi-times" 
                        className="p-button-danger p-button-sm"
                        onClick={() => handleRemoveFromComparison(b.id)}
                      />
                    )}
                  />
                </DataTable>
              </div>
            )}
          </TabPanel>
        )}
      </TabView>
    </div>
  );
};

export default BatteryStorageSelector;
