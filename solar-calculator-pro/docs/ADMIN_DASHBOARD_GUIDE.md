# Admin Dashboard - Complete Guide

## Overview

The Admin Dashboard provides comprehensive system monitoring, health checks, usage statistics, and performance metrics for the Solar Calculator Pro application. It enables administrators to monitor system health, track usage patterns, identify issues, and ensure optimal performance.

## Features

### 1. System Health Monitoring

Real-time monitoring of system resources and health status:

- **CPU Usage**: Monitor CPU utilization across all cores
- **Memory Usage**: Track RAM consumption and availability
- **Disk Usage**: Monitor disk space and storage capacity
- **Process Information**: View application process metrics
- **System Uptime**: Track system availability and uptime
- **Health Status**: Overall system health with color-coded indicators

### 2. Database Health

Monitor database connectivity and statistics:

- **Connection Status**: Real-time database connection monitoring
- **Table Statistics**: Record counts for all major tables
- **Total Records**: Aggregate database size metrics
- **Health Indicators**: Database performance and availability status

### 3. Usage Statistics

Track application usage across different time periods:

**User Statistics:**
- Total users in the system
- Active users (current period)
- New user registrations
- Login counts and session duration

**Project Statistics:**
- Total projects created
- New projects (current period)
- Completed projects
- Active projects
- Projects by type (Solar, Heat Pump, Combined)

**Calculation Statistics:**
- Total calculations performed
- Calculations by type
- Average calculation time
- Failed calculations

**PDF Statistics:**
- Total PDFs generated
- PDFs by type (Standard PV, Extended PV, Heat Pump, Multi-PDF)
- Average generation time
- Failed generations

**API Statistics:**
- Total API requests
- Successful vs failed requests
- Average response time
- Requests by endpoint
- Requests by status code

### 4. Performance Metrics

Monitor application performance in real-time:

**Response Times:**
- Average response time
- P50, P95, P99 percentiles
- Maximum response time
- Response times by endpoint

**Throughput:**
- Requests per second
- Requests per minute
- Requests per hour
- Peak throughput and timing

**Error Rates:**
- Overall error rate percentage
- Total errors
- Errors by type (validation, database, timeout, internal)
- Errors by endpoint

**Resource Usage Trends:**
- CPU usage over time
- Memory usage over time
- Disk I/O trends
- Network I/O trends

**Cache Performance:**
- Cache hit rate
- Cache miss rate
- Cache size
- Eviction count

### 5. User Activity Overview

Track user behavior and activity:

- **Recent Logins**: Latest user login events with IP and user agent
- **Active Sessions**: Current active user sessions by role
- **Recent Actions**: Latest user actions (create, update, delete, export)
- **Top Users**: Most active users by action count

### 6. System Alerts

Automated alert system for critical issues:

**Alert Types:**
- System alerts (CPU, memory, disk)
- Database alerts (connection, performance)
- Application alerts (errors, failures)

**Alert Severities:**
- Info: Informational messages
- Warning: Issues requiring attention
- Critical: Urgent issues requiring immediate action

**Alert Management:**
- View all active alerts
- Filter by severity
- Resolve alerts
- Alert history

## API Endpoints

### Dashboard Summary

```
GET /api/v1/admin/dashboard/summary
```

Returns comprehensive dashboard data including:
- System health
- Database health
- Usage statistics
- Performance metrics
- Active alerts
- User activity

### System Health

```
GET /api/v1/admin/dashboard/health/system
```

Returns detailed system health metrics:
- CPU usage and core count
- Memory usage (total, used, available)
- Disk usage (total, used, free)
- Process information
- System uptime
- Health status and issues

### Database Health

```
GET /api/v1/admin/dashboard/health/database
```

Returns database health and statistics:
- Connection status
- Table record counts
- Total records
- Database health status

### Usage Statistics

```
GET /api/v1/admin/dashboard/statistics/usage?period={period}
```

Parameters:
- `period`: today, week, month, year

Returns usage statistics for the specified period.

### Performance Metrics

```
GET /api/v1/admin/dashboard/metrics/performance
```

Returns comprehensive performance metrics.

### User Activity

```
GET /api/v1/admin/dashboard/activity/users?limit={limit}
```

Parameters:
- `limit`: Maximum number of records (1-1000)

Returns user activity overview.

### System Alerts

```
GET /api/v1/admin/dashboard/alerts?severity={severity}
```

Parameters:
- `severity`: info, warning, critical (optional)

Returns system alerts, optionally filtered by severity.

### Resolve Alert

```
POST /api/v1/admin/dashboard/alerts/{alert_id}/resolve
```

Resolves a specific alert.

### Historical Metrics

```
GET /api/v1/admin/dashboard/metrics/historical?metric_type={type}&period={period}
```

Parameters:
- `metric_type`: system_health, usage, performance
- `period`: today, week, month, year

Returns historical metrics data.

## Frontend Component

### Usage

```tsx
import AdminDashboard from './components/admin/AdminDashboard';

function AdminPage() {
  return <AdminDashboard />;
}
```

### Features

- **Auto-refresh**: Automatically refreshes data at configurable intervals
- **Period Selection**: View statistics for different time periods
- **Real-time Updates**: Live system health monitoring
- **Alert Management**: View and resolve system alerts
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### Configuration

