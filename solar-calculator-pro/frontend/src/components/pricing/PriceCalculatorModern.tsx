/**
 * Price Calculator (Modern - shadcn/ui)
 * 
 * Real-time price calculation with:
 * - Module count selection with validation
 * - Battery storage options
 * - Extras & accessories selection (checkboxes)
 * - Services selection
 * - Live price breakdown with German number formatting
 * - Tax calculation (19% MwSt)
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { useToast } from '@/components/ui/use-toast';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Calculator, RefreshCw, Trash2, Info, AlertCircle, CheckCircle2, Zap, Plus, Wrench } from 'lucide-react';
import api from '../../services/api';

interface StorageOption {
  id: string;
  name: string;
  capacity: string;
  manufacturer: string;
}

interface Extra {
  id: string;
  name: string;
  price: number;
  category: string;
  description?: string;
}

interface Service {
  id: string;
  name: string;
  price: number;
  description?: string;
}

interface PriceBreakdownItem {
  name: string;
  quantity: number;
  unit_price: number;
  total: number;
  type: 'base' | 'extra' | 'service';
}

interface PriceBreakdown {
  base_price: number;
  extras_total: number;
  services_total: number;
  subtotal: number;
  discount: number;
  tax: number;
  total: number;
  items: PriceBreakdownItem[];
}

interface CalculationResult {
  success: boolean;
  price?: number;
  breakdown?: PriceBreakdown;
  error?: string;
  metadata?: {
    module_count: number;
    storage_model: string | null;
    matrix_id: number;
  };
}

// German number formatting
const formatCurrency = (value: number): string => {
  return `${value.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €`;
};

const PriceCalculatorModern: React.FC = () => {
  const { toast } = useToast();
  const [moduleCount, setModuleCount] = useState<number>(20);
  const [storageModel, setStorageModel] = useState<string>('none');
  const [storageOptions, setStorageOptions] = useState<StorageOption[]>([]);
  const [selectedExtras, setSelectedExtras] = useState<string[]>([]);
  const [selectedServices, setSelectedServices] = useState<string[]>([]);
  const [availableExtras, setAvailableExtras] = useState<Extra[]>([]);
  const [availableServices, setAvailableServices] = useState<Service[]>([]);
  const [calculating, setCalculating] = useState(false);
  const [result, setResult] = useState<CalculationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (moduleCount > 0) {
      calculatePrice();
    }
  }, [moduleCount, storageModel, selectedExtras, selectedServices]);

  const loadData = async () => {
    const mockStorageOptions: StorageOption[] = [
      { id: 'none', name: 'Kein Speicher', capacity: '0 kWh', manufacturer: '-' },
      { id: 'byd_5', name: 'BYD Battery-Box Premium HVS 5.1', capacity: '5,1 kWh', manufacturer: 'BYD' },
      { id: 'byd_10', name: 'BYD Battery-Box Premium HVS 10.2', capacity: '10,2 kWh', manufacturer: 'BYD' },
      { id: 'byd_15', name: 'BYD Battery-Box Premium HVS 15.4', capacity: '15,4 kWh', manufacturer: 'BYD' },
      { id: 'sonnen_10', name: 'sonnenBatterie 10', capacity: '10 kWh', manufacturer: 'sonnen' },
      { id: 'sonnen_15', name: 'sonnenBatterie 15', capacity: '15 kWh', manufacturer: 'sonnen' },
    ];

    const mockExtras: Extra[] = [
      { id: 'optimizer', name: 'Leistungsoptimierer', price: 150, category: 'Optimierung', description: 'Pro Modul' },
      { id: 'monitoring', name: 'Monitoring-System', price: 500, category: 'Überwachung', description: 'Erweiterte Überwachung' },
      { id: 'wallbox', name: 'Wallbox 11kW', price: 1200, category: 'E-Mobilität', description: 'Ladestation für E-Auto' },
      { id: 'surge_protection', name: 'Überspannungsschutz', price: 300, category: 'Sicherheit', description: 'Typ 1+2' },
      { id: 'smart_meter', name: 'Smart Meter', price: 400, category: 'Messung', description: 'Intelligenter Stromzähler' },
    ];

    const mockServices: Service[] = [
      { id: 'installation', name: 'Installation & Inbetriebnahme', price: 2500, description: 'Komplette Installation' },
      { id: 'planning', name: 'Detailplanung', price: 500, description: 'Technische Planung' },
      { id: 'permit', name: 'Genehmigungsservice', price: 300, description: 'Behördliche Genehmigungen' },
      { id: 'warranty_extended', name: 'Erweiterte Garantie (5 Jahre)', price: 800, description: 'Zusätzliche Garantie' },
      { id: 'maintenance', name: 'Wartungsvertrag (1 Jahr)', price: 400, description: 'Jährliche Wartung' },
    ];

    setStorageOptions(mockStorageOptions);
    setAvailableExtras(mockExtras);
    setAvailableServices(mockServices);
  };

  const calculatePrice = useCallback(async () => {
    if (!moduleCount || moduleCount < 1 || moduleCount > 200) {
      setError('Bitte geben Sie eine gültige Modulanzahl ein (1-200)');
      return;
    }

    setCalculating(true);
    setError(null);

    try {
      const response = await api.post('/api/v1/pricing/calculate', {
        module_count: moduleCount,
        storage_model: storageModel === 'none' ? null : storageModel,
        enable_fallback: true
      });

      if (response.data.success) {
        const extrasTotal = selectedExtras.reduce((sum, extraId) => {
          const extra = availableExtras.find(e => e.id === extraId);
          return sum + (extra?.price || 0);
        }, 0);

        const servicesTotal = selectedServices.reduce((sum, serviceId) => {
          const service = availableServices.find(s => s.id === serviceId);
          return sum + (service?.price || 0);
        }, 0);

        const basePrice = response.data.price || 0;
        const subtotal = basePrice + extrasTotal + servicesTotal;
        const discount = 0;
        const tax = subtotal * 0.19;
        const total = subtotal - discount + tax;

        const items: PriceBreakdownItem[] = [
          {
            name: `PV-Anlage (${moduleCount} Module${storageModel !== 'none' ? ' + Speicher' : ''})`,
            quantity: 1,
            unit_price: basePrice,
            total: basePrice,
            type: 'base'
          },
          ...selectedExtras.map(extraId => {
            const extra = availableExtras.find(e => e.id === extraId)!;
            return {
              name: extra.name,
              quantity: 1,
              unit_price: extra.price,
              total: extra.price,
              type: 'extra' as const
            };
          }),
          ...selectedServices.map(serviceId => {
            const service = availableServices.find(s => s.id === serviceId)!;
            return {
              name: service.name,
              quantity: 1,
              unit_price: service.price,
              total: service.price,
              type: 'service' as const
            };
          })
        ];

        const breakdown: PriceBreakdown = {
          base_price: basePrice,
          extras_total: extrasTotal,
          services_total: servicesTotal,
          subtotal,
          discount,
          tax,
          total,
          items
        };

        setResult({
          success: true,
          price: total,
          breakdown,
          metadata: response.data.metadata
        });
      } else {
        setError(response.data.user_message || 'Fehler bei der Preisberechnung');
        setResult(null);
      }
    } catch (err: any) {
      console.error('Error calculating price:', err);
      setError(err.response?.data?.detail || 'Fehler bei der Preisberechnung');
      setResult(null);
    } finally {
      setCalculating(false);
    }
  }, [moduleCount, storageModel, selectedExtras, selectedServices, availableExtras, availableServices]);

  const handleReset = () => {
    setModuleCount(20);
    setStorageModel('none');
    setSelectedExtras([]);
    setSelectedServices([]);
    setResult(null);
    setError(null);
  };

  const getItemIcon = (type: string) => {
    if (type === 'base') return '🏠';
    if (type === 'extra') return '➕';
    if (type === 'service') return '🔧';
    return '📦';
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <Calculator className="h-6 w-6" />
            Preisberechnung
          </CardTitle>
          <CardDescription>
            Konfigurieren Sie Ihre PV-Anlage und erhalten Sie eine sofortige Preisberechnung
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Product Selection */}
          <Accordion type="single" defaultValue="product" collapsible>
            <AccordionItem value="product">
              <AccordionTrigger className="text-lg font-semibold">
                1️⃣ Produktauswahl
              </AccordionTrigger>
              <AccordionContent className="space-y-4 pt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="moduleCount">
                      Anzahl PV-Module <span className="text-red-600">*</span>
                    </Label>
                    <div className="flex gap-2">
                      <Input
                        id="moduleCount"
                        type="number"
                        value={moduleCount}
                        onChange={(e) => setModuleCount(parseInt(e.target.value) || 0)}
                        min={1}
                        max={200}
                      />
                      <div className="flex gap-1">
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => setModuleCount(Math.max(1, moduleCount - 1))}
                        >
                          -
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          onClick={() => setModuleCount(Math.min(200, moduleCount + 1))}
                        >
                          +
                        </Button>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Geben Sie die gewünschte Anzahl an PV-Modulen ein (1-200)
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="storageModel">Batteriespeicher</Label>
                    <Select value={storageModel} onValueChange={setStorageModel}>
                      <SelectTrigger id="storageModel">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {storageOptions.map(opt => (
                          <SelectItem key={opt.id} value={opt.id}>
                            {opt.name} ({opt.capacity})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-muted-foreground">
                      Optional: Wählen Sie einen Batteriespeicher aus
                    </p>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>

            {/* Extras */}
            <AccordionItem value="extras">
              <AccordionTrigger className="text-lg font-semibold">
                2️⃣ Extras & Zubehör
              </AccordionTrigger>
              <AccordionContent className="pt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {availableExtras.map(extra => (
                    <Card key={extra.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="pt-6">
                        <div className="flex items-start space-x-3">
                          <Checkbox
                            id={`extra-${extra.id}`}
                            checked={selectedExtras.includes(extra.id)}
                            onCheckedChange={(checked) => {
                              setSelectedExtras(prev =>
                                checked
                                  ? [...prev, extra.id]
                                  : prev.filter(id => id !== extra.id)
                              );
                            }}
                          />
                          <div className="flex-1">
                            <Label htmlFor={`extra-${extra.id}`} className="cursor-pointer font-semibold">
                              <div className="flex items-center justify-between">
                                <span>{extra.name}</span>
                                <Badge variant="secondary">{formatCurrency(extra.price)}</Badge>
                              </div>
                            </Label>
                            {extra.description && (
                              <p className="text-sm text-muted-foreground mt-1">{extra.description}</p>
                            )}
                            <Badge className="mt-2" variant="outline">{extra.category}</Badge>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </AccordionContent>
            </AccordionItem>

            {/* Services */}
            <AccordionItem value="services">
              <AccordionTrigger className="text-lg font-semibold">
                3️⃣ Dienstleistungen
              </AccordionTrigger>
              <AccordionContent className="pt-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {availableServices.map(service => (
                    <Card key={service.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="pt-6">
                        <div className="flex items-start space-x-3">
                          <Checkbox
                            id={`service-${service.id}`}
                            checked={selectedServices.includes(service.id)}
                            onCheckedChange={(checked) => {
                              setSelectedServices(prev =>
                                checked
                                  ? [...prev, service.id]
                                  : prev.filter(id => id !== service.id)
                              );
                            }}
                          />
                          <div className="flex-1">
                            <Label htmlFor={`service-${service.id}`} className="cursor-pointer font-semibold">
                              <div className="flex items-center justify-between">
                                <span>{service.name}</span>
                                <Badge variant="secondary">{formatCurrency(service.price)}</Badge>
                              </div>
                            </Label>
                            {service.description && (
                              <p className="text-sm text-muted-foreground mt-1">{service.description}</p>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button onClick={calculatePrice} disabled={calculating} className="gap-2">
              <RefreshCw className={`h-4 w-4 ${calculating ? 'animate-spin' : ''}`} />
              Neu berechnen
            </Button>
            <Button variant="outline" onClick={handleReset} disabled={calculating} className="gap-2">
              <Trash2 className="h-4 w-4" />
              Zurücksetzen
            </Button>
          </div>

          {/* Price Breakdown */}
          {result?.breakdown && !calculating && (
            <>
              <Separator />
              <div className="space-y-4">
                <h3 className="text-xl font-semibold flex items-center gap-2">
                  <Zap className="h-5 w-5 text-yellow-600" />
                  Preisaufschlüsselung
                </h3>

                <ScrollArea className="h-96">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Position</TableHead>
                        <TableHead className="text-center">Menge</TableHead>
                        <TableHead className="text-right">Einzelpreis</TableHead>
                        <TableHead className="text-right">Gesamt</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {result.breakdown.items.map((item, idx) => (
                        <TableRow key={idx}>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <span className="text-lg">{getItemIcon(item.type)}</span>
                              <span>{item.name}</span>
                            </div>
                          </TableCell>
                          <TableCell className="text-center">{item.quantity}</TableCell>
                          <TableCell className="text-right font-mono">{formatCurrency(item.unit_price)}</TableCell>
                          <TableCell className="text-right font-mono font-semibold">{formatCurrency(item.total)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </ScrollArea>

                <Separator />

                <div className="space-y-2">
                  <div className="flex justify-between text-lg">
                    <span>Zwischensumme:</span>
                    <span className="font-mono">{formatCurrency(result.breakdown.subtotal)}</span>
                  </div>
                  {result.breakdown.discount > 0 && (
                    <div className="flex justify-between text-lg text-green-600">
                      <span>Rabatt:</span>
                      <span className="font-mono">-{formatCurrency(result.breakdown.discount)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-lg text-muted-foreground">
                    <span>MwSt. (19%):</span>
                    <span className="font-mono">{formatCurrency(result.breakdown.tax)}</span>
                  </div>
                  
                  <Separator className="my-4" />
                  
                  <div className="flex justify-between text-2xl font-bold">
                    <span>Gesamtpreis:</span>
                    <span className="font-mono text-green-600">{formatCurrency(result.breakdown.total)}</span>
                  </div>
                </div>

                {result.metadata && (
                  <Alert>
                    <Info className="h-4 w-4" />
                    <AlertDescription>
                      Berechnung basiert auf {result.metadata.module_count} Modulen
                      {result.metadata.storage_model && ` mit ${result.metadata.storage_model}`}
                      {' '}(Matrix ID: {result.metadata.matrix_id})
                    </AlertDescription>
                  </Alert>
                )}
              </div>
            </>
          )}

          {calculating && (
            <div className="flex flex-col items-center justify-center py-12 space-y-4">
              <RefreshCw className="h-12 w-12 animate-spin text-primary" />
              <p className="text-lg text-muted-foreground">Preis wird berechnet...</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default PriceCalculatorModern;
