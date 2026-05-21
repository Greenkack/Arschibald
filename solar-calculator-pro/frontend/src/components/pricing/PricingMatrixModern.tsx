/**
 * Pricing Matrix (Modern - shadcn/ui)
 * 
 * Manages table-based pricing:
 * - Rows: Module count ranges
 * - Columns: Storage options
 * - Cells: Editable prices
 * - Import/Export CSV
 * - Version history
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { DollarSign, Upload, Download, Save, RotateCcw, Copy, Clock } from 'lucide-react';
import api from '../../services/api';

interface PriceCell {
  module_count_min: number;
  module_count_max: number;
  storage_model: string;
  price: number;
}

interface PricingMatrix {
  id: number;
  name: string;
  version: string;
  cells: PriceCell[];
  created_at?: string;
  updated_at?: string;
  is_active: boolean;
}

const STORAGE_OPTIONS = [
  'Ohne Speicher',
  'BYD 5 kWh',
  'BYD 10 kWh',
  'BYD 15 kWh',
  'sonnenBatterie 10',
  'sonnenBatterie 15'
];

const MODULE_RANGES = [
  { min: 1, max: 10 },
  { min: 11, max: 20 },
  { min: 21, max: 30 },
  { min: 31, max: 40 },
  { min: 41, max: 50 },
  { min: 51, max: 100 }
];

const PricingMatrixModern: React.FC = () => {
  const { toast } = useToast();
  const [matrix, setMatrix] = useState<PricingMatrix | null>(null);
  const [editingCell, setEditingCell] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [versions, setVersions] = useState<PricingMatrix[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<string>('');

  const loadMatrix = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/pricing/matrix');
      setMatrix(response.data.matrix);
      setSelectedVersion(response.data.matrix.version);
    } catch (error) {
      console.error('Failed to load matrix:', error);
      toast({
        title: 'Fehler',
        description: 'Preismatrix konnte nicht geladen werden',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  const loadVersions = useCallback(async () => {
    try {
      const response = await api.get('/pricing/matrix/versions');
      setVersions(response.data.versions || []);
    } catch (error) {
      console.error('Failed to load versions:', error);
    }
  }, []);

  useEffect(() => {
    loadMatrix();
    loadVersions();
  }, [loadMatrix, loadVersions]);

  const getCellPrice = (moduleMin: number, storage: string) => {
    if (!matrix) return 0;
    const cell = matrix.cells.find(
      c => c.module_count_min === moduleMin && c.storage_model === storage
    );
    return cell?.price || 0;
  };

  const updateCellPrice = (moduleMin: number, storage: string, price: number) => {
    if (!matrix) return;
    const updatedCells = matrix.cells.map(c =>
      c.module_count_min === moduleMin && c.storage_model === storage
        ? { ...c, price }
        : c
    );
    setMatrix({ ...matrix, cells: updatedCells });
  };

  const handleSave = async () => {
    if (!matrix) return;
    setLoading(true);
    try {
      await api.put(`/pricing/matrix/${matrix.id}`, {
        cells: matrix.cells,
        version: matrix.version
      });
      toast({
        title: 'Erfolgreich',
        description: 'Preismatrix gespeichert'
      });
      loadVersions();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: 'Preismatrix konnte nicht gespeichert werden',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    if (!matrix) return;
    const csv = ['Module Range,Storage,Price'];
    matrix.cells.forEach(cell => {
      csv.push(`${cell.module_count_min}-${cell.module_count_max},${cell.storage_model},${cell.price}`);
    });
    const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pricing_matrix_${matrix.version}.csv`;
    a.click();
    toast({
      title: 'Export erfolgreich',
      description: 'CSV-Datei wurde heruntergeladen'
    });
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !matrix) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const lines = text.split('\n').slice(1); // Skip header
      const updatedCells = [...matrix.cells];
      
      lines.forEach(line => {
        const [range, storage, price] = line.split(',');
        const [min] = range.split('-').map(Number);
        const cellIndex = updatedCells.findIndex(
          c => c.module_count_min === min && c.storage_model === storage
        );
        if (cellIndex !== -1) {
          updatedCells[cellIndex].price = parseFloat(price);
        }
      });

      setMatrix({ ...matrix, cells: updatedCells });
      toast({
        title: 'Import erfolgreich',
        description: 'Preise wurden aus CSV aktualisiert'
      });
    };
    reader.readAsText(file);
  };

  const formatCurrency = (value: number) => {
    return `${value.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €`;
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <DollarSign className="h-6 w-6" />
            Preismatrix verwalten
          </CardTitle>
          <CardDescription>
            Konfigurieren Sie Preise basierend auf Modulanzahl und Speichergröße
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Header Actions */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="space-y-2">
                <Label>Version</Label>
                <Select value={selectedVersion} onValueChange={setSelectedVersion}>
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {versions.map(v => (
                      <SelectItem key={v.id} value={v.version}>
                        {v.version} {v.is_active && <Badge className="ml-2">Aktiv</Badge>}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button variant="outline" size="icon" onClick={() => loadMatrix()} title="Aktualisieren">
                <RotateCcw className="h-4 w-4" />
              </Button>
            </div>

            <div className="flex gap-2">
              <Button variant="outline" onClick={handleExport}>
                <Download className="h-4 w-4 mr-2" />
                Export CSV
              </Button>
              <Button variant="outline" asChild>
                <label>
                  <Upload className="h-4 w-4 mr-2" />
                  Import CSV
                  <input
                    type="file"
                    accept=".csv"
                    className="hidden"
                    onChange={handleImport}
                  />
                </label>
              </Button>
              <Button onClick={handleSave} disabled={loading}>
                <Save className="h-4 w-4 mr-2" />
                Speichern
              </Button>
            </div>
          </div>

          {/* Matrix Info */}
          {matrix && (
            <Alert>
              <Clock className="h-4 w-4" />
              <AlertDescription>
                Letzte Änderung: {new Date(matrix.updated_at || '').toLocaleString('de-DE')} | 
                Version: {matrix.version} | 
                {matrix.is_active ? 'Aktiv' : 'Inaktiv'}
              </AlertDescription>
            </Alert>
          )}

          {/* Pricing Table */}
          <ScrollArea className="h-[500px]">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-40">Modulbereich</TableHead>
                  {STORAGE_OPTIONS.map(storage => (
                    <TableHead key={storage} className="text-right">{storage}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {MODULE_RANGES.map(range => (
                  <TableRow key={`${range.min}-${range.max}`}>
                    <TableCell className="font-medium">
                      {range.min} - {range.max} Module
                    </TableCell>
                    {STORAGE_OPTIONS.map(storage => {
                      const cellKey = `${range.min}-${storage}`;
                      const price = getCellPrice(range.min, storage);
                      const isEditing = editingCell === cellKey;

                      return (
                        <TableCell key={storage} className="text-right">
                          {isEditing ? (
                            <Input
                              type="number"
                              value={price}
                              onChange={(e) => updateCellPrice(range.min, storage, parseFloat(e.target.value) || 0)}
                              onBlur={() => setEditingCell(null)}
                              onKeyDown={(e) => e.key === 'Enter' && setEditingCell(null)}
                              step={0.01}
                              autoFocus
                              className="w-32 text-right"
                            />
                          ) : (
                            <div
                              className="cursor-pointer hover:bg-accent px-2 py-1 rounded"
                              onClick={() => setEditingCell(cellKey)}
                            >
                              {formatCurrency(price)}
                            </div>
                          )}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </ScrollArea>

          {/* Bulk Operations */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Bulk-Operationen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-end gap-4">
                <div className="flex-1 space-y-2">
                  <Label>Prozentuale Änderung</Label>
                  <div className="flex gap-2">
                    <Input type="number" placeholder="z.B. 5 für +5%" step={0.1} />
                    <Button variant="outline">
                      Anwenden
                    </Button>
                  </div>
                </div>
                <Button variant="outline">
                  <Copy className="h-4 w-4 mr-2" />
                  Zeile kopieren
                </Button>
              </div>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    </div>
  );
};

export default PricingMatrixModern;
