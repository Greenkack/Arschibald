import React, { useState } from 'react';
import { DataTable as PrimeDataTable, DataTableFilterMeta } from 'primereact/datatable';
import { Column, ColumnProps } from 'primereact/column';
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import { FilterMatchMode } from 'primereact/api';
import './DataTable.css';

export interface DataTableColumn extends Omit<ColumnProps, 'field'> {
  field: string;
  header: string;
  sortable?: boolean;
  filterable?: boolean;
  body?: (rowData: any) => React.ReactNode;
}

export interface DataTableProps {
  data: any[];
  columns: DataTableColumn[];
  loading?: boolean;
  paginator?: boolean;
  rows?: number;
  rowsPerPageOptions?: number[];
  selectionMode?: 'single' | 'multiple' | null;
  selection?: any;
  onSelectionChange?: (e: { value: any }) => void;
  onRowClick?: (e: { data: any }) => void;
  emptyMessage?: string;
  globalFilterFields?: string[];
  showGridlines?: boolean;
  stripedRows?: boolean;
  responsiveLayout?: 'scroll' | 'stack';
  className?: string;
}

export const DataTable: React.FC<DataTableProps> = ({
  data,
  columns,
  loading = false,
  paginator = true,
  rows = 10,
  rowsPerPageOptions = [5, 10, 25, 50],
  selectionMode = null,
  selection,
  onSelectionChange,
  onRowClick,
  emptyMessage = 'No data found',
  globalFilterFields,
  showGridlines = true,
  stripedRows = true,
  responsiveLayout = 'scroll',
  className = '',
}) => {
  const [globalFilterValue, setGlobalFilterValue] = useState('');
  const [filters, setFilters] = useState<DataTableFilterMeta>({});

  // Initialize filters for filterable columns
  React.useEffect(() => {
    const initialFilters: DataTableFilterMeta = {};
    columns.forEach((col) => {
      if (col.filterable) {
        initialFilters[col.field] = { value: null, matchMode: FilterMatchMode.CONTAINS };
      }
    });
    setFilters(initialFilters);
  }, [columns]);

  const onGlobalFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setGlobalFilterValue(value);
  };

  const clearFilters = () => {
    setGlobalFilterValue('');
    const clearedFilters: DataTableFilterMeta = {};
    columns.forEach((col) => {
      if (col.filterable) {
        clearedFilters[col.field] = { value: null, matchMode: FilterMatchMode.CONTAINS };
      }
    });
    setFilters(clearedFilters);
  };

  const renderHeader = () => {
    if (!globalFilterFields || globalFilterFields.length === 0) {
      return null;
    }

    return (
      <div className="flex justify-content-between align-items-center">
        <div className="flex gap-2">
          <span className="p-input-icon-left">
            <i className="pi pi-search" />
            <InputText
              value={globalFilterValue}
              onChange={onGlobalFilterChange}
              placeholder="Search..."
              className="w-full"
            />
          </span>
          {globalFilterValue && (
            <Button
              type="button"
              icon="pi pi-filter-slash"
              label="Clear"
              outlined
              onClick={clearFilters}
            />
          )}
        </div>
      </div>
    );
  };

  const header = renderHeader();

  return (
    <div className={`data-table-wrapper ${className}`}>
      <PrimeDataTable
        value={data}
        loading={loading}
        paginator={paginator}
        rows={rows}
        rowsPerPageOptions={rowsPerPageOptions}
        selectionMode={selectionMode}
        selection={selection}
        onSelectionChange={onSelectionChange}
        onRowClick={onRowClick}
        dataKey="id"
        filters={filters}
        globalFilterFields={globalFilterFields}
        globalFilter={globalFilterValue}
        header={header}
        emptyMessage={emptyMessage}
        showGridlines={showGridlines}
        stripedRows={stripedRows}
        responsiveLayout={responsiveLayout}
        className="data-table"
      >
        {selectionMode && (
          <Column
            selectionMode={selectionMode}
            headerStyle={{ width: '3rem' }}
            exportable={false}
          />
        )}
        {columns.map((col) => (
          <Column
            key={col.field}
            field={col.field}
            header={col.header}
            sortable={col.sortable !== false}
            filter={col.filterable}
            filterPlaceholder={col.filterable ? `Search by ${col.header}` : undefined}
            body={col.body}
            style={col.style}
            headerStyle={col.headerStyle}
            bodyStyle={col.bodyStyle}
            {...col}
          />
        ))}
      </PrimeDataTable>
    </div>
  );
};
