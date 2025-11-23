/**
 * Configuration Import/Export Component
 * 
 * Import and export configurations in various formats
 */

import React, { useState } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import { Button } from 'primereact/button';
import { Dropdown } from 'primereact/dropdown';
import { InputTextarea } from 'primereact/inputtextarea';
import { FileUpload, FileUploadHandlerEvent } from 'primereact/fileupload';
import { Checkbox } from 'primereact/checkbox';
import { Message } from 'primereact/message';
import { ProgressBar } from 'primereact/progressbar';
import { Card } from 'primereact/card';
import { Toast } from 'primereact/toast';
import { MultiSelect } from 'primereact/multiselect';

interface ConfigurationImportExportProps {
  onImportComplete: () => void;
  onClose: () => void;
}

const ConfigurationImportExport: React.FC<ConfigurationImportExportProps> = ({
  onImportComplete,
  onClose
}) => {
  // Export state
  const [exportFormat, setExportFormat] = useState('json');
  const [exportNamespaces, setExportNamespaces] = useState<string[]>([]);
  const [exportCategories, setExportCategories] = useState<string[]>([]);
  const [includeVersions, setIncludeVersions] = useState(false);
  const [includeAuditLogs, setIncludeAuditLogs] = useState(false);
  const [exporting, setExporting] = useState(false);
  
  // Import state
  const [importFormat, setImportFormat] = useState('json');
  const [importData, setImportData] = useState('');
  const [importMergeMode, setImportMergeMode] = useState('merge');
  const [validateBeforeImport, setValidateBeforeImport] = useState(true);
  const [dryRun, setDryRun] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<any>(null);
  
  const toast = React.useRef<Toast>(null);
  
  // Format options
  const formatOptions = [
    { label: 'JSON', value: 'json' },
    { label: 'YAML', value: 'yaml' },
    { label: 'CSV', value: 'csv' }
  ];
  
  // Namespace options
  const namespaceOptions = [
    { label: 'Global', value: 'global' },
    { label: 'Solar', value: 'solar' },
    { label: 'Heat Pump', value: 'heatpump' },
    { label: 'PDF', value: 'pdf' },
    { label: 'CRM', value: 'crm' },
    { label: 'Pricing', value: 'pricing' }
  ];
  
  // Category options
  const categoryOptions = [
    { label: 'System', value: 'system' },
    { label: 'User', value: 'user' },
    { label: 'Module', value: 'module' },
    { label: 'Feature', value: 'feature' }
  ];
  
  // Merge mode options
  const mergeModeOptions = [
    { label: 'Merge (Keep existing)', value: 'merge' },
    { label: 'Replace (Overwrite)', value: 'replace' },
    { label: 'Skip (Ignore duplicates)', value: 'skip' }
  ];
  
  // Handle export
  const handleExport = async () => {
    setExporting(true);
    try {
      const params = new URLSearchParams({
        format: exportFormat,
        include_versions: includeVersions.toString(),
        include_audit_logs: includeAuditLogs.toString()
      });
      
      if (exportNamespaces.length > 0) {
        exportNamespaces.forEach(ns => params.append('namespace_filter', ns));
      }
      
      if (exportCategories.length > 0) {
        exportCategories.forEach(cat => params.append('category_filter', cat));
      }
      
      const response = await fetch(`/api/v1/configurations/export?${params}`);
      
      if (response.ok) {
        const data = await response.text();
        
        // Download file
        const blob = new Blob([data], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `configurations-export.${exportFormat}`;
        link.click();
        URL.revokeObjectURL(url);
        
        toast.current?.show({
          severity: 'success',
          summary: 'Success',
          detail: 'Configurations exported successfully',
          life: 3000
        });
      } else {
        throw new Error('Export failed');
      }
    } catch (error) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to export configurations',
        life: 3000
      });
    } finally {
      setExporting(false);
    }
  };
  
  // Handle import
  const handleImport = async () => {
    if (!importData.trim()) {
      toast.current?.show({
        severity: 'warn',
        summary: 'Warning',
        detail: 'Please provide data to import',
        life: 3000
      });
      return;
    }
    
    setImporting(true);
    setImportResult(null);
    
    try {
      const response = await fetch('/api/v1/configurations/import', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          data: importData,
          format: importFormat,
          merge_mode: importMergeMode,
          validate_before_import: validateBeforeImport,
          dry_run: dryRun
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        setImportResult(result);
        
        if (!dryRun && result.errors.length === 0) {
          toast.current?.show({
            severity: 'success',
            summary: 'Success',
            detail: `Import completed: ${result.created} created, ${result.updated} updated`,
            life: 5000
          });
          
          if (result.created > 0 || result.updated > 0) {
            onImportComplete();
          }
        }
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Import failed');
      }
    } catch (error: any) {
      toast.current?.show({
        severity: 'error',
        summary: 'Error',
        detail: error.message || 'Failed to import configurations',
        life: 3000
      });
    } finally {
      setImporting(false);
    }
  };
  
  // Handle file upload
  const handleFileUpload = (event: FileUploadHandlerEvent) => {
    const file = event.files[0];
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const text = e.target?.result as string;
      setImportData(text);
      
      // Auto-detect format from file extension
      if (file.name.endsWith('.json')) {
        setImportFormat('json');
      } else if (file.name.endsWith('.yaml') || file.name.endsWith('.yml')) {
        setImportFormat('yaml');
      } else if (file.name.endsWith('.csv')) {
        setImportFormat('csv');
      }
      
      toast.current?.show({
        severity: 'success',
        summary: 'Success',
        detail: 'File loaded successfully',
        life: 3000
      });
    };
    
    reader.readAsText(file);
  };
  
  return (
    <div className="configuration-import-export">
      <Toast ref={toast} />
      
      <TabView>
        {/* Export Tab */}
        <TabPanel header="Export" leftIcon="pi pi-download">
          <div className="grid grid-cols-1 gap-4">
            <Card>
              <h4 className="font-semibold mb-3">Export Options</h4>
              
              <div className="grid grid-cols-1 gap-3">
                <div className="field">
                  <label htmlFor="export-format" className="block font-semibold mb-2">
                    Export Format
                  </label>
                  <Dropdown
                    id="export-format"
                    value={exportFormat}
                    options={formatOptions}
                    onChange={(e) => setExportFormat(e.value)}
                    className="w-full"
                  />
                </div>
                
                <div className="field">
                  <label htmlFor="export-namespaces" className="block font-semibold mb-2">
                    Filter by Namespaces (Optional)
                  </label>
                  <MultiSelect
                    id="export-namespaces"
                    value={exportNamespaces}
                    options={namespaceOptions}
                    onChange={(e) => setExportNamespaces(e.value)}
                    placeholder="All namespaces"
                    className="w-full"
                    display="chip"
                  />
                </div>
                
                <div className="field">
                  <label htmlFor="export-categories" className="block font-semibold mb-2">
                    Filter by Categories (Optional)
                  </label>
                  <MultiSelect
                    id="export-categories"
                    value={exportCategories}
                    options={categoryOptions}
                    onChange={(e) => setExportCategories(e.value)}
                    placeholder="All categories"
                    className="w-full"
                    display="chip"
                  />
                </div>
                
                <div className="field-checkbox">
                  <Checkbox
                    inputId="include-versions"
                    checked={includeVersions}
                    onChange={(e) => setIncludeVersions(e.checked || false)}
                  />
                  <label htmlFor="include-versions" className="ml-2">
                    Include version history
                  </label>
                </div>
                
                <div className="field-checkbox">
                  <Checkbox
                    inputId="include-audit"
                    checked={includeAuditLogs}
                    onChange={(e) => setIncludeAuditLogs(e.checked || false)}
                  />
                  <label htmlFor="include-audit" className="ml-2">
                    Include audit logs
                  </label>
                </div>
              </div>
            </Card>
            
            <Button
              label="Export Configurations"
              icon="pi pi-download"
              severity="success"
              onClick={handleExport}
              loading={exporting}
              className="w-full"
            />
          </div>
        </TabPanel>
        
        {/* Import Tab */}
        <TabPanel header="Import" leftIcon="pi pi-upload">
          <div className="grid grid-cols-1 gap-4">
            <Card>
              <h4 className="font-semibold mb-3">Import Options</h4>
              
              <div className="grid grid-cols-1 gap-3">
                <div className="field">
                  <label htmlFor="import-format" className="block font-semibold mb-2">
                    Import Format
                  </label>
                  <Dropdown
                    id="import-format"
                    value={importFormat}
                    options={formatOptions}
                    onChange={(e) => setImportFormat(e.value)}
                    className="w-full"
                  />
                </div>
                
                <div className="field">
                  <label htmlFor="merge-mode" className="block font-semibold mb-2">
                    Merge Mode
                  </label>
                  <Dropdown
                    id="merge-mode"
                    value={importMergeMode}
                    options={mergeModeOptions}
                    onChange={(e) => setImportMergeMode(e.value)}
                    className="w-full"
                  />
                </div>
                
                <div className="field-checkbox">
                  <Checkbox
                    inputId="validate-import"
                    checked={validateBeforeImport}
                    onChange={(e) => setValidateBeforeImport(e.checked || false)}
                  />
                  <label htmlFor="validate-import" className="ml-2">
                    Validate before import
                  </label>
                </div>
                
                <div className="field-checkbox">
                  <Checkbox
                    inputId="dry-run"
                    checked={dryRun}
                    onChange={(e) => setDryRun(e.checked || false)}
                  />
                  <label htmlFor="dry-run" className="ml-2">
                    Dry run (preview changes without applying)
                  </label>
                </div>
              </div>
            </Card>
            
            <Card>
              <h4 className="font-semibold mb-3">Import Data</h4>
              
              <FileUpload
                mode="basic"
                name="config-file"
                accept=".json,.yaml,.yml,.csv"
                maxFileSize={10000000}
                customUpload
                uploadHandler={handleFileUpload}
                auto
                chooseLabel="Upload File"
                className="mb-3"
              />
              
              <div className="field">
                <label htmlFor="import-data" className="block font-semibold mb-2">
                  Or paste data directly:
                </label>
                <InputTextarea
                  id="import-data"
                  value={importData}
                  onChange={(e) => setImportData(e.target.value)}
                  rows={12}
                  className="w-full font-mono text-sm"
                  placeholder={`Paste your ${importFormat.toUpperCase()} data here...`}
                />
              </div>
            </Card>
            
            {importResult && (
              <Card>
                <h4 className="font-semibold mb-3">
                  {dryRun ? 'Preview Results' : 'Import Results'}
                </h4>
                
                <div className="grid grid-cols-4 gap-3 mb-3">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{importResult.total}</div>
                    <div className="text-sm text-gray-600">Total</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{importResult.created}</div>
                    <div className="text-sm text-gray-600">Created</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">{importResult.updated}</div>
                    <div className="text-sm text-gray-600">Updated</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-600">{importResult.skipped}</div>
                    <div className="text-sm text-gray-600">Skipped</div>
                  </div>
                </div>
                
                {importResult.errors && importResult.errors.length > 0 && (
                  <div>
                    <Message
                      severity="error"
                      text={`${importResult.errors.length} error(s) occurred`}
                      className="mb-2 w-full"
                    />
                    <div className="max-h-40 overflow-auto bg-red-50 p-2 rounded">
                      {importResult.errors.map((error: any, index: number) => (
                        <div key={index} className="text-sm text-red-700 mb-1">
                          • {error.key}: {error.error}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            )}
            
            <Button
              label={dryRun ? 'Preview Import' : 'Import Configurations'}
              icon="pi pi-upload"
              severity="success"
              onClick={handleImport}
              loading={importing}
              disabled={!importData.trim()}
              className="w-full"
            />
          </div>
        </TabPanel>
      </TabView>
      
      {/* Action Buttons */}
      <div className="flex justify-end gap-2 mt-4">
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

export default ConfigurationImportExport;
