import React, { useState, useEffect } from 'react';
import { Dropdown } from 'primereact/dropdown';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Card } from 'primereact/card';
import { Tag } from 'primereact/tag';
import { Rating } from 'primereact/rating';
import './HeatPumpModelSelection.css';

interface HeatPumpModel {
  model: string;
  manufacturer: string;
  type: string;
  heating_power_kw: number[];
  scop: number;
  max_flow_temp: number;
  price_range: string;
  features: string[];
  refrigerant: string;
  rating: number;
  awards: string[];
}

interface HeatPumpModelSelectionProps {
  requiredPower: number;
  onSelect: (model: HeatPumpModel, selectedPower: number) => void;
}

export const HeatPumpModelSelection: React.FC<HeatPumpModelSelectionProps> = ({
  requiredPower,
  onSelect
}) => {
  const [manufacturers, setManufacturers] = useState<string[]>([]);
  const [selectedManufacturer, setSelectedManufacturer] = useState<string>('');
  const [types, setTypes] = useState<string[]>([]);
  const [selectedType, setSelectedType] = useState<string>('');
  const [models, setModels] = useState<HeatPumpModel[]>([]);
  const [filteredModels, setFilteredModels] = useState<HeatPumpModel[]>([]);
  const [selectedModel, setSelectedModel] = useState<HeatPumpModel | null>(null);
  const [selectedPower, setSelectedPower] = useState<number>(0);

  // Load manufacturers on mount
  useEffect(() => {
    // TODO: Replace with actual API call
    const mockManufacturers = ['Viessmann', 'Buderus', 'Vaillant'];
    setManufacturers(mockManufacturers);
  }, []);

  // Load types when manufacturer changes
  useEffect(() => {
    if (selectedManufacturer) {
      // TODO: Replace with actual API call
      const mockTypes = [
        'Luft-Wasser-Wärmepumpe',
        'Sole-Wasser-Wärmepumpe',
        'Wasser-Wasser-Wärmepumpe'
      ];
      setTypes(mockTypes);
    }
  }, [selectedManufacturer]);

  // Load models when type changes
  useEffect(() => {
    if (selectedManufacturer && selectedType) {
      // TODO: Replace with actual API call
      fetchModels();
    }
  }, [selectedManufacturer, selectedType]);

  const fetchModels = async () => {
    // Mock data - replace with actual API call
    const mockModels: HeatPumpModel[] = [
      {
        model: 'Vitocal 250-A',
        manufacturer: 'Viessmann',
        type: 'Luft-Wasser-Wärmepumpe',
        heating_power_kw: [6.0, 8.0, 10.0, 12.0, 15.0],
        scop: 4.6,
        max_flow_temp: 70,
        price_range: '€€€',
        features: ['Smart Grid Ready', 'Active Cooling', 'Internet Gateway'],
        refrigerant: 'R290 (Propan)',
        rating: 4.8,
        awards: ['Testsieger Stiftung Warentest 2024', 'Öko-Test SEHR GUT']
      }
    ];
    setModels(mockModels);
    filterModelsByPower(mockModels);
  };

  const filterModelsByPower = (allModels: HeatPumpModel[]) => {
    const filtered = allModels.filter(model => {
      const maxPower = Math.max(...model.heating_power_kw);
      const minPower = Math.min(...model.heating_power_kw);
      return requiredPower >= minPower * 0.8 && requiredPower <= maxPower * 1.2;
    });
    setFilteredModels(filtered);
  };

  const handleModelSelect = (model: HeatPumpModel) => {
    setSelectedModel(model);
    // Find closest power rating
    const closestPower = model.heating_power_kw.reduce((prev, curr) => 
      Math.abs(curr - requiredPower) < Math.abs(prev - requiredPower) ? curr : prev
    );
    setSelectedPower(closestPower);
  };

  const handleConfirmSelection = () => {
    if (selectedModel && selectedPower) {
      onSelect(selectedModel, selectedPower);
    }
  };

  const priceRangeTemplate = (rowData: HeatPumpModel) => {
    const severity = rowData.price_range === '€' ? 'success' : 
                     rowData.price_range === '€€' ? 'warning' : 'danger';
    return <Tag value={rowData.price_range} severity={severity} />;
  };

  const scopTemplate = (rowData: HeatPumpModel) => {
    const severity = rowData.scop >= 4.5 ? 'success' : 
                     rowData.scop >= 4.0 ? 'info' : 'warning';
    return <Tag value={`SCOP: ${rowData.scop}`} severity={severity} />;
  };

  const ratingTemplate = (rowData: HeatPumpModel) => {
    return <Rating value={rowData.rating} readOnly cancel={false} />;
  };

  const powerTemplate = (rowData: HeatPumpModel) => {
    const powers = rowData.heating_power_kw.join(', ');
    return <span>{powers} kW</span>;
  };

  const featuresTemplate = (rowData: HeatPumpModel) => {
    return (
      <div className="features-list">
        {rowData.features.slice(0, 3).map((feature, index) => (
          <Tag key={index} value={feature} className="feature-tag" />
        ))}
      </div>
    );
  };

  const awardsTemplate = (rowData: HeatPumpModel) => {
    if (rowData.awards.length === 0) return null;
    return (
      <div className="awards-list">
        {rowData.awards.map((award, index) => (
          <Tag key={index} value={award} severity="success" icon="pi pi-trophy" />
        ))}
      </div>
    );
  };

  const actionTemplate = (rowData: HeatPumpModel) => {
    const isSelected = selectedModel?.model === rowData.model;
    return (
      <Button
        label={isSelected ? 'Ausgewählt' : 'Auswählen'}
        icon={isSelected ? 'pi pi-check' : 'pi pi-plus'}
        className={isSelected ? 'p-button-success' : 'p-button-outlined'}
        onClick={() => handleModelSelect(rowData)}
      />
    );
  };

  return (
    <div className="heat-pump-model-selection">
      <Card title="🔥 Wärmepumpen-Auswahl" className="selection-card">
        <div className="selection-filters">
          <div className="p-fluid p-grid">
            <div className="p-col-12 p-md-6">
              <label htmlFor="manufacturer">Hersteller</label>
              <Dropdown
                id="manufacturer"
                value={selectedManufacturer}
                options={manufacturers.map(m => ({ label: m, value: m }))}
                onChange={(e) => setSelectedManufacturer(e.value)}
                placeholder="Wählen Sie einen Hersteller"
              />
            </div>

            <div className="p-col-12 p-md-6">
              <label htmlFor="type">Wärmepumpentyp</label>
              <Dropdown
                id="type"
                value={selectedType}
                options={types.map(t => ({ label: t, value: t }))}
                onChange={(e) => setSelectedType(e.value)}
                placeholder="Wählen Sie einen Typ"
                disabled={!selectedManufacturer}
              />
            </div>
          </div>
        </div>

        <div className="required-power-info">
          <h4>Benötigte Heizleistung: {requiredPower.toFixed(1)} kW</h4>
          <p>Empfohlener Bereich: {(requiredPower * 0.8).toFixed(1)} - {(requiredPower * 1.2).toFixed(1)} kW</p>
        </div>

        {filteredModels.length > 0 && (
          <DataTable
            value={filteredModels}
            selectionMode="single"
            selection={selectedModel}
            onSelectionChange={(e) => handleModelSelect(e.value)}
            dataKey="model"
            responsiveLayout="scroll"
            className="models-table"
          >
            <Column field="model" header="Modell" sortable />
            <Column body={powerTemplate} header="Leistung" sortable />
            <Column body={scopTemplate} header="Effizienz" sortable />
            <Column field="max_flow_temp" header="Max. Vorlauf" sortable body={(data) => `${data.max_flow_temp}°C`} />
            <Column body={priceRangeTemplate} header="Preis" sortable />
            <Column body={ratingTemplate} header="Bewertung" sortable />
            <Column body={featuresTemplate} header="Features" />
            <Column body={awardsTemplate} header="Auszeichnungen" />
            <Column body={actionTemplate} header="Aktion" />
          </DataTable>
        )}

        {selectedModel && (
          <div className="selected-model-details">
            <h3>Ausgewähltes Modell: {selectedModel.model}</h3>
            <div className="model-details-grid">
              <div className="detail-item">
                <strong>Hersteller:</strong> {selectedModel.manufacturer}
              </div>
              <div className="detail-item">
                <strong>Typ:</strong> {selectedModel.type}
              </div>
              <div className="detail-item">
                <strong>Gewählte Leistung:</strong> {selectedPower} kW
              </div>
              <div className="detail-item">
                <strong>SCOP:</strong> {selectedModel.scop}
              </div>
              <div className="detail-item">
                <strong>Kältemittel:</strong> {selectedModel.refrigerant}
              </div>
              <div className="detail-item">
                <strong>Max. Vorlauftemperatur:</strong> {selectedModel.max_flow_temp}°C
              </div>
            </div>

            <div className="power-selection">
              <label>Verfügbare Leistungsstufen:</label>
              <div className="power-buttons">
                {selectedModel.heating_power_kw.map(power => (
                  <Button
                    key={power}
                    label={`${power} kW`}
                    className={selectedPower === power ? 'p-button-success' : 'p-button-outlined'}
                    onClick={() => setSelectedPower(power)}
                  />
                ))}
              </div>
            </div>

            <Button
              label="Auswahl bestätigen"
              icon="pi pi-check"
              className="p-button-lg p-button-success confirm-button"
              onClick={handleConfirmSelection}
            />
          </div>
        )}

        {filteredModels.length === 0 && selectedManufacturer && selectedType && (
          <div className="no-models-message">
            <i className="pi pi-info-circle" style={{ fontSize: '2rem' }}></i>
            <p>Keine passenden Modelle für die benötigte Leistung gefunden.</p>
            <p>Bitte wählen Sie einen anderen Hersteller oder Typ.</p>
          </div>
        )}
      </Card>
    </div>
  );
};
