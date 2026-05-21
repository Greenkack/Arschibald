/**
 * Pricing Rules (Modern - shadcn/ui)
 * 
 * Rule builder for conditional pricing:
 * - IF-THEN rule logic
 * - Conditions: module_count, storage, customer_type, region
 * - Actions: discount, surcharge, override_price
 * - Rule priority/order
 * - Active/Inactive toggle
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Checkbox } from '@/components/ui/checkbox';
import { useToast } from '@/components/ui/use-toast';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Plus, Pencil, Trash2, ArrowUp, ArrowDown, Save, X, Zap } from 'lucide-react';
import api from '../../services/api';

interface Condition {
  field: string;
  operator: string;
  value: string | number;
}

interface Action {
  type: 'discount' | 'surcharge' | 'override';
  value: number;
  is_percentage: boolean;
}

interface PricingRule {
  id: number;
  name: string;
  description?: string;
  conditions: Condition[];
  actions: Action[];
  priority: number;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

const CONDITION_FIELDS = [
  { value: 'module_count', label: 'Modulanzahl' },
  { value: 'storage_model', label: 'Speichermodell' },
  { value: 'customer_type', label: 'Kundentyp' },
  { value: 'region', label: 'Region' },
  { value: 'total_power', label: 'Gesamtleistung (kWp)' }
];

const OPERATORS = [
  { value: 'equals', label: 'gleich' },
  { value: 'not_equals', label: 'ungleich' },
  { value: 'greater', label: 'größer als' },
  { value: 'less', label: 'kleiner als' },
  { value: 'contains', label: 'enthält' }
];

const ACTION_TYPES = [
  { value: 'discount', label: 'Rabatt' },
  { value: 'surcharge', label: 'Aufschlag' },
  { value: 'override', label: 'Preis überschreiben' }
];

const PricingRulesModern: React.FC = () => {
  const { toast } = useToast();
  const [rules, setRules] = useState<PricingRule[]>([]);
  const [loading, setLoading] = useState(false);
  const [showDialog, setShowDialog] = useState(false);
  const [editingRule, setEditingRule] = useState<PricingRule | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{
    show: boolean;
    rule: PricingRule | null;
  }>({ show: false, rule: null });

  const [form, setForm] = useState({
    name: '',
    description: '',
    conditions: [] as Condition[],
    actions: [] as Action[],
    is_active: true
  });

  const loadRules = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/pricing/rules');
      setRules(response.data.rules || []);
    } catch (error) {
      console.error('Failed to load rules:', error);
      toast({
        title: 'Fehler',
        description: 'Preisregeln konnten nicht geladen werden',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    loadRules();
  }, [loadRules]);

  const handleEdit = (rule: PricingRule | null) => {
    if (rule) {
      setEditingRule(rule);
      setForm({
        name: rule.name,
        description: rule.description || '',
        conditions: rule.conditions,
        actions: rule.actions,
        is_active: rule.is_active
      });
    } else {
      setEditingRule(null);
      setForm({
        name: '',
        description: '',
        conditions: [],
        actions: [],
        is_active: true
      });
    }
    setShowDialog(true);
  };

  const handleSave = async () => {
    if (!form.name) {
      toast({
        title: 'Validierungsfehler',
        description: 'Bitte geben Sie einen Namen ein',
        variant: 'destructive'
      });
      return;
    }

    setLoading(true);
    try {
      if (editingRule) {
        await api.put(`/pricing/rules/${editingRule.id}`, form);
        toast({
          title: 'Erfolgreich',
          description: 'Regel aktualisiert'
        });
      } else {
        await api.post('/pricing/rules', form);
        toast({
          title: 'Erfolgreich',
          description: 'Regel erstellt'
        });
      }
      setShowDialog(false);
      loadRules();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: 'Regel konnte nicht gespeichert werden',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteConfirm.rule) return;

    try {
      await api.delete(`/pricing/rules/${deleteConfirm.rule.id}`);
      toast({
        title: 'Erfolgreich',
        description: 'Regel gelöscht'
      });
      setDeleteConfirm({ show: false, rule: null });
      loadRules();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: 'Regel konnte nicht gelöscht werden',
        variant: 'destructive'
      });
    }
  };

  const handlePriorityChange = async (ruleId: number, direction: 'up' | 'down') => {
    try {
      await api.post(`/pricing/rules/${ruleId}/priority`, { direction });
      loadRules();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: 'Priorität konnte nicht geändert werden',
        variant: 'destructive'
      });
    }
  };

  const addCondition = () => {
    setForm({
      ...form,
      conditions: [...form.conditions, { field: 'module_count', operator: 'equals', value: '' }]
    });
  };

  const updateCondition = (index: number, updates: Partial<Condition>) => {
    const updatedConditions = [...form.conditions];
    updatedConditions[index] = { ...updatedConditions[index], ...updates };
    setForm({ ...form, conditions: updatedConditions });
  };

  const removeCondition = (index: number) => {
    setForm({
      ...form,
      conditions: form.conditions.filter((_, i) => i !== index)
    });
  };

  const addAction = () => {
    setForm({
      ...form,
      actions: [...form.actions, { type: 'discount', value: 0, is_percentage: true }]
    });
  };

  const updateAction = (index: number, updates: Partial<Action>) => {
    const updatedActions = [...form.actions];
    updatedActions[index] = { ...updatedActions[index], ...updates };
    setForm({ ...form, actions: updatedActions });
  };

  const removeAction = (index: number) => {
    setForm({
      ...form,
      actions: form.actions.filter((_, i) => i !== index)
    });
  };

  const formatCondition = (condition: Condition) => {
    const field = CONDITION_FIELDS.find(f => f.value === condition.field)?.label || condition.field;
    const operator = OPERATORS.find(o => o.value === condition.operator)?.label || condition.operator;
    return `${field} ${operator} ${condition.value}`;
  };

  const formatAction = (action: Action) => {
    const type = ACTION_TYPES.find(t => t.value === action.type)?.label || action.type;
    const value = action.is_percentage ? `${action.value}%` : `${action.value} €`;
    return `${type}: ${value}`;
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <Zap className="h-6 w-6" />
            Preisregeln verwalten
          </CardTitle>
          <CardDescription>
            Erstellen Sie Bedingungen für automatische Preisanpassungen
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-end">
            <Button onClick={() => handleEdit(null)} className="gap-2">
              <Plus className="h-4 w-4" />
              Neue Regel
            </Button>
          </div>

          <ScrollArea className="h-[600px]">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">Prio.</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Bedingungen</TableHead>
                  <TableHead>Aktionen</TableHead>
                  <TableHead className="text-center">Status</TableHead>
                  <TableHead className="text-right">Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rules.map((rule, index) => (
                  <TableRow key={rule.id}>
                    <TableCell>
                      <div className="flex flex-col gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handlePriorityChange(rule.id, 'up')}
                          disabled={index === 0}
                        >
                          <ArrowUp className="h-3 w-3" />
                        </Button>
                        <span className="text-xs text-center">{rule.priority}</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handlePriorityChange(rule.id, 'down')}
                          disabled={index === rules.length - 1}
                        >
                          <ArrowDown className="h-3 w-3" />
                        </Button>
                      </div>
                    </TableCell>
                    <TableCell className="font-medium">{rule.name}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {rule.conditions.map((cond, i) => (
                          <Badge key={i} variant="outline">{formatCondition(cond)}</Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {rule.actions.map((action, i) => (
                          <Badge key={i} variant="secondary">{formatAction(action)}</Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell className="text-center">
                      <Badge variant={rule.is_active ? 'default' : 'secondary'}>
                        {rule.is_active ? 'Aktiv' : 'Inaktiv'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="sm" onClick={() => handleEdit(rule)}>
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDeleteConfirm({ show: true, rule })}
                        >
                          <Trash2 className="h-4 w-4 text-red-600" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
                {rules.length === 0 && !loading && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-12 text-muted-foreground">
                      Keine Preisregeln vorhanden
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingRule ? 'Regel bearbeiten' : 'Neue Regel erstellen'}
            </DialogTitle>
            <DialogDescription>
              Definieren Sie Bedingungen und Aktionen für die Preisregel
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            <div className="grid grid-cols-1 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="z.B. Großkunden-Rabatt"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Beschreibung</Label>
                <Input
                  id="description"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  placeholder="Optional: Beschreiben Sie die Regel"
                />
              </div>
            </div>

            <Separator />

            {/* Conditions */}
            <Accordion type="single" defaultValue="conditions" collapsible>
              <AccordionItem value="conditions">
                <AccordionTrigger>Bedingungen ({form.conditions.length})</AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-4">
                    {form.conditions.map((condition, index) => (
                      <Card key={index}>
                        <CardContent className="pt-4">
                          <div className="grid grid-cols-3 gap-4">
                            <Select
                              value={condition.field}
                              onValueChange={(value) => updateCondition(index, { field: value })}
                            >
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {CONDITION_FIELDS.map(field => (
                                  <SelectItem key={field.value} value={field.value}>
                                    {field.label}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>

                            <Select
                              value={condition.operator}
                              onValueChange={(value) => updateCondition(index, { operator: value })}
                            >
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {OPERATORS.map(op => (
                                  <SelectItem key={op.value} value={op.value}>
                                    {op.label}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>

                            <div className="flex gap-2">
                              <Input
                                value={condition.value}
                                onChange={(e) => updateCondition(index, { value: e.target.value })}
                                placeholder="Wert"
                              />
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeCondition(index)}
                              >
                                <Trash2 className="h-4 w-4 text-red-600" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                    <Button variant="outline" onClick={addCondition} className="w-full">
                      <Plus className="h-4 w-4 mr-2" />
                      Bedingung hinzufügen
                    </Button>
                  </div>
                </AccordionContent>
              </AccordionItem>

              {/* Actions */}
              <AccordionItem value="actions">
                <AccordionTrigger>Aktionen ({form.actions.length})</AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-4">
                    {form.actions.map((action, index) => (
                      <Card key={index}>
                        <CardContent className="pt-4">
                          <div className="grid grid-cols-4 gap-4">
                            <Select
                              value={action.type}
                              onValueChange={(value) => updateAction(index, { type: value as Action['type'] })}
                            >
                              <SelectTrigger>
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {ACTION_TYPES.map(type => (
                                  <SelectItem key={type.value} value={type.value}>
                                    {type.label}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>

                            <Input
                              type="number"
                              value={action.value}
                              onChange={(e) => updateAction(index, { value: parseFloat(e.target.value) || 0 })}
                              placeholder="Wert"
                              step={0.01}
                            />

                            <div className="flex items-center space-x-2">
                              <Checkbox
                                id={`percentage-${index}`}
                                checked={action.is_percentage}
                                onCheckedChange={(checked) => updateAction(index, { is_percentage: !!checked })}
                              />
                              <Label htmlFor={`percentage-${index}`}>Prozent</Label>
                            </div>

                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeAction(index)}
                            >
                              <Trash2 className="h-4 w-4 text-red-600" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                    <Button variant="outline" onClick={addAction} className="w-full">
                      <Plus className="h-4 w-4 mr-2" />
                      Aktion hinzufügen
                    </Button>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="isActive"
                checked={form.is_active}
                onCheckedChange={(checked) => setForm({ ...form, is_active: !!checked })}
              />
              <Label htmlFor="isActive" className="cursor-pointer">
                Regel ist aktiv
              </Label>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDialog(false)}>
              <X className="h-4 w-4 mr-2" />
              Abbrechen
            </Button>
            <Button onClick={handleSave} disabled={loading}>
              <Save className="h-4 w-4 mr-2" />
              {loading ? 'Wird gespeichert...' : 'Speichern'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <AlertDialog open={deleteConfirm.show} onOpenChange={(open) => !open && setDeleteConfirm({ show: false, rule: null })}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Regel löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              Möchten Sie die Regel "{deleteConfirm.rule?.name}" wirklich löschen? 
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

export default PricingRulesModern;
