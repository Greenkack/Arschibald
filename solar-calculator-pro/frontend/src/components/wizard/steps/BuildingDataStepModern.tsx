/**
 * Step 3: Building Data Entry
 * Collects building and roof specifications
 */

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { AlertTriangle, Info } from 'lucide-react';
import type { ProjectWizardData } from '../ProjectWizardModern';

interface BuildingDataStepProps {
  data: ProjectWizardData;
  onUpdate: (updates: Partial<ProjectWizardData>) => void;
}

const buildingTypes = [
  { value: 'einfamilienhaus', label: 'Einfamilienhaus' },
  { value: 'mehrfamilienhaus', label: 'Mehrfamilienhaus' },
  { value: 'reihenhaus', label: 'Reihenhaus' },
  { value: 'doppelhaushaelfte', label: 'Doppelhaushälfte' },
  { value: 'bungalow', label: 'Bungalow' },
  { value: 'gewerbe', label: 'Gewerbegebäude' },
  { value: 'landwirtschaft', label: 'Landwirtschaft' },
  { value: 'industrie', label: 'Industriegebäude' },
  { value: 'sonstige', label: 'Sonstige' }
];

const roofTypes = [
  { value: 'satteldach', label: 'Satteldach' },
  { value: 'pultdach', label: 'Pultdach' },
  { value: 'walmdach', label: 'Walmdach' },
  { value: 'zeltdach', label: 'Zeltdach' },
  { value: 'flachdach', label: 'Flachdach' },
  { value: 'mansarddach', label: 'Mansarddach' },
  { value: 'tonnendach', label: 'Tonnendach' },
  { value: 'sheddach', label: 'Sheddach' }
];

const roofMaterials = [
  { value: 'ziegel', label: 'Ziegel' },
  { value: 'beton', label: 'Beton' },
  { value: 'schiefer', label: 'Schiefer' },
  { value: 'blech', label: 'Blech/Metall' },
  { value: 'bitumen', label: 'Bitumen' },
  { value: 'reet', label: 'Reet' },
  { value: 'faserzement', label: 'Faserzement' },
  { value: 'kunststoff', label: 'Kunststoff' },
  { value: 'trapezblech', label: 'Trapezblech' },
  { value: 'sonstige', label: 'Sonstige' }
];

const roofOrientations = [
  { value: 'süd', label: 'Süd' },
  { value: 'südost', label: 'Südost' },
  { value: 'südwest', label: 'Südwest' },
  { value: 'ost', label: 'Ost' },
  { value: 'west', label: 'West' },
  { value: 'nord', label: 'Nord' },
  { value: 'nordost', label: 'Nordost' },
  { value: 'nordwest', label: 'Nordwest' },
  { value: 'flach', label: 'Flach (Ost-West)' }
];

// Calculate insulation standard based on building year
const getInsulationStandard = (year: number | null): string => {
  if (!year) return 'Unbekannt';
  if (year < 1970) return 'Sehr schlecht';
  if (year < 1980) return 'Schlecht';
  if (year < 1995) return 'Mittel';
  if (year < 2002) return 'Gut (EnEV 2002)';
  if (year < 2009) return 'Sehr gut (EnEV 2009)';
  if (year < 2014) return 'Ausgezeichnet (EnEV 2014)';
  return 'Höchster Standard (GEG 2020)';
};

