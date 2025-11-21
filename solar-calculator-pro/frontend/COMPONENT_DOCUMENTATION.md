# Component Documentation Index

This document provides an overview of all UI components in the Solar Calculator Pro application, organized by category.

## Table of Contents

- [Common Components](#common-components)
- [Form Components](#form-components)
- [Chart Components](#chart-components)
- [Layout Components](#layout-components)
- [Solar Calculator Components](#solar-calculator-components)
- [Heat Pump Components](#heat-pump-components)
- [CRM Components](#crm-components)
- [Admin Components](#admin-components)
- [PDF Components](#pdf-components)
- [Pricing Components](#pricing-components)
- [Product Components](#product-components)
- [3D Visualization Components](#3d-visualization-components)
- [Migration Components](#migration-components)
- [Update Components](#update-components)
- [Settings Components](#settings-components)

---

## Common Components

### FormInput
**Location**: `src/components/common/FormInput.tsx`

Reusable input component with validation and error handling.

**Props**:
- `label`: string - Input label
- `value`: string - Current value
- `onChange`: (value: string) => void - Change handler
- `error`: string - Error message
- `required`: boolean - Required field indicator
- `disabled`: boolean - Disabled state
- `type`: string - HTML input type

**Accessibility**: WCAG AA compliant, keyboard navigable, screen reader support

**Story**: `FormInput.stories.tsx`

---

### Modal
**Location**: `src/components/common/Modal.tsx`

Dialog component for overlays and confirmations.

**Props**:
- `visible`: boolean - Visibility state
- `onHide`: () => void - Close callback
- `header`: ReactNode - Modal header
- `footer`: ReactNode - Modal footer
- `width`: string - Modal width
- `closable`: boolean - Show close button

**Accessibility**: Focus trap, ESC to close, ARIA dialog role

**Story**: `Modal.stories.tsx`

---

### DataTable
**Location**: `src/components/common/DataTable.tsx`

Feature-rich table with sorting, filtering, and pagination.

**Props**:
- `data`: Array<any> - Table data
- `columns`: Array<Column> - Column configuration
- `paginator`: boolean - Enable pagination
- `rows`: number - Rows per page
- `sortable`: boolean - Enable sorting
- `filterable`: boolean - Enable filtering

**Accessibility**: Keyboard navigation, sortable indicators, ARIA grid

**Story**: `DataTable.stories.tsx`

---

### ConfirmDialog
**Location**: `src/components/common/ConfirmDialog.tsx`

Confirmation dialog for destructive actions.

**Props**:
- `visible`: boolean - Visibility state
- `message`: string - Confirmation message
- `onConfirm`: () => void - Confirm callback
- `onCancel`: () => void - Cancel callback
- `severity`: 'info' | 'warning' | 'danger' - Visual severity

**Accessibility**: Focus on primary action, ESC to cancel

---

### ToastNotification
**Location**: `src/components/common/ToastNotification.tsx`

Toast notifications for user feedback.

**Props**:
- `message`: string - Notification message
- `severity`: 'success' | 'info' | 'warning' | 'error' - Type
- `duration`: number - Auto-dismiss duration
- `position`: string - Screen position

**Accessibility**: ARIA live region, dismissible

---

### SkeletonLoader
**Location**: `src/components/common/SkeletonLoader.tsx`

Loading placeholder for content.

**Props**:
- `width`: string - Skeleton width
- `height`: string - Skeleton height
- `count`: number - Number of skeletons
- `shape`: 'rectangle' | 'circle' - Shape

**Accessibility**: ARIA busy state

---

### LoadingSpinner
**Location**: `src/components/common/LoadingSpinner.tsx`

Animated loading indicator.

**Props**:
- `size`: 'small' | 'medium' | 'large' - Spinner size
- `message`: string - Loading message

**Accessibility**: ARIA live region, loading role

---

### VirtualList
**Location**: `src/components/common/VirtualList.tsx`

Virtualized list for large datasets.

**Props**:
- `items`: Array<any> - List items
- `itemHeight`: number - Fixed item height
- `renderItem`: (item) => ReactNode - Item renderer

**Accessibility**: Keyboard navigation, ARIA listbox

---

### LazyImage
**Location**: `src/components/common/LazyImage.tsx`

Lazy-loaded image component.

**Props**:
- `src`: string - Image source
- `alt`: string - Alt text
- `placeholder`: string - Placeholder image

**Accessibility**: Alt text required, loading state

---

## Form Components

### FormContainer
**Location**: `src/components/forms/FormContainer.tsx`

Container for form layout and submission.

**Props**:
- `onSubmit`: (data) => void - Submit handler
- `children`: ReactNode - Form fields
- `loading`: boolean - Submission state

**Accessibility**: Form role, submit on Enter

---

### FormField
**Location**: `src/components/forms/FormField.tsx`

Wrapper for form fields with label and error.

**Props**:
- `label`: string - Field label
- `error`: string - Error message
- `required`: boolean - Required indicator
- `children`: ReactNode - Input component

**Accessibility**: Label association, error linking

---

### GermanNumberInput
**Location**: `src/components/GermanNumberInput.tsx`

Number input with German formatting (1.234,56).

**Props**:
- `value`: number - Numeric value
- `onChange`: (value: number) => void - Change handler
- `label`: string - Input label
- `min`: number - Minimum value
- `max`: number - Maximum value

**Accessibility**: Numeric input, validation feedback

**Story**: `GermanNumberInput.stories.tsx`

---

### GermanCurrencyInput
**Location**: `src/components/GermanCurrencyInput.tsx`

Currency input with German formatting and € symbol.

**Props**:
- `value`: number - Currency value
- `onChange`: (value: number) => void - Change handler
- `label`: string - Input label

**Accessibility**: Currency format announced

---

### GermanPercentInput
**Location**: `src/components/GermanPercentInput.tsx`

Percentage input with German formatting.

**Props**:
- `value`: number - Percentage value (0-100)
- `onChange`: (value: number) => void - Change handler
- `label`: string - Input label

**Accessibility**: Percentage format announced

---

### GermanSlider
**Location**: `src/components/GermanSlider.tsx`

Slider with German number formatting.

**Props**:
- `value`: number - Current value
- `onChange`: (value: number) => void - Change handler
- `min`: number - Minimum value
- `max`: number - Maximum value
- `step`: number - Step increment

**Accessibility**: Keyboard arrows, value announced

---

### FormattedDisplay
**Location**: `src/components/FormattedDisplay.tsx`

Display component for formatted values.

**Props**:
- `value`: number - Value to display
- `format`: 'number' | 'currency' | 'percent' - Format type
- `locale`: string - Locale (default: de-DE)

**Accessibility**: Semantic value display

---

## Chart Components

### LineChart
**Location**: `src/components/charts/LineChart.tsx`

Line chart for trends and time-series data.

**Props**:
- `data`: Array<any> - Chart data
- `xKey`: string - X-axis key
- `yKey`: string - Y-axis key
- `title`: string - Chart title
- `color`: string - Line color

**Accessibility**: Data table alternative, keyboard navigation

**Story**: `LineChart.stories.tsx`

---

### BarChart
**Location**: `src/components/charts/BarChart.tsx`

Bar chart for comparisons.

**Props**:
- `data`: Array<any> - Chart data
- `xKey`: string - X-axis key
- `yKey`: string - Y-axis key
- `title`: string - Chart title

**Accessibility**: Data table alternative

---

### PieChart
**Location**: `src/components/charts/PieChart.tsx`

Pie chart for proportions.

**Props**:
- `data`: Array<any> - Chart data
- `nameKey`: string - Label key
- `valueKey`: string - Value key
- `title`: string - Chart title

**Accessibility**: Data table alternative, legend

---

### AreaChart
**Location**: `src/components/charts/AreaChart.tsx`

Area chart for cumulative data.

**Props**:
- `data`: Array<any> - Chart data
- `xKey`: string - X-axis key
- `yKey`: string - Y-axis key
- `title`: string - Chart title

**Accessibility**: Data table alternative

---

## Layout Components

### MainLayout
**Location**: `src/components/layout/MainLayout.tsx`

Main application layout with sidebar and header.

**Props**:
- `children`: ReactNode - Page content

**Accessibility**: Landmark regions, skip links

---

### Header
**Location**: `src/components/layout/Header.tsx`

Application header with navigation and user menu.

**Props**:
- `notificationCount`: number - Notification badge

**Accessibility**: Navigation landmark, keyboard menu

**Story**: `Header.stories.tsx`

---

### Sidebar
**Location**: `src/components/layout/Sidebar.tsx`

Navigation sidebar with menu items.

**Props**:
- `collapsed`: boolean - Collapsed state

**Accessibility**: Navigation landmark, keyboard navigation

---

### Footer
**Location**: `src/components/layout/Footer.tsx`

Application footer with links and info.

**Accessibility**: Contentinfo landmark

---

### MobileDrawer
**Location**: `src/components/layout/MobileDrawer.tsx`

Mobile navigation drawer.

**Props**:
- `visible`: boolean - Visibility state
- `onHide`: () => void - Close callback

**Accessibility**: Focus trap, ESC to close

---

## Solar Calculator Components

### SolarCalculatorForm
**Location**: `src/components/solar/SolarCalculatorForm.tsx`

Multi-step form for solar calculations.

**Props**:
- `onSubmit`: (data) => void - Submit handler
- `initialData`: object - Pre-filled data

**Accessibility**: Step indicators, validation feedback

**Story**: `SolarCalculatorForm.stories.tsx`

---

### SolarCalculationResults
**Location**: `src/components/solar/SolarCalculationResults.tsx`

Display solar calculation results.

**Props**:
- `results`: object - Calculation results

**Accessibility**: Semantic result display

---

## Heat Pump Components

### HeatPumpInputForm
**Location**: `src/components/heatpump/HeatPumpInputForm.tsx`

Input form for heat pump calculations.

**Props**:
- `onSubmit`: (data) => void - Submit handler

**Accessibility**: Form validation, error feedback

---

### HeatPumpResults
**Location**: `src/components/heatpump/HeatPumpResults.tsx`

Display heat pump calculation results.

**Props**:
- `results`: object - Calculation results

**Accessibility**: Semantic result display

---

### HeatPumpModelSelection
**Location**: `src/components/heatpump/HeatPumpModelSelection.tsx`

Heat pump model selection component.

**Props**:
- `models`: Array<Model> - Available models
- `onSelect`: (model) => void - Selection handler

**Accessibility**: Keyboard selection, model details

---

## CRM Components

### CustomerList
**Location**: `src/components/crm/CustomerList.tsx`

List of customers with search and filter.

**Props**:
- `customers`: Array<Customer> - Customer data
- `onSelect`: (customer) => void - Selection handler

**Accessibility**: Keyboard navigation, search

---

### CustomerForm
**Location**: `src/components/crm/CustomerForm.tsx`

Form for creating/editing customers.

**Props**:
- `customer`: Customer - Customer data
- `onSubmit`: (data) => void - Submit handler

**Accessibility**: Form validation

---

### CustomerDetail
**Location**: `src/components/crm/CustomerDetail.tsx`

Detailed customer view.

**Props**:
- `customer`: Customer - Customer data

**Accessibility**: Semantic sections

---

### TaskList
**Location**: `src/components/crm/TaskList.tsx`

List of tasks with status.

**Props**:
- `tasks`: Array<Task> - Task data
- `onUpdate`: (task) => void - Update handler

**Accessibility**: Keyboard actions, status indicators

---

### TaskForm
**Location**: `src/components/crm/TaskForm.tsx`

Form for creating/editing tasks.

**Props**:
- `task`: Task - Task data
- `onSubmit`: (data) => void - Submit handler

**Accessibility**: Form validation, date picker

---

### ActivityTimeline
**Location**: `src/components/crm/ActivityTimeline.tsx`

Timeline of customer activities.

**Props**:
- `activities`: Array<Activity> - Activity data

**Accessibility**: Chronological list, timestamps

---

### CommunicationLog
**Location**: `src/components/crm/CommunicationLog.tsx`

Log of customer communications.

**Props**:
- `communications`: Array<Communication> - Communication data

**Accessibility**: Filterable list

---

### EmailIntegration
**Location**: `src/components/crm/EmailIntegration.tsx`

Email integration component.

**Props**:
- `customer`: Customer - Customer data

**Accessibility**: Email composer

---

### CallLogging
**Location**: `src/components/crm/CallLogging.tsx`

Call logging component.

**Props**:
- `customer`: Customer - Customer data

**Accessibility**: Form inputs

---

### DocumentAttachments
**Location**: `src/components/crm/DocumentAttachments.tsx`

Document attachment manager.

**Props**:
- `documents`: Array<Document> - Document data

**Accessibility**: File upload, download

---

## Admin Components

### UserList
**Location**: `src/components/admin/UserList.tsx`

List of system users.

**Props**:
- `users`: Array<User> - User data

**Accessibility**: Keyboard navigation

---

### UserForm
**Location**: `src/components/admin/UserForm.tsx`

Form for creating/editing users.

**Props**:
- `user`: User - User data
- `onSubmit`: (data) => void - Submit handler

**Accessibility**: Form validation

---

### UserSettings
**Location**: `src/components/admin/UserSettings.tsx`

User settings management.

**Props**:
- `user`: User - User data

**Accessibility**: Settings form

---

### UserActivityLog
**Location**: `src/components/admin/UserActivityLog.tsx`

User activity log viewer.

**Props**:
- `activities`: Array<Activity> - Activity data

**Accessibility**: Filterable log

---

### SystemSettings
**Location**: `src/components/admin/SystemSettings.tsx`

System-wide settings management.

**Props**:
- `settings`: object - System settings

**Accessibility**: Settings form

---

### SystemInformation
**Location**: `src/components/admin/SystemInformation.tsx`

System information display.

**Props**:
- `info`: object - System info

**Accessibility**: Semantic display

---

### DatabaseManagement
**Location**: `src/components/admin/DatabaseManagement.tsx`

Database management interface.

**Props**:
- `database`: object - Database info

**Accessibility**: Action buttons

---

### BackupManagement
**Location**: `src/components/admin/BackupManagement.tsx`

Backup management interface.

**Props**:
- `backups`: Array<Backup> - Backup data

**Accessibility**: Action buttons

---

## PDF Components

### PDFGenerator
**Location**: `src/components/pdf/PDFGenerator.tsx`

PDF generation interface.

**Props**:
- `project`: object - Project data
- `onGenerate`: () => void - Generate handler

**Accessibility**: Form inputs

---

### PDFConfiguration
**Location**: `src/components/pdf/PDFConfiguration.tsx`

PDF configuration options.

**Props**:
- `config`: object - PDF config
- `onChange`: (config) => void - Change handler

**Accessibility**: Form inputs

---

### PDFPreviewViewer
**Location**: `src/components/pdf/PDFPreviewViewer.tsx`

PDF preview component.

**Props**:
- `pdfUrl`: string - PDF URL

**Accessibility**: Zoom controls

---

### TemplateGallery
**Location**: `src/components/pdf/TemplateGallery.tsx`

PDF template gallery.

**Props**:
- `templates`: Array<Template> - Template data
- `onSelect`: (template) => void - Selection handler

**Accessibility**: Keyboard selection

---

### TemplateManagement
**Location**: `src/components/pdf/TemplateManagement.tsx`

Template management interface.

**Props**:
- `templates`: Array<Template> - Template data

**Accessibility**: CRUD actions

---

### PDFHistory
**Location**: `src/components/pdf/PDFHistory.tsx`

PDF generation history.

**Props**:
- `history`: Array<PDF> - PDF history

**Accessibility**: Filterable list

---

### PDFEmailer
**Location**: `src/components/pdf/PDFEmailer.tsx`

Email PDF component.

**Props**:
- `pdfUrl`: string - PDF URL

**Accessibility**: Email form

---

### PDFDownloader
**Location**: `src/components/pdf/PDFDownloader.tsx`

PDF download component.

**Props**:
- `pdfUrl`: string - PDF URL

**Accessibility**: Download button

---

## Pricing Components

### MatrixUpload
**Location**: `src/components/pricing/MatrixUpload.tsx`

Price matrix upload interface.

**Props**:
- `onUpload`: (file) => void - Upload handler

**Accessibility**: File upload

---

### MatrixPreview
**Location**: `src/components/pricing/MatrixPreview.tsx`

Price matrix preview.

**Props**:
- `matrix`: object - Matrix data

**Accessibility**: Table navigation

---

### MatrixList
**Location**: `src/components/pricing/MatrixList.tsx`

List of price matrices.

**Props**:
- `matrices`: Array<Matrix> - Matrix data

**Accessibility**: Keyboard navigation

---

### MatrixVersionHistory
**Location**: `src/components/pricing/MatrixVersionHistory.tsx`

Matrix version history.

**Props**:
- `versions`: Array<Version> - Version data

**Accessibility**: Timeline navigation

---

### PriceCalculator
**Location**: `src/components/pricing/PriceCalculator.tsx`

Price calculation interface.

**Props**:
- `matrix`: object - Matrix data
- `onCalculate`: (data) => void - Calculate handler

**Accessibility**: Form inputs

---

## Product Components

### ProductCatalog
**Location**: `src/components/products/ProductCatalog.tsx`

Product catalog view.

**Props**:
- `products`: Array<Product> - Product data

**Accessibility**: Grid navigation

---

### ProductSearch
**Location**: `src/components/products/ProductSearch.tsx`

Product search interface.

**Props**:
- `onSearch`: (query) => void - Search handler

**Accessibility**: Search input

---

### ProductForm
**Location**: `src/components/products/ProductForm.tsx`

Product creation/edit form.

**Props**:
- `product`: Product - Product data
- `onSubmit`: (data) => void - Submit handler

**Accessibility**: Form validation

---

### ProductComparison
**Location**: `src/components/products/ProductComparison.tsx`

Product comparison view.

**Props**:
- `products`: Array<Product> - Products to compare

**Accessibility**: Comparison table

---

### ProductBulkImport
**Location**: `src/components/products/ProductBulkImport.tsx`

Bulk product import interface.

**Props**:
- `onImport`: (file) => void - Import handler

**Accessibility**: File upload

---

### ProductAttributeManager
**Location**: `src/components/products/ProductAttributeManager.tsx`

Product attribute management.

**Props**:
- `attributes`: Array<Attribute> - Attribute data

**Accessibility**: CRUD actions

---

## 3D Visualization Components

### Viewer3D
**Location**: `src/components/3d/Viewer3D.tsx`

3D visualization viewer.

**Props**:
- `model`: object - 3D model data

**Accessibility**: Keyboard controls

---

### RoofModel
**Location**: `src/components/3d/RoofModel.tsx`

3D roof model component.

**Props**:
- `roofData`: object - Roof configuration

**Accessibility**: Model description

---

### ModulePlacement
**Location**: `src/components/3d/ModulePlacement.tsx`

Module placement interface.

**Props**:
- `modules`: Array<Module> - Module data

**Accessibility**: Placement controls

---

### CameraControls
**Location**: `src/components/3d/CameraControls.tsx`

3D camera controls.

**Props**:
- `camera`: object - Camera state

**Accessibility**: Keyboard controls

---

### ExportControls
**Location**: `src/components/3d/ExportControls.tsx`

3D export controls.

**Props**:
- `onExport`: (format) => void - Export handler

**Accessibility**: Export buttons

---

## Migration Components

### MigrationWizard
**Location**: `src/components/migration/MigrationWizard.tsx`

Data migration wizard.

**Props**:
- `onComplete`: () => void - Completion handler

**Accessibility**: Step navigation

---

### MigrationProgress
**Location**: `src/components/migration/MigrationProgress.tsx`

Migration progress indicator.

**Props**:
- `progress`: number - Progress percentage

**Accessibility**: Progress bar

---

### MigrationReport
**Location**: `src/components/migration/MigrationReport.tsx`

Migration report display.

**Props**:
- `report`: object - Migration report

**Accessibility**: Report sections

---

### MigrationErrorReport
**Location**: `src/components/migration/MigrationErrorReport.tsx`

Migration error report.

**Props**:
- `errors`: Array<Error> - Error data

**Accessibility**: Error list

---

## Update Components

### UpdateNotification
**Location**: `src/components/update/UpdateNotification.tsx`

Update notification component.

**Props**:
- `version`: string - New version

**Accessibility**: Notification

---

### UpdateProgress
**Location**: `src/components/update/UpdateProgress.tsx`

Update progress indicator.

**Props**:
- `progress`: number - Progress percentage

**Accessibility**: Progress bar

---

### UpdateReady
**Location**: `src/components/update/UpdateReady.tsx`

Update ready notification.

**Props**:
- `version`: string - New version

**Accessibility**: Action buttons

---

### ReleaseNotes
**Location**: `src/components/update/ReleaseNotes.tsx`

Release notes display.

**Props**:
- `notes`: string - Release notes

**Accessibility**: Semantic content

---

### UpdatePreferences
**Location**: `src/components/update/UpdatePreferences.tsx`

Update preferences settings.

**Props**:
- `preferences`: object - Update preferences

**Accessibility**: Settings form

---

## Settings Components

### NotificationPreferences
**Location**: `src/components/settings/NotificationPreferences.tsx`

Notification preferences settings.

**Props**:
- `preferences`: object - Notification preferences

**Accessibility**: Settings form

---

### NotificationHistory
**Location**: `src/components/settings/NotificationHistory.tsx`

Notification history view.

**Props**:
- `notifications`: Array<Notification> - Notification data

**Accessibility**: Filterable list

---

### WindowManagement
**Location**: `src/components/settings/WindowManagement.tsx`

Window management settings.

**Props**:
- `settings`: object - Window settings

**Accessibility**: Settings form

---

## Component Development Guidelines

### Creating New Components

1. **Component File**: Create `ComponentName.tsx`
2. **Story File**: Create `ComponentName.stories.tsx`
3. **Documentation**: Add JSDoc comments
4. **Accessibility**: Implement ARIA attributes
5. **Testing**: Add interaction tests
6. **Export**: Add to `index.ts`

### Component Checklist

- [ ] TypeScript types defined
- [ ] Props documented
- [ ] Accessibility features implemented
- [ ] Story file created
- [ ] Multiple story variants
- [ ] Interactive examples
- [ ] Error states handled
- [ ] Loading states handled
- [ ] Responsive design
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] High contrast mode support

### Accessibility Requirements

All components must meet WCAG 2.1 Level AA standards:

- **Perceivable**: Text alternatives, adaptable content, distinguishable
- **Operable**: Keyboard accessible, enough time, navigable
- **Understandable**: Readable, predictable, input assistance
- **Robust**: Compatible with assistive technologies

### Testing Components

1. **Visual Testing**: Check in Storybook
2. **Interaction Testing**: Use addon-interactions
3. **Accessibility Testing**: Use addon-a11y
4. **Unit Testing**: Jest + React Testing Library
5. **E2E Testing**: Playwright

---

## Additional Resources

- [Storybook Guide](./STORYBOOK_GUIDE.md)
- [Component API Reference](./API_REFERENCE.md)
- [Accessibility Guidelines](./ACCESSIBILITY.md)
- [Design System](./DESIGN_SYSTEM.md)
