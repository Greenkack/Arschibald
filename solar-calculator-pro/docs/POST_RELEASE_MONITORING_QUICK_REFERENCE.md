# Post-Release Monitoring - Quick Reference

## Quick Start

```python
from backend.services.monitoring_service import MonitoringService

service = MonitoringService(db)
```

## Common Operations

### Track Performance

```python
# Track metric
service.track_performance_metric(
    metric_name='api_response_time',
    value=125.5,
    unit='ms'
)

# Get summary
summary = service.get_performance_summary()

# Get trends
trends = service.get_performance_trends('api_response_time', days=7)
```

### Report Crashes

```python
# Report crash
service.report_crash(
    error_type='TypeError',
    error_message='Error message',
    stack_trace='...',
    user_id=123,
    app_version='1.0.0'
)

# Get statistics
stats = service.get_crash_statistics(days=7)
```

### User Feedback

```python
# Submit feedback
service.submit_feedback(
    user_id=123,
    feedback_type='feature_request',
    title='Add dark mode',
    description='Details...',
    rating=5
)

# Get summary
summary = service.get_feedback_summary(days=30)
```

### Update Tracking

```python
# Track update
service.track_update_adoption(
    user_id=123,
    from_version='1.0.0',
    to_version='1.1.0',
    update_method='auto',
    success=True
)

# Get adoption stats
stats = service.get_update_adoption_stats('1.1.0')
```

### Improvement Planning

```python
# Analyze opportunities
opportunities = service.analyze_improvement_opportunities(days=30)

# Create roadmap
roadmap = service.create_improvement_roadmap(opportunities)
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/monitoring/performance/track` | POST | Track metric |
| `/monitoring/performance/summary` | GET | Get summary |
| `/monitoring/crashes/report` | POST | Report crash |
| `/monitoring/crashes/statistics` | GET | Get stats |
| `/monitoring/feedback/submit` | POST | Submit feedback |
| `/monitoring/feedback/summary` | GET | Get summary |
| `/monitoring/updates/track` | POST | Track update |
| `/monitoring/updates/adoption/{version}` | GET | Get adoption |
| `/monitoring/improvements/opportunities` | GET | Get opportunities |
| `/monitoring/health` | GET | Health check |

## Frontend Usage

```typescript
import { MonitoringDashboard } from './components/monitoring/MonitoringDashboard';

// Use dashboard
<MonitoringDashboard />

// Track performance
await api.post('/api/v1/monitoring/performance/track', {
  metric_name: 'page_load_time',
  value: 1250,
  unit: 'ms'
});

// Report crash
await api.post('/api/v1/monitoring/crashes/report', {
  error_type: 'TypeError',
  error_message: 'Error',
  stack_trace: '...'
});
```

## Key Metrics

### Performance
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- API response time (ms)

### Crashes
- Total crashes
- Crash-free rate (%)
- Unique errors
- Affected users

### Feedback
- Total feedback
- By type (bug, feature, improvement, praise)
- Average rating (1-5)
- Sentiment (positive, neutral, negative)

### Updates
- Adoption rate (%)
- Success rate (%)
- Update methods (auto, manual, forced)
- Version distribution

## Health Status

```python
health = service.get_health_status()
# Returns: 'healthy', 'degraded', or 'critical'
```

## Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| CPU Usage | 70% | 90% |
| Memory Usage | 80% | 95% |
| Crash-Free Rate | <98% | <95% |
| Disk Usage | 80% | 95% |

## Time Ranges

- Last 24 hours: `days=1`
- Last 7 days: `days=7`
- Last 30 days: `days=30`
- Last 90 days: `days=90`

## Feedback Types

- `bug`: Bug report
- `feature_request`: Feature request
- `improvement`: Improvement suggestion
- `praise`: Positive feedback

## Update Methods

- `auto`: Automatic update
- `manual`: User-initiated update
- `forced`: Forced update (critical)

## Priority Levels

- `high_priority`: Critical issues
- `medium_priority`: Important improvements
- `low_priority`: Nice-to-have features
- `quick_wins`: Easy, high-impact changes
- `long_term`: Strategic initiatives

## Best Practices

1. **Track Consistently**: Monitor key metrics regularly
2. **Set Alerts**: Configure alerts for critical thresholds
3. **Review Regularly**: Check dashboard daily/weekly
4. **Act on Data**: Use insights to drive improvements
5. **Communicate**: Share findings with team
6. **Iterate**: Continuously improve monitoring

## Common Issues

### High Memory Usage
```python
# Check performance
summary = service.get_performance_summary()
print(summary['system']['memory_percent'])

# Review trends
trends = service.get_performance_trends('memory_usage', days=7)
```

### Frequent Crashes
```python
# Get crash stats
stats = service.get_crash_statistics(days=7)
print(stats['most_common_errors'])

# Get reports
reports = service.get_crash_reports(status='new', days=7)
```

### Low Update Adoption
```python
# Check adoption
stats = service.get_update_adoption_stats('1.1.0')
print(f"Adoption rate: {stats['adoption_rate']}%")

# Check distribution
dist = service.get_version_distribution()
print(f"Outdated users: {dist['outdated_percentage']}%")
```

## Integration Examples

### Electron App

```javascript
// Track performance
ipcRenderer.invoke('track-performance', {
  metric_name: 'startup_time',
  value: 2500,
  unit: 'ms'
});

// Report crash
process.on('uncaughtException', (error) => {
  ipcRenderer.invoke('report-crash', {
    error_type: error.name,
    error_message: error.message,
    stack_trace: error.stack
  });
});
```

### React Component

```typescript
useEffect(() => {
  const startTime = performance.now();
  
  return () => {
    const loadTime = performance.now() - startTime;
    api.post('/api/v1/monitoring/performance/track', {
      metric_name: 'component_render_time',
      value: loadTime,
      unit: 'ms',
      metadata: { component: 'SolarCalculator' }
    });
  };
}, []);
```

## Data Export

```python
# Export performance data
performance_data = service.get_performance_summary()

# Export crash reports
crash_reports = service.get_crash_reports(days=30, limit=1000)

# Export feedback
feedback = service.get_feedback_summary(days=30)
```

## Support

- 📖 Full Guide: `POST_RELEASE_MONITORING_GUIDE.md`
- 🔧 API Docs: `/api/v1/docs`
- 💬 Feedback: Use the monitoring system itself!
