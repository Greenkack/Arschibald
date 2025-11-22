# Component-Level Feature Toggles Guide

## Overview

The Component-Level Feature Toggle system provides granular control over individual UI components and features in the Solar Calculator Pro application. This allows administrators to enable or disable specific functionality at a component level.

## Features

### 1. Chart Visibility Toggles

Control which chart types are visible to users:

- **Line Charts**: Time series and trend visualization
- **Bar Charts**: Comparison and categorical data
- **Pie Charts**: Proportional data visualization
- **Area Charts**: Cumulative data over time
- **Donut Charts**: Proportional data with center space
- **Scatter Charts**: Correlation and distribution
- **Radar Charts**: Multi-dimensional comparison
- **Waterfall Charts**: Sequential value changes

### 2. Form Field Toggles

Enable or disable specific form fields:

- Control visibility of individual input fields
- Manage field editability
- Organize forms by showing only relevant fields
- Create custom form configurations per user

### 3. Calculation Option Toggles

Control which calculation options are available:

- **Solar Calculator Options**: Module types, inverter options, battery storage
- **Heat Pump Options**: COP calculations, dynamic tariffs, seasonal analysis
- **Combined System Options**: Synergy calculations, optimization strategies

### 4. Export Format Toggles

Manage available export formats:

- **PDF**: Portable Document Format
- **Excel**: Microsoft Excel spreadsheet
- **CSV**: Comma-separated values
- **JSON**: JavaScript Object Notation
- **XML**: Extensible Markup Language

### 5. UI Theme Toggles

Control available UI themes:

- **Light Theme**: Standard light color scheme
- **Dark Theme**: Dark color scheme for low-light environments
- **High Contrast**: Enhanced visibility theme
- **Custom Theme**: User-defined color schemes

### 6. Language Toggles

Manage available languages:

- **German (de)**: Deutsch
- **English (en)**: English
- **French (fr)**: Français
- **Spanish (es)**: Español
- **Italian (it)**: Italiano
- **Dutch (nl)**: Nederlands
- **Polish (pl)**: Polski
- **Czech (cs)**: Čeština

## Backend API

### Endpoints

#### Chart Toggles

```http
GET /api/v1/component-toggles/charts
POST /api/v1/component-toggles/charts/toggle
GET /api/v1/component-toggles/charts/visible
```

#### Form Field Toggles

```http
GET /api/v1/component-toggles/form-fields
POST /api/v1/component-toggles/form-fields/toggle
GET /api/v1/component-toggles/form-fields/enabled/{form_name}
```

#### Calculation Option Toggles

```http
GET /api/v1/component-toggles/calculation-options
POST /api/v1/component-toggles/calculation-options/toggle
GET /api/v1/component-toggles/calculation-options/enabled/{calculator_type}
```

#### Export Format Toggles

```http
GET /api/v1/component-toggles/export-formats
POST /api/v1/component-toggles/export-formats/toggle
GET /api/v1/component-toggles/export-formats/available
```

#### Theme Toggles

```http
GET /api/v1/component-toggles/themes
POST /api/v1/component-toggles/themes/toggle
GET /api/v1/component-toggles/themes/available
```

#### Language Toggles

```http
GET /api/v1/component-toggles/languages
POST /api/v1/component-toggles/languages/toggle
GET /api/v1/component-toggles/languages/available
```

#### Bulk Operations

```http
POST /api/v1/component-toggles/bulk-toggle
POST /api/v1/component-toggles/reset
GET /api/v1/component-toggles/all
```

### Example Requests

#### Toggle a Chart

```javascript
POST /api/v1/component-toggles/charts/toggle
{
  "chart_type": "line_chart",
  "enabled": true
}
```

#### Toggle a Form Field

```javascript
POST /api/v1/component-toggles/form-fields/toggle
{
  "form_name": "solar_calculator",
  "field_key": "roof_area",
  "enabled": true
}
```

#### Toggle a Calculation Option

```javascript
POST /api/v1/component-toggles/calculation-options/toggle
{
  "calculator_type": "solar",
  "option_key": "battery_storage",
  "enabled": true
}
```

#### Bulk Toggle

```javascript
POST /api/v1/component-toggles/bulk-toggle
{
  "category": "chart",
  "enabled": true
}
```

## Frontend Usage

### Using the Hook

```typescript
import { useComponentToggles } from '../hooks/useComponentToggles';

function MyComponent() {
  const {
    visibleCharts,
    toggleChart,
    isChartVisible,
    availableExportFormats,
    toggleExportFormat,
    isExportFormatAvailable,
    loading,
    error
  } = useComponentToggles();

  // Check if a chart is visible
  if (isChartVisible('line_chart')) {
    // Render line chart
  }

  // Check if an export format is available
  if (isExportFormatAvailable('pdf')) {
    // Show PDF export button
  }

  // Toggle a chart
  const handleToggle = async () => {
    await toggleChart('bar_chart', true);
  };

  return (
    <div>
      {/* Your component JSX */}
    </div>
  );
}
```

### Conditional Rendering

```typescript
// Conditionally render charts
{isChartVisible('line_chart') && (
  <LineChart data={chartData} />
)}

// Conditionally render export buttons
{availableExportFormats.map(format => (
  <Button
    key={format}
    label={`Export as ${format.toUpperCase()}`}
    onClick={() => handleExport(format)}
  />
))}

// Conditionally render form fields
{isFormFieldEnabled('solar_calculator', 'battery_storage') && (
  <FormField name="battery_storage" />
)}
```

