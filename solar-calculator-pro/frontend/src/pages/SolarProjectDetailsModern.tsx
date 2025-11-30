/**
 * Modern Solar Project Details Page with shadcn/ui
 * 
 * Detailed view with project info, calculation results, and 3D visualization
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Pencil, Trash2, FileText, Box, Info, BarChart3, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
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
import { toast } from 'sonner';
import SolarCalculationResults from '../components/solar/SolarCalculationResults';
import { Viewer3D } from '../components/3d/Viewer3D';
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

const SolarProjectDetailsModern: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('info');
  const [generatingPDF, setGeneratingPDF] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  
  useEffect(() => {
    loadProject();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);
  
  const loadProject = async () => {
    if (!projectId) return;
    
    setLoading(true);
    
    try {
      const response = await api.get<Project>(`/api/v1/solar/projects/${projectId}`);
      setProject(response.data);
    } catch (error) {
      console.error('Failed to load project:', error);
      const err = error as { response?: { status?: number; data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || 'Projekt konnte nicht geladen werden');
      
      if (err.response?.status === 404) {
        setTimeout(() => navigate('/solar-projects'), 2000);
      }
    } finally {
      setLoading(false);
    }
  };
  
  const handleDelete = async () => {
    try {
      await api.delete(`/api/v1/solar/projects/${projectId}`);
      toast.success('Projekt wurde gelöscht');
      setTimeout(() => navigate('/solar-projects'), 1000);
    } catch (error) {
      console.error('Failed to delete project:', error);
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || 'Projekt konnte nicht gelöscht werden');
    }
  };
  
  const handleGeneratePDF = async () => {
    if (!project || !projectId) return;
    
    setGeneratingPDF(true);
    
    try {
      const response = await api.post(`/api/v1/pdf/generate`, {
        project_id: parseInt(projectId),
        template: 'solar_offer',
        options: {
          include_3d: true,
          include_charts: true,
          language: 'de'
        }
      }, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${project.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('PDF wurde erfolgreich erstellt und heruntergeladen');
    } catch (error) {
      console.error('Failed to generate PDF:', error);
      const err = error as { response?: { data?: { detail?: string } } };
      toast.error(err.response?.data?.detail || 'PDF konnte nicht erstellt werden');
    } finally {
      setGeneratingPDF(false);
    }
  };
  
  const getStatusVariant = (status: string): "default" | "secondary" | "destructive" | "outline" => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      draft: 'secondary',
      active: 'default',
      completed: 'outline',
      archived: 'destructive'
    };
    return variants[status] || 'default';
  };
  
  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      draft: 'Entwurf',
      active: 'Aktiv',
      completed: 'Abgeschlossen',
      archived: 'Archiviert'
    };
    return labels[status] || status;
  };
  
  const getProjectTypeLabel = (type: string): string => {
    const labels: Record<string, string> = {
      solar: 'Solar',
      heatpump: 'Wärmepumpe',
      combined: 'Kombiniert'
    };
    return labels[type] || type;
  };
  
  const hasCalculationResults = () => {
    return project?.data?.calculation_results && 
           Object.keys(project.data.calculation_results).length > 0;
  };
  
  const getCalculationResults = () => {
    if (!hasCalculationResults()) return null;
    return project?.data?.calculation_results || null;
  };
  
  const get3DVisualizationData = () => {
    const data = project?.data?.input_data || {};
    return {
      roofType: data.roof_type || 'flat',
      roofWidth: data.roof_width || 10,
      roofLength: data.roof_length || 10,
      roofHeight: data.roof_height || 3,
      roofAngle: data.roof_angle || 30,
      moduleCount: project?.data?.calculation_results?.system_sizing?.module_count || 20
    };
  };
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Projekt wird geladen...</p>
        </div>
      </div>
    );
  }
  
  if (!project) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="flex flex-col items-center py-12">
            <Info className="h-16 w-16 text-destructive mb-4" />
            <h2 className="text-2xl font-bold mb-2">Projekt nicht gefunden</h2>
            <Button onClick={() => navigate('/solar-projects')} className="mt-4">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Zurück zur Übersicht
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  const calculationResults = getCalculationResults();
  const visualizationData = get3DVisualizationData();
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate('/solar-projects')}
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-3xl font-bold tracking-tight">{project.name}</h1>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant={getStatusVariant(project.status)}>
                    {getStatusLabel(project.status)}
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    {getProjectTypeLabel(project.project_type)}
                  </span>
                  <span className="text-sm text-muted-foreground font-mono">
                    {project.dynamic_key}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex gap-2">
              {hasCalculationResults() && (
                <>
                  <Button
                    variant="outline"
                    onClick={() => setActiveTab('3d')}
                  >
                    <Box className="mr-2 h-4 w-4" />
                    3D-Ansicht
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleGeneratePDF}
                    disabled={generatingPDF}
                  >
                    {generatingPDF ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <FileText className="mr-2 h-4 w-4" />
                    )}
                    PDF erstellen
                  </Button>
                </>
              )}
              <Button
                variant="outline"
                onClick={() => navigate(`/solar-projects/${projectId}/edit`)}
              >
                <Pencil className="mr-2 h-4 w-4" />
                Bearbeiten
              </Button>
              <Button
                variant="destructive"
                onClick={() => setShowDeleteDialog(true)}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Löschen
              </Button>
            </div>
          </div>
        </div>

        {/* Content */}
        <Card>
          <CardContent className="p-6">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="info" className="gap-2">
                  <Info className="h-4 w-4" />
                  Projektinformationen
                </TabsTrigger>
                <TabsTrigger value="results" className="gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Berechnungsergebnisse
                </TabsTrigger>
                <TabsTrigger value="3d" className="gap-2">
                  <Box className="h-4 w-4" />
                  3D-Visualisierung
                </TabsTrigger>
              </TabsList>

              <TabsContent value="info" className="space-y-6 mt-6">
                <div className="grid gap-6 md:grid-cols-2">
                  <Card>
                    <CardHeader>
                      <CardTitle>Projektdetails</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div className="font-medium">Projekt-ID:</div>
                        <div>{project.id}</div>
                        
                        <div className="font-medium">Projekttyp:</div>
                        <div>{getProjectTypeLabel(project.project_type)}</div>
                        
                        <div className="font-medium">Status:</div>
                        <div>
                          <Badge variant={getStatusVariant(project.status)}>
                            {getStatusLabel(project.status)}
                          </Badge>
                        </div>
                        
                        <div className="font-medium">Kunden-ID:</div>
                        <div>{project.customer_id}</div>
                        
                        <div className="font-medium">Schlüssel:</div>
                        <div className="font-mono text-xs">{project.dynamic_key}</div>
                        
                        <div className="font-medium">Erstellt am:</div>
                        <div>{new Date(project.created_at).toLocaleString('de-DE')}</div>
                        
                        {project.updated_at && (
                          <>
                            <div className="font-medium">Aktualisiert:</div>
                            <div>{new Date(project.updated_at).toLocaleString('de-DE')}</div>
                          </>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  {project.data?.input_data && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Eingabedaten</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          {project.data.input_data.roof_area && (
                            <>
                              <div className="font-medium">Dachfläche:</div>
                              <div>{project.data.input_data.roof_area} m²</div>
                            </>
                          )}
                          {project.data.input_data.roof_type && (
                            <>
                              <div className="font-medium">Dachtyp:</div>
                              <div>{project.data.input_data.roof_type}</div>
                            </>
                          )}
                          {project.data.input_data.roof_angle && (
                            <>
                              <div className="font-medium">Dachneigung:</div>
                              <div>{project.data.input_data.roof_angle}°</div>
                            </>
                          )}
                          {project.data.input_data.orientation && (
                            <>
                              <div className="font-medium">Ausrichtung:</div>
                              <div>{project.data.input_data.orientation}</div>
                            </>
                          )}
                          {project.data.input_data.annual_consumption && (
                            <>
                              <div className="font-medium">Jahresverbrauch:</div>
                              <div>{project.data.input_data.annual_consumption} kWh</div>
                            </>
                          )}
                          {project.data.input_data.location && (
                            <>
                              <div className="font-medium">Standort:</div>
                              <div>{project.data.input_data.location}</div>
                            </>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="results" className="mt-6">
                {hasCalculationResults() && calculationResults ? (
                  <SolarCalculationResults
                    results={calculationResults}
                    onEdit={() => navigate('/solar-calculator', { state: { projectId, projectData: project?.data } })}
                    onGeneratePDF={handleGeneratePDF}
                    onView3D={() => setActiveTab('3d')}
                  />
                ) : (
                  <Card>
                    <CardContent className="flex flex-col items-center py-12">
                      <BarChart3 className="h-16 w-16 text-muted-foreground mb-4" />
                      <CardTitle className="mb-2">Keine Berechnungsergebnisse vorhanden</CardTitle>
                      <CardDescription className="text-center max-w-md mb-6">
                        Führen Sie eine Berechnung durch, um detaillierte Ergebnisse, Diagramme und 
                        Wirtschaftlichkeitsanalysen anzuzeigen.
                      </CardDescription>
                      <Button
                        onClick={() => navigate('/solar-calculator', { state: { projectId } })}
                        size="lg"
                      >
                        Neue Berechnung starten
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="3d" className="mt-6">
                {hasCalculationResults() ? (
                  <div className="space-y-6">
                    <div className="aspect-video bg-slate-100 dark:bg-slate-900 rounded-lg overflow-hidden">
                      <Viewer3D
                        roofType={visualizationData.roofType as 'flat' | 'gable' | 'hip'}
                        roofWidth={visualizationData.roofWidth}
                        roofLength={visualizationData.roofLength}
                        roofHeight={visualizationData.roofHeight}
                        roofAngle={visualizationData.roofAngle}
                        moduleCount={visualizationData.moduleCount}
                      />
                    </div>
                    
                    <Card>
                      <CardHeader>
                        <CardTitle>Visualisierungsdetails</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                          <div>
                            <div className="font-medium">Dachtyp</div>
                            <div>{visualizationData.roofType}</div>
                          </div>
                          <div>
                            <div className="font-medium">Dachbreite</div>
                            <div>{visualizationData.roofWidth} m</div>
                          </div>
                          <div>
                            <div className="font-medium">Dachlänge</div>
                            <div>{visualizationData.roofLength} m</div>
                          </div>
                          <div>
                            <div className="font-medium">Dachhöhe</div>
                            <div>{visualizationData.roofHeight} m</div>
                          </div>
                          <div>
                            <div className="font-medium">Dachneigung</div>
                            <div>{visualizationData.roofAngle}°</div>
                          </div>
                          <div>
                            <div className="font-medium">Modulanzahl</div>
                            <div>{visualizationData.moduleCount} Module</div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  <Card>
                    <CardContent className="flex flex-col items-center py-12">
                      <Box className="h-16 w-16 text-muted-foreground mb-4" />
                      <CardTitle className="mb-2">Keine 3D-Visualisierung verfügbar</CardTitle>
                      <CardDescription className="text-center max-w-md mb-6">
                        Führen Sie zuerst eine Berechnung durch, um die 3D-Visualisierung 
                        Ihrer PV-Anlage anzuzeigen.
                      </CardDescription>
                      <Button
                        onClick={() => navigate('/solar-calculator', { state: { projectId } })}
                        size="lg"
                      >
                        Berechnung starten
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Delete Confirmation */}
        <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Löschen bestätigen</AlertDialogTitle>
              <AlertDialogDescription>
                Möchten Sie das Projekt "{project.name}" wirklich löschen? 
                Diese Aktion kann nicht rückgängig gemacht werden.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Abbrechen</AlertDialogCancel>
              <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                Ja, löschen
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
};

export default SolarProjectDetailsModern;
