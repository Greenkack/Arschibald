/**
 * Translation Management Component
 * Admin interface for managing translations
 */

import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { Dropdown } from 'primereact/dropdown';
import { InputTextarea } from 'primereact/inputtextarea';
import { Toast } from 'primereact/toast';
import { Toolbar } from 'primereact/toolbar';
import { FileUpload } from 'primereact/fileupload';
import { supportedLanguages, SupportedLanguage } from '../../i18n/i18nConfig';
import './TranslationManager.css';

interface Translation {
  key: string;
  namespace: string;
  translations: Record<SupportedLanguage, string>;
  lastModified: string;
  modifiedBy: string;
}

export const TranslationManager: React.FC = () => {
  const { t, i18n } = useTranslation();
  const [translations, setTranslations] = useState<Translation[]>([]);
  const [selectedTranslation, setSelectedTranslation] = useState<Translation | null>(null);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [globalFilter, setGlobalFilter] = useState('');
  const [selectedNamespace, setSelectedNamespace] = useState('all');
  const [loading, setLoading] = useState(false);
  const toastRef = React.useRef<Toast>(null);

  const namespaces = ['all', 'common', 'navigation', 'solar', 'heatpump', 'pricing', 'pdf', 'crm', 'products', 'admin', 'errors', 'validation'];

  useEffect(() => {
    loadTranslations();
  }, [selectedNamespace]);

  const loadTranslations = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/i18n/translations?namespace=${selectedNamespace}`);
      const data = await response.json();
      setTranslations(data);
    } catch (error) {
      toastRef.current?.show({
        severity: 'error',
        summary: t('errors.generic'),
        detail: 'Failed to load translations',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (translation: Translation) => {
    setSelectedTranslation({ ...translation });
    setShowEditDialog(true);
  };

  const handleSave = async () => {
    if (!selectedTranslation) return;

    try {
      await fetch('/api/v1/i18n/translations', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selectedTranslation),
      });

      // Reload translations in i18next
      Object.entries(selectedTranslation.translations).forEach(([lang, value]) => {
        i18n.addResource(lang, selectedTranslation.namespace, selectedTranslation.key, value);
      });

      toastRef.current?.show({
        severity: 'success',
        summary: t('messages.save_success'),
        detail: 'Translation updated successfully',
      });

      setShowEditDialog(false);
      loadTranslations();
    } catch (error) {
      toastRef.current?.show({
        severity: 'error',
        summary: t('errors.generic'),
        detail: 'Failed to save translation',
      });
    }
  };

  const handleExport = async () => {
    try {
      const response = await fetch('/api/v1/i18n/export');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `translations_${new Date().toISOString()}.zip`;
      a.click();
      window.URL.revokeObjectURL(url);

      toastRef.current?.show({
        severity: 'success',
        summary: t('common.export'),
        detail: 'Translations exported successfully',
      });
    } catch (error) {
      toastRef.current?.show({
        severity: 'error',
        summary: t('errors.generic'),
        detail: 'Failed to export translations',
      });
    }
  };

  const handleImport = async (event: any) => {
    const file = event.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
      await fetch('/api/v1/i18n/import', {
        method: 'POST',
        body: formData,
      });

      toastRef.current?.show({
        severity: 'success',
        summary: t('common.import'),
        detail: 'Translations imported successfully',
      });

      setShowImportDialog(false);
      loadTranslations();
      
      // Reload i18next
      await i18n.reloadResources();
    } catch (error) {
      toastRef.current?.show({
        severity: 'error',
        summary: t('errors.generic'),
        detail: 'Failed to import translations',
      });
    }
  };

  const handleAddNew = () => {
    setSelectedTranslation({
      key: '',
      namespace: 'common',
      translations: Object.keys(supportedLanguages).reduce(
        (acc, lang) => ({ ...acc, [lang]: '' }),
        {} as Record<SupportedLanguage, string>
      ),
      lastModified: new Date().toISOString(),
      modifiedBy: 'current_user',
    });
    setShowEditDialog(true);
  };

  const translationTemplate = (rowData: Translation, lang: SupportedLanguage) => {
    return (
      <div className="translation-cell">
        <span className="translation-text">{rowData.translations[lang]}</span>
      </div>
    );
  };

  const actionTemplate = (rowData: Translation) => {
    return (
      <div className="action-buttons">
        <Button
          icon="pi pi-pencil"
          className="p-button-rounded p-button-text"
          onClick={() => handleEdit(rowData)}
          tooltip={t('common.edit')}
        />
      </div>
    );
  };

  const leftToolbarTemplate = () => {
    return (
      <div className="toolbar-left">
        <Button
          label={t('common.add')}
          icon="pi pi-plus"
          className="p-button-success"
          onClick={handleAddNew}
        />
        <Dropdown
          value={selectedNamespace}
          options={namespaces}
          onChange={(e) => setSelectedNamespace(e.value)}
          placeholder="Select Namespace"
        />
      </div>
    );
  };

  const rightToolbarTemplate = () => {
    return (
      <div className="toolbar-right">
        <Button
          label={t('common.export')}
          icon="pi pi-download"
          className="p-button-help"
          onClick={handleExport}
        />
        <Button
          label={t('common.import')}
          icon="pi pi-upload"
          className="p-button-warning"
          onClick={() => setShowImportDialog(true)}
        />
        <Button
          label={t('common.refresh')}
          icon="pi pi-refresh"
          onClick={loadTranslations}
        />
      </div>
    );
  };

  return (
    <div className="translation-manager">
      <Toast ref={toastRef} />

      <Toolbar left={leftToolbarTemplate} right={rightToolbarTemplate} />

      <div className="search-bar">
        <span className="p-input-icon-left">
          <i className="pi pi-search" />
          <InputText
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            placeholder={t('common.search')}
          />
        </span>
      </div>

      <DataTable
        value={translations}
        loading={loading}
        globalFilter={globalFilter}
        paginator
        rows={20}
        rowsPerPageOptions={[10, 20, 50, 100]}
        className="translation-table"
        emptyMessage="No translations found"
      >
        <Column field="key" header="Key" sortable filter />
        <Column field="namespace" header="Namespace" sortable filter />
        <Column
          header="DE"
          body={(rowData) => translationTemplate(rowData, 'de')}
        />
        <Column
          header="EN"
          body={(rowData) => translationTemplate(rowData, 'en')}
        />
        <Column
          header="FR"
          body={(rowData) => translationTemplate(rowData, 'fr')}
        />
        <Column
          header="ES"
          body={(rowData) => translationTemplate(rowData, 'es')}
        />
        <Column
          field="lastModified"
          header="Last Modified"
          sortable
          body={(rowData) => new Date(rowData.lastModified).toLocaleString()}
        />
        <Column body={actionTemplate} style={{ width: '100px' }} />
      </DataTable>

      <Dialog
        header="Edit Translation"
        visible={showEditDialog}
        onHide={() => setShowEditDialog(false)}
        className="translation-edit-dialog"
        style={{ width: '800px' }}
      >
        {selectedTranslation && (
          <div className="translation-edit-form">
            <div className="form-field">
              <label>Key</label>
              <InputText
                value={selectedTranslation.key}
                onChange={(e) =>
                  setSelectedTranslation({
                    ...selectedTranslation,
                    key: e.target.value,
                  })
                }
                disabled={!!selectedTranslation.lastModified}
              />
            </div>

            <div className="form-field">
              <label>Namespace</label>
              <Dropdown
                value={selectedTranslation.namespace}
                options={namespaces.filter((ns) => ns !== 'all')}
                onChange={(e) =>
                  setSelectedTranslation({
                    ...selectedTranslation,
                    namespace: e.value,
                  })
                }
              />
            </div>

            {Object.entries(supportedLanguages).map(([lang, info]) => (
              <div key={lang} className="form-field">
                <label>
                  {info.flag} {info.nativeName}
                </label>
                <InputTextarea
                  value={selectedTranslation.translations[lang as SupportedLanguage]}
                  onChange={(e) =>
                    setSelectedTranslation({
                      ...selectedTranslation,
                      translations: {
                        ...selectedTranslation.translations,
                        [lang]: e.target.value,
                      },
                    })
                  }
                  rows={3}
                />
              </div>
            ))}

            <div className="dialog-actions">
              <Button
                label={t('common.cancel')}
                icon="pi pi-times"
                className="p-button-text"
                onClick={() => setShowEditDialog(false)}
              />
              <Button
                label={t('common.save')}
                icon="pi pi-check"
                onClick={handleSave}
              />
            </div>
          </div>
        )}
      </Dialog>

      <Dialog
        header={t('common.import')}
        visible={showImportDialog}
        onHide={() => setShowImportDialog(false)}
        className="translation-import-dialog"
      >
        <FileUpload
          mode="basic"
          accept=".json,.zip"
          maxFileSize={10000000}
          customUpload
          uploadHandler={handleImport}
          auto
          chooseLabel={t('common.upload')}
        />
      </Dialog>
    </div>
  );
};

export default TranslationManager;
