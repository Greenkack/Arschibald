# Results Visualization Quick Reference

## Quick Start

### Create Interactive Dashboard

```python
from services.results_visualization_service import ResultsVisualizationService

service = ResultsVisualizationService()

dashboard = service.create_default_dashboard(
    calculation_id=123,
    calculation_data=your_calculation_data
)
```

### Create Comparison

```python
comparison = service.compare_calculations(
    calculation_data_list=[calc1, calc2, calc3],
    metrics=["total_cost", "annual_savings", "payback_period"]
)
```

### Create Scenario Analysis

```python
from models.results_schemas import ScenarioParameter

analysis = service.create_scenario_analysis(
    name="Scenarios",
    base_calculation_id=123,
    parameters=[
        ScenarioParameter(
            name="system_size",
            base_value=10.0,
            min_value=8.0,
            max_value=12.0,
            step=0.5,
            unit="kWp"
        )
    ],
    base_calculation_data=base_data,
    num_scenarios=5
)
```

### Create Sensitivity Analysis

```python
from models.results_schemas import SensitivityParameter

analysis = service.create_sensitivity_analysis(
    name="Sensitivity",
    base_calculation_id=123,
    parameters=[
        SensitivityParameter(
            name="electricity_price",
            base_value=0.30,
            variation_range=20.0,  # ±20%
            unit="€/kWh"
        )
    ],
    base_calculation_data=base_data
)
```

### Create What-If Analysis

```python
from models.results_schemas import WhatIfParameter

analysis = service.create_what_if_analysis(
    name="What If",
    base_calculation_id=123,
    parameter_changes=[
        WhatIfParameter(
            name="system_size",
            current_value=10.0,
            new_value=12.0,
            unit="kWp"
        )
    ],
    base_calculation_data=base_data
)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/results-visualization/dashboards` | Create dashboard |
| GET | `/api/v1/results-visualization/dashboards/{id}` | Get dashboard |
| POST | `/api/v1/results-visualization/comparisons` | Create comparison |
| POST | `/api/v1/results-visualization/scenarios` | Create scenario analysis |
| POST | `/api/v1/results-visualization/sensitivity` | Create sensitivity analysis |
| POST | `/api/v1/results-visualization/what-if` | Create what-if analysis |
| POST | `/api/v1/results-visualization/export` | Export visualization |

## Frontend Components

### Interactive Dashboard

```tsx
import { InteractiveDashboard } from '@/components/results/InteractiveDashboard';

<InteractiveDashboard
  dashboardId="dashboard-123"
  onSave={(dashboard) => console.log(dashboard)}
/>
```

### Comparison View

```tsx
import { ComparisonView } from '@/components/results/ComparisonView';

<ComparisonView
  calculationIds={[123, 124, 125]}
  onExport={(format) => handleExport(format)}
/>
```

## Widget Types

| Type | Description | Use Case |
|------|-------------|----------|
| `metric` | Display single value | KPIs, totals |
| `chart` | Visualize data | Trends, comparisons |
| `table` | Show detailed data | Lists, breakdowns |
| `text` | Custom text | Notes, descriptions |

## Chart Types

- `line` - Time series, trends
- `bar` - Comparisons, categories
- `pie` - Proportions, percentages
- `area` - Cumulative values
- `scatter` - Correlations
- `radar` - Multi-dimensional
- `waterfall` - Sequential changes

## Export Formats

- `pdf` - Documents
- `excel` - Spreadsheets
- `csv` - Data files
- `json` - API integration
- `png` - Images
- `svg` - Vector graphics

## Common Metrics

- `total_cost` - Total system cost
- `annual_savings` - Yearly savings
- `payback_period` - Years to break even
- `system_size` - System capacity (kWp)
- `roi` - Return on investment (%)
- `co2_savings` - CO2 reduction (kg)

## Best Practices

1. **Dashboards**: Focus on 4-8 key metrics
2. **Comparisons**: Compare 2-5 similar items
3. **Scenarios**: Generate 3-10 scenarios
4. **Sensitivity**: Test 3-6 key parameters
5. **What-If**: Change 1-3 parameters at a time

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Dashboard not loading | Check calculation_id exists |
| Comparison empty | Verify calculation_ids are valid |
| Export fails | Check format is supported |
| Slow performance | Reduce number of widgets/scenarios |

## Performance Tips

- Cache dashboards for reuse
- Limit comparison to 5 items
- Use appropriate scenario count
- Export asynchronously
- Optimize chart data

## Support

- Documentation: `/docs/RESULTS_VISUALIZATION_GUIDE.md`
- Demo: `backend/demo_results_visualization.py`
- API Docs: `/api/v1/docs`
