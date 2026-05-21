# Demo: Reporting and Analytics System

"""
Demonstration of the Reporting and Analytics system capabilities.

This script shows how to:
1. Create custom reports
2. Execute reports with filters
3. Schedule automated reports
4. Create dashboards with widgets
5. Track KPIs
6. Generate predictions
7. Export data
"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.services.reporting_service import ReportingService
from backend.models.reporting_schemas import (
    ReportDefinition, ReportCreate, ReportExecute, ReportField, ReportFilter,
    ReportSort, ReportVisualization, ScheduleCreate, DashboardCreate,
    WidgetCreate, WidgetConfig, KPICreate, KPITarget, PredictionRequest,
    ExportRequest, ReportType, ReportFormat, ScheduleFrequency, WidgetType,
    WidgetSize, ChartType, KPIMetric, PredictionModel, ExportFormat,
    AggregationType
)


def demo_report_builder(db: Session):
    """Demonstrate custom report builder"""
    print("\n" + "="*60)
    print("DEMO 1: Custom Report Builder")
    print("="*60)
    
    service = ReportingService(db)
    
    # Create a sales report
    report_definition = ReportDefinition(
        name="Monthly Sales Report",
        description="Sales breakdown by customer",
        report_type=ReportType.SALES,
        data_source="projects",
        fields=[
            ReportField(
                name="customer_name",
                label="Customer",
                data_type="string"
            ),
            ReportField(
                name="total_price",
                label="Revenue",
                data_type="number",
                aggregation=AggregationType.SUM,
                format="currency"
            ),
            ReportField(
                name="id",
                label="Project Count",
                data_type="number",
                aggregation=AggregationType.COUNT
            )
        ],
        filters=[
            ReportFilter(
                field="created_at",
                operator="gte",
                value="2024-01-01"
            ),
            ReportFilter(
                field="status",
                operator="eq",
                value="completed"
            )
        ],
        sorts=[
            ReportSort(field="total_price", direction="desc")
        ],
        visualizations=[
            ReportVisualization(
                chart_type=ChartType.BAR,
                x_axis="customer_name",
                y_axis="total_price",
                title="Revenue by Customer",
                color_scheme="blue"
            )
        ],
        group_by=["customer_name"],
        limit=10
    )
    
    report_create = ReportCreate(
        definition=report_definition,
        owner_id=1,
        is_public=False,
        tags=["sales", "monthly", "revenue"]
    )
    
    report = service.create_report(report_create, user_id=1)
    print(f" Created report: {report.name} (ID: {report.id})")
    
    # Execute the report
    execute_request = ReportExecute(
        report_id=report.id,
        parameters={},
        format=ReportFormat.JSON
    )
    
    try:
        result = service.execute_report(execute_request, user_id=1)
        print(f" Executed report successfully")
        print(f"   - Rows returned: {result.metadata['row_count']}")
        print(f"   - Execution time: {result.metadata['execution_time_ms']}ms")
        print(f"   - Visualizations: {len(result.visualizations)}")
    except Exception as e:
        print(f"  Report execution failed: {e}")


def demo_scheduled_reports(db: Session):
    """Demonstrate scheduled reports"""
    print("\n" + "="*60)
    print("DEMO 2: Scheduled Reports")
    print("="*60)
    
    service = ReportingService(db)
    
    # Create a daily schedule
    schedule_data = ScheduleCreate(
        report_id=1,
        frequency=ScheduleFrequency.DAILY,
        time_of_day="08:00",
        recipients=["manager@company.com", "team@company.com"],
        format=ReportFormat.PDF,
        enabled=True
    )
    
    schedule = service.create_schedule(schedule_data)
    print(f" Created daily schedule (ID: {schedule.id})")
    print(f"   - Frequency: {schedule.frequency}")
    print(f"   - Time: {schedule.time_of_day}")
    print(f"   - Recipients: {len(schedule.recipients)}")
    print(f"   - Next run: {schedule.next_run}")
    
    # Create a weekly schedule
    weekly_schedule = ScheduleCreate(
        report_id=1,
        frequency=ScheduleFrequency.WEEKLY,
        time_of_day="09:00",
        recipients=["executive@company.com"],
        format=ReportFormat.EXCEL,
        enabled=True
    )
    
    schedule2 = service.create_schedule(weekly_schedule)
    print(f" Created weekly schedule (ID: {schedule2.id})")
    print(f"   - Next run: {schedule2.next_run}")


def demo_dashboards(db: Session):
    """Demonstrate dashboard creation"""
    print("\n" + "="*60)
    print("DEMO 3: Dashboard Widgets")
    print("="*60)
    
    service = ReportingService(db)
    
    # Create dashboard
    dashboard_data = DashboardCreate(
        name="Sales Dashboard",
        description="Real-time sales metrics and trends",
        is_public=False,
        layout="grid"
    )
    
    dashboard = service.create_dashboard(dashboard_data, user_id=1)
    print(f" Created dashboard: {dashboard.name} (ID: {dashboard.id})")
    
    # Add metric widget
    metric_widget = WidgetCreate(
        dashboard_id=dashboard.id,
        config=WidgetConfig(
            widget_type=WidgetType.METRIC,
            title="Total Revenue",
            data_source="projects",
            query={"sql": "SELECT SUM(total_price) as revenue FROM projects WHERE status='completed'"},
            size=WidgetSize.SMALL
        ),
        position_x=0,
        position_y=0
    )
    
    widget1 = service.create_widget(metric_widget)
    print(f" Added metric widget (ID: {widget1.id})")
    
    # Add chart widget
    chart_widget = WidgetCreate(
        dashboard_id=dashboard.id,
        config=WidgetConfig(
            widget_type=WidgetType.CHART,
            title="Revenue Trend",
            data_source="projects",
            query={"sql": "SELECT DATE(created_at) as date, SUM(total_price) as revenue FROM projects GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 30"},
            visualization={
                "chart_type": "line",
                "x_axis": "date",
                "y_axis": "revenue"
            },
            size=WidgetSize.LARGE
        ),
        position_x=1,
        position_y=0
    )
    
    widget2 = service.create_widget(chart_widget)
    print(f" Added chart widget (ID: {widget2.id})")


def demo_kpi_tracking(db: Session):
    """Demonstrate KPI tracking"""
    print("\n" + "="*60)
    print("DEMO 4: KPI Tracking")
    print("="*60)
    
    service = ReportingService(db)
    
    # Create revenue KPI
    kpi_data = KPICreate(
        name="Monthly Revenue Target",
        metric=KPIMetric.REVENUE,
        target=KPITarget(
            metric=KPIMetric.REVENUE,
            target_value=100000.0,
            period="monthly",
            comparison_operator="gte"
        ),
        data_source="projects",
        calculation={
            "sql": "SELECT SUM(total_price) FROM projects WHERE status='completed' AND MONTH(created_at) = MONTH(CURRENT_DATE)"
        }
    )
    
    kpi = service.create_kpi(kpi_data, user_id=1)
    print(f" Created KPI: {kpi.name} (ID: {kpi.id})")
    
    # Calculate KPI
    try:
        result = service.calculate_kpi(kpi.id)
        print(f" KPI Calculation:")
        print(f"   - Current Value: €{result.current_value:,.2f}")
        print(f"   - Target Value: €{result.target_value:,.2f}")
        print(f"   - Achievement: {result.achievement_percentage:.1f}%")
        print(f"   - Trend: {result.trend}")
    except Exception as e:
        print(f"  KPI calculation failed: {e}")


def demo_predictive_analytics(db: Session):
    """Demonstrate predictive analytics"""
    print("\n" + "="*60)
    print("DEMO 5: Predictive Analytics")
    print("="*60)
    
    service = ReportingService(db)
    
    # Create prediction
    prediction_request = PredictionRequest(
        model_type=PredictionModel.LINEAR_REGRESSION,
        data_source="projects",
        target_field="total_price",
        feature_fields=["module_count", "system_size"],
        prediction_period=30,
        confidence_level=0.95
    )
    
    try:
        result = service.create_prediction(prediction_request, user_id=1)
        print(f" Generated predictions for {len(result.predictions)} days")
        print(f"   - Model Type: {result.model_type}")
        print(f"   - R² Score: {result.accuracy_metrics['r2_score']:.3f}")
        print(f"   - RMSE: {result.accuracy_metrics['rmse']:.2f}")
        print(f"\n   First 3 predictions:")
        for pred in result.predictions[:3]:
            print(f"   - {pred['date']}: €{pred['predicted_value']:,.2f}")
    except Exception as e:
        print(f"  Prediction failed: {e}")


def demo_data_export(db: Session):
    """Demonstrate data export"""
    print("\n" + "="*60)
    print("DEMO 6: Data Export")
    print("="*60)
    
    service = ReportingService(db)
    
    # Export to Excel with German formatting
    export_request = ExportRequest(
        data_source="projects",
        filters=[
            ReportFilter(field="status", operator="eq", value="completed")
        ],
        fields=["customer_name", "total_price", "created_at", "module_count"],
        format=ExportFormat.EXCEL,
        include_headers=True,
        german_formatting=True
    )
    
    try:
        result = service.export_data(export_request, user_id=1)
        print(f" Data exported successfully")
        print(f"   - File: {result.file_name}")
        print(f"   - Size: {result.file_size:,} bytes")
        print(f"   - Format: {result.format}")
        print(f"   - Download URL: {result.download_url}")
        print(f"   - Expires: {result.expires_at}")
    except Exception as e:
        print(f"  Export failed: {e}")


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("REPORTING AND ANALYTICS SYSTEM DEMO")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Run demos
        demo_report_builder(db)
        demo_scheduled_reports(db)
        demo_dashboards(db)
        demo_kpi_tracking(db)
        demo_predictive_analytics(db)
        demo_data_export(db)
        
        print("\n" + "="*60)
        print(" ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
