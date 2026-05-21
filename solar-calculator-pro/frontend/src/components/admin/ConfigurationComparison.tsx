/**
 * Configuration Comparison Component
 * 
 * Side-by-side comparison of multiple configurations
 */

import React, { useState } from 'react';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
import { Tag } from 'primereact/tag';
import { Divider } from 'primereact/divider';
import { Card } from 'primereact/card';

interface Configuration {
  id: number;
  key: string;
  value: string;
  value_type: string;
  description: string;
  category: string;
  namespace: string;
  version: number;
  is_active: boolean;
  is_system: boolean;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
}

interface ConfigurationComparisonProps {
  configurations: Configuration[];
  onClose: () => void;
}

const ConfigurationComparison: React.FC<ConfigurationComparisonProps> = ({
  configurations,
  onClose
}) => {
  const [comparisonData, setComparisonData] = useState<any[]>([]);
  
  // Prepare comparison data
  React.useEffect(() => {
    if (configurations.length === 0) return;
    
    const fields = [
      { key: 'key', label: 'Key' },
      { key: 'value', label: 'Value' },
      { key: 'value_type', label: 'Type' },
      { key: 'description', label: 'Description' },
      { key: 'category', label: 'Category' },
      { key: 'namespace', label: 'Namespace' },
      { key: 'version', label: 'Version' },
      { key: 'is_active', label: 'Active' },
      { key: 'is_system', label: 'System' },
      { key: 'created_at', label: 'Created' },
      { key: 'updated_at', label: 'Updated' },
      { key: 'created_by', label: 'Created By' },
      { key: 'updated_by', label: 'Updated By' }
    ];
    
    const data = fields.map(field => {
      const row: any = { field: field.label };
      
      configurations.forEach((config, index) => {
        const value = (config as any)[field.key];
        row[`config_${index}`] = value;
      });
      
      // Check if values differ
      const values = configurations.map((c: any) => c[field.key]);
      const allSame = values.every(v => v === values[0]);
      row.differs = !allSame;
      
      return row;
    });
    
    setComparisonData(data);
  }, [configurations]);
  
  // Render value with highlighting
  const renderValue = (value: any, differs: boolean) => {
    if (value === null || value === undefined) {
      return <span className="text-gray-400 italic">null</span>;
    }
    
    if (typeof value === 'boolean') {
      return (
        <Tag
          value={value ? 'Yes' : 'No'}
          severity={value ? 'success' : 'danger'}
        />
      );
    }
    
    if (typeof value === 'string' && value.length > 100) {
      return (
        <div className="text-sm">
          {value.substring(0, 100)}...
          <Button
            label="Show Full"
            link
            size="small"
            className="ml-2"
          />
        </div>
      );
    }
    
    return (
      <span className={differs ? 'font-semibold text-blue-600' : ''}>
        {String(value)}
      </span>
    );
  };
  
  // Field body template
  const fieldBodyTemplate = (rowData: any) => {
    return (
      <div className="flex align-items-center gap-2">
        <span className="font-semibold">{rowData.field}</span>
        {rowData.differs && (
          <i className="pi pi-exclamation-triangle text-orange-500" title="Values differ" />
        )}
      </div>
    );
  };
  
  // Generate dynamic columns for each configuration
  const configColumns = configurations.map((config, index) => (
    <Column
      key={config.id}
      header={
        <div className="text-center">
          <div className="font-bold">{config.key}</div>
          <div className="text-sm text-gray-600">v{config.version}</div>
        </div>
      }
      body={(rowData) => renderValue(rowData[`config_${index}`], rowData.differs)}
      style={{ minWidth: '200px' }}
    />
  ));
  
  // Calculate differences summary
  const differenceCount = comparisonData.filter(row => row.differs).length;
  const totalFields = comparisonData.length;
  const similarityPercentage = ((totalFields - differenceCount) / totalFields * 100).toFixed(1);
  
  return (
    <div className="configuration-comparison">
      {/* Summary Card */}
      <Card className="mb-4">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-600">{configurations.length}</div>
            <div className="text-sm text-gray-600">Configurations</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-orange-600">{differenceCount}</div>
            <div className="text-sm text-gray-600">Differences</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">{similarityPercentage}%</div>
            <div className="text-sm text-gray-600">Similarity</div>
          </div>
        </div>
      </Card>
      
      {/* Comparison Table */}
      <DataTable
        value={comparisonData}
        scrollable
        scrollHeight="500px"
        className="comparison-table"
        showGridlines
        stripedRows
      >
        <Column
          field="field"
          header="Field"
          body={fieldBodyTemplate}
          frozen
          style={{ minWidth: '150px', fontWeight: 'bold' }}
        />
        {configColumns}
      </DataTable>
      
      {/* Legend */}
      <div className="mt-4 p-3 bg-gray-50 rounded">
        <div className="flex align-items-center gap-4">
          <div className="flex align-items-center gap-2">
            <i className="pi pi-exclamation-triangle text-orange-500" />
            <span className="text-sm">Indicates differing values</span>
          </div>
          <div className="flex align-items-center gap-2">
            <span className="font-semibold text-blue-600">Highlighted</span>
            <span className="text-sm">= Different value</span>
          </div>
        </div>
      </div>
      
      {/* Action Buttons */}
      <div className="flex justify-end gap-2 mt-4">
        <Button
          label="Export Comparison"
          icon="pi pi-download"
          severity="info"
          onClick={() => {
            // Export comparison as CSV or JSON
            const dataStr = JSON.stringify(comparisonData, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'configuration-comparison.json';
            link.click();
          }}
        />
        <Button
          label="Close"
          icon="pi pi-times"
          severity="secondary"
          onClick={onClose}
        />
      </div>
    </div>
  );
};

export default ConfigurationComparison;