const BuildingDataStepModern: React.FC<BuildingDataStepProps> = ({ data, onUpdate }) => {
  const insulationStandard = getInsulationStandard(data.buildingYear);
  const showHeightWarning = data.buildingHeight !== null && data.buildingHeight > 7;
  const showOrientationWarning = data.roofOrientation === 'nord';

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Gebäudedaten erfassen</h3>
        <p className="text-sm text-muted-foreground">
          Geben Sie Details zum Gebäude und zur Dachfläche ein
        </p>
      </div>

      {/* Building Information */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <h4 className="font-semibold mb-4">Gebäudeinformationen</h4>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="buildingType">Gebäudetyp</Label>
              <Select value={data.buildingType} onValueChange={(value) => onUpdate({ buildingType: value })}>
                <SelectTrigger id="buildingType">
                  <SelectValue placeholder="Wählen..." />
                </SelectTrigger>
                <SelectContent>
                  {buildingTypes.map(t => (
                    <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="buildingYear">Baujahr</Label>
              <Input
                id="buildingYear"
                type="number"
                value={data.buildingYear ?? ''}
                onChange={(e) => onUpdate({ buildingYear: e.target.value ? parseInt(e.target.value) : null })}
                placeholder="z.B. 2010"
                min={1900}
                max={new Date().getFullYear() + 1}
              />
              {data.buildingYear && (
                <p className="text-xs text-muted-foreground">
                  Dämmstandard: <strong>{insulationStandard}</strong>
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="buildingHeight">Gebäudehöhe (m)</Label>
              <Input
                id="buildingHeight"
                type="number"
                value={data.buildingHeight ?? ''}
                onChange={(e) => onUpdate({ buildingHeight: e.target.value ? parseFloat(e.target.value) : null })}
                placeholder="z.B. 8.5"
                step={0.1}
                min={0}
              />
            </div>
          </div>

          {showHeightWarning && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Bei Gebäudehöhen über 7 Metern können zusätzliche Kosten für Gerüstbau anfallen.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      <Separator />

      {/* Roof Information */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <h4 className="font-semibold mb-4">Dachinformationen</h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="roofType">Dachtyp</Label>
              <Select value={data.roofType} onValueChange={(value) => onUpdate({ roofType: value })}>
                <SelectTrigger id="roofType">
                  <SelectValue placeholder="Wählen..." />
                </SelectTrigger>
                <SelectContent>
                  {roofTypes.map(t => (
                    <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="roofMaterial">Dachmaterial</Label>
              <Select value={data.roofMaterial} onValueChange={(value) => onUpdate({ roofMaterial: value })}>
                <SelectTrigger id="roofMaterial">
                  <SelectValue placeholder="Wählen..." />
                </SelectTrigger>
                <SelectContent>
                  {roofMaterials.map(m => (
                    <SelectItem key={m.value} value={m.value}>{m.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="roofInclination">
              Dachneigung: {data.roofInclination}°
            </Label>
            <Slider
              id="roofInclination"
              value={[data.roofInclination]}
              onValueChange={(value) => onUpdate({ roofInclination: value[0] })}
              min={0}
              max={60}
              step={1}
              className="mt-2"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>0° (Flach)</span>
              <span>30° (Optimal)</span>
              <span>60° (Steil)</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="roofOrientation">Dachausrichtung *</Label>
              <Select 
                value={data.roofOrientation} 
                onValueChange={(value) => onUpdate({ roofOrientation: value })}
              >
                <SelectTrigger id="roofOrientation">
                  <SelectValue placeholder="Wählen..." />
                </SelectTrigger>
                <SelectContent>
                  {roofOrientations.map(o => (
                    <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="roofArea">Dachfläche (m²) *</Label>
              <Input
                id="roofArea"
                type="number"
                value={data.roofArea ?? ''}
                onChange={(e) => onUpdate({ roofArea: e.target.value ? parseFloat(e.target.value) : null })}
                placeholder="z.B. 120"
                step={0.1}
                min={0}
                required
              />
            </div>
          </div>

          {showOrientationWarning && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Eine Nordausrichtung ist für PV-Anlagen nicht optimal. Erwägen Sie alternative Dachflächen.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          <strong>Tipp:</strong> Für PV-Anlagen ist eine Südausrichtung mit 30-35° Neigung optimal. 
          Ost-West-Anlagen bieten eine gleichmäßigere Energieverteilung über den Tag.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default BuildingDataStepModern;
