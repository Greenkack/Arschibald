# Solar Monitoring Integration Guide

## Overview

The Solar Monitoring Integration system provides comprehensive monitoring capabilities for solar PV systems, including real-time production tracking, performance analysis, alert management, maintenance scheduling, and performance reporting.

## Features

### 1. Monitoring System API Integration

Connect to various monitoring system APIs:
- **SolarEdge**: Industry-leading monitoring platform
- **Fronius**: Solar.web monitoring
- **SMA**: Sunny Portal
- **Enphase**: Enlighten platform
- **Huawei**: FusionSolar
- **Generic**: Custom monitoring systems

### 2. Real-time Production Tracking

Monitor system performance in real-time:
- Current power output (kW)
- Daily, monthly, yearly, and lifetime energy production
- System status and health
- Inverter performance
- Module temperatures
- Grid voltage and frequency

### 3. Performance Analysis

Comprehensive performance metrics:
- **Performance Ratio**: Actual vs. theoretical output
- **Capacity Factor**: Utilization of system capacity
- **Specific Yield**: Energy per installed kWp
- **Availability**: System uptime percentage
- **Degradation Rate**: Annual performance decline
- **Weather Correlation**: Impact of weather on production

### 4. Alert System

Proactive monitoring with configurable alerts:
- Low production warnings
- System offline notifications
- Inverter error alerts
- Module failure detection
- Grid disconnection alerts
- Performance degradation warnings
- Maintenance due reminders

### 5. Maintenance Scheduling

Organized maintenance management:
- Schedule cleaning, inspections, repairs
- Track maintenance history
- Set recurring maintenance tasks
- Assign tasks to technicians
- Priority management
- Automated reminders

### 6. Performance Reporting

Detailed performance reports:
- Daily, weekly, monthly, yearly reports
- Production data and trends
- Financial analysis
- Alert history
- Maintenance records
- Export to PDF or Excel

## API Endpoints

### Connection

```http
POST /api/v1/monitoring/connect
```

Connect to monitoring system.

**Request Body:**
```json
{
  "system_type": "solaredge",
  "api_key": "your-api-key",
  "site_id": "12345",
  "refresh_interval": 300,
  "enabled": true
}
```

### Real-time Data

```http
GET /api/v1/monitoring/realtime/{site_id}
```

Get real-time production data.

**Response:**
```json
{
  "timestamp": "2024-01-15T14:30:00Z",
  "current_power": 8.5,
  "daily_energy": 45.2,
  "monthly_energy": 1250.0,
  "yearly_energy": 12500.0,
  "lifetime_energy": 50000.0,
  "system_status": "active",
  "grid_voltage": 230.5,
  "grid_frequency": 50.0
}
```

### Performance Analysis

```http
POST /api/v1/monitoring/analyze
```

Analyze system performance over a period.

**Request Body:**
```json
{
  "site_id": "12345",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z",
  "include_weather": true,
  "include_comparison": true,
  "granularity": "daily"
}
```

### Alerts

```http
POST /api/v1/monitoring/alerts
GET /api/v1/monitoring/alerts/{site_id}
PUT /api/v1/monitoring/alerts/{alert_id}/resolve
POST /api/v1/monitoring/alerts/rules/{site_id}
```

Manage alerts and alert rules.

### Maintenance

```http
POST /api/v1/monitoring/maintenance
PUT /api/v1/monitoring/maintenance/{task_id}
GET /api/v1/monitoring/maintenance/{site_id}/upcoming
GET /api/v1/monitoring/maintenance/{site_id}/overdue
```

Manage maintenance tasks.

### Reports

```http
POST /api/v1/monitoring/reports
```

Generate performance reports.

**Request Body:**
```json
{
  "site_id": "12345",
  "report_type": "monthly",
  "include_charts": true,
  "include_weather": true,
  "include_financial": true,
  "format": "pdf"
}
```

### Dashboard

```http
GET /api/v1/monitoring/dashboard/{site_id}
GET /api/v1/monitoring/health/{site_id}
```

Get dashboard data and system health.

## Usage Examples

### Python

```python
import aiohttp
import asyncio

async def monitor_system():
    # Connect to monitoring system
    async with aiohttp.ClientSession() as session:
        # Connect
        config = {
            "system_type": "solaredge",
            "api_key": "your-api-key",
            "site_id": "12345",
            "refresh_interval": 300
        }
        
        async with session.post(
            "http://localhost:8000/api/v1/monitoring/connect",
            json=config
        ) as response:
            result = await response.json()
            print(f"Connected: {result}")
        
        # Get real-time data
        async with session.get(
            "http://localhost:8000/api/v1/monitoring/realtime/12345"
        ) as response:
            data = await response.json()
            print(f"Current Power: {data['current_power']} kW")
            print(f"Daily Energy: {data['daily_energy']} kWh")

asyncio.run(monitor_system())
```

