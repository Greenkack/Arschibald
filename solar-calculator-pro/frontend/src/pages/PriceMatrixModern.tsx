/**
 * Modern Price Matrix Page with shadcn/ui
 * 
 * Price matrix management and calculations
 */

import React, { useState } from 'react';
import { Upload, Table, Eye, History, Calculator } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import MatrixUpload from '../components/pricing/MatrixUpload';
import MatrixList from '../components/pricing/MatrixList';
import MatrixPreview from '../components/pricing/MatrixPreview';
import MatrixVersionHistory from '../components/pricing/MatrixVersionHistory';
import PriceCalculator from '../components/pricing/PriceCalculator';

interface Matrix {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  pricing_mode: string;
  include_accessories: boolean;
  include_misc: boolean;
  created_at: string;
  updated_at: string;
}

const PriceMatrixModern: React.FC = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [selectedMatrix, setSelectedMatrix] = useState<Matrix | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadSuccess = (data: any) => {
    console.log('Matrix uploaded successfully:', data);
    setRefreshKey(prev => prev + 1);
    setActiveTab('management');
  };

  const handleUploadError = (error: string) => {
    console.error('Matrix upload failed:', error);
  };

  const handleMatrixSelect = (matrix: Matrix) => {
    setSelectedMatrix(matrix);
    setActiveTab('preview');
  };

  const handleMatrixActivate = (matrix: Matrix) => {
    setSelectedMatrix(matrix);
    setRefreshKey(prev => prev + 1);
  };

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 shadow-lg">
              <Table className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Preismatrix-Verwaltung</h1>
              <p className="text-muted-foreground">
                Verwalten Sie Ihre Preismatrizen für PV-Anlagen und Batteriespeicher
              </p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <Card>
          <CardContent className="p-6">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="upload" className="gap-2">
                  <Upload className="h-4 w-4" />
                  Upload
                </TabsTrigger>
                <TabsTrigger value="management" className="gap-2">
                  <Table className="h-4 w-4" />
                  Verwaltung
                </TabsTrigger>
                <TabsTrigger value="preview" className="gap-2">
                  <Eye className="h-4 w-4" />
                  Vorschau
                </TabsTrigger>
                <TabsTrigger value="history" className="gap-2">
                  <History className="h-4 w-4" />
                  Versionshistorie
                </TabsTrigger>
                <TabsTrigger value="calculator" className="gap-2">
                  <Calculator className="h-4 w-4" />
                  Berechnung
                </TabsTrigger>
              </TabsList>

              <TabsContent value="upload" className="space-y-4">
                <MatrixUpload 
                  onUploadSuccess={handleUploadSuccess}
                  onUploadError={handleUploadError}
                />
              </TabsContent>

              <TabsContent value="management" className="space-y-4">
                <MatrixList
                  key={refreshKey}
                  onMatrixSelect={handleMatrixSelect}
                  onMatrixActivate={handleMatrixActivate}
                  onRefresh={handleRefresh}
                />
              </TabsContent>

              <TabsContent value="preview" className="space-y-4">
                {selectedMatrix ? (
                  <MatrixPreview
                    matrixId={selectedMatrix.id}
                    onClose={() => setSelectedMatrix(null)}
                  />
                ) : (
                  <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed">
                    <div className="text-center">
                      <Eye className="mx-auto h-12 w-12 text-muted-foreground" />
                      <h3 className="mt-4 text-lg font-semibold">Keine Matrix ausgewählt</h3>
                      <p className="mt-2 text-sm text-muted-foreground">
                        Wählen Sie eine Matrix aus der Verwaltung aus, um eine Vorschau anzuzeigen.
                      </p>
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="history" className="space-y-4">
                <MatrixVersionHistory matrixId={selectedMatrix?.id} />
              </TabsContent>

              <TabsContent value="calculator" className="space-y-4">
                <PriceCalculator />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PriceMatrixModern;