### Admin Component

```typescript
import { ComponentToggleManager } from '../components/admin/ComponentToggleManager';

function AdminPanel() {
  return (
    <div>
      <h1>Admin Panel</h1>
      <ComponentToggleManager />
    </div>
  );
}
```

## Database Schema

### component_toggles Table

```sql
CREATE TABLE component_toggles (
  id INTEGER PRIMARY KEY,
  category VARCHAR(50) NOT NULL,  -- chart, form_field, calculation_option, export_format, ui_theme, language
  component_key VARCHAR(255) NOT NULL,
  component_name VARCHAR(255) NOT NULL,
  enabled BOOLEAN DEFAULT TRUE,
  toggle_type VARCHAR(50) DEFAULT 'feature',  -- visibility, feature, permission
  user_id INTEGER,  -- NULL for global toggles
  metadata JSON DEFAULT '{}',
  description VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE INDEX idx_component_toggles_category ON component_toggles(category);
CREATE INDEX idx_component_toggles_key ON component_toggles(component_key);
CREATE INDEX idx_component_toggles_user ON component_toggles(user_id);
```

## Use Cases

### 1. Progressive Feature Rollout

Enable new features for specific users or groups:

```python
# Enable new chart type for beta users
service.toggle_chart('waterfall_chart', enabled=True, user_id=beta_user.id)
```

### 2. Customized User Experience

Create different experiences for different user types:

```python
# Basic users: Only essential charts
service.bulk_toggle('chart', enabled=False, user_id=basic_user.id)
service.toggle_chart('line_chart', enabled=True, user_id=basic_user.id)
service.toggle_chart('bar_chart', enabled=True, user_id=basic_user.id)

# Premium users: All charts
service.bulk_toggle('chart', enabled=True, user_id=premium_user.id)
```

### 3. Simplified Interfaces

Hide advanced features for novice users:

```python
# Hide advanced calculation options
service.toggle_calculation_option(
    'solar',
    'advanced_shading_analysis',
    enabled=False,
    user_id=novice_user.id
)
```

### 4. Compliance and Licensing

Control feature access based on licensing:

```python
# Disable premium export formats for free tier
service.toggle_export_format('excel', enabled=False, user_id=free_user.id)
service.toggle_export_format('json', enabled=False, user_id=free_user.id)
```

## Best Practices

### 1. Default Values

Always provide sensible defaults:

```python
# Enable commonly used features by default
defaults = {
    'charts': ['line_chart', 'bar_chart', 'pie_chart'],
    'export_formats': ['pdf', 'csv'],
    'themes': ['light', 'dark'],
    'languages': ['de', 'en']
}
```

### 2. User-Specific vs Global

- Use **global toggles** (user_id=None) for system-wide settings
- Use **user-specific toggles** for personalization

### 3. Caching

Cache toggle states to minimize database queries:

```typescript
// Frontend caching in the hook
const [visibleCharts, setVisibleCharts] = useState<string[]>([]);

// Backend caching in the service
@lru_cache(maxsize=128)
def get_visible_charts(user_id: int) -> List[str]:
    # ...
```

### 4. Bulk Operations

Use bulk operations for efficiency:

```python
# Enable all charts at once
service.bulk_toggle('chart', enabled=True, user_id=user.id)

# Instead of individual toggles
for chart in charts:
    service.toggle_chart(chart, enabled=True, user_id=user.id)  # Slower
```

### 5. Validation

Always validate toggle states before rendering:

```typescript
// Check if feature is enabled before using it
if (isChartVisible('line_chart')) {
  renderLineChart();
} else {
  renderAlternativeVisualization();
}
```

## Troubleshooting

### Toggles Not Persisting

Check database connection and ensure migrations are run:

```bash
python backend/migrations/add_component_toggles.py
```

### Toggles Not Updating in UI

Refresh the toggle state:

```typescript
const { refresh } = useComponentToggles();
await refresh();
```

### Performance Issues

Enable caching and use bulk operations:

```python
# Use bulk queries instead of individual queries
toggles = service.get_all_toggles(user_id=user.id, category='chart')
```

## Migration

To add component toggles to an existing installation:

1. Run the migration script:
```bash
python backend/migrations/add_component_toggles.py
```

2. Initialize default toggles:
```python
from backend.services.component_toggle_service import ComponentToggleService
service = ComponentToggleService(db)
service._create_default_toggles()
```

3. Update frontend to use the hook:
```typescript
import { useComponentToggles } from '../hooks/useComponentToggles';
```

## Requirements Validation

This implementation satisfies:

- ✅ **Requirement 2.3**: Component-level UI customization
- ✅ **Requirement 7.1**: Feature toggle system integration
- ✅ **Chart visibility toggles**: Complete
- ✅ **Form field toggles**: Complete
- ✅ **Calculation option toggles**: Complete
- ✅ **Export format toggles**: Complete
- ✅ **UI theme toggles**: Complete
- ✅ **Language toggles**: Complete

## Support

For issues or questions:
- Check the API documentation: `/api/v1/docs`
- Review the component source code
- Contact the development team
