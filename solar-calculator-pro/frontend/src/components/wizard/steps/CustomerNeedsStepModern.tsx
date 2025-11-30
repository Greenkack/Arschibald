/**
 * Step 5: Customer Needs & Preferences
 * Collects customer-specific requirements (wallbox, battery, priorities)
 */

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Info, Battery, Car, TrendingUp } from 'lucide-react';
import type { ProjectWizardData } from '../ProjectWizardModern';

interface CustomerNeedsStepProps {
  data: ProjectWizardData;
  onUpdate: (updates: Partial<ProjectWizardData>) => void;
}

const CustomerNeedsStepModern: React.FC<CustomerNeedsStepProps> = ({ data, onUpdate }) => {
  const hasPV = data.systemType === 'pv' || data.systemType === 'pv_wp';

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Kundenbedürfnisse erfassen</h3>
        <p className="text-sm text-muted-foreground">
          Welche zusätzlichen Anforderungen hat der Kunde?
        </p>
      </div>

      {/* E-Mobility (only for PV systems) */}
      {hasPV && (
        <>
          <Card>
            <CardContent className="pt-6 space-y-4">
              <div className="flex items-start gap-3">
                <Car className="h-5 w-5 text-primary mt-1" />
                <div className="flex-1 space-y-3">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="wantsWallbox"
                      checked={data.wantsWallbox}
                      onCheckedChange={(checked) => onUpdate({ wantsWallbox: !!checked })}
                    />
                    <Label htmlFor="wantsWallbox" className="cursor-pointer font-semibold">
                      E-Mobilität / Wallbox
                    </Label>
                  </div>
                  
                  {data.wantsWallbox && (
                    <Alert>
                      <Info className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Hinweis:</strong> Eine Wallbox erhöht den Strombedarf um ca. 2.500-3.000 kWh/Jahr 
                        (bei 15.000 km Fahrleistung). Dies wird bei der PV-Auslegung berücksichtigt.
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          <Separator />

          {/* Battery Storage */}
          <Card>
            <CardContent className="pt-6 space-y-4">
              <div className="flex items-start gap-3">
                <Battery className="h-5 w-5 text-primary mt-1" />
                <div className="flex-1 space-y-3">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="wantsBatteryStorage"
                      checked={data.wantsBatteryStorage}
                      onCheckedChange={(checked) => onUpdate({ wantsBatteryStorage: !!checked })}
                    />
                    <Label htmlFor="wantsBatteryStorage" className="cursor-pointer font-semibold">
                      Batteriespeicher
                    </Label>
                  </div>
                  
                  {data.wantsBatteryStorage && (
                    <Alert>
                      <Info className="h-4 w-4" />
                      <AlertDescription>
                        <strong>Vorteile:</strong> Ein Batteriespeicher erhöht den Eigenverbrauch von ca. 30% 
                        auf 70-80% und steigert die Unabhängigkeit vom Netz. Die Amortisation verlängert sich 
                        jedoch um ca. 3-5 Jahre.
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          <Separator />
        </>
      )}

      {/* Economic Priorities */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="flex items-start gap-3">
            <TrendingUp className="h-5 w-5 text-primary mt-1" />
            <div className="flex-1 space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="prioritizeAmortization"
                  checked={data.prioritizeAmortization}
                  onCheckedChange={(checked) => onUpdate({ prioritizeAmortization: !!checked })}
                />
                <Label htmlFor="prioritizeAmortization" className="cursor-pointer font-semibold">
                  Amortisation priorisieren
                </Label>
              </div>
              
              <p className="text-sm text-muted-foreground">
                Die Anlagengröße und Komponentenauswahl werden so optimiert, dass die Amortisationszeit 
                minimiert wird (auch wenn dies zu Lasten der maximalen Autarkie geht).
              </p>

              {data.prioritizeAmortization && (
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    <strong>Hinweis:</strong> Bei Priorisierung der Amortisation werden tendenziell kleinere 
                    Anlagen ohne oder mit kleinerem Batteriespeicher empfohlen. Die Wirtschaftlichkeit steht 
                    im Vordergrund.
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Additional Wishes */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="space-y-2">
            <Label htmlFor="additionalWishes">Weitere Wünsche & Anforderungen (optional)</Label>
            <Textarea
              id="additionalWishes"
              value={data.additionalWishes}
              onChange={(e) => onUpdate({ additionalWishes: e.target.value })}
              placeholder="z.B. Notstromfunktion, bestimmte Hersteller-Präferenzen, optische Anforderungen, Zeitplan..."
              rows={6}
            />
            <p className="text-xs text-muted-foreground">
              Hier können Sie alle weiteren Anforderungen, Besonderheiten oder Wünsche des Kunden festhalten.
            </p>
          </div>
        </CardContent>
      </Card>

      {!hasPV && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            <strong>Hinweis:</strong> Für reine Wärmepumpen-Projekte sind E-Mobilität und Batteriespeicher 
            nicht relevant. Diese Optionen erscheinen nur bei PV-Anlagen.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default CustomerNeedsStepModern;
