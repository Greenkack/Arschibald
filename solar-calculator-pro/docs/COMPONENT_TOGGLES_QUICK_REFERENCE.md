# Component Toggles Quick Reference

## Quick Start

### Backend

```python
from backend.services.component_toggle_service import ComponentToggleService

service = ComponentToggleService(db)

# Toggle a chart
service.toggle_chart('line_chart', enabled=True, user_id=user.id)

# Get visible charts
charts = service.get_visible_charts(user_id=user.id)

# Toggle export format
service.toggle_export_format('pdf', enabled=True, user_id=user.id)

# Bulk toggle
service.bulk_toggle('chart', enabled=True, user_id=user.id)

# Reset to defaults
service.reset_to_defaults(user_id=user.id)
```

### Frontend

```typescript
import { useComponentToggles } from '../hooks/useComponentToggles';

const {
  visibleCharts,
  toggleChart,
  isChartVisible,
  availableExportFormats,
  toggleExportFormat,
  isExportFormatAvailable
} = useComponentToggles();

// Check if chart is visible
if (isChartVisible('line_chart')) {
  // Render chart
}

// Toggle chart
await toggleChart('bar_chart', true);

// Check export format
if (isExportFormatAvailable('pdf')) {
  // Show export button
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/component-toggles/charts` | GET | Get all chart toggles |
| `/api/v1/component-toggles/charts/toggle` | POST | Toggle a chart |
| `/api/v1/component-toggles/charts/visible` | GET | Get visible charts |
| `/api/v1/component-toggles/form-fields` | GET | Get form field toggles |
| `/api/v1/component-toggles/form-fields/toggle` | POST | Toggle a form field |
| `/api/v1/component-toggles/calculation-options` | GET | Get calculation options |
| `/api/v1/component-toggles/calculation-options/toggle` | POST | Toggle calculation option |
| `/api/v1/component-toggles/export-formats` | GET | Get export formats |
| `/api/v1/component-toggles/export-formats/toggle` | POST | Toggle export format |
| `/api/v1/component-toggles/themes` | GET | Get themes |
| `/api/v1/component-toggles/themes/toggle` | POST | Toggle theme |
| `/api/v1/component-toggles/languages` | GET | Get languages |
| `/api/v1/component-toggles/languages/toggle` | POST | Toggle language |
| `/api/v1/component-toggles/bulk-toggle` | POST | Bulk toggle category |
| `/api/v1/component-toggles/reset` | POST | Reset to defaults |

## Toggle Categories

- `chart` - Chart visibility
- `form_field` - Form field visibility/editability
- `calculation_option` - Calculation options
- `export_format` - Export format availability
- `ui_theme` - UI theme availability
- `language` - Language availability

## Common Chart Types

- `line_chart` - Line Chart
- `bar_chart` - Bar Chart
- `pie_chart` - Pie Chart
- `area_chart` - Area Chart
- `donut_chart` - Donut Chart
- `scatter_chart` - Scatter Chart
- `radar_chart` - Radar Chart
- `waterfall_chart` - Waterfall Chart

## Common Export Formats

- `pdf` - PDF
- `excel` - Excel
- `csv` - CSV
- `json` - JSON
- `xml` - XML

## Common Themes

- `light` - Light Theme
- `dark` - Dark Theme
- `high_contrast` - High Contrast
- `custom` - Custom Theme

## Common Languages

- `de` - German (Deutsch)
- `en` - English
- `fr` - French (Français)
- `es` - Spanish (Español)
- `it` - Italian (Italiano)
- `nl` - Dutch (Nederlands)
- `pl` - Polish (Polski)
- `cs` - Czech (Čeština)

## Request Examples

### Toggle Chart

```json
POST /api/v1/component-toggles/charts/toggle
{
  "chart_type": "line_chart",
  "enabled": true
}
```

### Toggle Form Field

```json
POST /api/v1/component-toggles/form-fields/toggle
{
  "form_name": "solar_calculator",
  "field_key": "roof_area",
  "enabled": true
}
```

### Toggle Calculation Option

```json
POST /api/v1/component-toggles/calculation-options/toggle
{
  "calculator_type": "solar",
  "option_key": "battery_storage",
  "enabled": true
}
```

### Bulk Toggle

```json
POST /api/v1/component-toggles/bulk-toggle
{
  "category": "chart",
  "enabled": true
}
```

## Response Examples

### Visible Charts

```json
{
  "charts": ["line_chart", "bar_chart", "pie_chart"]
}
```

### Available Export Formats

```json
{
  "formats": ["pdf", "excel", "csv"]
}
```

### Available Themes

```json
{
  "themes": ["light", "dark", "high_contrast"]
}
```

### Available Languages

```json
{
  "languages": ["de", "en", "fr"]
}
```

## Admin UI Component

```typescript
import { ComponentToggleManager } from '../components/admin/ComponentToggleManager';

<ComponentToggleManager />
```

## Database Migration

```bash
python backend/migrations/add_component_toggles.py
```

## Files

- **Backend Service**: `backend/services/component_toggle_service.py`
- **Database Models**: `backend/models/component_toggle_models.py`
- **Pydantic Schemas**: `backend/models/component_toggle_schemas.py`
- **API Endpoints**: `backend/api/v1/component_toggles.py`
- **Migration Script**: `backend/migrations/add_component_toggles.py`
- **Frontend Hook**: `frontend/src/hooks/useComponentToggles.ts`
- **Admin Component**: `frontend/src/components/admin/ComponentToggleManager.tsx`
- **Styles**: `frontend/src/components/admin/ComponentToggleManager.css`

## Requirements

- ✅ Chart visibility toggles
- ✅ Form field toggles
- ✅ Calculation option toggles
- ✅ Export format toggles
- ✅ UI theme toggles
- ✅ Language toggles
- ✅ Requirements 2.3, 7.1
