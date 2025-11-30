/**
 * Product Attribute Manager (Modern - shadcn/ui)
 * 
 * Complete product attribute management with:
 * - Attribute CRUD operations
 * - Attribute groups management
 * - Attribute templates
 * - Type validation (text, number, boolean, select, multiselect, date)
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
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
import { Plus, Pencil, Trash2, Save, X, List, Folder, Copy, Check } from 'lucide-react';
import api from '../../services/api';

interface ProductAttribute {
  id: number;
  name: string;
  label: string;
  type: 'text' | 'number' | 'boolean' | 'select' | 'multiselect' | 'date';
  required: boolean;
  default_value?: any;
  options?: string[];
  validation_rules?: Record<string, any>;
  group_id?: number;
  group_name?: string;
  description?: string;
  unit?: string;
  order: number;
  is_custom: boolean;
  created_at?: string;
  updated_at?: string;
}

interface AttributeGroup {
  id: number;
  name: string;
  label: string;
  description?: string;
  order: number;
  is_collapsible: boolean;
  is_expanded_by_default: boolean;
  created_at?: string;
  updated_at?: string;
}

interface AttributeTemplate {
  id: number;
  name: string;
  description?: string;
  category: string;
  attributes: number[];
  created_at?: string;
  updated_at?: string;
}

const ATTRIBUTE_TYPES = [
  { value: 'text', label: 'Text' },
  { value: 'number', label: 'Zahl' },
  { value: 'boolean', label: 'Ja/Nein' },
  { value: 'select', label: 'Auswahl (Einfach)' },
  { value: 'multiselect', label: 'Auswahl (Mehrfach)' },
  { value: 'date', label: 'Datum' }
];

const ProductAttributeManagerModern: React.FC = () => {
  const { toast } = useToast();
  const [attributes, setAttributes] = useState<ProductAttribute[]>([]);
  const [groups, setGroups] = useState<AttributeGroup[]>([]);
  const [templates, setTemplates] = useState<AttributeTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('attributes');

  // Attribute dialog
  const [showAttributeDialog, setShowAttributeDialog] = useState(false);
  const [editingAttribute, setEditingAttribute] = useState<ProductAttribute | null>(null);
  const [attributeForm, setAttributeForm] = useState({
    name: '',
    label: '',
    type: 'text' as const,
    required: false,
    description: '',
    unit: '',
    group_id: null as number | null,
    order: 0,
    options: [] as string[]
  });

  // Group dialog
  const [showGroupDialog, setShowGroupDialog] = useState(false);
  const [editingGroup, setEditingGroup] = useState<AttributeGroup | null>(null);
  const [groupForm, setGroupForm] = useState({
    name: '',
    label: '',
    description: '',
    order: 0,
    is_collapsible: true,
    is_expanded_by_default: true
  });

  // Template dialog
  const [showTemplateDialog, setShowTemplateDialog] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<AttributeTemplate | null>(null);
  const [templateForm, setTemplateForm] = useState({
    name: '',
    description: '',
    category: '',
    attributes: [] as number[]
  });

  // Delete confirmation
  const [deleteConfirm, setDeleteConfirm] = useState<{
    show: boolean;
    type: 'attribute' | 'group' | 'template';
    item: any;
  }>({ show: false, type: 'attribute', item: null });

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([loadAttributes(), loadGroups(), loadTemplates()]);
    } finally {
      setLoading(false);
    }
  };

  const loadAttributes = async () => {
    try {
      const response = await api.get('/products/attributes');
      setAttributes(response.data.attributes || []);
    } catch (error) {
      console.error('Failed to load attributes:', error);
      toast({
        title: 'Fehler',
        description: 'Attribute konnten nicht geladen werden',
        variant: 'destructive'
      });
    }
  };

  const loadGroups = async () => {
    try {
      const response = await api.get('/products/attribute-groups');
      setGroups(response.data.groups || []);
    } catch (error) {
      console.error('Failed to load groups:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await api.get('/products/attribute-templates');
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const handleSaveAttribute = async () => {
    try {
      if (editingAttribute) {
        await api.put(`/products/attributes/${editingAttribute.id}`, attributeForm);
        toast({
          title: 'Erfolgreich',
          description: 'Attribut aktualisiert'
        });
      } else {
        await api.post('/products/attributes', attributeForm);
        toast({
          title: 'Erfolgreich',
          description: 'Attribut erstellt'
        });
      }
      setShowAttributeDialog(false);
      resetAttributeForm();
      loadAttributes();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: 'Attribut konnte nicht gespeichert werden',
        variant: 'destructive'
      });
    }
  };

  const handleSaveGroup = async () => {
    try {
      if (editingGroup) {
        await api.put(`/products/attribute-groups/${editingGroup.id}`, groupForm);
        toast({
          title: 'Erfolgreich',
          description: 'Gruppe aktualisiert'
        });
      } else {
        await api.post('/products/attribute-groups', groupForm);
        toast({
          title: 'Erfolgreich',
          description: 'Gruppe erstellt'
        });
      }
      setShowGroupDialog(false);
      resetGroupForm();
      loadGroups();
      loadAttributes();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: 'Gruppe konnte nicht gespeichert werden',
        variant: 'destructive'
      });
    }
  };

  const handleSaveTemplate = async () => {
    try {
      if (editingTemplate) {
        await api.put(`/products/attribute-templates/${editingTemplate.id}`, templateForm);
        toast({
          title: 'Erfolgreich',
          description: 'Template aktualisiert'
        });
      } else {
        await api.post('/products/attribute-templates', templateForm);
        toast({
          title: 'Erfolgreich',
          description: 'Template erstellt'
        });
      }
      setShowTemplateDialog(false);
      resetTemplateForm();
      loadTemplates();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: 'Template konnte nicht gespeichert werden',
        variant: 'destructive'
      });
    }
  };

  const handleDelete = async () => {
    const { type, item } = deleteConfirm;
    try {
      if (type === 'attribute') {
        await api.delete(`/products/attributes/${item.id}`);
        loadAttributes();
      } else if (type === 'group') {
        await api.delete(`/products/attribute-groups/${item.id}`);
        loadGroups();
        loadAttributes();
      } else if (type === 'template') {
        await api.delete(`/products/attribute-templates/${item.id}`);
        loadTemplates();
      }
      toast({
        title: 'Erfolgreich',
        description: `${type === 'attribute' ? 'Attribut' : type === 'group' ? 'Gruppe' : 'Template'} gelöscht`
      });
      setDeleteConfirm({ show: false, type: 'attribute', item: null });
    } catch (error) {
      toast({
        title: 'Fehler',
        description: 'Löschen fehlgeschlagen',
        variant: 'destructive'
      });
    }
  };

  const resetAttributeForm = () => {
    setAttributeForm({
      name: '',
      label: '',
      type: 'text',
      required: false,
      description: '',
      unit: '',
      group_id: null,
      order: 0,
      options: []
    });
    setEditingAttribute(null);
  };

  const resetGroupForm = () => {
    setGroupForm({
      name: '',
      label: '',
      description: '',
      order: 0,
      is_collapsible: true,
      is_expanded_by_default: true
    });
    setEditingGroup(null);
  };

  const resetTemplateForm = () => {
    setTemplateForm({
      name: '',
      description: '',
      category: '',
      attributes: []
    });
    setEditingTemplate(null);
  };

  const getTypeBadgeColor = (type: string) => {
    const colors: Record<string, string> = {
      text: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      number: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      boolean: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      select: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      multiselect: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      date: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Produktattribute verwalten</CardTitle>
          <CardDescription>
            Definieren und verwalten Sie Produktattribute, Gruppen und Templates
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="attributes" className="gap-2">
                <List className="h-4 w-4" />
                Attribute
              </TabsTrigger>
              <TabsTrigger value="groups" className="gap-2">
                <Folder className="h-4 w-4" />
                Gruppen
              </TabsTrigger>
              <TabsTrigger value="templates" className="gap-2">
                <Copy className="h-4 w-4" />
                Templates
              </TabsTrigger>
            </TabsList>

            {/* Attributes Tab */}
            <TabsContent value="attributes" className="space-y-4">
              <div className="flex justify-end">
                <Button
                  onClick={() => {
                    resetAttributeForm();
                    setShowAttributeDialog(true);
                  }}
                  className="gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Neues Attribut
                </Button>
              </div>

              <ScrollArea className="h-[600px]">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Label</TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Typ</TableHead>
                      <TableHead>Gruppe</TableHead>
                      <TableHead className="text-center">Pflicht</TableHead>
                      <TableHead className="text-center">Art</TableHead>
                      <TableHead className="text-right">Reihenfolge</TableHead>
                      <TableHead className="text-right">Aktionen</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {attributes.map((attr) => (
                      <TableRow key={attr.id}>
                        <TableCell className="font-medium">{attr.label}</TableCell>
                        <TableCell className="font-mono text-sm">{attr.name}</TableCell>
                        <TableCell>
                          <Badge className={getTypeBadgeColor(attr.type)}>
                            {attr.type}
                          </Badge>
                        </TableCell>
                        <TableCell>{attr.group_name || '-'}</TableCell>
                        <TableCell className="text-center">
                          {attr.required ? (
                            <Check className="h-4 w-4 text-green-600 inline" />
                          ) : (
                            <X className="h-4 w-4 text-gray-400 inline" />
                          )}
                        </TableCell>
                        <TableCell className="text-center">
                          <Badge variant={attr.is_custom ? 'default' : 'secondary'}>
                            {attr.is_custom ? 'Custom' : 'Standard'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">{attr.order}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setEditingAttribute(attr);
                                setAttributeForm({
                                  name: attr.name,
                                  label: attr.label,
                                  type: attr.type,
                                  required: attr.required,
                                  description: attr.description || '',
                                  unit: attr.unit || '',
                                  group_id: attr.group_id || null,
                                  order: attr.order,
                                  options: attr.options || []
                                });
                                setShowAttributeDialog(true);
                              }}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setDeleteConfirm({ show: true, type: 'attribute', item: attr })}
                            >
                              <Trash2 className="h-4 w-4 text-red-600" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </ScrollArea>
            </TabsContent>

            {/* Groups Tab */}
            <TabsContent value="groups" className="space-y-4">
              <div className="flex justify-end">
                <Button
                  onClick={() => {
                    resetGroupForm();
                    setShowGroupDialog(true);
                  }}
                  className="gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Neue Gruppe
                </Button>
              </div>

              <ScrollArea className="h-[600px]">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Label</TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Beschreibung</TableHead>
                      <TableHead className="text-right">Reihenfolge</TableHead>
                      <TableHead className="text-right">Aktionen</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {groups.map((group) => (
                      <TableRow key={group.id}>
                        <TableCell className="font-medium">{group.label}</TableCell>
                        <TableCell className="font-mono text-sm">{group.name}</TableCell>
                        <TableCell>{group.description || '-'}</TableCell>
                        <TableCell className="text-right">{group.order}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setEditingGroup(group);
                                setGroupForm({
                                  name: group.name,
                                  label: group.label,
                                  description: group.description || '',
                                  order: group.order,
                                  is_collapsible: group.is_collapsible,
                                  is_expanded_by_default: group.is_expanded_by_default
                                });
                                setShowGroupDialog(true);
                              }}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setDeleteConfirm({ show: true, type: 'group', item: group })}
                            >
                              <Trash2 className="h-4 w-4 text-red-600" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </ScrollArea>
            </TabsContent>

            {/* Templates Tab */}
            <TabsContent value="templates" className="space-y-4">
              <div className="flex justify-end">
                <Button
                  onClick={() => {
                    resetTemplateForm();
                    setShowTemplateDialog(true);
                  }}
                  className="gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Neues Template
                </Button>
              </div>

              <ScrollArea className="h-[600px]">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Kategorie</TableHead>
                      <TableHead>Beschreibung</TableHead>
                      <TableHead className="text-center">Attribute</TableHead>
                      <TableHead className="text-right">Aktionen</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {templates.map((template) => (
                      <TableRow key={template.id}>
                        <TableCell className="font-medium">{template.name}</TableCell>
                        <TableCell>{template.category}</TableCell>
                        <TableCell>{template.description || '-'}</TableCell>
                        <TableCell className="text-center">
                          <Badge>{template.attributes.length} Attribute</Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setEditingTemplate(template);
                                setTemplateForm({
                                  name: template.name,
                                  description: template.description || '',
                                  category: template.category,
                                  attributes: template.attributes
                                });
                                setShowTemplateDialog(true);
                              }}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setDeleteConfirm({ show: true, type: 'template', item: template })}
                            >
                              <Trash2 className="h-4 w-4 text-red-600" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Attribute Dialog */}
      <Dialog open={showAttributeDialog} onOpenChange={setShowAttributeDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingAttribute ? 'Attribut bearbeiten' : 'Neues Attribut'}
            </DialogTitle>
            <DialogDescription>
              Definieren Sie die Eigenschaften des Produktattributs
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="attr-name">Name (technisch) *</Label>
                <Input
                  id="attr-name"
                  value={attributeForm.name}
                  onChange={(e) => setAttributeForm({ ...attributeForm, name: e.target.value })}
                  placeholder="z.B. watt_peak"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="attr-label">Label (Anzeige) *</Label>
                <Input
                  id="attr-label"
                  value={attributeForm.label}
                  onChange={(e) => setAttributeForm({ ...attributeForm, label: e.target.value })}
                  placeholder="z.B. Nennleistung"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="attr-type">Typ *</Label>
                <Select
                  value={attributeForm.type}
                  onValueChange={(value: any) => setAttributeForm({ ...attributeForm, type: value })}
                >
                  <SelectTrigger id="attr-type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {ATTRIBUTE_TYPES.map(t => (
                      <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="attr-unit">Einheit</Label>
                <Input
                  id="attr-unit"
                  value={attributeForm.unit}
                  onChange={(e) => setAttributeForm({ ...attributeForm, unit: e.target.value })}
                  placeholder="z.B. Wp, kWh, mm"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="attr-group">Gruppe</Label>
                <Select
                  value={attributeForm.group_id?.toString() || ''}
                  onValueChange={(value) => setAttributeForm({ ...attributeForm, group_id: value ? parseInt(value) : null })}
                >
                  <SelectTrigger id="attr-group">
                    <SelectValue placeholder="Keine Gruppe" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Keine Gruppe</SelectItem>
                    {groups.map(g => (
                      <SelectItem key={g.id} value={g.id.toString()}>{g.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="attr-order">Reihenfolge</Label>
                <Input
                  id="attr-order"
                  type="number"
                  value={attributeForm.order}
                  onChange={(e) => setAttributeForm({ ...attributeForm, order: parseInt(e.target.value) || 0 })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="attr-description">Beschreibung</Label>
              <Textarea
                id="attr-description"
                value={attributeForm.description}
                onChange={(e) => setAttributeForm({ ...attributeForm, description: e.target.value })}
                rows={3}
              />
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="attr-required"
                checked={attributeForm.required}
                onCheckedChange={(checked) => setAttributeForm({ ...attributeForm, required: !!checked })}
              />
              <Label htmlFor="attr-required" className="cursor-pointer">
                Pflichtfeld
              </Label>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAttributeDialog(false)}>
              <X className="h-4 w-4 mr-2" />
              Abbrechen
            </Button>
            <Button onClick={handleSaveAttribute}>
              <Save className="h-4 w-4 mr-2" />
              Speichern
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Group Dialog */}
      <Dialog open={showGroupDialog} onOpenChange={setShowGroupDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingGroup ? 'Gruppe bearbeiten' : 'Neue Gruppe'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="group-name">Name (technisch) *</Label>
                <Input
                  id="group-name"
                  value={groupForm.name}
                  onChange={(e) => setGroupForm({ ...groupForm, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="group-label">Label (Anzeige) *</Label>
                <Input
                  id="group-label"
                  value={groupForm.label}
                  onChange={(e) => setGroupForm({ ...groupForm, label: e.target.value })}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="group-description">Beschreibung</Label>
              <Textarea
                id="group-description"
                value={groupForm.description}
                onChange={(e) => setGroupForm({ ...groupForm, description: e.target.value })}
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="group-order">Reihenfolge</Label>
              <Input
                id="group-order"
                type="number"
                value={groupForm.order}
                onChange={(e) => setGroupForm({ ...groupForm, order: parseInt(e.target.value) || 0 })}
              />
            </div>

            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="group-collapsible"
                  checked={groupForm.is_collapsible}
                  onCheckedChange={(checked) => setGroupForm({ ...groupForm, is_collapsible: !!checked })}
                />
                <Label htmlFor="group-collapsible" className="cursor-pointer">
                  Einklappbar
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="group-expanded"
                  checked={groupForm.is_expanded_by_default}
                  onCheckedChange={(checked) => setGroupForm({ ...groupForm, is_expanded_by_default: !!checked })}
                />
                <Label htmlFor="group-expanded" className="cursor-pointer">
                  Standardmäßig ausgeklappt
                </Label>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowGroupDialog(false)}>
              <X className="h-4 w-4 mr-2" />
              Abbrechen
            </Button>
            <Button onClick={handleSaveGroup}>
              <Save className="h-4 w-4 mr-2" />
              Speichern
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Template Dialog */}
      <Dialog open={showTemplateDialog} onOpenChange={setShowTemplateDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingTemplate ? 'Template bearbeiten' : 'Neues Template'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="template-name">Name *</Label>
                <Input
                  id="template-name"
                  value={templateForm.name}
                  onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="template-category">Kategorie *</Label>
                <Input
                  id="template-category"
                  value={templateForm.category}
                  onChange={(e) => setTemplateForm({ ...templateForm, category: e.target.value })}
                  placeholder="z.B. PV-Module, Wechselrichter"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="template-description">Beschreibung</Label>
              <Textarea
                id="template-description"
                value={templateForm.description}
                onChange={(e) => setTemplateForm({ ...templateForm, description: e.target.value })}
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label>Attribute ({templateForm.attributes.length} ausgewählt)</Label>
              <ScrollArea className="h-64 border rounded-md p-4">
                {attributes.map((attr) => (
                  <div key={attr.id} className="flex items-center space-x-2 py-2">
                    <Checkbox
                      id={`template-attr-${attr.id}`}
                      checked={templateForm.attributes.includes(attr.id)}
                      onCheckedChange={(checked) => {
                        setTemplateForm({
                          ...templateForm,
                          attributes: checked
                            ? [...templateForm.attributes, attr.id]
                            : templateForm.attributes.filter(id => id !== attr.id)
                        });
                      }}
                    />
                    <Label htmlFor={`template-attr-${attr.id}`} className="cursor-pointer flex-1">
                      {attr.label} <span className="text-sm text-muted-foreground">({attr.type})</span>
                    </Label>
                  </div>
                ))}
              </ScrollArea>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowTemplateDialog(false)}>
              <X className="h-4 w-4 mr-2" />
              Abbrechen
            </Button>
            <Button onClick={handleSaveTemplate}>
              <Save className="h-4 w-4 mr-2" />
              Speichern
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation */}
      <AlertDialog open={deleteConfirm.show} onOpenChange={(open) => !open && setDeleteConfirm({ ...deleteConfirm, show: false })}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Wirklich löschen?</AlertDialogTitle>
            <AlertDialogDescription>
              Möchten Sie {deleteConfirm.type === 'attribute' ? 'dieses Attribut' : deleteConfirm.type === 'group' ? 'diese Gruppe' : 'dieses Template'} 
              "{deleteConfirm.item?.name || deleteConfirm.item?.label}" wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.
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

export default ProductAttributeManagerModern;
