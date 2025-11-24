import React from 'react';
import { DataTable, DataTableProps } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { useResponsive } from '../../hooks/useResponsive';
import '../../styles/responsive.css';

interface ResponsiveTableProps<T> extends Omit<DataTableProps<T>, 'value'> {
  data: T[];
  columns: Array<{
    field: string;
    header: string;
    body?: (rowData: T) => React.ReactNode;
    hideOnMobile?: boolean;
    hideOnTablet?: boolean;
  }>;
  mobileCardTemplate?: (rowData: T) => React.ReactNode;
}

/**
 * Responsive table component
 * Switches to card layout on mobile devices
 */
export function ResponsiveTable<T extends Record<string, any>>({
  data,
  columns,
  mobileCardTemplate,
  className = '',
  ...props
}: ResponsiveTableProps<T>) {
  const { isMobile, isTablet } = useResponsive();

  // Mobile card view
  if (isMobile && mobileCardTemplate) {
    return (
      <div className={`responsive-table-mobile ${className}`}>
        {data.map((item, index) => (
          <div key={index} className="p-card p-responsive mb-3">
            {mobileCardTemplate(item)}
          </div>
        ))}
      </div>
    );
  }

  // Filter columns based on device
  const visibleColumns = columns.filter(col => {
    if (isMobile && col.hideOnMobile) return false;
    if (isTablet && col.hideOnTablet) return false;
    return true;
  });

  return (
    <DataTable
      value={data}
      className={`responsive-table ${className}`}
      responsiveLayout="scroll"
      scrollable
      scrollHeight={isMobile ? '400px' : '600px'}
      {...props}
    >
      {visibleColumns.map((col) => (
        <Column
          key={col.field}
          field={col.field}
          header={col.header}
          body={col.body}
          style={{
            minWidth: isMobile ? '100px' : '150px',
          }}
        />
      ))}
    </DataTable>
  );
}
