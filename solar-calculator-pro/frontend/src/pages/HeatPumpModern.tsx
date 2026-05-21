/**
 * Modern Heat Pump Page with shadcn/ui
 * 
 * Optimale Dimensionierung und Wirtschaftlichkeitsanalyse für Wärmepumpen
 */

import React, { useState } from 'react';
import { Home, Flame, Euro, Sun, BarChart3 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { HeatPumpInputForm } from '../components/heatpump/HeatPumpInputForm';
import { HeatPumpModelSelection } from '../components/heatpump/HeatPumpModelSelection';
import { HeatPumpResults } from '../components/heatpump/HeatPumpResults';

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

export const HeatPumpModern: React.FC = () => {
  const [activeTab, setActiveTab] = useState('building');
  const [buildingData, setBuildingData] = useState<BuildingData | null>(null);
  const [calculatedHeatLoad, setCalculatedHeatLoad] = useState<number>(0);
  const [selectedHeatPump, setSelectedHeatPump] = useState<{
    model: HeatPumpModel;
    power: number;
  } | null>(null);

  const handleBuildingDataSubmit = async (data: BuildingData) => {
    setBuildingData(data);
    
    const estimatedHeatLoad = calculateHeatLoad(data);
    setCalculatedHeatLoad(estimatedHeatLoad);
    
    setActiveTab('selection');
  };

  const calculateHeatLoad = (data: BuildingData): number => {
    let baseLoad = data.heatedArea * 0.08;
    
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
    
    const insulationFactors: { [key: string]: number } = {
      'Sehr gut': 0.8,
      'Gut': 0.9,
      'Mittel': 1.0,
      'Schlecht': 1.2,
      'Sehr schlecht': 1.4
    };
    
    const insulationFactor = insulationFactors[data.insulationQuality] || 1.0;
    baseLoad *= insulationFactor;
    
    return baseLoad * 1.2;
  };

  const handleHeatPumpSelect = (model: HeatPumpModel, power: number) => {
    setSelectedHeatPump({ model, power });
    setActiveTab('economics');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-red-500 to-orange-600 shadow-lg">
              <Flame className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Wärmepumpen-Analyse</h1>
              <p className="text-muted-foreground">
                Optimale Dimensionierung und Wirtschaftlichkeitsanalyse für Wärmepumpen
              </p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <Card>
          <CardContent className="p-6">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="building" className="gap-2">
                  <Home className="h-4 w-4" />
                  Gebäudeanalyse
                </TabsTrigger>
                <TabsTrigger value="selection" disabled={!buildingData} className="gap-2">
                  <Flame className="h-4 w-4" />
                  WP-Auswahl
                </TabsTrigger>
                <TabsTrigger value="economics" disabled={!selectedHeatPump} className="gap-2">
                  <Euro className="h-4 w-4" />
                  Wirtschaftlichkeit
                </TabsTrigger>
                <TabsTrigger value="pv" disabled={!selectedHeatPump} className="gap-2">
                  <Sun className="h-4 w-4" />
                  PV-Integration
                </TabsTrigger>
                <TabsTrigger value="results" disabled={!selectedHeatPump} className="gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Ergebnisse
                </TabsTrigger>
              </TabsList>

              <TabsContent value="building" className="space-y-4">
                <HeatPumpInputForm
                  onSubmit={handleBuildingDataSubmit}
                  initialData={buildingData || undefined}
                />
              </TabsContent>

              <TabsContent value="selection" className="space-y-4">
                {buildingData && calculatedHeatLoad > 0 ? (
                  <>
                    <Card>
                      <CardHeader>
                        <CardTitle>Berechnete Heizlast</CardTitle>
                        <CardDescription>
                          Basierend auf {buildingData.heatedArea} m² Wohnfläche
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-4xl font-bold text-primary">
                          {calculatedHeatLoad.toFixed(2)} kW
                        </div>
                      </CardContent>
                    </Card>
                    
                    <HeatPumpModelSelection
                      requiredPower={calculatedHeatLoad}
                      onSelect={handleHeatPumpSelect}
                    />
                  </>
                ) : (
                  <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed">
                    <div className="text-center">
                      <Home className="mx-auto h-12 w-12 text-muted-foreground" />
                      <h3 className="mt-4 text-lg font-semibold">Gebäudeanalyse erforderlich</h3>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Bitte führen Sie zuerst die Gebäudeanalyse durch.
                      </p>
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="economics" className="space-y-4">
                {selectedHeatPump ? (
                  <Card>
                    <CardHeader>
                      <CardTitle>Wirtschaftlichkeitsanalyse</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm font-medium">Ausgewähltes Modell</p>
                          <p className="text-2xl font-bold">{selectedHeatPump.model.model}</p>
                        </div>
                        <div>
                          <p className="text-sm font-medium">Leistung</p>
                          <p className="text-2xl font-bold">{selectedHeatPump.power} kW</p>
                        </div>
                        <div>
                          <p className="text-sm font-medium">SCOP</p>
                          <p className="text-2xl font-bold">{selectedHeatPump.model.scop}</p>
                        </div>
                      </div>
                      <div className="rounded-lg border border-dashed p-8 text-center">
                        <p className="text-muted-foreground">
                          Wirtschaftlichkeitsanalyse wird in Kürze verfügbar sein
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed">
                    <div className="text-center">
                      <Flame className="mx-auto h-12 w-12 text-muted-foreground" />
                      <h3 className="mt-4 text-lg font-semibold">Wärmepumpe auswählen</h3>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Bitte wählen Sie zuerst eine Wärmepumpe aus.
                      </p>
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="pv" className="space-y-4">
                <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed">
                  <div className="text-center">
                    <Sun className="mx-auto h-12 w-12 text-muted-foreground" />
                    <h3 className="mt-4 text-lg font-semibold">PV-Integration</h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                      PV-Integrations-Analyse wird in Kürze verfügbar sein
                    </p>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="results" className="space-y-4">
                {selectedHeatPump && buildingData ? (
                  <HeatPumpResults
                    buildingData={buildingData}
                    heatLoad={calculatedHeatLoad}
                    selectedHeatPump={selectedHeatPump}
                  />
                ) : (
                  <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed">
                    <div className="text-center">
                      <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground" />
                      <h3 className="mt-4 text-lg font-semibold">Analyse abschließen</h3>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Bitte führen Sie die Gebäudeanalyse durch und wählen Sie eine Wärmepumpe aus.
                      </p>
                    </div>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
