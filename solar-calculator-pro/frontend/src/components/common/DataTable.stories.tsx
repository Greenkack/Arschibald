import type { Meta, StoryObj } from '@storybook/react';
import { DataTable } from './DataTable';

/**
 * DataTable is a powerful component for displaying tabular data with sorting,
 * filtering, and pagination capabilities.
 * 
 * ## Features
 * - Column sorting (single and multiple)
 * - Global and column-specific filtering
 * - Pagination with customizable page sizes
 * - Row selection (single and multiple)
 * - Responsive design
 * - Custom cell renderers
 * - Export functionality
 * 
 * ## Accessibility
 * - Keyboard navigation (arrow keys, tab)
 * - Screen reader support with proper ARIA labels
 * - Sortable column indicators
 * - Focus management
 * - High contrast mode support
 */
const meta = {
  title: 'Common/DataTable',
  component: DataTable,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'A feature-rich data table component with sorting, filtering, and pagination.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    data: {
      description: 'Array of data objects to display',
    },
    columns: {
      description: 'Column configuration array',
    },
    paginator: {
      control: 'boolean',
      description: 'Enable pagination',
    },
    rows: {
      control: 'number',
      description: 'Number of rows per page',
    },
    sortable: {
      control: 'boolean',
      description: 'Enable column sorting',
    },
    filterable: {
      control: 'boolean',
      description: 'Enable filtering',
    },
  },
} satisfies Meta<typeof DataTable>;

export default meta;
type Story = StoryObj<typeof meta>;

const sampleData = [
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin', status: 'Active' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User', status: 'Active' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'User', status: 'Inactive' },
  { id: 4, name: 'Alice Williams', email: 'alice@example.com', role: 'Manager', status: 'Active' },
  { id: 5, name: 'Charlie Brown', email: 'charlie@example.com', role: 'User', status: 'Active' },
];

const columns = [
  { field: 'id', header: 'ID', sortable: true },
  { field: 'name', header: 'Name', sortable: true, filterable: true },
  { field: 'email', header: 'Email', sortable: true, filterable: true },
  { field: 'role', header: 'Role', sortable: true },
  { field: 'status', header: 'Status', sortable: true },
];

/**
 * Basic table with data
 */
export const Default: Story = {
  args: {
    data: sampleData,
    columns: columns,
  },
};

/**
 * Table with pagination
 */
export const WithPagination: Story = {
  args: {
    data: [...sampleData, ...sampleData, ...sampleData], // More data to show pagination
    columns: columns,
    paginator: true,
    rows: 5,
  },
};

/**
 * Sortable table
 */
export const Sortable: Story = {
  args: {
    data: sampleData,
    columns: columns,
    sortable: true,
  },
};

/**
 * Filterable table
 */
export const Filterable: Story = {
  args: {
    data: sampleData,
    columns: columns,
    filterable: true,
  },
};

/**
 * Full-featured table
 */
export const FullFeatured: Story = {
  args: {
    data: [...sampleData, ...sampleData],
    columns: columns,
    paginator: true,
    rows: 5,
    sortable: true,
    filterable: true,
  },
};

/**
 * Empty table state
 */
export const Empty: Story = {
  args: {
    data: [],
    columns: columns,
  },
};
