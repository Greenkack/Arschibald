"""
Solar Monitoring Integration Demo
Demonstrates monitoring system integration capabilities
"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from services.monitoring_service import MonitoringService
from models.monitoring_schemas import (
    MonitoringSystemType, MonitoringSystemConfig,
    PerformanceAnalysisRequest, AlertCreate, AlertType, AlertSeverity,
    AlertRule, MaintenanceTaskCreate, PerformanceReportRequest
)


async def demo_monitoring_integration():
    """Demonstrate monitoring integration features"""
    
    # Create service (would use actual database session)
    service = MonitoringService(None)
    
    print("=" * 80)
    print("SOLAR MONITORING INTEGRATION DEMO")
    print("=" * 80)
    
    # 1. Connect to Monitoring System
    print("\n1. CONNECTING TO MONITORING SYSTEM")
    print("-" * 80)
    
    config = MonitoringSystemConfig(
        system_type=MonitoringSystemType.SOLAR_EDGE,
        api_key="demo-api-key-12345",
        site_id="SITE-001",
        refresh_interval=300,
        enabled=True
    )
    
    try:
        connection_result = await service.connect_monitoring_system(config)
        print(f" Connected to {config.system_type}")
        print(f"  Site ID: {config.site_id}")
        print(f"  Status: {connection_result.get('status')}")
    except Exception as e:
        print(f" Connection failed: {str(e)}")
    
    # 2. Get Real-time Production Data
    print("\n2. REAL-TIME PRODUCTION DATA")
    print("-" * 80)
    
    try:
        realtime_data = await service.get_realtime_production("SITE-001")
        print(f"Timestamp: {realtime_data.timestamp}")
        print(f"Current Power: {realtime_data.current_power:.2f} kW")
        print(f"Daily Energy: {realtime_data.daily_energy:.2f} kWh")
        print(f"Monthly Energy: {realtime_data.monthly_energy:.2f} kWh")
        print(f"Yearly Energy: {realtime_data.yearly_energy:.2f} kWh")
        print(f"Lifetime Energy: {realtime_data.lifetime_energy:.2f} kWh")
        print(f"System Status: {realtime_data.system_status}")
        if realtime_data.grid_voltage:
            print(f"Grid Voltage: {realtime_data.grid_voltage:.1f} V")
        if realtime_data.grid_frequency:
            print(f"Grid Frequency: {realtime_data.grid_frequency:.1f} Hz")
    except Exception as e:
        print(f" Failed to get real-time data: {str(e)}")
    
    # 3. Performance Analysis
    print("\n3. PERFORMANCE ANALYSIS")
    print("-" * 80)
    
    analysis_request = PerformanceAnalysisRequest(
        site_id="SITE-001",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        include_weather=True,
        include_comparison=True,
        granularity="daily"
    )
    
    try:
        analysis = await service.analyze_performance(analysis_request)
        print(f"Analysis Period: {analysis.period['start']} to {analysis.period['end']}")
        print(f"\nPerformance Metrics:")
        print(f"  Performance Ratio: {analysis.metrics.performance_ratio:.2%}")
        print(f"  Capacity Factor: {analysis.metrics.capacity_factor:.2%}")
        print(f"  Specific Yield: {analysis.metrics.specific_yield:.0f} kWh/kWp")
        print(f"  Availability: {analysis.metrics.availability:.2%}")
        print(f"  Degradation Rate: {analysis.metrics.degradation_rate:.2f}%/year")
        print(f"  Expected vs Actual: {analysis.metrics.expected_vs_actual:.2%}")
        
        if analysis.insights:
            print(f"\nInsights:")
            for insight in analysis.insights:
                print(f"  • {insight}")
        
        if analysis.recommendations:
            print(f"\nRecommendations:")
            for rec in analysis.recommendations:
                print(f"  • {rec}")
    except Exception as e:
        print(f" Analysis failed: {str(e)}")
    
    # 4. Alert System
    print("\n4. ALERT SYSTEM")
    print("-" * 80)
    
    # Add alert rule
    print("Adding alert rule for low production...")
    low_production_rule = AlertRule(
        name="Low Production Warning",
        alert_type=AlertType.LOW_PRODUCTION,
        severity=AlertSeverity.WARNING,
        condition="current_power < threshold",
        threshold=5.0,
        duration=30,
        enabled=True,
        notification_channels=["email"]
    )
    service.add_alert_rule("SITE-001", low_production_rule)
    print(" Alert rule added")
    
    # Create manual alert
    print("\nCreating manual alert...")
    alert = AlertCreate(
        site_id="SITE-001",
        alert_type=AlertType.PERFORMANCE_DEGRADATION,
        severity=AlertSeverity.WARNING,
        title="Performance Below Expected",
        description="System performance is 10% below expected values",
        data={"expected": 100, "actual": 90, "difference": -10},
        auto_resolve=False
    )
    
    try:
        alert_response = await service.create_alert(alert)
        print(f" Alert created: {alert_response.title}")
        print(f"  Severity: {alert_response.severity}")
        print(f"  Created: {alert_response.created_at}")
    except Exception as e:
        print(f" Failed to create alert: {str(e)}")
    
    # 5. Maintenance Scheduling
    print("\n5. MAINTENANCE SCHEDULING")
    print("-" * 80)
    
    maintenance_task = MaintenanceTaskCreate(
        site_id="SITE-001",
        title="Quarterly Panel Cleaning",
        description="Clean all solar panels and check for damage",
        task_type="cleaning",
        scheduled_date=datetime.now() + timedelta(days=30),
        estimated_duration=120,
        assigned_to="technician@example.com",
        priority="normal",
        recurring=True,
        recurrence_pattern="quarterly"
    )
    
    try:
        task_response = await service.create_maintenance_task(maintenance_task)
        print(f" Maintenance task created: {task_response.title}")
        print(f"  Type: {task_response.task_type}")
        print(f"  Scheduled: {task_response.scheduled_date}")
        print(f"  Duration: {task_response.estimated_duration} minutes")
        print(f"  Assigned to: {task_response.assigned_to}")
        print(f"  Recurring: {task_response.recurring}")
    except Exception as e:
        print(f" Failed to create maintenance task: {str(e)}")
    
    # 6. Performance Reporting
    print("\n6. PERFORMANCE REPORTING")
    print("-" * 80)
    
    report_request = PerformanceReportRequest(
        site_id="SITE-001",
        report_type="monthly",
        include_charts=True,
        include_weather=True,
        include_financial=True,
        format="pdf"
    )
    
    try:
        report = await service.generate_performance_report(report_request)
        print(f" Report generated: {report.report_id}")
        print(f"  Type: {report.report_type}")
        print(f"  Period: {report.period['start']} to {report.period['end']}")
        print(f"\nSummary:")
        print(f"  Total Energy: {report.summary['total_energy']:.2f} kWh")
        print(f"  Average Power: {report.summary['average_power']:.2f} kW")
        print(f"  Peak Power: {report.summary['peak_power']:.2f} kW")
        
        if report.financial_summary:
            print(f"\nFinancial Summary:")
            print(f"  Feed-in Revenue: €{report.financial_summary['feed_in_revenue']:.2f}")
            print(f"  Self-consumption Savings: €{report.financial_summary['self_consumption_savings']:.2f}")
            print(f"  Total Savings: €{report.financial_summary['total_savings']:.2f}")
        
        if report.file_url:
            print(f"\nReport File: {report.file_url}")
    except Exception as e:
        print(f" Failed to generate report: {str(e)}")
    
    # 7. Dashboard Data
    print("\n7. DASHBOARD DATA")
    print("-" * 80)
    
    try:
        dashboard = await service.get_dashboard_data("SITE-001")
        print(f"Current Production:")
        print(f"  Power: {dashboard.current_production.current_power:.2f} kW")
        print(f"  Status: {dashboard.current_production.system_status}")
        
        print(f"\nToday's Summary:")
        print(f"  Total Energy: {dashboard.today_summary['total_energy']:.2f} kWh")
        print(f"  Peak Power: {dashboard.today_summary['peak_power']:.2f} kW")
        
        print(f"\nWeek Summary:")
        print(f"  Total Energy: {dashboard.week_summary['total_energy']:.2f} kWh")
        
        print(f"\nMonth Summary:")
        print(f"  Total Energy: {dashboard.month_summary['total_energy']:.2f} kWh")
        
        print(f"\nActive Alerts: {len(dashboard.active_alerts)}")
        print(f"Upcoming Maintenance: {len(dashboard.upcoming_maintenance)}")
    except Exception as e:
        print(f" Failed to get dashboard data: {str(e)}")
    
    # 8. System Health Check
    print("\n8. SYSTEM HEALTH CHECK")
    print("-" * 80)
    
    try:
        health = await service.check_system_health("SITE-001")
        print(f"Overall Status: {health.overall_status.upper()}")
        print(f"Last Communication: {health.last_communication}")
        print(f"Uptime: {health.uptime_percentage:.2f}%")
        
        print(f"\nComponent Status:")
        for component, status in health.components.items():
            print(f"  {component}: {status['status']}")
        
        if health.issues:
            print(f"\nIssues:")
            for issue in health.issues:
                print(f"   {issue}")
        
        if health.recommendations:
            print(f"\nRecommendations:")
            for rec in health.recommendations:
                print(f"  • {rec}")
    except Exception as e:
        print(f" Failed to check system health: {str(e)}")
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    print("\nStarting Solar Monitoring Integration Demo...")
    print("This demo showcases the monitoring system capabilities.\n")
    
    asyncio.run(demo_monitoring_integration())
    
    print("\nDemo finished successfully!")
    print("\nKey Features Demonstrated:")
    print("   Monitoring system API integration")
    print("   Real-time production tracking")
    print("   Performance analysis with metrics")
    print("   Alert system with rules")
    print("   Maintenance scheduling")
    print("   Performance reporting")
    print("   Dashboard data aggregation")
    print("   System health monitoring")
