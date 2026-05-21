/**
 * Step 4: Energy Demand Analysis
 * Collects energy consumption data for sizing calculations
 */

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Info, Lightbulb } from 'lucide-react';
import type { ProjectWizardData } from '../ProjectWizardModern';

interface EnergyDemandStepProps {
  data: ProjectWizardData;
  onUpdate: (updates: Partial<ProjectWizardData>) => void;
}

const feedInTypes = [
  { value: 'partial', label: 'Überschusseinspeisung' },
  { value: 'full', label: 'Volleinspeisung' }
];

// Estimate heating consumption based on building data
const estimateHeatingConsumption = (
  buildingYear: number | null,
  roofArea: number | null
): number | null => {
  if (!buildingYear || !roofArea) return null;
  
  let consumptionPerSqm: number;
  if (buildingYear < 1970) consumptionPerSqm = 200;
  else if (buildingYear < 1980) consumptionPerSqm = 150;
  else if (buildingYear < 1995) consumptionPerSqm = 120;
  else if (buildingYear < 2002) consumptionPerSqm = 100;
  else if (buildingYear < 2009) consumptionPerSqm = 80;
  else if (buildingYear < 2014) consumptionPerSqm = 60;
  else consumptionPerSqm = 40;
  
  // Estimate total area (roof area * 2 floors assumption)
  const estimatedArea = roofArea * 2;
  return Math.round(estimatedArea * consumptionPerSqm);
};

const EnergyDemandStepModern: React.FC<EnergyDemandStepProps> = ({ data, onUpdate }) => {
  const hasPV = data.systemType === 'pv' || data.systemType === 'pv_wp';
  const hasWP = data.systemType === 'wp' || data.systemType === 'pv_wp';

  const estimatedHeating = estimateHeatingConsumption(data.buildingYear, data.roofArea);

  const handleAutoEstimate = () => {
    if (estimatedHeating !== null && hasWP) {
      onUpdate({ annualHeatingConsumption: estimatedHeating });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Energiebedarfsanalyse</h3>
        <p className="text-sm text-muted-foreground">
          Geben Sie den aktuellen Energiebedarf ein
        </p>
      </div>

      {/* Customer Type */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="space-y-2">
            <Label>Kundentyp</Label>
            <ToggleGroup 
              type="single" 
              value={data.customerType}
              onValueChange={(value) => {
                if (value) onUpdate({ customerType: value as 'private' | 'commercial' });
              }}
              className="justify-start"
            >
              <ToggleGroupItem value="private" aria-label="Privat">
                Privat
              </ToggleGroupItem>
              <ToggleGroupItem value="commercial" aria-label="Gewerbe">
                Gewerbe
              </ToggleGroupItem>
            </ToggleGroup>
          </div>

          <div className="space-y-2">
            <Label>Gebäudestatus</Label>
            <ToggleGroup 
              type="single" 
              value={data.isNewBuilding ? 'new' : 'existing'}
              onValueChange={(value) => {
                if (value) onUpdate({ isNewBuilding: value === 'new' });
              }}
              className="justify-start"
            >
              <ToggleGroupItem value="existing" aria-label="Bestand">
                Bestandsgebäude
              </ToggleGroupItem>
              <ToggleGroupItem value="new" aria-label="Neubau">
                Neubau
              </ToggleGroupItem>
            </ToggleGroup>
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Electricity Consumption (if PV) */}
      {hasPV && (
        <Card>
          <CardContent className="pt-6 space-y-4">
            <h4 className="font-semibold mb-4">Strombedarf</h4>

            <div className="space-y-2">
              <Label htmlFor="electricityConsumption">Jährlicher Stromverbrauch (kWh) *</Label>
              <Input
                id="electricityConsumption"
                type="number"
                value={data.annualElectricityConsumption ?? ''}
                onChange={(e) => onUpdate({ 
                  annualElectricityConsumption: e.target.value ? parseFloat(e.target.value) : null 
                })}
                placeholder="z.B. 4500"
                step={100}
                min={0}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="feedInType">Einspeiseart</Label>
              <Select value={data.feedInType} onValueChange={(value) => onUpdate({ feedInType: value as 'partial' | 'full' })}>
                <SelectTrigger id="feedInType">
                  <SelectValue placeholder="Wählen..." />
                </SelectTrigger>
                <SelectContent>
                  {feedInTypes.map(t => (
                    <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <strong>Richtwerte Haushalt:</strong><br />
                1 Person: ~1.500 kWh/Jahr<br />
                2 Personen: ~2.500 kWh/Jahr<br />
                3 Personen: ~3.500 kWh/Jahr<br />
                4 Personen: ~4.500 kWh/Jahr<br />
                5+ Personen: ~5.500 kWh/Jahr
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      {hasPV && hasWP && <Separator />}

      {/* Heating Consumption (if WP) */}
      {hasWP && (
        <Card>
          <CardContent className="pt-6 space-y-4">
            <h4 className="font-semibold mb-4">Wärmebedarf</h4>

            <div className="space-y-2">
              <Label htmlFor="heatingConsumption">Jährlicher Heizenergiebedarf (kWh) *</Label>
              <Input
                id="heatingConsumption"
                type="number"
                value={data.annualHeatingConsumption ?? ''}
                onChange={(e) => onUpdate({ 
                  annualHeatingConsumption: e.target.value ? parseFloat(e.target.value) : null 
                })}
                placeholder="z.B. 12000"
                step={100}
                min={0}
                required
              />
            </div>

            {estimatedHeating !== null && (
              <Alert>
                <Lightbulb className="h-4 w-4" />
                <AlertDescription className="flex items-center justify-between">
                  <div>
                    <strong>Geschätzter Wärmebedarf:</strong> {estimatedHeating.toLocaleString('de-DE')} kWh/Jahr<br />
                    <span className="text-xs text-muted-foreground">
                      Basierend auf Baujahr {data.buildingYear} und Dachfläche {data.roofArea} m²
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={handleAutoEstimate}
                    className="text-sm text-primary hover:underline ml-4"
                  >
                    Übernehmen
                  </button>
                </AlertDescription>
              </Alert>
            )}

            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <strong>Hinweis:</strong> Der Heizenergiebedarf hängt stark von Gebäudegröße, Dämmstandard 
                und Heizverhalten ab. Nutzen Sie vorhandene Verbrauchsdaten für eine präzise Auslegung.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default EnergyDemandStepModern;
