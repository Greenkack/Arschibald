/**
 * Advanced Filter Component
 * 
 * Provides comprehensive filtering functionality with:
 * - Dynamic filter fields based on entity type
 * - Multiple filter conditions
 * - Date range filtering
 * - Price range filtering
 * - Saved filters
 * - Filter presets
 */

import React, { useState, useEffect } from 'react';
import { Panel } from 'primereact/panel';
import { Dropdown } from 'primereact/dropdown';
import { MultiSelect } from 'primereact/multiselect';
import { Calendar } from 'primereact/calendar';
import { InputNumber } from 'primereact/inputnumber';
import { Button } from 'primereact/button';
import { Chip } from 'primereact/chip';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { Message } from 'primereact/message';
import './AdvancedFilter.css';

interface FilterField {
  name: string;
  label: string;
  type: 'select' | 'multiselect' | 'date_range' | 'price_range' | 'text';
  options?: Array<{ label: string; value: any }>;
}

interface FilterValue {
  field: string;
  operator: string;
  value: any;
}

interface AdvancedFilterProps {
  entityType: string;
  onFilterApply: (filters: Record<string, any>) => void;
  onFilterClear: () => void;
}

export const AdvancedFilter: React.FC<AdvancedFilterProps> = ({
  entityType,
  onFilterApply,
  onFilterClear
}) => {
  const [filterFields, setFilterFields] = useState<FilterField[]>([]);
  const [activeFilters, setActiveFilters] = useState<FilterValue[]>([]);
  const [filterValues, setFilterValues] = useState<Record<string, any>>({});
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [filterName, setFilterName] = useState('');
  const [savedFilters, setSavedFilters] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Load filter options for entity type
  useEffect(() => {
    loadFilterOptions();
  }, [entityType]);

  const loadFilterOptions = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/search/filter-options/${entityType}`);
      if (response.ok) {
        const options = await response.json();
        const fields = buildFilterFields(options);
        setFilterFields(fields);
      }
    } catch (error) {
      console.error('Error loading filter options:', error);
    } finally {
      setLoading(false);
    }
  };

  const buildFilterFields = (options: Record<string, any>): FilterField[] => {
    const fields: FilterField[] = [];

    Object.entries(options).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        fields.push({
          name: key,
          label: formatFieldLabel(key),
          type: 'multiselect',
          options: value.map(v => ({ label: v, value: v }))
        });
      } else if (value === true) {
        if (key === 'date_range') {
          fields.push({
            name: 'date_range',
            label: 'Date Range',
            type: 'date_range'
          });
        } else if (key === 'price_range') {
          fields.push({
            name: 'price_range',
            label: 'Price Range',
            type: 'price_range'
          });
        }
      }
    });

    return fields;
  };

  const formatFieldLabel = (fieldName: string): string => {
    return fieldName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const handleFilterChange = (fieldName: string, value: any) => {
    setFilterValues(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  const applyFilters = () => {
    const filters: Record<string, any> = {};

    Object.entries(filterValues).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        if (Array.isArray(value) && value.length === 0) {
          return;
        }
        filters[key] = value;
      }
    });

    onFilterApply(filters);
  };

  const clearFilters = () => {
    setFilterValues({});
    setActiveFilters([]);
    onFilterClear();
  };

  const saveFilter = async () => {
    if (!filterName.trim()) {
      return;
    }

    try {
      const response = await fetch('/api/v1/search/saved', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: filterName,
          entity_type: entityType,
          query: '',
          filters: filterValues,
          is_public: false
        })
      });

      if (response.ok) {
        setShowSaveDialog(false);
        setFilterName('');
        loadSavedFilters();
      }
    } catch (error) {
      console.error('Error saving filter:', error);
    }
  };

  const loadSavedFilters = async () => {
    try {
      const response = await fetch('/api/v1/search/saved?user_id=1');
      if (response.ok) {
        const filters = await response.json();
        setSavedFilters(filters.filter((f: any) => f.entity_type === entityType));
      }
    } catch (error) {
      console.error('Error loading saved filters:', error);
    }
  };

  const applySavedFilter = (savedFilter: any) => {
    setFilterValues(savedFilter.filters);
    onFilterApply(savedFilter.filters);
  };

  const renderFilterField = (field: FilterField) => {
    const value = filterValues[field.name];

    switch (field.type) {
      case 'select':
        return (
          <Dropdown
            value={value}
            options={field.options || []}
            onChange={(e) => handleFilterChange(field.name, e.value)}
            placeholder={`Select ${field.label}`}
            className="filter-field"
            showClear
          />
        );

      case 'multiselect':
        return (
          <MultiSelect
            value={value || []}
            options={field.options || []}
            onChange={(e) => handleFilterChange(field.name, e.value)}
            placeholder={`Select ${field.label}`}
            className="filter-field"
            display="chip"
          />
        );

      case 'date_range':
        return (
          <div className="date-range-filter">
            <Calendar
              value={value?.start}
              onChange={(e) => handleFilterChange(field.name, {
                ...value,
                start: e.value
              })}
              placeholder="Start Date"
              showIcon
              className="filter-field"
            />
            <span className="range-separator">to</span>
            <Calendar
              value={value?.end}
              onChange={(e) => handleFilterChange(field.name, {
                ...value,
                end: e.value
              })}
              placeholder="End Date"
              showIcon
              className="filter-field"
            />
          </div>
        );

      case 'price_range':
        return (
          <div className="price-range-filter">
            <InputNumber
              value={value?.min}
              onValueChange={(e) => handleFilterChange(field.name, {
                ...value,
                min: e.value
              })}
              placeholder="Min Price"
              mode="currency"
              currency="EUR"
              locale="de-DE"
              className="filter-field"
            />
            <span className="range-separator">to</span>
            <InputNumber
              value={value?.max}
              onValueChange={(e) => handleFilterChange(field.name, {
                ...value,
                max: e.value
              })}
              placeholder="Max Price"
              mode="currency"
              currency="EUR"
              locale="de-DE"
              className="filter-field"
            />
          </div>
        );

      case 'text':
        return (
          <InputText
            value={value || ''}
            onChange={(e) => handleFilterChange(field.name, e.target.value)}
            placeholder={`Enter ${field.label}`}
            className="filter-field"
          />
        );

      default:
        return null;
    }
  };

  const activeFilterCount = Object.keys(filterValues).filter(
    key => filterValues[key] !== null && filterValues[key] !== undefined && filterValues[key] !== ''
  ).length;

  return (
    <div className="advanced-filter-container">
      <Panel header="Advanced Filters" toggleable>
        {loading ? (
          <Message severity="info" text="Loading filter options..." />
        ) : (
          <>
            <div className="filter-fields-grid">
              {filterFields.map(field => (
                <div key={field.name} className="filter-field-wrapper">
                  <label className="filter-label">{field.label}</label>
                  {renderFilterField(field)}
                </div>
              ))}
            </div>

            <div className="filter-actions">
              <Button
                label="Apply Filters"
                icon="pi pi-check"
                onClick={applyFilters}
                className="p-button-primary"
                disabled={activeFilterCount === 0}
              />
              <Button
                label="Clear All"
                icon="pi pi-times"
                onClick={clearFilters}
                className="p-button-secondary"
                disabled={activeFilterCount === 0}
              />
              <Button
                label="Save Filter"
                icon="pi pi-save"
                onClick={() => setShowSaveDialog(true)}
                className="p-button-outlined"
                disabled={activeFilterCount === 0}
              />
            </div>

            {activeFilterCount > 0 && (
              <div className="active-filters-display">
                <span className="active-filters-label">
                  Active Filters ({activeFilterCount}):
                </span>
                <div className="active-filters-chips">
                  {Object.entries(filterValues).map(([key, value]) => {
                    if (value === null || value === undefined || value === '') {
                      return null;
                    }
                    
                    const field = filterFields.find(f => f.name === key);
                    if (!field) return null;

                    let displayValue = value;
                    if (Array.isArray(value)) {
                      displayValue = value.join(', ');
                    } else if (typeof value === 'object') {
                      displayValue = JSON.stringify(value);
                    }

                    return (
                      <Chip
                        key={key}
                        label={`${field.label}: ${displayValue}`}
                        removable
                        onRemove={() => handleFilterChange(key, null)}
                      />
                    );
                  })}
                </div>
              </div>
            )}

            {savedFilters.length > 0 && (
              <div className="saved-filters-section">
                <h4>Saved Filters</h4>
                <div className="saved-filters-list">
                  {savedFilters.map(filter => (
                    <Button
                      key={filter.id}
                      label={filter.name}
                      icon="pi pi-filter"
                      onClick={() => applySavedFilter(filter)}
                      className="p-button-outlined p-button-sm"
                    />
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </Panel>

      {/* Save Filter Dialog */}
      <Dialog
        header="Save Filter"
        visible={showSaveDialog}
        style={{ width: '400px' }}
        onHide={() => setShowSaveDialog(false)}
        footer={
          <div>
            <Button
              label="Cancel"
              icon="pi pi-times"
              onClick={() => setShowSaveDialog(false)}
              className="p-button-text"
            />
            <Button
              label="Save"
              icon="pi pi-check"
              onClick={saveFilter}
              disabled={!filterName.trim()}
            />
          </div>
        }
      >
        <div className="p-fluid">
          <label htmlFor="filter-name">Filter Name</label>
          <InputText
            id="filter-name"
            value={filterName}
            onChange={(e) => setFilterName(e.target.value)}
            placeholder="Enter filter name"
            autoFocus
          />
        </div>
      </Dialog>
    </div>
  );
};

export default AdvancedFilter;
