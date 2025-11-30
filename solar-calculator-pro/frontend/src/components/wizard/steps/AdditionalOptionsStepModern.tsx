/**
 * Step 6: Additional Options
 * Financing, discounts, payment terms, and maintenance contracts
 */

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Info, CreditCard, DollarSign, Wrench } from 'lucide-react';
import type { ProjectWizardData } from '../ProjectWizardModern';

interface AdditionalOptionsStepProps {
  data: ProjectWizardData;
  onUpdate: (updates: Partial<ProjectWizardData>) => void;
}

const loanTermOptions = [
  { value: 5, label: '5 Jahre' },
  { value: 7, label: '7 Jahre' },
  { value: 10, label: '10 Jahre' },
  { value: 12, label: '12 Jahre' },
  { value: 15, label: '15 Jahre' },
  { value: 20, label: '20 Jahre' }
];

const paymentTermsOptions = [
  { value: '50_50', label: '50% Anzahlung, 50% bei Abnahme' },
  { value: '30_70', label: '30% Anzahlung, 70% bei Abnahme' },
  { value: '0_100', label: '100% bei Abnahme' },
  { value: '30_30_40', label: '30% Anzahlung, 30% bei Montage, 40% bei Abnahme' },
  { value: 'custom', label: 'Individuelle Vereinbarung' }
];

const AdditionalOptionsStepModern: React.FC<AdditionalOptionsStepProps> = ({ data, onUpdate }) => {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Zusatzoptionen</h3>
        <p className="text-sm text-muted-foreground">
          Finanzierung, Rabatte und weitere Optionen
        </p>
      </div>

      {/* Financing */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="flex items-start gap-3">
            <CreditCard className="h-5 w-5 text-primary mt-1" />
            <div className="flex-1 space-y-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="wantsFinancing"
                  checked={data.wantsFinancing}
                  onCheckedChange={(checked) => onUpdate({ wantsFinancing: !!checked })}
                />
                <Label htmlFor="wantsFinancing" className="cursor-pointer font-semibold">
                  Finanzierung
                </Label>
              </div>

              {data.wantsFinancing && (
                <div className="space-y-4 pl-8">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="downPayment">Anzahlung (€)</Label>
                      <Input
                        id="downPayment"
                        type="number"
                        value={data.downPayment ?? ''}
                        onChange={(e) => onUpdate({ 
                          downPayment: e.target.value ? parseFloat(e.target.value) : null 
                        })}
                        placeholder="z.B. 5000"
                        step={100}
                        min={0}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="loanTerm">Laufzeit *</Label>
                      <Select 
                        value={data.loanTerm?.toString()} 
                        onValueChange={(value) => onUpdate({ loanTerm: parseInt(value) })}
                      >
                        <SelectTrigger id="loanTerm">
                          <SelectValue placeholder="Wählen..." />
                        </SelectTrigger>
                        <SelectContent>
                          {loanTermOptions.map(t => (
                            <SelectItem key={t.value} value={t.value.toString()}>{t.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="interestRate">Zinssatz (%) *</Label>
                      <Input
                        id="interestRate"
                        type="number"
                        value={data.interestRate ?? ''}
                        onChange={(e) => onUpdate({ 
                          interestRate: e.target.value ? parseFloat(e.target.value) : null 
                        })}
                        placeholder="z.B. 3.5"
                        step={0.1}
                        min={0}
                        max={20}
                        required={data.wantsFinancing}
                      />
                    </div>
                  </div>

                  <Alert>
                    <Info className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Hinweis:</strong> Für PV-Anlagen gibt es günstige KfW-Kredite 
                      (Programm 270, ab 4,15% eff. Jahreszins). Für Wärmepumpen können BAFA-Förderungen 
                      in Anspruch genommen werden.
                    </AlertDescription>
                  </Alert>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Discounts & Surcharges */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="flex items-start gap-3">
            <DollarSign className="h-5 w-5 text-primary mt-1" />
            <div className="flex-1 space-y-4">
              <h4 className="font-semibold">Rabatte & Zuschläge</h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="discountPercent">Rabatt (%)</Label>
                  <Input
                    id="discountPercent"
                    type="number"
                    value={data.discountPercent ?? ''}
                    onChange={(e) => onUpdate({ 
                      discountPercent: e.target.value ? parseFloat(e.target.value) : null 
                    })}
                    placeholder="z.B. 5"
                    step={0.1}
                    min={0}
                    max={100}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="discountFixed">Rabatt (€ fest)</Label>
                  <Input
                    id="discountFixed"
                    type="number"
                    value={data.discountFixed ?? ''}
                    onChange={(e) => onUpdate({ 
                      discountFixed: e.target.value ? parseFloat(e.target.value) : null 
                    })}
                    placeholder="z.B. 1000"
                    step={10}
                    min={0}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="surchargePercent">Zuschlag (%)</Label>
                  <Input
                    id="surchargePercent"
                    type="number"
                    value={data.surchargePercent ?? ''}
                    onChange={(e) => onUpdate({ 
                      surchargePercent: e.target.value ? parseFloat(e.target.value) : null 
                    })}
                    placeholder="z.B. 3"
                    step={0.1}
                    min={0}
                    max={100}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="surchargeFixed">Zuschlag (€ fest)</Label>
                  <Input
                    id="surchargeFixed"
                    type="number"
                    value={data.surchargeFixed ?? ''}
                    onChange={(e) => onUpdate({ 
                      surchargeFixed: e.target.value ? parseFloat(e.target.value) : null 
                    })}
                    placeholder="z.B. 500"
                    step={10}
                    min={0}
                  />
                </div>
              </div>

              <p className="text-xs text-muted-foreground">
                Prozentuale Rabatte/Zuschläge werden vor festen Beträgen angewendet.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Maintenance Contract */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="flex items-start gap-3">
            <Wrench className="h-5 w-5 text-primary mt-1" />
            <div className="flex-1 space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="wantsMaintenanceContract"
                  checked={data.wantsMaintenanceContract}
                  onCheckedChange={(checked) => onUpdate({ wantsMaintenanceContract: !!checked })}
                />
                <Label htmlFor="wantsMaintenanceContract" className="cursor-pointer font-semibold">
                  Wartungsvertrag
                </Label>
              </div>

              <p className="text-sm text-muted-foreground">
                Ein Wartungsvertrag umfasst jährliche Inspektionen, Reinigung und Leistungsprüfung 
                der Anlage. Empfohlen für optimale Anlagenleistung und Garantieerhalt.
              </p>

              {data.wantsMaintenanceContract && (
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Kosten ca. 150-300 €/Jahr je nach Anlagengröße. 
                    Verlängert typischerweise Hersteller-Garantien und sichert optimale Erträge.
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Payment Terms */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="space-y-2">
            <Label htmlFor="paymentTerms">Zahlungsbedingungen</Label>
            <Select value={data.paymentTerms} onValueChange={(value) => onUpdate({ paymentTerms: value })}>
              <SelectTrigger id="paymentTerms">
                <SelectValue placeholder="Wählen..." />
              </SelectTrigger>
              <SelectContent>
                {paymentTermsOptions.map(t => (
                  <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Standard: 50% Anzahlung bei Auftragserteilung, 50% nach erfolgreicher Abnahme
            </p>
          </div>
        </CardContent>
      </Card>

      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          <strong>Tipp:</strong> Alle Angaben sind optional und können später noch angepasst werden. 
          Sie dienen der Vorkalkulation und können im Angebot flexibel geändert werden.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default AdditionalOptionsStepModern;
