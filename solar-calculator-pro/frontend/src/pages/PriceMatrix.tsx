/**
 * Price Matrix Page
 * 
 * Price matrix management and calculations
 * Task 37: Price Matrix Management - Complete implementation
 */

import React, { useState } from 'react';
import { Card } from 'primereact/card';
import { TabView, TabPanel } from 'primereact/tabview';
import MatrixUpload from '../components/pricing/MatrixUpload';
import MatrixList from '../components/pricing/MatrixList';
import MatrixPreview from '../components/pricing/MatrixPreview';
import MatrixVersionHistory from '../components/pricing/MatrixVersionHistory';
import PriceCalculator from '../components/pricing/PriceCalculator';
import './PriceMatrix.css';

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

const PriceMatrix: React.FC = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [selectedMatrix, setSelectedMatrix] = useState<Matrix | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadSuccess = (data: any) => {
    console.log('Matrix uploaded successfully:', data);
    // Refresh the matrix list
    setRefreshKey(prev => prev + 1);
    // Switch to management tab after successful upload
    setActiveIndex(1);
  };

  const handleUploadError = (error: string) => {
    console.error('Matrix upload failed:', error);
  };

  const handleMatrixSelect = (matrix: Matrix) => {
    setSelectedMatrix(matrix);
    // Switch to preview tab
    setActiveIndex(2);
  };

  const handleMatrixActivate = (matrix: Matrix) => {
    setSelectedMatrix(matrix);
    setRefreshKey(prev => prev + 1);
  };

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="price-matrix-page">
      <div className="page-header">
        <h1>💰 Preismatrix-Verwaltung</h1>
        <p className="page-description">
          Verwalten Sie Ihre Preismatrizen für PV-Anlagen und Batteriespeicher
        </p>
      </div>

      <TabView activeIndex={activeIndex} onTabChange={(e) => setActiveIndex(e.index)}>
        <TabPanel header="📤 Upload" leftIcon="pi pi-upload">
          <MatrixUpload 
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </TabPanel>

        <TabPanel header="📊 Verwaltung" leftIcon="pi pi-table">
          <MatrixList
            key={refreshKey}
            onMatrixSelect={handleMatrixSelect}
            onMatrixActivate={handleMatrixActivate}
            onRefresh={handleRefresh}
          />
        </TabPanel>

        <TabPanel header="🔍 Vorschau" leftIcon="pi pi-eye">
          {selectedMatrix ? (
            <MatrixPreview
              matrixId={selectedMatrix.id}
              onClose={() => setSelectedMatrix(null)}
            />
          ) : (
            <Card title="Matrix-Vorschau">
              <div className="empty-preview">
                <i className="pi pi-inbox" style={{ fontSize: '3rem', color: 'var(--text-color-secondary)' }}></i>
                <p>Keine Matrix ausgewählt</p>
                <p className="hint">Wählen Sie eine Matrix aus der Verwaltung aus, um eine Vorschau anzuzeigen.</p>
              </div>
            </Card>
          )}
        </TabPanel>

        <TabPanel header="📜 Versionshistorie" leftIcon="pi pi-history">
          <MatrixVersionHistory matrixId={selectedMatrix?.id} />
        </TabPanel>

        <TabPanel header="🧮 Berechnung" leftIcon="pi pi-calculator">
          <PriceCalculator />
        </TabPanel>
      </TabView>
    </div>
  );
};

export default PriceMatrix;
