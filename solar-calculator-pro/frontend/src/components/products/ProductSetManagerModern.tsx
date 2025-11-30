/**
 * Product Set Manager (Modern - shadcn/ui)
 * 
 * Manages predefined product sets/bundles:
 * - List all product sets
 * - Create/Edit/Delete sets
 * - Assign products to sets
 * - Set pricing rules
 */

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/components/ui/use-toast';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Plus, Pencil, Trash2, Package } from 'lucide-react';
import api from '../../services/api';

interface ProductSet {
  id: number;
  name: string;
  description?: string;
  category: string;
  products: number[];
  product_names?: string[];
  base_price?: number;
  discount_percent?: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

interface ProductSetManagerProps {
  onEdit?: (set: ProductSet) => void;
}

const ProductSetManagerModern: React.FC<ProductSetManagerProps> = ({ onEdit }) => {
  const { toast } = useToast();
  const [sets, setSets] = useState<ProductSet[]>([]);
  const [loading, setLoading] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<{
    show: boolean;
    set: ProductSet | null;
  }>({ show: false, set: null });

  const loadSets = React.useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/products/sets');
      setSets(response.data.sets || []);
    } catch (error) {
      console.error('Failed to load sets:', error);
      toast({
        title: 'Fehler',
        description: 'Produktsets konnten nicht geladen werden',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  React.useEffect(() => {
    loadSets();
  }, [loadSets]);

  const handleDelete = async () => {
    if (!deleteConfirm.set) return;

    try {
      await api.delete(`/products/sets/${deleteConfirm.set.id}`);
      toast({
        title: 'Erfolgreich',
        description: 'Produktset gelöscht'
      });
      setDeleteConfirm({ show: false, set: null });
      loadSets();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: 'Produktset konnte nicht gelöscht werden',
        variant: 'destructive'
      });
    }
  };

  React.useEffect(() => {
    loadSets();
  }, [loadSets]);

  const formatCurrency = (value?: number) => {
    if (!value) return '-';
    return `${value.toLocaleString('de-DE', { minimumFractionDigits: 2 })} €`;
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <Package className="h-6 w-6" />
            Produktsets verwalten
          </CardTitle>
          <CardDescription>
            Erstellen und verwalten Sie vordefinierte Produktbundles
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-end">
            <Button
              onClick={() => onEdit?.({
                id: 0,
                name: '',
                category: '',
                products: [],
                is_active: true
              })}
              className="gap-2"
            >
              <Plus className="h-4 w-4" />
              Neues Produktset
            </Button>
          </div>

          <ScrollArea className="h-[600px]">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Kategorie</TableHead>
                  <TableHead>Beschreibung</TableHead>
                  <TableHead className="text-center">Produkte</TableHead>
                  <TableHead className="text-right">Basispreis</TableHead>
                  <TableHead className="text-center">Rabatt</TableHead>
                  <TableHead className="text-center">Status</TableHead>
                  <TableHead className="text-right">Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sets.map((set) => (
                  <TableRow key={set.id}>
                    <TableCell className="font-medium">{set.name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{set.category}</Badge>
                    </TableCell>
                    <TableCell className="max-w-xs truncate">{set.description || '-'}</TableCell>
                    <TableCell className="text-center">
                      <Badge>{set.products.length} Produkte</Badge>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {formatCurrency(set.base_price)}
                    </TableCell>
                    <TableCell className="text-center">
                      {set.discount_percent ? (
                        <Badge variant="secondary">{set.discount_percent}%</Badge>
                      ) : '-'}
                    </TableCell>
                    <TableCell className="text-center">
                      <Badge variant={set.is_active ? 'default' : 'secondary'}>
                        {set.is_active ? 'Aktiv' : 'Inaktiv'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onEdit?.(set)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeleteConfirm({ show: true, set })}
                        >
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
                {sets.length === 0 && !loading && (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-12 text-muted-foreground">
                      Keine Produktsets vorhanden
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </ScrollArea>
        </CardContent>
      </Card>

      <AlertDialog open={deleteConfirm.show} onOpenChange={(open: boolean) => !open && setDeleteConfirm({ show: false, set: null })}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Produktset löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              Möchten Sie das Produktset "{deleteConfirm.set?.name}" wirklich löschen? 
              Diese Aktion kann nicht rückgängig gemacht werden.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-red-600 hover:bg-red-700">
              Löschen
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default ProductSetManagerModern;
