/**
 * Step 2: Customer Data Entry
 * Collects customer contact information with address auto-parsing
 */

import React, { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ChevronDown, ChevronUp } from 'lucide-react';
import type { ProjectWizardData } from '../ProjectWizardModern';

interface CustomerDataStepProps {
  data: ProjectWizardData;
  onUpdate: (updates: Partial<ProjectWizardData>) => void;
}

const salutations = [
  { value: 'herr', label: 'Herr' },
  { value: 'frau', label: 'Frau' },
  { value: 'divers', label: 'Divers' },
  { value: '', label: 'Keine Angabe' }
];

const titles = [
  { value: '', label: 'Kein Titel' },
  { value: 'dr', label: 'Dr.' },
  { value: 'prof', label: 'Prof.' },
  { value: 'prof_dr', label: 'Prof. Dr.' },
  { value: 'dipl_ing', label: 'Dipl.-Ing.' },
  { value: 'ing', label: 'Ing.' }
];

const bundeslaender = [
  { value: 'bw', label: 'Baden-Württemberg' },
  { value: 'by', label: 'Bayern' },
  { value: 'be', label: 'Berlin' },
  { value: 'bb', label: 'Brandenburg' },
  { value: 'hb', label: 'Bremen' },
  { value: 'hh', label: 'Hamburg' },
  { value: 'he', label: 'Hessen' },
  { value: 'mv', label: 'Mecklenburg-Vorpommern' },
  { value: 'ni', label: 'Niedersachsen' },
  { value: 'nw', label: 'Nordrhein-Westfalen' },
  { value: 'rp', label: 'Rheinland-Pfalz' },
  { value: 'sl', label: 'Saarland' },
  { value: 'sn', label: 'Sachsen' },
  { value: 'st', label: 'Sachsen-Anhalt' },
  { value: 'sh', label: 'Schleswig-Holstein' },
  { value: 'th', label: 'Thüringen' }
];

// PLZ to Bundesland mapping (first 2 digits)
const plzToBundesland: Record<string, string> = {
  '01': 'sn', '02': 'sn', '03': 'bb', '04': 'sn', '06': 'st', '07': 'th', '08': 'sn',
  '09': 'by', '10': 'be', '12': 'be', '13': 'be', '14': 'bb', '15': 'bb', '16': 'bb',
  '17': 'mv', '18': 'mv', '19': 'mv', '20': 'hh', '21': 'hh', '22': 'hh', '23': 'sh',
  '24': 'sh', '25': 'sh', '26': 'ni', '27': 'ni', '28': 'hb', '29': 'ni', '30': 'ni',
  '31': 'ni', '32': 'ni', '33': 'ni', '34': 'he', '35': 'he', '36': 'he', '37': 'ni',
  '38': 'ni', '39': 'st', '40': 'nw', '41': 'nw', '42': 'nw', '44': 'nw', '45': 'nw',
  '46': 'nw', '47': 'nw', '48': 'nw', '49': 'nw', '50': 'nw', '51': 'nw', '52': 'nw',
  '53': 'nw', '54': 'rp', '55': 'rp', '56': 'rp', '57': 'nw', '58': 'nw', '59': 'nw',
  '60': 'he', '61': 'he', '63': 'he', '64': 'he', '65': 'he', '66': 'sl', '67': 'rp',
  '68': 'bw', '69': 'bw', '70': 'bw', '71': 'bw', '72': 'bw', '73': 'bw', '74': 'bw',
  '75': 'bw', '76': 'bw', '77': 'bw', '78': 'bw', '79': 'bw', '80': 'by', '81': 'by',
  '82': 'by', '83': 'by', '84': 'by', '85': 'by', '86': 'by', '87': 'by', '88': 'by',
  '89': 'by', '90': 'by', '91': 'by', '92': 'by', '93': 'by', '94': 'by', '95': 'by',
  '96': 'by', '97': 'by', '98': 'th', '99': 'th'
};