### TypeScript/JavaScript

```typescript
// Connect to monitoring system
const connectMonitoring = async () => {
  const config = {
    system_type: 'solaredge',
    api_key: 'your-api-key',
    site_id: '12345',
    refresh_interval: 300
  };
  
  const response = await fetch('/api/v1/monitoring/connect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  });
  
  const result = await response.json();
  console.log('Connected:', result);
};

// Get real-time data
const getRealTimeData = async (siteId: string) => {
  const response = await fetch(`/api/v1/monitoring/realtime/${siteId}`);
  const data = await response.json();
  
  console.log(`Current Power: ${data.current_power} kW`);
  console.log(`Daily Energy: ${data.daily_energy} kWh`);
  
  return data;
};

// Create alert
const createAlert = async (siteId: string) => {
  const alert = {
    site_id: siteId,
    alert_type: 'low_production',
    severity: 'warning',
    title: 'Low Production Alert',
    description: 'System production is below expected levels',
    data: {}
  };
  
  const response = await fetch('/api/v1/monitoring/alerts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(alert)
  });
  
  return await response.json();
};
```

## Alert Rules Configuration

Configure automatic alert rules:

```python
from backend.models.monitoring_schemas import AlertRule, AlertType, AlertSeverity

# Low production alert
low_production_rule = AlertRule(
    name="Low Production Warning",
    alert_type=AlertType.LOW_PRODUCTION,
    severity=AlertSeverity.WARNING,
    condition="current_power < threshold",
    threshold=5.0,  # kW
    duration=30,  # minutes
    enabled=True,
    notification_channels=["email", "sms"]
)

# System offline alert
offline_rule = AlertRule(
    name="System Offline",
    alert_type=AlertType.SYSTEM_OFFLINE,
    severity=AlertSeverity.CRITICAL,
    condition="system_status == 'offline'",
    threshold=0,
    duration=5,  # minutes
    enabled=True,
    notification_channels=["email", "sms", "push"]
)
```

## Maintenance Scheduling

Schedule maintenance tasks:

```python
from backend.models.monitoring_schemas import MaintenanceTaskCreate
from datetime import datetime, timedelta

# Schedule cleaning
cleaning_task = MaintenanceTaskCreate(
    site_id="12345",
    title="Panel Cleaning",
    description="Clean all solar panels",
    task_type="cleaning",
    scheduled_date=datetime.now() + timedelta(days=30),
    estimated_duration=120,  # minutes
    assigned_to="technician@example.com",
    priority="normal",
    recurring=True,
    recurrence_pattern="monthly"
)
```

## Performance Metrics

Understanding performance metrics:

- **Performance Ratio (PR)**: Ratio of actual to theoretical energy output
  - Good: > 0.80
  - Excellent: > 0.85
  
- **Capacity Factor**: Percentage of maximum possible output
  - Typical: 15-25% depending on location
  
- **Specific Yield**: kWh produced per kWp installed
  - Good: > 1000 kWh/kWp/year
  - Excellent: > 1200 kWh/kWp/year

- **Availability**: System uptime percentage
  - Target: > 98%

## Best Practices

1. **Regular Monitoring**: Check dashboard daily
2. **Alert Configuration**: Set appropriate thresholds
3. **Maintenance Schedule**: Follow manufacturer recommendations
4. **Performance Analysis**: Review monthly reports
5. **Weather Correlation**: Understand weather impact
6. **Documentation**: Keep maintenance records
7. **Trend Analysis**: Monitor long-term performance

## Troubleshooting

### Connection Issues

If unable to connect to monitoring system:
1. Verify API credentials
2. Check network connectivity
3. Confirm site ID is correct
4. Review API rate limits

### Data Discrepancies

If data doesn't match expectations:
1. Check system configuration
2. Verify sensor calibration
3. Review weather conditions
4. Compare with inverter display

### Alert Fatigue

If receiving too many alerts:
1. Adjust alert thresholds
2. Increase duration before triggering
3. Review alert rules
4. Consolidate similar alerts

## Integration with Other Systems

The monitoring system integrates with:
- Solar calculator for expected vs. actual comparison
- CRM system for customer notifications
- PDF generation for reports
- Email system for alerts
- SMS gateway for critical alerts

## Requirements

- Python 3.10+
- FastAPI
- aiohttp for async HTTP requests
- SQLAlchemy for database
- Access to monitoring system API

## Support

For issues or questions:
- Check API documentation
- Review error logs
- Contact monitoring system support
- Consult system integrator
