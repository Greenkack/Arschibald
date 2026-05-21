# Solar Monitoring Integration - Quick Reference

## Quick Start

```python
# 1. Connect to monitoring system
config = MonitoringSystemConfig(
    system_type="solaredge",
    api_key="your-api-key",
    site_id="12345"
)
await service.connect_monitoring_system(config)

# 2. Get real-time data
data = await service.get_realtime_production("12345")
print(f"Power: {data.current_power} kW")

# 3. Create alert rule
rule = AlertRule(
    name="Low Production",
    alert_type=AlertType.LOW_PRODUCTION,
    severity=AlertSeverity.WARNING,
    threshold=5.0,
    duration=30
)
service.add_alert_rule("12345", rule)

# 4. Schedule maintenance
task = MaintenanceTaskCreate(
    site_id="12345",
    title="Panel Cleaning",
    task_type="cleaning",
    scheduled_date=datetime.now() + timedelta(days=30)
)
await service.create_maintenance_task(task)

# 5. Generate report
report_request = PerformanceReportRequest(
    site_id="12345",
    report_type="monthly",
    format="pdf"
)
report = await service.generate_performance_report(report_request)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/monitoring/connect` | POST | Connect to monitoring system |
| `/monitoring/realtime/{site_id}` | GET | Get real-time data |
| `/monitoring/analyze` | POST | Analyze performance |
| `/monitoring/alerts` | POST | Create alert |
| `/monitoring/alerts/{site_id}` | GET | Get active alerts |
| `/monitoring/alerts/{id}/resolve` | PUT | Resolve alert |
| `/monitoring/maintenance` | POST | Create maintenance task |
| `/monitoring/maintenance/{id}` | PUT | Update maintenance task |
| `/monitoring/reports` | POST | Generate report |
| `/monitoring/dashboard/{site_id}` | GET | Get dashboard data |
| `/monitoring/health/{site_id}` | GET | Check system health |

## Monitoring System Types

- `solaredge` - SolarEdge Monitoring
- `fronius` - Fronius Solar.web
- `sma` - SMA Sunny Portal
- `enphase` - Enphase Enlighten
- `huawei` - Huawei FusionSolar
- `generic` - Generic/Custom

## Alert Types

- `low_production` - Production below threshold
- `system_offline` - System not communicating
- `inverter_error` - Inverter malfunction
- `module_failure` - Module not producing
- `grid_disconnection` - Grid connection lost
- `performance_degradation` - Performance declining
- `maintenance_due` - Maintenance scheduled
- `weather_impact` - Weather affecting production

## Alert Severity Levels

- `info` - Informational
- `warning` - Needs attention
- `error` - Problem detected
- `critical` - Immediate action required

## Maintenance Task Types

- `cleaning` - Panel cleaning
- `inspection` - System inspection
- `repair` - Repair work
- `upgrade` - System upgrade

## Performance Metrics

| Metric | Good | Excellent |
|--------|------|-----------|
| Performance Ratio | > 0.80 | > 0.85 |
| Capacity Factor | 15-20% | > 20% |
| Specific Yield | > 1000 kWh/kWp | > 1200 kWh/kWp |
| Availability | > 95% | > 98% |
| Degradation Rate | < 1.0% | < 0.5% |

## Report Types

- `daily` - Last 24 hours
- `weekly` - Last 7 days
- `monthly` - Current month
- `yearly` - Current year
- `custom` - Custom date range

## Report Formats

- `pdf` - PDF document
- `excel` - Excel spreadsheet
- `json` - JSON data

## Common Tasks

### Check System Health
```python
health = await service.check_system_health("12345")
print(f"Status: {health.overall_status}")
print(f"Uptime: {health.uptime_percentage}%")
```

### Get Dashboard Data
```python
dashboard = await service.get_dashboard_data("12345")
print(f"Current: {dashboard.current_production.current_power} kW")
print(f"Today: {dashboard.today_summary['total_energy']} kWh")
print(f"Active Alerts: {len(dashboard.active_alerts)}")
```

### Analyze Performance
```python
analysis = await service.analyze_performance(
    PerformanceAnalysisRequest(
        site_id="12345",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now(),
        include_weather=True
    )
)
print(f"PR: {analysis.metrics.performance_ratio}")
print(f"Insights: {analysis.insights}")
```

## Error Handling

```python
try:
    data = await service.get_realtime_production(site_id)
except Exception as e:
    logger.error(f"Failed to get data: {str(e)}")
    # Handle error appropriately
```

## Best Practices

1. ✅ Check connection status before operations
2. ✅ Set appropriate alert thresholds
3. ✅ Schedule regular maintenance
4. ✅ Review performance reports monthly
5. ✅ Monitor system health daily
6. ✅ Keep API credentials secure
7. ✅ Handle errors gracefully
8. ✅ Log all operations
9. ✅ Use async operations for better performance
10. ✅ Cache frequently accessed data

## Requirements

```txt
fastapi>=0.100.0
aiohttp>=3.8.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
```

## Environment Variables

```bash
MONITORING_API_KEY=your-api-key
MONITORING_SITE_ID=12345
MONITORING_REFRESH_INTERVAL=300
```

## Support

- Documentation: `/docs/MONITORING_INTEGRATION_GUIDE.md`
- API Docs: `http://localhost:8000/docs`
- Issues: Contact system administrator
