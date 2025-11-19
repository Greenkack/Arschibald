import React, { useState } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { Card } from 'primereact/card';
import { HeatPumpInputForm } from '../components/heatpump/HeatPumpInputForm';
import { HeatPumpModelSelection } from '../components/heatpump/HeatPumpModelSelection';
import { HeatPumpResults } from '../components/heatpump/HeatPumpResults';
import './HeatPump.css';

interface BuildingData {
  heatedArea: number;
  buildingType: string;
  buildingYear: string;
  insulationQuality: string;
  currentHeatingSystem: string;
  hotWaterDemand: string;
  oilConsumption: number;
  gasConsumption: number;
  woodConsumption: number;
  systemEfficiency: number;
  heatingHours: number;
  gasMonthlyCost: number;
  oilPricePerTon: number;
  woodPricePerSter: number;
  desiredTemperature: number;
  heatingDays: number;
  outsideTempDesign: number;
  heatingSystemTemp: string;
  location: string;
  climateZone: string;
}

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

export const HeatPump: React.FC = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [buildingData, setBuildingData] = useState<BuildingData | null>(null);
  const [calculatedHeatLoad, setCalculatedHeatLoad] = useState<number>(0);
  const [selectedHeatPump, setSelectedHeatPump] = useState<{
    model: HeatPumpModel;
    power: number;
  } | null>(null);

  const handleBuildingDataSubmit = async (data: BuildingData) => {
    setBuildingData(data);
    
    // TODO: Ca
ll backend API to calculate heat load
    // For now, use a simple estimation
    const estimatedHeatLoad = calculateHeatLoad(data);
    setCalculatedHeatLoad(estimatedHeatLoad);
    
    // Move to next tab
    setActiveIndex(1);
  };

  const calculateHeatLoad = (data: BuildingData): number => {
    // Simple heat load calculation based on building area and type
    // This should be replaced with actual backend API call
    let baseLoad = data.heatedArea * 0.08; // 80W per m² as baseline
    
    // Adjust for building type
    const buildingTypeFactors: { [key: string]: number } = {
      'Neubau KfW40': 0.6,
      'Neubau KfW55': 0.7,
      'Neubau Standard': 0.8,
      'Altbau saniert': 1.0,
      'Altbau teilsaniert': 1.3,
      'Altbau unsaniert': 1.6
    };
    
    const typeFactor = buildingTypeFactors[data.buildingType] || 1.0;
    baseLoad *= typeFactor;
    
    // Adjust for insulation
    const insulationFactors: { [key: string]: number } = {
      'Sehr gut': 0.8,
      'Gut': 0.9,
      'Mittel': 1.0,
      'Schlecht': 1.2,
      'Sehr schlecht': 1.4
    };
    
    const insulationFactor = insulationFactors[data.insulationQuality] || 1.0;
    baseLoad *= insulationFactor;
    
    // Add safety margin
    return baseLoad * 1.2;
  };

  const handleHeatPumpSelect = (model: HeatPumpModel, power: number) => {
    setSelectedHeatPump({ model, power });
    // Move to next tab for economics analysis
    setActiveIndex(2);
  };

  return (
    <div className="heat-pump-page">
      <div className="page-header">
        <h1>🔥 Wärmepumpen-Analyse</h1>
        <p>Optimale Dimensionierung und Wirtschaftlichkeitsanalyse für Wärmepumpen</p>
      </div>

      <TabView activeIndex={activeIndex} onTabChange={(e) => setActiveIndex(e.index)}>
        <TabPanel header="🏠 Gebäudeanalyse" leftIcon="pi pi-home">
          <HeatPumpInputForm
            onSubmit={handleBuildingDataSubmit}
            initialData={buildingData || undefined}
          />
        </TabPanel>

        <TabPanel 
          header="🔥 Wärmepumpen-Auswahl" 
          leftIcon="pi pi-cog"
          disabled={!buildingData}
        >
          {buildingData && calculatedHeatLoad > 0 ? (
            <>
              <Card className="heat-load-result">
                <h3>Berechnete Heizlast</h3>
                <div className="heat-load-value">
                  {calculatedHeatLoad.toFixed(2)} kW
                </div>
                <p>Basierend auf {buildingData.heatedArea} m² Wohnfläche</p>
              </Card>
              
              <HeatPumpModelSelection
                requiredPower={calculatedHeatLoad}
                onSelect={handleHeatPumpSelect}
              />
            </>
          ) : (
            <div className="info-message">
              <i className="pi pi-info-circle"></i>
              <p>Bitte führen Sie zuerst die Gebäudeanalyse durch.</p>
            </div>
          )}
        </TabPanel>

        <TabPanel 
          header="💰 Wirtschaftlichkeit" 
          leftIcon="pi pi-euro"
          disabled={!selectedHeatPump}
        >
          {selectedHeatPump ? (
            <Card>
              <h3>Wirtschaftlichkeitsanalyse</h3>
              <p>Ausgewähltes Modell: {selectedHeatPump.model.model}</p>
              <p>Leistung: {selectedHeatPump.power} kW</p>
              <p>SCOP: {selectedHeatPump.model.scop}</p>
              {/* TODO: Add economics analysis component */}
              <div className="coming-soon">
                <i className="pi pi-clock"></i>
                <p>Wirtschaftlichkeitsanalyse wird in Kürze verfügbar sein</p>
              </div>
            </Card>
          ) : (
            <div className="info-message">
              <i className="pi pi-info-circle"></i>
              <p>Bitte wählen Sie zuerst eine Wärmepumpe aus.</p>
            </div>
          )}
        </TabPanel>

        <TabPanel 
          header="☀️ PV-Integration" 
          leftIcon="pi pi-sun"
          disabled={!selectedHeatPump}
        >
          <Card>
            <h3>PV-Integration</h3>
            {/* TODO: Add PV integration component */}
            <div className="coming-soon">
              <i className="pi pi-clock"></i>
              <p>PV-Integrations-Analyse wird in Kürze verfügbar sein</p>
            </div>
          </Card>
        </TabPanel>

        <TabPanel 
          header="📊 Ergebnisse" 
          leftIcon="pi pi-chart-bar"
          disabled={!selectedHeatPump}
        >
          {selectedHeatPump && buildingData ? (
            <HeatPumpResults
              buildingData={buildingData}
              heatLoad={calculatedHeatLoad}
              selectedHeatPump={selectedHeatPump}
            />
          ) : (
            <div className="info-message">
              <i className="pi pi-info-circle"></i>
              <p>Bitte führen Sie die Gebäudeanalyse durch und wählen Sie eine Wärmepumpe aus.</p>
            </div>
          )}
        </TabPanel>
      </TabView>
    </div>
  );
};
