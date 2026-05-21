# Admin Dashboard - Quick Reference

## Quick Start

```bash
# Backend
cd solar-calculator-pro/backend
python -m uvicorn main:app --reload

# Frontend
cd solar-calculator-pro/frontend
npm start

# Access Dashboard
http://localhost:3000/admin/dashboard
```

## API Endpoints Cheat Sheet

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/dashboard/summary` | GET | Complete dashboard data |
| `/admin/dashboard/health/system` | GET | System health metrics |
| `/admin/dashboard/health/database` | GET | Database health |
| `/admin/dashboard/statistics/usage` | GET | Usage statistics |
| `/admin/dashboard/metrics/performance` | GET | Performance metrics |
| `/admin/dashboard/activity/users` | GET | User activity |
| `/admin/dashboard/alerts` | GET | System alerts |
| `/admin/dashboard/alerts/{id}/resolve` | POST | Resolve alert |
| `/admin/dashboard/metrics/historical` | GET | Historical data |

## Health Status Colors

| Color | Status | Threshold |
|-------|--------|-----------|
| 🟢 Green | Healthy | Normal operation |
| 🟡 Yellow | Warning | Attention needed |
| 🔴 Red | Critical | Immediate action |

## Resource Thresholds

| Resource | Healthy | Warning | Critical |
|----------|---------|---------|----------|
| CPU | < 80% | 80-100% | - |
| Memory | < 85% | 85-100% | - |
| Disk | < 80% | 80-90% | > 90% |

## Common Commands

### Check System Health
```bash
curl http://localhost:8000/api/v1/admin/dashboard/health/system
```

### Get Usage Statistics
```bash
curl http://localhost:8000/api/v1/admin/dashboard/statistics/usage?period=today
```

### Get Active Alerts
```bash
curl http://localhost:8000/api/v1/admin/dashboard/alerts
```

### Resolve Alert
```bash
curl -X POST http://localhost:8000/api/v1/admin/dashboard/alerts/1/resolve
```

## Frontend Component Usage

```tsx
import AdminDashboard from './components/admin/AdminDashboard';

// Basic usage
<AdminDashboard />

// With custom API URL
<AdminDashboard apiUrl="https://api.example.com/v1" />
```

## Environment Variables

```env
# Backend
DATABASE_URL=postgresql://user:pass@localhost/db
LOG_LEVEL=INFO

# Frontend
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_REFRESH_INTERVAL=30000
```

## Troubleshooting Quick Fixes

### High CPU
```bash
# Check processes
ps aux --sort=-%cpu | head -10

# Restart service
systemctl restart solar-calculator
```

### High Memory
```bash
# Check memory usage
free -h

# Clear cache
sync; echo 3 > /proc/sys/vm/drop_caches
```

### Low Disk Space
```bash
# Check disk usage
df -h

# Clean logs
find /var/log -name "*.log" -mtime +30 -delete
```

### Database Issues
```bash
# Check database status
systemctl status postgresql

# Restart database
systemctl restart postgresql
```

## Alert Severity Levels

| Level | Icon | Action Required |
|-------|------|-----------------|
| Info | ℹ️ | Monitor |
| Warning | ⚠️ | Investigate soon |
| Critical | 🚨 | Immediate action |

## Performance Targets

| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| Response Time | < 100ms | < 200ms | > 500ms |
| Error Rate | < 0.5% | < 1% | > 5% |
| Throughput | > 50 rps | > 20 rps | < 10 rps |
| Cache Hit Rate | > 90% | > 80% | < 70% |

## Monitoring Schedule

| Task | Frequency | Priority |
|------|-----------|----------|
| Check alerts | Real-time | High |
| Review health | Hourly | High |
| Analyze trends | Daily | Medium |
| Generate reports | Weekly | Medium |
| Capacity planning | Monthly | Low |

## Key Metrics to Watch

### System Health
- CPU usage < 80%
- Memory usage < 85%
- Disk usage < 80%
- System uptime > 99.9%

### Application Performance
- Average response time < 200ms
- Error rate < 1%
- Throughput > 20 rps
- Cache hit rate > 80%

### User Activity
- Active users trend
- New user registrations
- Session duration
- Action patterns

### Business Metrics
- Projects created
- Calculations performed
- PDFs generated
- API usage

## Common Issues & Solutions

| Issue | Quick Fix |
|-------|-----------|
| Dashboard not loading | Check API connection |
| No data showing | Verify backend is running |
| Alerts not appearing | Check alert service |
| Slow performance | Clear cache, restart services |
| High error rate | Check logs, review recent changes |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `R` | Refresh dashboard |
| `A` | Toggle auto-refresh |
| `P` | Change period |
| `Esc` | Close modal |

## Best Practices

✅ **DO:**
- Monitor dashboard daily
- Address critical alerts immediately
- Review trends weekly
- Document recurring issues
- Keep services updated

❌ **DON'T:**
- Ignore warning alerts
- Disable monitoring
- Skip regular reviews
- Overlook trends
- Delay critical updates

## Support Resources

- 📖 Full Guide: `/docs/ADMIN_DASHBOARD_GUIDE.md`
- 🐛 Report Issues: GitHub Issues
- 💬 Community: Discord Server
- 📧 Email: support@solarcalculatorpro.com

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01 | Initial release |
| 1.1.0 | 2024-02 | Added historical metrics |
| 1.2.0 | 2024-03 | Enhanced alerts |

---

**Last Updated:** 2024-01-15
**Maintained By:** Solar Calculator Pro Team