const CustomerDataStepModern: React.FC<CustomerDataStepProps> = ({ data, onUpdate }) => {
  const [manualEntry, setManualEntry] = useState(false);

  // Address parsing function
  const parseAddress = (fullAddress: string) => {
    // Pattern: "Street Number, PLZ City" or "Street Number PLZ City"
    const pattern1 = /^(.+?)\s+(\d+[a-zA-Z]?)\s*,?\s*(\d{5})\s+(.+)$/;
    const match = fullAddress.match(pattern1);
    
    if (match) {
      const [, street, houseNumber, postalCode, city] = match;
      onUpdate({
        street: street.trim(),
        houseNumber: houseNumber.trim(),
        postalCode: postalCode.trim(),
        city: city.trim()
      });
    }
  };

  // Auto-detect Bundesland from PLZ
  useEffect(() => {
    if (data.postalCode && data.postalCode.length >= 2) {
      const prefix = data.postalCode.substring(0, 2);
      const bundesland = plzToBundesland[prefix];
      if (bundesland && bundesland !== data.bundesland) {
        onUpdate({ bundesland });
      }
    }
  }, [data.postalCode, data.bundesland, onUpdate]);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Kundendaten erfassen</h3>
        <p className="text-sm text-muted-foreground">
          Geben Sie die Kontaktdaten des Kunden ein
        </p>
      </div>

      {/* Name Section */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="salutation">Anrede</Label>
              <Select value={data.salutation} onValueChange={(value) => onUpdate({ salutation: value })}>
                <SelectTrigger id="salutation">
                  <SelectValue placeholder="Wählen..." />
                </SelectTrigger>
                <SelectContent>
                  {salutations.map(s => (
                    <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="title">Titel</Label>
              <Select value={data.title} onValueChange={(value) => onUpdate({ title: value })}>
                <SelectTrigger id="title">
                  <SelectValue placeholder="Wählen..." />
                </SelectTrigger>
                <SelectContent>
                  {titles.map(t => (
                    <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="firstName">Vorname *</Label>
              <Input
                id="firstName"
                value={data.firstName}
                onChange={(e) => onUpdate({ firstName: e.target.value })}
                placeholder="Max"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="lastName">Nachname *</Label>
              <Input
                id="lastName"
                value={data.lastName}
                onChange={(e) => onUpdate({ lastName: e.target.value })}
                placeholder="Mustermann"
                required
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Address Section */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-semibold">Adresse</h4>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setManualEntry(!manualEntry)}
              className="gap-2"
            >
              {manualEntry ? (
                <>
                  <ChevronUp className="h-4 w-4" />
                  Auto-Parsing
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4" />
                  Manuelle Eingabe
                </>
              )}
            </Button>
          </div>

          {!manualEntry ? (
            <div className="space-y-2">
              <Label htmlFor="fullAddress">Vollständige Adresse (wird automatisch geparst)</Label>
              <Input
                id="fullAddress"
                value={data.fullAddress}
                onChange={(e) => {
                  onUpdate({ fullAddress: e.target.value });
                  parseAddress(e.target.value);
                }}
                placeholder="Beispiel: Musterstraße 123, 12345 Musterstadt"
              />
              <p className="text-xs text-muted-foreground">
                Format: Straße Hausnummer, PLZ Stadt
              </p>
            </div>
          ) : null}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2 space-y-2">
              <Label htmlFor="street">Straße *</Label>
              <Input
                id="street"
                value={data.street}
                onChange={(e) => onUpdate({ street: e.target.value })}
                placeholder="Musterstraße"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="houseNumber">Hausnummer *</Label>
              <Input
                id="houseNumber"
                value={data.houseNumber}
                onChange={(e) => onUpdate({ houseNumber: e.target.value })}
                placeholder="123"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="postalCode">PLZ *</Label>
              <Input
                id="postalCode"
                value={data.postalCode}
                onChange={(e) => onUpdate({ postalCode: e.target.value })}
                placeholder="12345"
                maxLength={5}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="city">Stadt *</Label>
              <Input
                id="city"
                value={data.city}
                onChange={(e) => onUpdate({ city: e.target.value })}
                placeholder="Musterstadt"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="bundesland">Bundesland</Label>
              <Select value={data.bundesland} onValueChange={(value) => onUpdate({ bundesland: value })}>
                <SelectTrigger id="bundesland">
                  <SelectValue placeholder="Automatisch" />
                </SelectTrigger>
                <SelectContent>
                  {bundeslaender.map(b => (
                    <SelectItem key={b.value} value={b.value}>{b.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Contact Section */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <h4 className="font-semibold mb-4">Kontaktinformationen</h4>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="email">E-Mail</Label>
              <Input
                id="email"
                type="email"
                value={data.email}
                onChange={(e) => onUpdate({ email: e.target.value })}
                placeholder="max@beispiel.de"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phoneFixed">Telefon (Festnetz)</Label>
              <Input
                id="phoneFixed"
                type="tel"
                value={data.phoneFixed}
                onChange={(e) => onUpdate({ phoneFixed: e.target.value })}
                placeholder="0123 456789"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phoneMobile">Telefon (Mobil)</Label>
              <Input
                id="phoneMobile"
                type="tel"
                value={data.phoneMobile}
                onChange={(e) => onUpdate({ phoneMobile: e.target.value })}
                placeholder="0170 1234567"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Notes */}
      <Card>
        <CardContent className="pt-6 space-y-4">
          <div className="space-y-2">
            <Label htmlFor="notes">Notizen (optional)</Label>
            <Textarea
              id="notes"
              value={data.notes}
              onChange={(e) => onUpdate({ notes: e.target.value })}
              placeholder="Zusätzliche Informationen zum Kunden..."
              rows={4}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CustomerDataStepModern;
