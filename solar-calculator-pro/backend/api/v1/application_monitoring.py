"""
Application Monitoring System
Task 79: Monitoring, alerts, log aggregation, and dashboards
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
import statistics
import random

router = APIRouter(prefix="/monitoring", tags=["Application Monitoring"])


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class Alert(BaseModel):
    """Alert model"""
    id: str
    name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    source: str
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    labels: Dict[str, str] = {}


class AlertRule(BaseModel):
    """Alert rule configuration"""
    id: str
    name: str
    description: str
    condition: str
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    notification_channels: List[str] = []
    cooldown_minutes: int = 5


class Metric(BaseModel):
    """Metric data point"""
    name: str
    type: MetricType
    value: float
    timestamp: datetime
    labels: Dict[str, str] = {}


class LogEntry(BaseModel):
    """Log entry"""
    timestamp: datetime
    level: str
    service: str
    message: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class Dashboard(BaseModel):
    """Dashboard configuration"""
    id: str
    name: str
    description: str
    panels: List[Dict[str, Any]]
    refresh_interval: int = 30
    time_range: str = "1h"


# In-memory storage
alerts_db: List[Alert] = []
alert_rules_db: List[AlertRule] = []
metrics_db: List[Metric] = []
logs_db: List[LogEntry] = []
dashboards_db: List[Dashboard] = []

# Initialize default alert rules
default_rules = [
    AlertRule(
        id="cpu_high",
        name="High CPU Usage",
        description="CPU usage exceeds threshold",
        condition="cpu_percent > threshold",
        threshold=90.0,
        severity=AlertSeverity.WARNING,
        notification_channels=["email", "slack"]
    ),
    AlertRule(
        id="memory_high",
        name="High Memory Usage",
        description="Memory usage exceeds threshold",
        condition="memory_percent > threshold",
        threshold=85.0,
        severity=AlertSeverity.WARNING,
        notification_channels=["email", "slack"]
    ),
    AlertRule(
        id="error_rate_high",
        name="High Error Rate",
        description="Error rate exceeds threshold",
        condition="error_rate > threshold",
        threshold=5.0,
        severity=AlertSeverity.ERROR,
        notification_channels=["email", "slack", "pagerduty"]
    ),
    AlertRule(
        id="response_time_high",
        name="High Response Time",
        description="Average response time exceeds threshold",
        condition="avg_response_time_ms > threshold",
        threshold=1000.0,
        severity=AlertSeverity.WARNING,
        notification_channels=["slack"]
    ),
    AlertRule(
        id="disk_space_low",
        name="Low Disk Space",
        description="Available disk space below threshold",
        condition="disk_free_percent < threshold",
        threshold=10.0,
        severity=AlertSeverity.CRITICAL,
        notification_channels=["email", "slack", "pagerduty"]
    )
]
alert_rules_db.extend(default_rules)


# ============================================
# Metrics Endpoints
# ============================================

@router.get("/metrics")
async def get_metrics(
    name: Optional[str] = None,
    time_range: str = "1h",
    aggregation: str = "avg"
):
    """Get application metrics"""
    # Generate sample metrics
    now = datetime.now()
    metrics = {
        "http_requests_total": {
            "type": "counter",
            "value": 150000,
            "rate_per_second": 25.5
        },
        "http_request_duration_seconds": {
            "type": "histogram",
            "avg": 0.125,
            "p50": 0.100,
            "p95": 0.350,
            "p99": 0.750
        },
        "active_connections": {
            "type": "gauge",
            "value": 45
        },
        "cpu_usage_percent": {
            "type": "gauge",
            "value": 35.5
        },
        "memory_usage_percent": {
            "type": "gauge",
            "value": 62.3
        },
        "disk_usage_percent": {
            "type": "gauge",
            "value": 45.8
        },
        "database_connections": {
            "type": "gauge",
            "value": 20
        },
        "cache_hit_ratio": {
            "type": "gauge",
            "value": 0.92
        },
        "error_rate_percent": {
            "type": "gauge",
            "value": 0.5
        }
    }
    
    if name:
        return {name: metrics.get(name, {})}
    return {"metrics": metrics, "timestamp": now.isoformat()}


@router.get("/metrics/timeseries")
async def get_metrics_timeseries(
    metric_name: str,
    time_range: str = "1h",
    interval: str = "1m"
):
    """Get metric time series data"""
    now = datetime.now()
    
    # Parse time range
    hours = 1
    if time_range.endswith("h"):
        hours = int(time_range[:-1])
    elif time_range.endswith("d"):
        hours = int(time_range[:-1]) * 24
    
    # Generate sample time series
    data_points = []
    for i in range(hours * 60):  # One point per minute
        timestamp = now - timedelta(minutes=hours * 60 - i)
        value = 50 + random.uniform(-10, 10) + (i % 60) * 0.1
        data_points.append({
            "timestamp": timestamp.isoformat(),
            "value": round(value, 2)
        })
    
    return {
        "metric": metric_name,
        "time_range": time_range,
        "interval": interval,
        "data": data_points[-100:]  # Last 100 points
    }


@router.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Get metrics in Prometheus format"""
    metrics = []
    
    # HTTP metrics
    metrics.append("# HELP http_requests_total Total HTTP requests")
    metrics.append("# TYPE http_requests_total counter")
    metrics.append('http_requests_total{method="GET",status="200"} 100000')
    metrics.append('http_requests_total{method="POST",status="200"} 45000')
    metrics.append('http_requests_total{method="GET",status="500"} 500')
    
    # Response time
    metrics.append("# HELP http_request_duration_seconds HTTP request duration")
    metrics.append("# TYPE http_request_duration_seconds histogram")
    metrics.append('http_request_duration_seconds_bucket{le="0.1"} 80000')
    metrics.append('http_request_duration_seconds_bucket{le="0.5"} 140000')
    metrics.append('http_request_duration_seconds_bucket{le="1.0"} 148000')
    metrics.append('http_request_duration_seconds_bucket{le="+Inf"} 150000')
    
    # System metrics
    metrics.append("# HELP process_cpu_percent CPU usage percentage")
    metrics.append("# TYPE process_cpu_percent gauge")
    metrics.append("process_cpu_percent 35.5")
    
    metrics.append("# HELP process_memory_percent Memory usage percentage")
    metrics.append("# TYPE process_memory_percent gauge")
    metrics.append("process_memory_percent 62.3")
    
    return "\n".join(metrics)


