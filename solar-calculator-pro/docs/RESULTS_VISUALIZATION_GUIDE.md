# Results Visualization Guide

## Overview

The Results Visualization system provides interactive dashboards, comparison views, scenario analysis, sensitivity analysis, and what-if analysis for solar calculator results.

## Features

### 1. Interactive Dashboards

Create customizable dashboards with various widget types:

- **Metric Widgets**: Display key performance indicators
- **Chart Widgets**: Visualize data with multiple chart types
- **Table Widgets**: Show detailed data in tabular format
- **Text Widgets**: Add custom text and descriptions

**Example:**
```typescript
const dashboard = await createDashboard({
  name: "Solar System Dashboard",
  calculation_id: 123,
  widgets: [
    {
      id: "system-size",
      type: "metric",
      title: "System Size",
      position: { x: 0, y: 0, width: 3, height: 2 },
      data: { value: 10.5, unit: "kWp" }
    }
  ]
});
```

### 2. Comparison Views

Compare multiple calculations side-by-side:

- Visual comparison with charts
- Detailed comparison tables
- Summary statistics (average, min, max)
- Customizable metrics selection

**Example:**
```typescript
const comparison = await createComparison({
  name: "System Comparison",
  calculation_ids: [123, 124, 125],
  metrics_to_compare: ["total_cost", "annual_savings", "payback_period"],
  chart_type: "bar"
});
```

### 3. Scenario Analysis

Analyze multiple scenarios with varying parameters:

- Best case, worst case, and base case scenarios
- Custom scenario generation
- Parameter variation ranges
- Scenario comparison

**Example:**
```typescript
const scenarioAnalysis = await createScenarioAnalysis({
  name: "System Size Scenarios",
  base_calculation_id: 123,
  parameters: [
    {
      name: "system_size",
      base_value: 10.0,
      min_value: 8.0,
      max_value: 12.0,
      step: 0.5,
      unit: "kWp"
    }
  ],
  num_scenarios: 5
});
```

### 4. Sensitivity Analysis

Understand parameter impacts on results:

- Tornado charts showing parameter sensitivity
- Impact on ROI, payback period, and savings
- Parameter variation analysis
- Sensitivity ranking

**Example:**
```typescript
const sensitivityAnalysis = await createSensitivityAnalysis({
  name: "Parameter Sensitivity",
  base_calculation_id: 123,
  parameters: [
    {
      name: "electricity_price",
      base_value: 0.30,
      variation_range: 20,  // ±20%
      unit: "€/kWh"
    }
  ],
  num_points: 10
});
```

### 5. What-If Analysis

Explore "what if" scenarios with parameter changes:

- Compare original vs. modified results
- Show delta metrics
- Multiple parameter changes
- Instant recalculation

**Example:**
```typescript
const whatIfAnalysis = await createWhatIfAnalysis({
  name: "What If Analysis",
  base_calculation_id: 123,
  parameter_changes: [
    {
      name: "system_size",
      current_value: 10.0,
      new_value: 12.0,
      unit: "kWp"
    }
  ]
});
```

## API Endpoints

### Dashboards

- `POST /api/v1/results-visualization/dashboards` - Create dashboard
- `GET /api/v1/results-visualization/dashboards/{id}` - Get dashboard
- `PUT /api/v1/results-visualization/dashboards/{id}` - Update dashboard
- `DELETE /api/v1/results-visualization/dashboards/{id}` - Delete dashboard
- `POST /api/v1/results-visualization/dashboards/default` - Create default dashboard

### Comparisons

- `POST /api/v1/results-visualization/comparisons` - Create comparison
- `GET /api/v1/results-visualization/comparisons/{id}` - Get comparison
- `POST /api/v1/results-visualization/comparisons/compare` - Compare calculations

### Scenario Analysis

- `POST /api/v1/results-visualization/scenarios` - Create scenario analysis
- `GET /api/v1/results-visualization/scenarios/{id}` - Get scenario analysis

### Sensitivity Analysis

- `POST /api/v1/results-visualization/sensitivity` - Create sensitivity analysis
- `GET /api/v1/results-visualization/sensitivity/{id}` - Get sensitivity analysis

### What-If Analysis

- `POST /api/v1/results-visualization/what-if` - Create what-if analysis
- `GET /api/v1/results-visualization/what-if/{id}` - Get what-if analysis

### Export

- `POST /api/v1/results-visualization/export` - Export visualization
- `GET /api/v1/results-visualization/export/formats` - Get available formats

## Export Formats

Supported export formats:

- **PDF**: High-quality PDF documents
- **Excel**: Spreadsheet format with data and charts
- **CSV**: Comma-separated values for data
- **JSON**: Machine-readable format
- **PNG**: Image format for charts
- **SVG**: Vector graphics for charts

## Frontend Components

### InteractiveDashboard

```tsx
import { InteractiveDashboard } from '@/components/results/InteractiveDashboard';

<InteractiveDashboard
  dashboardId="dashboard-123"
  onSave={(dashboard) => console.log('Saved:', dashboard)}
/>
```

### ComparisonView

```tsx
import { ComparisonView } from '@/components/results/ComparisonView';

<ComparisonView
  calculationIds={[123, 124, 125]}
  onExport={(format) => console.log('Export:', format)}
/>
```

## Best Practices

1. **Dashboard Design**
   - Keep dashboards focused on key metrics
   - Use appropriate widget types for data
   - Organize widgets logically
   - Provide clear titles and descriptions

2. **Comparisons**
   - Compare similar calculation types
   - Select relevant metrics
   - Use appropriate chart types
   - Include context in descriptions

3. **Scenario Analysis**
   - Define realistic parameter ranges
   - Include best/worst case scenarios
   - Generate sufficient scenarios for analysis
   - Document assumptions

4. **Sensitivity Analysis**
   - Focus on key parameters
   - Use appropriate variation ranges
   - Interpret tornado charts correctly
   - Consider parameter interactions

5. **What-If Analysis**
   - Make realistic parameter changes
   - Compare multiple scenarios
   - Document reasoning for changes
   - Consider cascading effects

## Performance Considerations

- Dashboards are cached for faster loading
- Large comparisons may take longer to process
- Scenario generation is optimized for speed
- Export operations are asynchronous

## Troubleshooting

### Dashboard Not Loading

- Check calculation_id is valid
- Verify API endpoint is accessible
- Check browser console for errors

### Comparison Shows No Data

- Ensure calculation_ids exist
- Verify metrics are available
- Check API response format

### Export Fails

- Verify export format is supported
- Check file size limits
- Ensure sufficient permissions

## Future Enhancements

- Real-time collaboration on dashboards
- Advanced chart customization
- Machine learning predictions
- Automated insights generation
- Mobile-optimized views
