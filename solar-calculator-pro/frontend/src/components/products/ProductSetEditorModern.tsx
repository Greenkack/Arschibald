/**
 * Product Set Editor (Modern - shadcn/ui)
 * 
 * Edit/Create product sets:
 * - Set metadata (name, description, category)
 * - Product selection (multi-select)
 * - Pricing configuration (base price, discount)
 * - Active/Inactive toggle
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Save, X, Package } from 'lucide-react';
import api from '../../services/api';

interface Product {
  id: number;
  name: string;
  category: string;
  manufacturer?: string;
}

interface ProductSet {
  id: number;
  name: string;
  description?: string;
  category: string;
  products: number[];
  base_price?: number;
  discount_percent?: number;
  is_active: boolean;
}

interface ProductSetEditorProps {
  set: ProductSet | null;
  onSave: () => void;
  onCancel: () => void;
}

const CATEGORIES = [
  'PV-Komplettset',
  'Speicherset',
  'E-Mobilitätsset',
  'Montage-Set',
  'Premium-Paket',
  'Starter-Paket',
  'Sonstige'
];

const ProductSetEditorModern: React.FC<ProductSetEditorProps> = ({ set, onSave, onCancel }) => {
  const { toast } = useToast();
  const [form, setForm] = useState({
    name: '',
    description: '',
    category: '',
    products: [] as number[],
    base_price: 0,
    discount_percent: 0,
    is_active: true
  });
  const [availableProducts, setAvailableProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (set && set.id > 0) {
      setForm({
        name: set.name,
        description: set.description || '',
        category: set.category,
        products: set.products || [],
        base_price: set.base_price || 0,
        discount_percent: set.discount_percent || 0,
        is_active: set.is_active
      });
    }
    loadProducts();
  }, [set]);

  const loadProducts = async () => {
    try {
      const response = await api.get('/products');
      setAvailableProducts(response.data.products || []);
    } catch (error) {
      console.error('Failed to load products:', error);
    }
  };

  const handleSave = async () => {
    if (!form.name || !form.category) {
      toast({
        title: 'Validierungsfehler',
        description: 'Bitte füllen Sie alle Pflichtfelder aus',
        variant: 'destructive'
      });
      return;
    }

    setLoading(true);
    try {
      if (set && set.id > 0) {
        await api.put(`/products/sets/${set.id}`, form);
        toast({
          title: 'Erfolgreich',
          description: 'Produktset aktualisiert'
        });
      } else {
        await api.post('/products/sets', form);
        toast({
          title: 'Erfolgreich',
          description: 'Produktset erstellt'
        });
      }
      onSave();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: 'Produktset konnte nicht gespeichert werden',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          <Package className="h-6 w-6" />
          {set && set.id > 0 ? 'Produktset bearbeiten' : 'Neues Produktset'}
        </CardTitle>
        <CardDescription>
          Konfigurieren Sie die Eigenschaften des Produktsets
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Basic Information */}
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="z.B. Starter-Paket 10 kWp"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="category">Kategorie *</Label>
              <Select value={form.category} onValueChange={(value) => setForm({ ...form, category: value })}>
                <SelectTrigger id="category">
                  <SelectValue placeholder="Kategorie wählen" />
                </SelectTrigger>
                <SelectContent>
                  {CATEGORIES.map(cat => (
                    <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Beschreibung</Label>
            <Textarea
              id="description"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={3}
              placeholder="Beschreiben Sie das Produktset..."
            />
          </div>
        </div>

        <Separator />

        {/* Product Selection */}
        <div className="space-y-4">
          <Label>Produkte ({form.products.length} ausgewählt)</Label>
          <ScrollArea className="h-64 border rounded-md p-4">
            {availableProducts.map((product) => (
              <div key={product.id} className="flex items-center space-x-3 py-2">
                <Checkbox
                  id={`product-${product.id}`}
                  checked={form.products.includes(product.id)}
                  onCheckedChange={(checked) => {
                    setForm({
                      ...form,
                      products: checked
                        ? [...form.products, product.id]
                        : form.products.filter(id => id !== product.id)
                    });
                  }}
                />
                <Label htmlFor={`product-${product.id}`} className="cursor-pointer flex-1">
                  <div className="flex items-center justify-between">
                    <span>{product.name}</span>
                    <span className="text-sm text-muted-foreground">
                      {product.manufacturer || product.category}
                    </span>
                  </div>
                </Label>
              </div>
            ))}
          </ScrollArea>
        </div>

        <Separator />

        {/* Pricing */}
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="basePrice">Basispreis (€)</Label>
              <Input
                id="basePrice"
                type="number"
                value={form.base_price}
                onChange={(e) => setForm({ ...form, base_price: parseFloat(e.target.value) || 0 })}
                step={0.01}
                min={0}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="discount">Rabatt (%)</Label>
              <Input
                id="discount"
                type="number"
                value={form.discount_percent}
                onChange={(e) => setForm({ ...form, discount_percent: parseFloat(e.target.value) || 0 })}
                step={0.1}
                min={0}
                max={100}
              />
            </div>
          </div>
        </div>

        <Separator />

        {/* Status */}
        <div className="flex items-center space-x-2">
          <Checkbox
            id="isActive"
            checked={form.is_active}
            onCheckedChange={(checked) => setForm({ ...form, is_active: !!checked })}
          />
          <Label htmlFor="isActive" className="cursor-pointer">
            Produktset ist aktiv und kann verkauft werden
          </Label>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4">
          <Button variant="outline" onClick={onCancel} disabled={loading}>
            <X className="h-4 w-4 mr-2" />
            Abbrechen
          </Button>
          <Button onClick={handleSave} disabled={loading}>
            <Save className="h-4 w-4 mr-2" />
            {loading ? 'Wird gespeichert...' : 'Speichern'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProductSetEditorModern;
