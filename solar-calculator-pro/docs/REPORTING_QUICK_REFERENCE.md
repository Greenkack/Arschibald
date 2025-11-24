# Reporting and Analytics - Quick Reference

## API Endpoints

### Report Builder

```http
# Create Report
POST /api/v1/reporting/reports
Content-Type: application/json

{
  "definition": {
    "name": "Monthly Sales Report",
    "report_type": "sales",
    "data_source": "projects",
    "fields": [
      {"name": "customer_name", "label": "Customer", "data_type": "string"},
      {"name": "total_price", "label": "Revenue", "data_type": "number", "aggregation": "sum"}
    ],
    "filters": [
      {"field": "created_at", "operator": "gte", "value": "2024-01-01"}
    ],
    "group_by": ["customer_name"]
  },
  "is_public": false
}

# Execute Report
POST /api/v1/reporting/reports/execute
{
  "report_id": 1,
  "parameters": {},
  "format": "json"
}

# List Reports
GET /api/v1/reporting/reports?report_type=sales

# Get Report
GET /api/v1/reporting/reports/1

# Update Report
PUT /api/v1/reporting/reports/1

# Delete Report
DELETE /api/v1/reporting/reports/1
```

### Scheduled Reports

```http
# Create Schedule
POST /api/v1/reporting/schedules
{
  "report_id": 1,
  "frequency": "weekly",
  "time_of_day": "09:00",
  "recipients": ["manager@company.com"],
  "format": "pdf",
  "enabled": true
}

# List Schedules
GET /api/v1/reporting/schedules?report_id=1

# Update Schedule
PUT /api/v1/reporting/schedules/1

# Delete Schedule
DELETE /api/v1/reporting/schedules/1
```

### Dashboards

```http
# Create Dashboard
POST /api/v1/reporting/dashboards
{
  "name": "Sales Dashboard",
  "description": "Monthly sales overview",
  "is_public": false,
  "layout": "grid"
}

# Add Widget
POST /api/v1/reporting/dashboards/1/widgets
{
  "dashboard_id": 1,
  "config": {
    "widget_type": "chart",
    "title": "Revenue Trend",
    "data_source": "projects",
    "query": {"sql": "SELECT date, SUM(total_price) FROM projects GROUP BY date"},
    "visualization": {
      "chart_type": "line",
      "x_axis": "date",
      "y_axis": "total_price"
    },
    "size": "large"
  },
  "position_x": 0,
  "position_y": 0
}

# Get Dashboard
GET /api/v1/reporting/dashboards/1

# List Dashboards
GET /api/v1/reporting/dashboards
```

### KPI Tracking

```http
# Create KPI
POST /api/v1/reporting/kpis
{
  "name": "Monthly Revenue",
  "metric": "revenue",
  "target": {
    "metric": "revenue",
    "target_value": 100000,
    "period": "monthly",
    "comparison_operator": "gte"
  },
  "data_source": "projects",
  "calculation": {
    "sql": "SELECT SUM(total_price) FROM projects WHERE MONTH(created_at) = MONTH(CURRENT_DATE)"
  }
}

# Calculate KPI
GET /api/v1/reporting/kpis/1/calculate

# List KPIs
GET /api/v1/reporting/kpis
```

### Predictive Analytics

```http
# Generate Predictions
POST /api/v1/reporting/predictions
{
  "model_type": "linear_regression",
  "data_source": "projects",
  "target_field": "total_price",
  "feature_fields": ["module_count", "system_size"],
  "prediction_period": 30,
  "confidence_level": 0.95
}
```

### Data Export

```http
# Export Data
POST /api/v1/reporting/exports
{
  "data_source": "projects",
  "filters": [
    {"field": "status", "operator": "eq", "value": "completed"}
  ],
  "fields": ["customer_name", "total_price", "created_at"],
  "format": "excel",
  "include_headers": true,
  "german_formatting": true
}

# Download Export
GET /api/v1/reporting/exports/download/1
```

## Common Use Cases

### 1. Sales Report with Aggregation

```python
report_definition = {
    "name": "Sales by Customer",
    "report_type": "sales",
    "data_source": "projects",
    "fields": [
        {"name": "customer_name", "label": "Customer", "data_type": "string"},
        {"name": "total_price", "label": "Total Revenue", "data_type": "number", "aggregation": "sum"},
        {"name": "id", "label": "Project Count", "data_type": "number", "aggregation": "count"}
    ],
    "group_by": ["customer_name"],
    "sorts": [{"field": "total_price", "direction": "desc"}],
    "limit": 10
}
```

### 2. Daily Scheduled Report

```python
schedule = {
    "report_id": 1,
    "frequency": "daily",
    "time_of_day": "08:00",
    "recipients": ["team@company.com"],
    "format": "pdf",
    "enabled": true
}
```

### 3. Revenue KPI

```python
kpi = {
    "name": "Monthly Revenue Target",
    "metric": "revenue",
    "target": {
        "target_value": 100000,
        "period": "monthly"
    },
    "data_source": "projects",
    "calculation": {
        "sql": "SELECT SUM(total_price) FROM projects WHERE status='completed' AND MONTH(created_at) = MONTH(CURRENT_DATE)"
    }
}
```

### 4. Sales Forecast

```python
prediction = {
    "model_type": "time_series",
    "data_source": "projects",
    "target_field": "total_price",
    "feature_fields": ["created_at", "module_count"],
    "prediction_period": 90
}
```

## Response Examples

### Report Execution Response

```json
{
  "id": 1,
  "name": "Monthly Sales Report",
  "report_type": "sales",
  "executed_at": "2024-01-15T10:30:00Z",
  "data": [
    {"customer_name": "Customer A", "total_price": 50000},
    {"customer_name": "Customer B", "total_price": 35000}
  ],
  "metadata": {
    "execution_time_ms": 245,
    "row_count": 2
  },
  "visualizations": [
    {
      "type": "bar",
      "title": "Revenue by Customer",
      "data": {
        "labels": ["Customer A", "Customer B"],
        "values": [50000, 35000]
      }
    }
  ]
}
```

### KPI Response

```json
{
  "id": 1,
  "name": "Monthly Revenue",
  "metric": "revenue",
  "current_value": 85000,
  "target_value": 100000,
  "achievement_percentage": 85.0,
  "trend": "up",
  "period": "monthly",
  "last_updated": "2024-01-15T10:30:00Z"
}
```

### Prediction Response

```json
{
  "model_type": "linear_regression",
  "predictions": [
    {"date": "2024-01-16", "predicted_value": 52000},
    {"date": "2024-01-17", "predicted_value": 53500}
  ],
  "confidence_intervals": [
    {"date": "2024-01-16", "lower_bound": 48000, "upper_bound": 56000}
  ],
  "accuracy_metrics": {
    "mse": 1250000,
    "rmse": 1118.03,
    "r2_score": 0.85
  },
  "feature_importance": {
    "module_count": 0.65,
    "system_size": 0.35
  }
}
```

## Error Handling

All endpoints return standard error responses:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

Common status codes:
- 200: Success
- 201: Created
- 204: No Content (delete)
- 400: Bad Request
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error
