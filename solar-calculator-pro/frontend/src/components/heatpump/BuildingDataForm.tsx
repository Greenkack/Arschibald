/**
 * Building Data Form Component
 * 
 * Form for entering building data for heat pump calculations.
 * 
 * Requirements: funktionen.txt - "Gebäude- und Heizungsdaten"
 * Task: 254. Heat Pump Building Data Integration
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  heatpumpBuildingService,
  BuildingDataRequest,
  BuildingDataResponse,
  InsulationStandard,
  HeatingSystemType,
  BuildingType,
  OldHeatingSystem,
  InsulationInfo,
  HeatingSystemInfo
} from '../../services/heatpumpBuildingService';
import './BuildingDataForm.css';

// ==================== Interfaces ====================

interface BuildingDataFormProps {
  onCalculationComplete?: (result: BuildingDataResponse) => void;
  onDataChange?: (data: BuildingDataRequest) => void;
  initialData?: Partial<BuildingDataRequest>;
  showResults?: boolean;
  compact?: boolean;
}

// ==================== Component ====================

const BuildingDataForm: React.FC<BuildingDataFormProps> = ({
  onCalculationComplete,
  onDataChange,
  initialData,
  showResults = true,
  compact = false
}) => {
  // Form state
  const [formData, setFormData] = useState<BuildingDataRequest>({
    heated_area_m2: initialData?.heated_area_m2 || 150,
    building_year: initialData?.building_year || 2000,
    building_type: initialData?.building_type || BuildingType.SINGLE_FAMILY,
    insulation_standard: initialData?.insulation_standard,
    heating_system_type: initialData?.heating_system_type || HeatingSystemType.FLOOR_HEATING,
    old_heating_system: initialData?.old_heating_system || OldHeatingSystem.GAS,
    number_of_floors: initialData?.number_of_floors || 2,
    number_of_residents: initialData?.number_of_residents || 4,
    hot_water_included: initialData?.hot_water_included ?? true
  });

  // Reference data
  const [insulationStandards, setInsulationStandards] = useState<InsulationInfo[]>([]);
  const [heatingSystems, setHeatingSystems] = useState<HeatingSystemInfo[]>([]);

  // Calculation result
  const [result, setResult] = useState<BuildingDataResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-estimate insulation
  const [autoEstimateInsulation, setAutoEstimateInsulation] = useState(true);

  // Load reference data
  useEffect(() => {
    const loadReferenceData = async () => {
      try {
        const [insulation, heating] = await Promise.all([
          heatpumpBuildingService.getInsulationStandards(),
          heatpumpBuildingService.getHeatingSystems()
        ]);
        setInsulationStandards(insulation);
        setHeatingSystems(heating);
      } catch (err) {
        console.error('Failed to load reference data:', err);
      }
    };
    loadReferenceData();
  }, []);

  // Auto-estimate insulation from building year
  useEffect(() => {
    if (autoEstimateInsulation && formData.building_year) {
      const estimated = heatpumpBuildingService.estimateInsulationFromYear(formData.building_year);
      setFormData(prev => ({ ...prev, insulation_standard: estimated }));
    }
  }, [formData.building_year, autoEstimateInsulation]);

  // Notify parent of data changes
  useEffect(() => {
    onDataChange?.(formData);
  }, [formData, onDataChange]);

  // Handle form field changes
  const handleChange = useCallback((field: keyof BuildingDataRequest, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  }, []);

  // Calculate heating load
  const handleCalculate = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await heatpumpBuildingService.calculate(formData);
      setResult(response);
      onCalculationComplete?.(response);
    } catch (err: any) {
      setError(err.message || 'Berechnung fehlgeschlagen');
    } finally {
      setLoading(false);
    }
  };

  // Get heating system info
  const getHeatingSystemInfo = (type: HeatingSystemType): HeatingSystemInfo | undefined => {
    return heatingSystems.find(s => s.system_type === type);
  };

  // Render form
  return (
    <div className={`building-data-form ${compact ? 'compact' : ''}`}>
      <div className="form-header">
        <h3>🏠 Gebäudedaten</h3>
        <p className="form-description">
          Geben Sie die Gebäudedaten ein, um die Heizlast und den Wärmebedarf zu berechnen.
        </p>
      </div>

      <div className="form-grid">
        {/* Heated Area */}
        <div className="form-group">
          <label htmlFor="heated_area">Beheizte Fläche (m²)</label>
          <input
            type="number"
            id="heated_area"
            value={formData.heated_area_m2}
            onChange={(e) => handleChange('heated_area_m2', parseFloat(e.target.value) || 0)}
            min={10}
            max={10000}
            step={10}
          />
          <span className="form-hint">Gesamte beheizte Wohnfläche</span>
        </div>

        {/* Building Year */}
        <div className="form-group">
          <label htmlFor="building_year">Baujahr</label>
          <input
            type="number"
            id="building_year"
            value={formData.building_year || ''}
            onChange={(e) => handleChange('building_year', parseInt(e.target.value) || undefined)}
            min={1800}
            max={2030}
            placeholder="z.B. 1990"
          />
          <span className="form-hint">Für automatische Dämmstandard-Schätzung</span>
        </div>

        {/* Building Type */}
        <div className="form-group">
          <label htmlFor="building_type">Gebäudetyp</label>
          <select
            id="building_type"
            value={formData.building_type}
            onChange={(e) => handleChange('building_type', e.target.value as BuildingType)}
          >
            <option value={BuildingType.SINGLE_FAMILY}>Einfamilienhaus</option>
            <option value={BuildingType.SEMI_DETACHED}>Doppelhaushälfte</option>
            <option value={BuildingType.ROW_HOUSE}>Reihenhaus</option>
            <option value={BuildingType.APARTMENT}>Wohnung</option>
            <option value={BuildingType.MULTI_FAMILY}>Mehrfamilienhaus</option>
            <option value={BuildingType.COMMERCIAL}>Gewerbe</option>
          </select>
        </div>

        {/* Insulation Standard */}
        <div className="form-group">
          <label htmlFor="insulation_standard">
            Dämmstandard
            <label className="checkbox-inline">
              <input
                type="checkbox"
                checked={autoEstimateInsulation}
                onChange={(e) => setAutoEstimateInsulation(e.target.checked)}
              />
              Auto
            </label>
          </label>
          <select
            id="insulation_standard"
            value={formData.insulation_standard || ''}
            onChange={(e) => {
              setAutoEstimateInsulation(false);
              handleChange('insulation_standard', e.target.value as InsulationStandard);
            }}
          >
            {insulationStandards.map(std => (
              <option key={std.standard} value={std.standard}>
                {std.label_de} ({std.specific_heat_demand_kwh_m2} kWh/m²)
              </option>
            ))}
          </select>
        </div>

        {/* Heating System Type */}
        <div className="form-group">
          <label htmlFor="heating_system">Heizsystem</label>
          <select
            id="heating_system"
            value={formData.heating_system_type}
            onChange={(e) => handleChange('heating_system_type', e.target.value as HeatingSystemType)}
          >
            {heatingSystems.map(sys => (
              <option key={sys.system_type} value={sys.system_type}>
                {sys.label_de} ({sys.flow_temperature_c}°C)
              </option>
            ))}
          </select>
          {formData.heating_system_type === HeatingSystemType.RADIATORS_HIGH && (
            <span className="form-warning">
              ⚠️ Hochtemperatur-Heizkörper reduzieren die WP-Effizienz
            </span>
          )}
        </div>

        {/* Old Heating System */}
        <div className="form-group">
          <label htmlFor="old_heating">Bisheriges Heizsystem</label>
          <select
            id="old_heating"
            value={formData.old_heating_system}
            onChange={(e) => handleChange('old_heating_system', e.target.value as OldHeatingSystem)}
          >
            <option value={OldHeatingSystem.OIL}>Ölheizung</option>
            <option value={OldHeatingSystem.GAS}>Gasheizung</option>
            <option value={OldHeatingSystem.ELECTRIC}>Elektroheizung</option>
            <option value={OldHeatingSystem.COAL}>Kohleheizung</option>
            <option value={OldHeatingSystem.WOOD}>Holzheizung</option>
            <option value={OldHeatingSystem.DISTRICT}>Fernwärme</option>
            <option value={OldHeatingSystem.NONE}>Keine/Neubau</option>
          </select>
        </div>

        {/* Number of Floors */}
        <div className="form-group">
          <label htmlFor="floors">Anzahl Etagen</label>
          <input
            type="number"
            id="floors"
            value={formData.number_of_floors}
            onChange={(e) => handleChange('number_of_floors', parseInt(e.target.value) || 1)}
            min={1}
            max={10}
          />
        </div>

        {/* Number of Residents */}
        <div className="form-group">
          <label htmlFor="residents">Anzahl Bewohner</label>
          <input
            type="number"
            id="residents"
            value={formData.number_of_residents}
            onChange={(e) => handleChange('number_of_residents', parseInt(e.target.value) || 1)}
            min={1}
            max={20}
          />
          <span className="form-hint">Für Warmwasserberechnung</span>
        </div>

        {/* Hot Water Included */}
        <div className="form-group checkbox-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={formData.hot_water_included}
              onChange={(e) => handleChange('hot_water_included', e.target.checked)}
            />
            Warmwasser über Wärmepumpe
          </label>
        </div>
      </div>

      {/* Calculate Button */}
      <div className="form-actions">
        <button
          className="btn-calculate"
          onClick={handleCalculate}
          disabled={loading}
        >
          {loading ? 'Berechne...' : '🔥 Heizlast berechnen'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <span className="error-icon">❌</span>
          {error}
        </div>
      )}

      {/* Results Display */}
      {showResults && result && (
        <div className="calculation-results">
          <h4>📊 Berechnungsergebnis</h4>
          
          <div className="results-grid">
            <div className="result-card primary">
              <span className="result-label">Heizlast</span>
              <span className="result-value">
                {heatpumpBuildingService.formatHeatingLoad(result.heating_load.heating_load_kw)}
              </span>
              <span className="result-detail">
                {heatpumpBuildingService.formatSpecificHeatingLoad(result.heating_load.specific_heating_load_w_m2)}
              </span>
            </div>

            <div className="result-card">
              <span className="result-label">Jahresheizwärmebedarf</span>
              <span className="result-value">
                {heatpumpBuildingService.formatEnergyDemand(result.heating_load.annual_heating_demand_kwh)}
              </span>
            </div>

            <div className="result-card">
              <span className="result-label">Warmwasserbedarf</span>
              <span className="result-value">
                {heatpumpBuildingService.formatEnergyDemand(result.heating_load.hot_water_demand_kwh)}
              </span>
            </div>

            <div className="result-card">
              <span className="result-label">Gesamtwärmebedarf</span>
              <span className="result-value">
                {heatpumpBuildingService.formatEnergyDemand(result.heating_load.total_heat_demand_kwh)}
              </span>
            </div>

            <div className="result-card highlight">
              <span className="result-label">Empfohlene WP-Leistung</span>
              <span className="result-value">
                {result.heating_load.recommended_hp_power_kw} kW
              </span>
            </div>

            <div className="result-card">
              <span className="result-label">Vorlauftemperatur</span>
              <span className="result-value">
                {heatpumpBuildingService.formatTemperature(result.heating_load.flow_temperature_c)}
              </span>
            </div>
          </div>

          {/* Warnings */}
          {result.warnings.length > 0 && (
            <div className="warnings-section">
              <h5>⚠️ Hinweise</h5>
              <ul>
                {result.warnings.map((warning, index) => (
                  <li key={index} className="warning-item">{warning}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {result.recommendations.length > 0 && (
            <div className="recommendations-section">
              <h5>💡 Empfehlungen</h5>
              <ul>
                {result.recommendations.map((rec, index) => (
                  <li key={index} className="recommendation-item">{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BuildingDataForm;
