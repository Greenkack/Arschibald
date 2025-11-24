# Reporting and Analytics - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Run Database Migration

```bash
cd solar-calculator-pro/backend
python migrations/add_reporting_tables.py
```

### 2. Test the System

```bash
python demo_reporting.py
```

### 3. Create Your First Report

```python
from backend.services.reporting_service import ReportingService
from backend.models.reporting_schemas import *

# Initialize service
service = ReportingService(db)

# Define report
report = ReportCreate(
    definition=ReportDefinition(
        name="Sales Report",
        report_type=ReportType.SALES,
        data_source="projects",
        fields=[
            ReportField(name="customer_name", label="Customer", data_type="string"),
            ReportField(name="total_price", label="Revenue", data_type="number", aggregation=AggregationType.SUM)
        ],
        group_by=["customer_name"]
    ),
    owner_id=1
)

# Create and execute
created_report = service.create_report(report, user_id=1)
result = service.execute_report(
    ReportExecute(report_id=created_report.id, format=ReportFormat.JSON),
    user_id=1
)
```

### 4. Schedule a Report

```python
schedule = service.create_schedule(ScheduleCreate(
    report_id=1,
    frequency=ScheduleFrequency.DAILY,
    time_of_day="08:00",
    recipients=["team@company.com"],
    format=ReportFormat.PDF
))
```

### 5. Create a Dashboard

```python
# Create dashboard
dashboard = service.create_dashboard(
    DashboardCreate(name="Sales Dashboard"),
    user_id=1
)

# Add widget
widget = service.create_widget(WidgetCreate(
    dashboard_id=dashboard.id,
    config=WidgetConfig(
        widget_type=WidgetType.METRIC,
        title="Total Revenue",
        data_source="projects",
        query={"sql": "SELECT SUM(total_price) FROM projects"}
    )
))
```

### 6. Track a KPI

```python
kpi = service.create_kpi(KPICreate(
    name="Monthly Revenue",
    metric=KPIMetric.REVENUE,
    target=KPITarget(
        metric=KPIMetric.REVENUE,
        target_value=100000,
        period="monthly"
    ),
    data_source="projects",
    calculation={"sql": "SELECT SUM(total_price) FROM projects"}
), user_id=1)

# Calculate
result = service.calculate_kpi(kpi.id)
print(f"Achievement: {result.achievement_percentage}%")
```

### 7. Generate Predictions

```python
predictions = service.create_prediction(PredictionRequest(
    model_type=PredictionModel.LINEAR_REGRESSION,
    data_source="projects",
    target_field="total_price",
    feature_fields=["module_count", "system_size"],
    prediction_period=30
), user_id=1)

print(f"R² Score: {predictions.accuracy_metrics['r2_score']}")
```

### 8. Export Data

```python
export = service.export_data(ExportRequest(
    data_source="projects",
    format=ExportFormat.EXCEL,
    german_formatting=True
), user_id=1)

print(f"Download: {export.download_url}")
```

## 📚 Common Patterns

### Report with Filters

```python
ReportDefinition(
    name="Completed Projects",
    data_source="projects",
    fields=[...],
    filters=[
        ReportFilter(field="status", operator="eq", value="completed"),
        ReportFilter(field="created_at", operator="gte", value="2024-01-01")
    ]
)
```

### Report with Visualization

```python
ReportDefinition(
    name="Revenue Chart",
    data_source="projects",
    fields=[...],
    visualizations=[
        ReportVisualization(
            chart_type=ChartType.BAR,
            x_axis="customer_name",
            y_axis="total_price",
            title="Revenue by Customer"
        )
    ]
)
```

### Weekly Scheduled Report

```python
ScheduleCreate(
    report_id=1,
    frequency=ScheduleFrequency.WEEKLY,
    time_of_day="09:00",
    recipients=["manager@company.com"],
    format=ReportFormat.PDF
)
```

### Dashboard with Multiple Widgets

```python
# Metric widget
WidgetCreate(
    dashboard_id=1,
    config=WidgetConfig(
        widget_type=WidgetType.METRIC,
        title="Total Revenue",
        data_source="projects",
        query={"sql": "SELECT SUM(total_price) FROM projects"},
        size=WidgetSize.SMALL
    ),
    position_x=0,
    position_y=0
)

# Chart widget
WidgetCreate(
    dashboard_id=1,
    config=WidgetConfig(
        widget_type=WidgetType.CHART,
        title="Revenue Trend",
        data_source="projects",
        query={"sql": "SELECT date, SUM(total_price) FROM projects GROUP BY date"},
        visualization={"chart_type": "line", "x_axis": "date", "y_axis": "total_price"},
        size=WidgetSize.LARGE
    ),
    position_x=1,
    position_y=0
)
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=sqlite:///./solar_calculator.db

# Export Settings
EXPORT_DIR=/tmp/exports
EXPORT_EXPIRATION_DAYS=7

# Email (for scheduled reports)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

### Database Connection

```python
from backend.core.database import SessionLocal

db = SessionLocal()
service = ReportingService(db)
```

## 📖 Documentation

- **Complete Guide**: `docs/REPORTING_ANALYTICS_GUIDE.md`
- **API Reference**: `docs/REPORTING_QUICK_REFERENCE.md`
- **Examples**: `backend/demo_reporting.py`

## 🆘 Troubleshooting

### Report Execution Fails

```python
try:
    result = service.execute_report(execute_request, user_id=1)
except Exception as e:
    print(f"Error: {e}")
    # Check report definition
    # Verify data source exists
    # Check SQL syntax
```

### Schedule Not Running

```python
# Check schedule status
schedule = db.query(ReportSchedule).filter(ReportSchedule.id == schedule_id).first()
print(f"Enabled: {schedule.enabled}")
print(f"Next run: {schedule.next_run}")

# Get due schedules
due_schedules = service.get_due_schedules()
```

### Export File Not Found

```python
# Check export record
export = db.query(DataExport).filter(DataExport.id == export_id).first()
print(f"File path: {export.file_path}")
print(f"Expires: {export.expires_at}")

# Verify file exists
import os
print(f"File exists: {os.path.exists(export.file_path)}")
```

## ✅ Next Steps

1. ✅ Run migration
2. ✅ Test with demo script
3. ✅ Create your first report
4. ✅ Set up a schedule
5. ✅ Build a dashboard
6. ✅ Track KPIs
7. ✅ Generate predictions
8. ✅ Export data

## 🎯 Success!

You now have a fully functional Reporting and Analytics system!

For more details, see the complete documentation in `docs/REPORTING_ANALYTICS_GUIDE.md`.
