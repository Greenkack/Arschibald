/**
 * Modern Solar Projects Page with shadcn/ui
 * 
 * Project list with advanced table, search, filtering, and CRUD operations
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { FolderOpen, Plus, Eye, Pencil, Trash2, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import api from '../services/api';

interface Project {
  id: number;
  name: string;
  customer_id: number;
  project_type: string;
  status: string;
  data: Record<string, unknown>;
  dynamic_key: string;
  created_at: string;
  updated_at: string;
}

interface ProjectListResponse {
  items: Project[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const SolarProjectsModern: React.FC = () => {
  const navigate = useNavigate();
  
  // State
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalRecords, setTotalRecords] = useState(0);
  const [page, setPage] = useState(1);
  const pageSize = 20;
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [projectTypeFilter, setProjectTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  
  // Dialog state
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectType, setNewProjectType] = useState('solar');
  const newCustomerId = 1;
  
  // Delete confirmation
  const [deleteProject, setDeleteProject] = useState<Project | null>(null);
  
  // Load projects
  const loadProjects = async () => {
    setLoading(true);
    
    try {
      const params: Record<string, string | number> = {
        page,
        page_size: pageSize
      };
      
      if (searchTerm) params.search = searchTerm;
      if (projectTypeFilter !== 'all') params.project_type = projectTypeFilter;
      if (statusFilter !== 'all') params.status = statusFilter;
      
      const response = await api.get<ProjectListResponse>('/api/v1/solar/projects', { params });
      
      setProjects(response.data.items);
      setTotalRecords(response.data.total);
    } catch (error) {
      console.error('Failed to load projects:', error);
      const errorMessage = error && typeof error === 'object' && 'response' in error 
        ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail 
        : undefined;
      toast.error(errorMessage || 'Projekte konnten nicht geladen werden');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    loadProjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, searchTerm, projectTypeFilter, statusFilter]);
  
  // Create project
  const handleCreateProject = async () => {
    if (!newProjectName.trim()) {
      toast.warning('Bitte geben Sie einen Projektnamen ein');
      return;
    }
    
    try {
      await api.post('/api/v1/solar/projects', {
        name: newProjectName,
        customer_id: newCustomerId,
        project_type: newProjectType,
        data: {}
      });
      
      toast.success('Projekt wurde erfolgreich erstellt');
      setShowCreateDialog(false);
      setNewProjectName('');
      setNewProjectType('solar');
      loadProjects();
    } catch (error) {
      console.error('Failed to create project:', error);
      const errorMessage = error && typeof error === 'object' && 'response' in error 
        ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail 
        : undefined;
      toast.error(errorMessage || 'Projekt konnte nicht erstellt werden');
    }
  };
  
  // Delete project
  const handleDeleteConfirm = async () => {
    if (!deleteProject) return;
    
    try {
      await api.delete(`/api/v1/solar/projects/${deleteProject.id}`);
      toast.success('Projekt wurde gelöscht');
      setDeleteProject(null);
      loadProjects();
    } catch (error) {
      console.error('Failed to delete project:', error);
      const errorMessage = error && typeof error === 'object' && 'response' in error 
        ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail 
        : undefined;
      toast.error(errorMessage || 'Projekt konnte nicht gelöscht werden');
    }
  };
  
  // Get status badge variant
  const getStatusVariant = (status: string): "default" | "secondary" | "destructive" | "outline" => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      draft: 'secondary',
      active: 'default',
      completed: 'outline',
      archived: 'destructive'
    };
    return variants[status] || 'default';
  };
  
  // Get status label
  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      draft: 'Entwurf',
      active: 'Aktiv',
      completed: 'Abgeschlossen',
      archived: 'Archiviert'
    };
    return labels[status] || status;
  };
  
  // Get project type label
  const getProjectTypeLabel = (type: string): string => {
    const labels: Record<string, string> = {
      solar: 'Solar',
      heatpump: 'Wärmepumpe',
      combined: 'Kombiniert'
    };
    return labels[type] || type;
  };
  
  // Table columns
  const columns: ColumnDef<Project>[] = [
    {
      accessorKey: 'name',
      header: 'Projektname',
      cell: ({ row }) => (
        <div className="font-medium">{row.original.name}</div>
      ),
    },
    {
      accessorKey: 'project_type',
      header: 'Typ',
      cell: ({ row }) => getProjectTypeLabel(row.original.project_type),
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => (
        <Badge variant={getStatusVariant(row.original.status)}>
          {getStatusLabel(row.original.status)}
        </Badge>
      ),
    },
    {
      accessorKey: 'created_at',
      header: 'Erstellt am',
      cell: ({ row }) => new Date(row.original.created_at).toLocaleDateString('de-DE'),
    },
    {
      id: 'actions',
      header: 'Aktionen',
      cell: ({ row }) => (
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(`/solar-projects/${row.original.id}`)}
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(`/solar-projects/${row.original.id}/edit`)}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setDeleteProject(row.original)}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ),
    },
  ];
  
  const table = useReactTable({
    data: projects,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    manualPagination: true,
    pageCount: Math.ceil(totalRecords / pageSize),
  });
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-orange-500 to-amber-600 shadow-lg">
              <FolderOpen className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Solar Projekte</h1>
              <p className="text-muted-foreground">
                Verwalten Sie Ihre Solarprojekte
              </p>
            </div>
          </div>
          <Button onClick={() => setShowCreateDialog(true)} size="lg">
            <Plus className="mr-2 h-5 w-5" />
            Neues Projekt
          </Button>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-wrap gap-4">
              <div className="flex-1 min-w-[250px]">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Suchen..."
                    className="pl-9"
                  />
                </div>
              </div>
              
              <Select value={projectTypeFilter} onValueChange={setProjectTypeFilter}>
                <SelectTrigger className="w-[180px]">
                  <Filter className="mr-2 h-4 w-4" />
                  <SelectValue placeholder="Projekttyp" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle Typen</SelectItem>
                  <SelectItem value="solar">Solar</SelectItem>
                  <SelectItem value="heatpump">Wärmepumpe</SelectItem>
                  <SelectItem value="combined">Kombiniert</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[180px]">
                  <Filter className="mr-2 h-4 w-4" />
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle Status</SelectItem>
                  <SelectItem value="draft">Entwurf</SelectItem>
                  <SelectItem value="active">Aktiv</SelectItem>
                  <SelectItem value="completed">Abgeschlossen</SelectItem>
                  <SelectItem value="archived">Archiviert</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Table */}
        <Card>
          <CardContent className="p-6">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  {table.getHeaderGroups().map((headerGroup) => (
                    <TableRow key={headerGroup.id}>
                      {headerGroup.headers.map((header) => (
                        <TableHead key={header.id}>
                          {header.isPlaceholder
                            ? null
                            : flexRender(
                                header.column.columnDef.header,
                                header.getContext()
                              )}
                        </TableHead>
                      ))}
                    </TableRow>
                  ))}
                </TableHeader>
                <TableBody>
                  {loading ? (
                    <TableRow>
                      <TableCell colSpan={columns.length} className="h-24 text-center">
                        Lädt...
                      </TableCell>
                    </TableRow>
                  ) : table.getRowModel().rows?.length ? (
                    table.getRowModel().rows.map((row) => (
                      <TableRow key={row.id}>
                        {row.getVisibleCells().map((cell) => (
                          <TableCell key={cell.id}>
                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={columns.length} className="h-24 text-center">
                        Keine Projekte gefunden
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-muted-foreground">
                {totalRecords > 0
                  ? `${(page - 1) * pageSize + 1} bis ${Math.min(page * pageSize, totalRecords)} von ${totalRecords} Projekten`
                  : 'Keine Projekte'}
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  Zurück
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => p + 1)}
                  disabled={page >= Math.ceil(totalRecords / pageSize)}
                >
                  Weiter
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Create Dialog */}
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Neues Projekt erstellen</DialogTitle>
              <DialogDescription>
                Erstellen Sie ein neues Solarprojekt
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="projectName">Projektname *</Label>
                <Input
                  id="projectName"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="Mein Solar Projekt"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="projectType">Projekttyp</Label>
                <Select value={newProjectType} onValueChange={setNewProjectType}>
                  <SelectTrigger id="projectType">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="solar">Solar</SelectItem>
                    <SelectItem value="heatpump">Wärmepumpe</SelectItem>
                    <SelectItem value="combined">Kombiniert</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Abbrechen
              </Button>
              <Button onClick={handleCreateProject}>
                Erstellen
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation */}
        <AlertDialog open={!!deleteProject} onOpenChange={() => setDeleteProject(null)}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Löschen bestätigen</AlertDialogTitle>
              <AlertDialogDescription>
                Möchten Sie das Projekt "{deleteProject?.name}" wirklich löschen? 
                Diese Aktion kann nicht rückgängig gemacht werden.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Abbrechen</AlertDialogCancel>
              <AlertDialogAction onClick={handleDeleteConfirm} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                Ja, löschen
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
};

export default SolarProjectsModern;
