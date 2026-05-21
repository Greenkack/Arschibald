"""
Performance Monitoring System
Task 190: APM, metrics, dashboards, and alerting
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
import time
import statistics
import asyncio


router = APIRouter(prefix="/monitoring", tags=["Performance Monitoring"])


class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Metric(BaseModel):
    name: str
    type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = {}
    unit: str = ""


class Alert(BaseModel):
    id: str
    name: str
    severity: AlertSeverity
    message: str
    metric_name: str
    threshold: float
    current_value: float
    triggered_at: datetime
    resolved_at: Optional[datetime] = None


class AlertRule(BaseModel):
    id: str
    name: str
    metric_name: str
    condition: str  # gt, lt, eq, gte, lte
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 5


class PerformanceMetrics:
    """Performance metrics collector"""
    
    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = {}
        self.alerts: List[Alert] = []
        self.alert_rules: List[AlertRule] = []
        self.request_times: List[float] = []
        self.error_counts: Dict[str, int] = {}
        self.endpoint_stats: Dict[str, Dict] = {}
        
    def record_metric(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE,
                      tags: Dict[str, str] = {}, unit: str = ""):
        metric = Metric(name=name, type=metric_type, value=value, timestamp=datetime.now(), tags=tags, unit=unit)
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(metric)
        # Keep last 1000 entries
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
        self._check_alerts(name, value)
        
    def record_request(self, endpoint: str, method: str, duration_ms: float, status_code: int):
        self.request_times.append(duration_ms)
        if len(self.request_times) > 10000:
            self.request_times = self.request_times[-10000:]
        key = f"{method}:{endpoint}"
        if key not in self.endpoint_stats:
            self.endpoint_stats[key] = {"count": 0, "total_time": 0, "errors": 0, "times": []}
        self.endpoint_stats[key]["count"] += 1
        self.endpoint_stats[key]["total_time"] += duration_ms
        self.endpoint_stats[key]["times"].append(duration_ms)
        if len(self.endpoint_stats[key]["times"]) > 100:
            self.endpoint_stats[key]["times"] = self.endpoint_stats[key]["times"][-100:]
        if status_code >= 400:
            self.endpoint_stats[key]["errors"] += 1
            
    def record_error(self, error_type: str):
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
    def _check_alerts(self, metric_name: str, value: float):
        for rule in self.alert_rules:
            if not rule.enabled or rule.metric_name != metric_name:
                continue
            triggered = False
            if rule.condition == "gt" and value > rule.threshold:
                triggered = True
            elif rule.condition == "lt" and value < rule.threshold:
                triggered = True
            elif rule.condition == "gte" and value >= rule.threshold:
                triggered = True
            elif rule.condition == "lte" and value <= rule.threshold:
                triggered = True
            elif rule.condition == "eq" and value == rule.threshold:
                triggered = True
            if triggered:
                alert = Alert(id=f"alert_{len(self.alerts)}", name=rule.name, severity=rule.severity,
                             message=f"{metric_name} {rule.condition} {rule.threshold} (current: {value})",
                             metric_name=metric_name, threshold=rule.threshold, current_value=value,
                             triggered_at=datetime.now())
                self.alerts.append(alert)
                
    def get_metric_stats(self, name: str, minutes: int = 60) -> Dict:
        if name not in self.metrics:
            return {}
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent = [m.value for m in self.metrics[name] if m.timestamp >= cutoff]
        if not recent:
            return {}
        return {"min": min(recent), "max": max(recent), "avg": statistics.mean(recent),
                "count": len(recent), "latest": recent[-1]}
                
    def get_request_stats(self) -> Dict:
        if not self.request_times:
            return {}
        return {"total_requests": len(self.request_times), "avg_response_ms": statistics.mean(self.request_times),
                "p50_ms": statistics.median(self.request_times),
                "p95_ms": statistics.quantiles(self.request_times, n=20)[18] if len(self.request_times) > 20 else max(self.request_times),
                "p99_ms": statistics.quantiles(self.request_times, n=100)[98] if len(self.request_times) > 100 else max(self.request_times)}


# Global metrics instance
metrics = PerformanceMetrics()

# Default alert rules
metrics.alert_rules = [
    AlertRule(id="high_response_time", name="High Response Time", metric_name="response_time_ms",
              condition="gt", threshold=2000, severity=AlertSeverity.WARNING),
    AlertRule(id="high_memory", name="High Memory Usage", metric_name="memory_usage_mb",
              condition="gt", threshold=500, severity=AlertSeverity.WARNING),
    AlertRule(id="high_cpu", name="High CPU Usage", metric_name="cpu_usage_percent",
              condition="gt", threshold=80, severity=AlertSeverity.ERROR),
    AlertRule(id="high_error_rate", name="High Error Rate", metric_name="error_rate_percent",
              condition="gt", threshold=5, severity=AlertSeverity.CRITICAL)
]


@router.post("/metrics")
async def record_metric(name: str, value: float, metric_type: MetricType = MetricType.GAUGE,
                        tags: Dict[str, str] = {}, unit: str = ""):
    metrics.record_metric(name, value, metric_type, tags, unit)
    return {"status": "recorded"}


@router.get("/metrics/{name}")
async def get_metric(name: str, minutes: int = 60):
    stats = metrics.get_metric_stats(name, minutes)
    if not stats:
        raise HTTPException(status_code=404, detail="Metric not found")
    return stats


@router.get("/metrics")
async def list_metrics():
    return {"metrics": list(metrics.metrics.keys()), "count": len(metrics.metrics)}


@router.get("/requests/stats")
async def get_request_stats():
    return metrics.get_request_stats()


@router.get("/endpoints/stats")
async def get_endpoint_stats():
    result = {}
    for key, stats in metrics.endpoint_stats.items():
        result[key] = {"count": stats["count"], "avg_ms": stats["total_time"] / stats["count"] if stats["count"] > 0 else 0,
                       "errors": stats["errors"], "error_rate": stats["errors"] / stats["count"] * 100 if stats["count"] > 0 else 0}
    return result


@router.get("/alerts")
async def get_alerts(severity: Optional[AlertSeverity] = None, resolved: Optional[bool] = None):
    filtered = metrics.alerts
    if severity:
        filtered = [a for a in filtered if a.severity == severity]
    if resolved is not None:
        filtered = [a for a in filtered if (a.resolved_at is not None) == resolved]
    return filtered


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    for alert in metrics.alerts:
        if alert.id == alert_id:
            alert.resolved_at = datetime.now()
            return {"status": "resolved"}
    raise HTTPException(status_code=404, detail="Alert not found")


@router.get("/alert-rules")
async def get_alert_rules():
    return metrics.alert_rules


@router.post("/alert-rules")
async def create_alert_rule(rule: AlertRule):
    metrics.alert_rules.append(rule)
    return rule


@router.get("/dashboard")
async def get_dashboard():
    return {"request_stats": metrics.get_request_stats(), "active_alerts": len([a for a in metrics.alerts if not a.resolved_at]),
            "total_errors": sum(metrics.error_counts.values()), "metrics_tracked": len(metrics.metrics),
            "top_endpoints": sorted(metrics.endpoint_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:5]}


@router.get("/health")
async def get_health():
    request_stats = metrics.get_request_stats()
    issues = []
    if request_stats.get("avg_response_ms", 0) > 1000:
        issues.append("High average response time")
    active_alerts = [a for a in metrics.alerts if not a.resolved_at]
    critical = [a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]
    if critical:
        issues.append(f"{len(critical)} critical alerts")
    status = "healthy" if not issues else "degraded" if len(issues) < 3 else "unhealthy"
    return {"status": status, "issues": issues, "active_alerts": len(active_alerts)}