Environment variables:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## Health Status Indicators

### Status Colors

- **Green (Healthy)**: System is operating normally
- **Yellow (Warning)**: Issues detected, attention recommended
- **Red (Critical)**: Critical issues, immediate action required

### Thresholds

**CPU:**
- Healthy: < 80%
- Warning: 80-100%

**Memory:**
- Healthy: < 85%
- Warning: 85-100%

**Disk:**
- Healthy: < 80%
- Warning: 80-90%
- Critical: > 90%

## Best Practices

### Monitoring

1. **Regular Checks**: Review dashboard at least daily
2. **Alert Response**: Address critical alerts immediately
3. **Trend Analysis**: Monitor trends over time to identify patterns
4. **Capacity Planning**: Use metrics to plan for scaling needs

### Performance Optimization

1. **Response Times**: Keep average response time under 200ms
2. **Error Rates**: Maintain error rate below 1%
3. **Resource Usage**: Keep CPU and memory usage below 70% during normal operation
4. **Cache Hit Rate**: Aim for cache hit rate above 80%

### Alert Management

1. **Prioritize**: Address critical alerts first
2. **Root Cause**: Investigate underlying causes, not just symptoms
3. **Document**: Keep notes on recurring issues and solutions
4. **Automate**: Set up automated responses for common issues

## Troubleshooting

### High CPU Usage

**Symptoms:**
- CPU usage consistently above 80%
- Slow response times
- System lag

**Solutions:**
1. Check for resource-intensive calculations
2. Review recent code changes
3. Optimize database queries
4. Scale horizontally if needed

### High Memory Usage

**Symptoms:**
- Memory usage above 85%
- Out of memory errors
- Application crashes

**Solutions:**
1. Check for memory leaks
2. Review caching strategy
3. Optimize data structures
4. Increase available memory

### Low Disk Space

**Symptoms:**
- Disk usage above 90%
- Write failures
- Log rotation issues

**Solutions:**
1. Clean up old logs
2. Archive old data
3. Remove temporary files
4. Increase disk capacity

### Database Connection Issues

**Symptoms:**
- Database health status: error
- Connection failures
- Timeout errors

**Solutions:**
1. Check database server status
2. Verify connection credentials
3. Review connection pool settings
4. Check network connectivity

### High Error Rates

**Symptoms:**
- Error rate above 5%
- Frequent 500 errors
- User complaints

**Solutions:**
1. Review error logs
2. Identify common error patterns
3. Fix underlying issues
4. Improve error handling

## Security Considerations

### Access Control

- Dashboard should only be accessible to administrators
- Implement role-based access control (RBAC)
- Use authentication middleware
- Log all admin actions

### Data Protection

- Sensitive data should be masked or encrypted
- Implement rate limiting on API endpoints
- Use HTTPS for all communications
- Regular security audits

### Monitoring

- Monitor for unusual activity patterns
- Set up alerts for security events
- Regular review of access logs
- Implement intrusion detection

## Integration

### With Monitoring Service

The Admin Dashboard integrates with the existing Monitoring Service for solar system monitoring:

```python
from services.monitoring_service import MonitoringService
from services.admin_dashboard_service import AdminDashboardService

# Both services can be used together
monitoring = MonitoringService(db)
dashboard = AdminDashboardService(db)

# Get solar system health
solar_health = await monitoring.check_system_health(site_id)

# Get overall system health
system_health = dashboard.get_system_health()
```

### With Logging System

Integrate with application logging:

```python
import logging

logger = logging.getLogger(__name__)

# Log admin actions
logger.info(f"Admin {user_id} accessed dashboard")
logger.warning(f"High CPU usage detected: {cpu_percent}%")
logger.error(f"Database connection failed: {error}")
```

### With Alert System

Integrate with notification systems:

```python
# Send email alerts
if alert.severity == "critical":
    send_email_alert(alert)

# Send SMS alerts
if alert.severity == "critical":
    send_sms_alert(alert)

# Send push notifications
send_push_notification(alert)
```

## Future Enhancements

### Planned Features

1. **Custom Dashboards**: User-configurable dashboard layouts
2. **Advanced Analytics**: Machine learning-based anomaly detection
3. **Predictive Alerts**: Predict issues before they occur
4. **Multi-tenant Support**: Separate dashboards for different organizations
5. **Export Reports**: Generate PDF/Excel reports
6. **Mobile App**: Native mobile dashboard application
7. **Real-time Collaboration**: Multiple admins viewing dashboard simultaneously
8. **Custom Metrics**: User-defined metrics and KPIs

### Roadmap

- Q1 2024: Custom dashboards and advanced analytics
- Q2 2024: Predictive alerts and machine learning integration
- Q3 2024: Mobile app and real-time collaboration
- Q4 2024: Multi-tenant support and custom metrics

## Support

For issues or questions:
- Email: support@solarcalculatorpro.com
- Documentation: https://docs.solarcalculatorpro.com
- GitHub: https://github.com/solarcalculatorpro/issues

## License

Copyright © 2024 Solar Calculator Pro. All rights reserved.