# ============================================
# Alerts Endpoints
# ============================================

@router.get("/alerts", response_model=List[Alert])
async def get_alerts(
    status: Optional[AlertStatus] = None,
    severity: Optional[AlertSeverity] = None,
    limit: int = 50
):
    """Get alerts"""
    filtered = alerts_db
    if status:
        filtered = [a for a in filtered if a.status == status]
    if severity:
        filtered = [a for a in filtered if a.severity == severity]
    return filtered[-limit:]


@router.get("/alerts/active")
async def get_active_alerts():
    """Get active alerts summary"""
    active = [a for a in alerts_db if a.status == AlertStatus.ACTIVE]
    
    by_severity = {
        "critical": len([a for a in active if a.severity == AlertSeverity.CRITICAL]),
        "error": len([a for a in active if a.severity == AlertSeverity.ERROR]),
        "warning": len([a for a in active if a.severity == AlertSeverity.WARNING]),
        "info": len([a for a in active if a.severity == AlertSeverity.INFO])
    }
    
    return {
        "total_active": len(active),
        "by_severity": by_severity,
        "alerts": active[:10]
    }


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, acknowledged_by: str):
    """Acknowledge an alert"""
    for alert in alerts_db:
        if alert.id == alert_id:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = acknowledged_by
            return alert
    raise HTTPException(status_code=404, detail="Alert not found")


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert"""
    for alert in alerts_db:
        if alert.id == alert_id:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            return alert
    raise HTTPException(status_code=404, detail="Alert not found")


@router.get("/alerts/rules", response_model=List[AlertRule])
async def get_alert_rules():
    """Get alert rules"""
    return alert_rules_db


@router.post("/alerts/rules", response_model=AlertRule)
async def create_alert_rule(rule: AlertRule):
    """Create alert rule"""
    alert_rules_db.append(rule)
    return rule


@router.put("/alerts/rules/{rule_id}")
async def update_alert_rule(rule_id: str, enabled: Optional[bool] = None, threshold: Optional[float] = None):
    """Update alert rule"""
    for rule in alert_rules_db:
        if rule.id == rule_id:
            if enabled is not None:
                rule.enabled = enabled
            if threshold is not None:
                rule.threshold = threshold
            return rule
    raise HTTPException(status_code=404, detail="Rule not found")


# ============================================
# Logs Endpoints
# ============================================

@router.get("/logs")
async def get_logs(
    level: Optional[str] = None,
    service: Optional[str] = None,
    search: Optional[str] = None,
    time_range: str = "1h",
    limit: int = 100
):
    """Get application logs"""
    # Generate sample logs
    now = datetime.now()
    sample_logs = []
    
    services = ["api", "worker", "scheduler", "database"]
    levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
    messages = [
        "Request processed successfully",
        "Database query executed in 5ms",
        "Cache hit for key: user_123",
        "Background job completed",
        "Connection pool size: 15/20",
        "Rate limit applied for IP: 10.0.0.5",
        "PDF generation completed",
        "Email sent successfully"
    ]
    
    for i in range(limit):
        log = {
            "timestamp": (now - timedelta(minutes=i)).isoformat(),
            "level": random.choice(levels) if not level else level,
            "service": random.choice(services) if not service else service,
            "message": random.choice(messages),
            "trace_id": f"trace_{random.randint(1000, 9999)}",
            "metadata": {
                "request_id": f"req_{random.randint(10000, 99999)}",
                "duration_ms": random.randint(1, 500)
            }
        }
        
        if search and search.lower() not in log["message"].lower():
            continue
            
        sample_logs.append(log)
    
    return {
        "logs": sample_logs[:limit],
        "total": len(sample_logs),
        "filters": {
            "level": level,
            "service": service,
            "search": search,
            "time_range": time_range
        }
    }


@router.get("/logs/stats")
async def get_log_stats(time_range: str = "1h"):
    """Get log statistics"""
    return {
        "time_range": time_range,
        "total_logs": 15000,
        "by_level": {
            "DEBUG": 5000,
            "INFO": 8000,
            "WARNING": 1500,
            "ERROR": 450,
            "CRITICAL": 50
        },
        "by_service": {
            "api": 8000,
            "worker": 4000,
            "scheduler": 2000,
            "database": 1000
        },
        "error_rate": 3.3,
        "top_errors": [
            {"message": "Connection timeout", "count": 150},
            {"message": "Rate limit exceeded", "count": 100},
            {"message": "Invalid input", "count": 80}
        ]
    }


# ============================================
# Dashboards Endpoints
# ============================================

@router.get("/dashboards", response_model=List[Dashboard])
async def get_dashboards():
    """Get all dashboards"""
    if not dashboards_db:
        # Create default dashboard
        default_dashboard = Dashboard(
            id="main",
            name="Main Dashboard",
            description="Overview of system health and performance",
            panels=[
                {
                    "id": "requests",
                    "title": "HTTP Requests",
                    "type": "timeseries",
                    "metric": "http_requests_total"
                },
                {
                    "id": "response_time",
                    "title": "Response Time",
                    "type": "timeseries",
                    "metric": "http_request_duration_seconds"
                },
                {
                    "id": "cpu",
                    "title": "CPU Usage",
                    "type": "gauge",
                    "metric": "cpu_usage_percent"
                },
                {
                    "id": "memory",
                    "title": "Memory Usage",
                    "type": "gauge",
                    "metric": "memory_usage_percent"
                },
                {
                    "id": "errors",
                    "title": "Error Rate",
                    "type": "stat",
                    "metric": "error_rate_percent"
                },
                {
                    "id": "active_alerts",
                    "title": "Active Alerts",
                    "type": "alertlist"
                }
            ]
        )
        dashboards_db.append(default_dashboard)
    
    return dashboards_db


@router.get("/dashboards/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    """Get dashboard by ID"""
    for dashboard in dashboards_db:
        if dashboard.id == dashboard_id:
            return dashboard
    raise HTTPException(status_code=404, detail="Dashboard not found")


@router.post("/dashboards", response_model=Dashboard)
async def create_dashboard(dashboard: Dashboard):
    """Create a new dashboard"""
    dashboards_db.append(dashboard)
    return dashboard


@router.get("/dashboards/{dashboard_id}/data")
async def get_dashboard_data(dashboard_id: str):
    """Get dashboard data with all panel values"""
    dashboard = None
    for d in dashboards_db:
        if d.id == dashboard_id:
            dashboard = d
            break
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Generate panel data
    panel_data = {}
    for panel in dashboard.panels:
        if panel["type"] == "gauge":
            panel_data[panel["id"]] = {
                "value": random.uniform(20, 80),
                "min": 0,
                "max": 100
            }
        elif panel["type"] == "stat":
            panel_data[panel["id"]] = {
                "value": random.uniform(0, 5),
                "trend": random.choice(["up", "down", "stable"])
            }
        elif panel["type"] == "timeseries":
            panel_data[panel["id"]] = {
                "data": [
                    {"timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(),
                     "value": random.uniform(50, 150)}
                    for i in range(60)
                ]
            }
        elif panel["type"] == "alertlist":
            panel_data[panel["id"]] = {
                "alerts": [a.dict() for a in alerts_db if a.status == AlertStatus.ACTIVE][:5]
            }
    
    return {
        "dashboard": dashboard,
        "data": panel_data,
        "timestamp": datetime.now().isoformat()
    }


# ============================================
# Health and Status
# ============================================

@router.get("/health")
async def get_monitoring_health():
    """Get monitoring system health"""
    return {
        "status": "healthy",
        "components": {
            "metrics_collector": "running",
            "alert_manager": "running",
            "log_aggregator": "running",
            "dashboard_service": "running"
        },
        "stats": {
            "metrics_collected": 150000,
            "alerts_processed": 500,
            "logs_ingested": 1000000,
            "dashboards_active": len(dashboards_db)
        },
        "timestamp": datetime.now().isoformat()
    }


@router.get("/status/overview")
async def get_status_overview():
    """Get system status overview"""
    active_alerts = len([a for a in alerts_db if a.status == AlertStatus.ACTIVE])
    critical_alerts = len([a for a in alerts_db if a.status == AlertStatus.ACTIVE and a.severity == AlertSeverity.CRITICAL])
    
    if critical_alerts > 0:
        status = "critical"
    elif active_alerts > 5:
        status = "warning"
    else:
        status = "healthy"
    
    return {
        "status": status,
        "uptime_percent": 99.95,
        "active_alerts": active_alerts,
        "critical_alerts": critical_alerts,
        "services": {
            "api": {"status": "healthy", "latency_ms": 45},
            "database": {"status": "healthy", "latency_ms": 5},
            "cache": {"status": "healthy", "latency_ms": 1},
            "worker": {"status": "healthy", "jobs_pending": 12}
        },
        "last_incident": None,
        "timestamp": datetime.now().isoformat()
    }
