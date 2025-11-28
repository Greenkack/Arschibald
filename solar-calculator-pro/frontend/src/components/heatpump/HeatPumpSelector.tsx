/**
 * Heat Pump Selector Component
 * 
 * Component for selecting heat pump models based on sizing requirements.
 * 
 * Requirements: funktionen.txt - "Wärmepumpen-Auslegung"
 * Task: 255. Heat Pump Model Selection
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  heatpumpModelService,
  HeatPumpModel,
  HeatPumpSizingResult,
  HeatPumpType,
  HeatPumpCategory
} from '../../services/heatpumpModelService';
import './HeatPumpSelector.css';

// ==================== Interfaces ====================

interface HeatPumpSelectorProps {
  heatingLoadKw: number;
  hotWaterIncluded?: boolean;
  flowTemperatureC?: number;
  onModelSelect?: (model: HeatPumpModel) => void;
  onSizingComplete?: (result: HeatPumpSizingResult) => void;
  selectedModelId?: string;
}

// ==================== Component ====================

const HeatPumpSelector: React.FC<HeatPumpSelectorProps> = ({
  heatingLoadKw,
  hotWaterIncluded = true,
  flowTemperatureC = 35,
  onModelSelect,
  onSizingComplete,
  selectedModelId
}) => {
  // State
  const [sizingResult, setSizingResult] = useState<HeatPumpSizingResult | null>(null);
  const [allModels, setAllModels] = useState<HeatPumpModel[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [preferredType, setPreferredType] = useState<HeatPumpType | ''>('');
  const [maxPrice, setMaxPrice] = useState<number | ''>('');
  const [minCOP, setMinCOP] = useState<number | ''>('');
  const [maxNoise, setMaxNoise] = useState<number | ''>('');
  
  // View mode
  const [viewMode, setViewMode] = useState<'recommended' | 'all'>('recommended');
  const [sortBy, setSortBy] = useState<'cop' | 'price' | 'power' | 'noise'>('cop');

  // Calculate sizing
  const calculateSizing = useCallback(async () => {
    if (heatingLoadKw <= 0) return;
    
    setLoading(true);
    setError(null);

    try {
      const result = await heatpumpModelService.calculateSizing({
        heating_load_kw: heatingLoadKw,
        hot_water_included: hotWaterIncluded,
        preferred_type: preferredType || undefined,
        max_price_eur: maxPrice || undefined,
        min_cop: minCOP || undefined,
        max_noise_db: maxNoise || undefined,
        flow_temperature_c: flowTemperatureC
      });
      
      setSizingResult(result);
      onSizingComplete?.(result);
    } catch (err: any) {
      setError(err.message || 'Sizing calculation failed');
    } finally {
      setLoading(false);
    }
  }, [heatingLoadKw, hotWaterIncluded, flowTemperatureC, preferredType, maxPrice, minCOP, maxNoise, onSizingComplete]);

  // Load all models
  const loadAllModels = useCallback(async () => {
    try {
      const models = await heatpumpModelService.getAllModels({
        heat_pump_type: preferredType || undefined,
        sort_by: sortBy
      });
      setAllModels(models);
    } catch (err) {
      console.error('Failed to load models:', err);
    }
  }, [preferredType, sortBy]);

  // Initial load
  useEffect(() => {
    calculateSizing();
  }, [calculateSizing]);

  useEffect(() => {
    if (viewMode === 'all') {
      loadAllModels();
    }
  }, [viewMode, loadAllModels]);

  // Handle model selection
  const handleSelectModel = (model: HeatPumpModel) => {
    onModelSelect?.(model);
  };

  // Get models to display
  const displayModels = viewMode === 'recommended' 
    ? (sizingResult?.recommended_models || [])
    : allModels;

  // Render model card
  const renderModelCard = (model: HeatPumpModel) => {
    const isSelected = model.id === selectedModelId;
    const copRating = heatpumpModelService.getCOPRating(model.cop_a7w35);
    
    return (
      <div 
        key={model.id}
        className={`heat-pump-card ${isSelected ? 'selected' : ''}`}
        onClick={() => handleSelectModel(model)}
      >
        <div className="card-header">
          <span className="manufacturer">{model.manufacturer}</span>
          <span className={`efficiency-badge ${model.efficiency_class.replace(/\+/g, 'plus')}`}>
            {model.efficiency_class}
          </span>
        </div>
        
        <h4 className="model-name">{model.model_name}</h4>
        
        <div className="specs-grid">
          <div className="spec">
            <span className="spec-label">Leistung</span>
            <span className="spec-value">{heatpumpModelService.formatPower(model.heating_power_kw)}</span>
          </div>
          <div className="spec">
            <span className="spec-label">COP (A7/W35)</span>
            <span className={`spec-value cop-${copRating}`}>
              {heatpumpModelService.formatCOP(model.cop_a7w35)}
            </span>
          </div>
          <div className="spec">
            <span className="spec-label">JAZ</span>
            <span className="spec-value">{model.jaz_estimate.toFixed(1)}</span>
          </div>
          {model.noise_level_db && (
            <div className="spec">
              <span className="spec-label">Lautstärke</span>
              <span className="spec-value">{heatpumpModelService.formatNoise(model.noise_level_db)}</span>
            </div>
          )}
        </div>
        
        <div className="card-footer">
          <span className="price">{heatpumpModelService.formatPrice(model.price_gross_eur)}</span>
          <span className="type-badge">{heatpumpModelService.getTypeLabel(model.heat_pump_type)}</span>
        </div>
        
        {model.features.length > 0 && (
          <div className="features">
            {model.features.slice(0, 3).map((feature, idx) => (
              <span key={idx} className="feature-tag">{feature}</span>
            ))}
          </div>
        )}
        
        {isSelected && <div className="selected-indicator">✓ Ausgewählt</div>}
      </div>
    );
  };

  return (
    <div className="heat-pump-selector">
      <div className="selector-header">
        <h3>🔥 Wärmepumpen-Auswahl</h3>
        <p className="selector-description">
          Basierend auf Ihrer Heizlast von <strong>{heatingLoadKw.toFixed(1)} kW</strong>
        </p>
      </div>

      {/* Sizing Summary */}
      {sizingResult && (
        <div className="sizing-summary">
          <div className="summary-item">
            <span className="summary-label">Empfohlene Leistung</span>
            <span className="summary-value">{sizingResult.recommended_power_kw} kW</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Pufferspeicher</span>
            <span className="summary-value">
              {sizingResult.buffer_storage_recommendation.optimal_volume_liters} L
            </span>
          </div>
          {sizingResult.buffer_storage_recommendation.hot_water_storage_liters && (
            <div className="summary-item">
              <span className="summary-label">Warmwasserspeicher</span>
              <span className="summary-value">
                {sizingResult.buffer_storage_recommendation.hot_water_storage_liters} L
              </span>
            </div>
          )}
        </div>
      )}

      {/* Filters */}
      <div className="filters-section">
        <div className="filter-group">
          <label>Typ</label>
          <select 
            value={preferredType} 
            onChange={(e) => setPreferredType(e.target.value as HeatPumpType | '')}
          >
            <option value="">Alle Typen</option>
            <option value={HeatPumpType.AIR_WATER}>Luft/Wasser</option>
            <option value={HeatPumpType.BRINE_WATER}>Sole/Wasser</option>
            <option value={HeatPumpType.WATER_WATER}>Wasser/Wasser</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label>Max. Preis (€)</label>
          <input
            type="number"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value ? parseInt(e.target.value) : '')}
            placeholder="z.B. 20000"
          />
        </div>
        
        <div className="filter-group">
          <label>Min. COP</label>
          <input
            type="number"
            value={minCOP}
            onChange={(e) => setMinCOP(e.target.value ? parseFloat(e.target.value) : '')}
            placeholder="z.B. 4.5"
            step="0.1"
          />
        </div>
        
        <div className="filter-group">
          <label>Max. Lautstärke (dB)</label>
          <input
            type="number"
            value={maxNoise}
            onChange={(e) => setMaxNoise(e.target.value ? parseInt(e.target.value) : '')}
            placeholder="z.B. 55"
          />
        </div>
        
        <button className="btn-filter" onClick={calculateSizing} disabled={loading}>
          {loading ? 'Suche...' : '🔍 Filtern'}
        </button>
      </div>

      {/* View Toggle */}
      <div className="view-toggle">
        <button 
          className={viewMode === 'recommended' ? 'active' : ''}
          onClick={() => setViewMode('recommended')}
        >
          Empfohlen ({sizingResult?.recommended_models.length || 0})
        </button>
        <button 
          className={viewMode === 'all' ? 'active' : ''}
          onClick={() => setViewMode('all')}
        >
          Alle Modelle ({allModels.length})
        </button>
      </div>

      {/* Sort Options */}
      {viewMode === 'all' && (
        <div className="sort-options">
          <span>Sortieren nach:</span>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value as any)}>
            <option value="cop">Effizienz (COP)</option>
            <option value="price">Preis</option>
            <option value="power">Leistung</option>
            <option value="noise">Lautstärke</option>
          </select>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <span>❌</span> {error}
        </div>
      )}

      {/* Models Grid */}
      <div className="models-grid">
        {loading ? (
          <div className="loading-state">Lade Wärmepumpen...</div>
        ) : displayModels.length > 0 ? (
          displayModels.map(renderModelCard)
        ) : (
          <div className="empty-state">
            Keine passenden Wärmepumpen gefunden. Passen Sie die Filter an.
          </div>
        )}
      </div>

      {/* Notes */}
      {sizingResult && sizingResult.notes.length > 0 && (
        <div className="notes-section">
          <h5>💡 Hinweise</h5>
          <ul>
            {sizingResult.notes.map((note, idx) => (
              <li key={idx}>{note}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default HeatPumpSelector;
