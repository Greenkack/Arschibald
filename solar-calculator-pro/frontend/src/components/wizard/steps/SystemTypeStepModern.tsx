/**
 * Step 1: System Type Selection
 * Allows user to choose between PV, Heat Pump, or combined system
 */

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ProjectWizardData } from '../ProjectWizardModern';

interface SystemTypeStepProps {
  data: ProjectWizardData;
  onUpdate: (updates: Partial<ProjectWizardData>) => void;
}

const systemTypes = [
  {
    id: 'pv' as const,
    icon: '☀️',
    title: 'Photovoltaik',
    description: 'Solaranlage zur Stromerzeugung mit optionalem Batteriespeicher',
    features: [
      'Stromerzeugung durch Sonnenlicht',
      'Reduzierung der Stromkosten',
      'Optionale Batteriespeicherung',
      'THG-Quote möglich'
    ]
  },
  {
    id: 'wp' as const,
    icon: '🔥',
    title: 'Wärmepumpe',
    description: 'Effiziente Heizungslösung für Ihr Gebäude',
    features: [
      'Umweltfreundliche Wärmeerzeugung',
      'Reduzierung der Heizkosten',
      'Kühlung im Sommer möglich',
      'BAFA-Förderung verfügbar'
    ]
  },
  {
    id: 'pv_wp' as const,
    icon: '⚡',
    title: 'PV + Wärmepumpe',
    description: 'Kombinierte Lösung für maximale Energieeffizienz und Autarkie',
    features: [
      'Maximale Energieautarkie',
      'Optimale Nutzung des Eigenstroms',
      'Höchste CO₂-Einsparung',
      'Kombination aus allen Vorteilen'
    ]
  }
];

const SystemTypeStepModern: React.FC<SystemTypeStepProps> = ({ data, onUpdate }) => {
  const handleSelection = (systemType: 'pv' | 'wp' | 'pv_wp') => {
    onUpdate({ systemType });
  };

  const handleKeyDown = (e: React.KeyboardEvent, systemType: 'pv' | 'wp' | 'pv_wp') => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleSelection(systemType);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Wählen Sie den Anlagenmodus</h3>
        <p className="text-sm text-muted-foreground">
          Bitte wählen Sie aus, welches System Sie für Ihr Projekt konfigurieren möchten
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {systemTypes.map((type) => (
          <Card
            key={type.id}
            className={cn(
              'cursor-pointer transition-all hover:shadow-lg border-2',
              data.systemType === type.id
                ? 'border-primary bg-primary/5 shadow-md'
                : 'border-muted hover:border-primary/50'
            )}
            onClick={() => handleSelection(type.id)}
            onKeyDown={(e) => handleKeyDown(e, type.id)}
            tabIndex={0}
            role="button"
            aria-pressed={data.systemType === type.id}
          >
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="text-4xl">{type.icon}</div>
                <div>
                  <CardTitle className="text-lg">{type.title}</CardTitle>
                </div>
              </div>
              <CardDescription className="mt-2">
                {type.description}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-1.5">
                {type.features.map((feature, idx) => (
                  <li key={idx} className="text-sm flex items-start gap-2">
                    <span className="text-green-600 mt-0.5">✓</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
      </div>

      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          <strong>Tipp:</strong> Die Kombination aus PV und Wärmepumpe bietet die höchste Energieautarkie 
          und Kosteneinsparung, da der selbst erzeugte Strom direkt für die Heizung genutzt werden kann.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default SystemTypeStepModern;
