"""
Task 38: Analytics und Insights
===============================
Theme Analytics für Nutzungsverfolgung und Insights.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import csv
from io import StringIO


@dataclass
class ThemeEvent:
    """Theme-related event."""
    event_type: str
    theme_name: str
    timestamp: str
    user_id: Optional[str]
    metadata: Dict


@dataclass
class ComponentUsage:
    """Component usage statistics."""
    component_name: str
    usage_count: int
    last_used: str


@dataclass
class PerformanceMetric:
    """Performance metric entry."""
    metric_name: str
    value: float
    unit: str
    timestamp: str


class ThemeAnalytics:
    """Analytics system for theme usage tracking."""
    
    def __init__(self, gdpr_compliant: bool = True):
        self.events: List[ThemeEvent] = []
        self.component_usage: Dict[str, ComponentUsage] = {}
        self.performance_metrics: List[PerformanceMetric] = []
        self.gdpr_compliant = gdpr_compliant
    
    def track_theme_change(self, theme_name: str, user_id: Optional[str] = None,
                          previous_theme: Optional[str] = None):
        """Track theme change event."""
        # GDPR: Anonymize user_id if required
        safe_user_id = self._anonymize_user(user_id) if self.gdpr_compliant else user_id
        
        event = ThemeEvent(
            event_type="theme_change",
            theme_name=theme_name,
            timestamp=datetime.now().isoformat(),
            user_id=safe_user_id,
            metadata={"previous_theme": previous_theme}
        )
        self.events.append(event)
    
    def track_component_usage(self, component_name: str):
        """Track component usage."""
        now = datetime.now().isoformat()
        
        if component_name in self.component_usage:
            usage = self.component_usage[component_name]
            self.component_usage[component_name] = ComponentUsage(
                component_name=component_name,
                usage_count=usage.usage_count + 1,
                last_used=now
            )
        else:
            self.component_usage[component_name] = ComponentUsage(
                component_name=component_name,
                usage_count=1,
                last_used=now
            )
    
    def track_performance(self, metric_name: str, value: float, unit: str = "ms"):
        """Track performance metric."""
        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            unit=unit,
            timestamp=datetime.now().isoformat()
        )
        self.performance_metrics.append(metric)
    
    def _anonymize_user(self, user_id: Optional[str]) -> Optional[str]:
        """Anonymize user ID for GDPR compliance."""
        if user_id is None:
            return None
        # Simple hash-based anonymization
        return f"user_{hash(user_id) % 10000:04d}"
    
    def get_theme_popularity(self) -> Dict[str, int]:
        """Get theme popularity statistics."""
        popularity = {}
        for event in self.events:
            if event.event_type == "theme_change":
                theme = event.theme_name
                popularity[theme] = popularity.get(theme, 0) + 1
        return dict(sorted(popularity.items(), key=lambda x: x[1], reverse=True))
    
    def get_component_stats(self) -> List[Dict]:
        """Get component usage statistics."""
        return [asdict(usage) for usage in self.component_usage.values()]
    
    def get_performance_summary(self) -> Dict[str, Dict]:
        """Get performance metrics summary."""
        summary = {}
        for metric in self.performance_metrics:
            name = metric.metric_name
            if name not in summary:
                summary[name] = {"values": [], "unit": metric.unit}
            summary[name]["values"].append(metric.value)
        
        # Calculate averages
        for name, data in summary.items():
            values = data["values"]
            summary[name] = {
                "avg": sum(values) / len(values) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
                "count": len(values),
                "unit": data["unit"]
            }
        
        return summary
    
    def export_as_csv(self) -> str:
        """Export analytics data as CSV."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Events
        writer.writerow(["Events"])
        writer.writerow(["Type", "Theme", "Timestamp", "User ID"])
        for event in self.events:
            writer.writerow([
                event.event_type,
                event.theme_name,
                event.timestamp,
                event.user_id or "anonymous"
            ])
        
        writer.writerow([])
        
        # Component Usage
        writer.writerow(["Component Usage"])
        writer.writerow(["Component", "Usage Count", "Last Used"])
        for usage in self.component_usage.values():
            writer.writerow([
                usage.component_name,
                usage.usage_count,
                usage.last_used
            ])
        
        writer.writerow([])
        
        # Performance
        writer.writerow(["Performance Metrics"])
        writer.writerow(["Metric", "Value", "Unit", "Timestamp"])
        for metric in self.performance_metrics:
            writer.writerow([
                metric.metric_name,
                metric.value,
                metric.unit,
                metric.timestamp
            ])
        
        return output.getvalue()
    
    def export_as_json(self) -> str:
        """Export analytics data as JSON."""
        data = {
            "events": [asdict(e) for e in self.events],
            "component_usage": self.get_component_stats(),
            "performance_summary": self.get_performance_summary(),
            "theme_popularity": self.get_theme_popularity()
        }
        return json.dumps(data, indent=2)
    
    def get_dashboard_data(self) -> Dict:
        """Get data for analytics dashboard."""
        return {
            "total_theme_changes": len([e for e in self.events if e.event_type == "theme_change"]),
            "unique_themes_used": len(self.get_theme_popularity()),
            "most_popular_theme": list(self.get_theme_popularity().keys())[0] if self.get_theme_popularity() else None,
            "total_component_renders": sum(u.usage_count for u in self.component_usage.values()),
            "most_used_component": max(self.component_usage.values(), key=lambda x: x.usage_count).component_name if self.component_usage else None,
            "performance_summary": self.get_performance_summary()
        }
    
    def clear_data(self):
        """Clear all analytics data (GDPR right to erasure)."""
        self.events.clear()
        self.component_usage.clear()
        self.performance_metrics.clear()


# Global instance
analytics = ThemeAnalytics(gdpr_compliant=True)


def track_theme_change(theme_name: str, user_id: Optional[str] = None):
    """Track theme change."""
    analytics.track_theme_change(theme_name, user_id)


def track_component(component_name: str):
    """Track component usage."""
    analytics.track_component_usage(component_name)


def track_performance(metric_name: str, value: float, unit: str = "ms"):
    """Track performance metric."""
    analytics.track_performance(metric_name, value, unit)


def get_analytics_dashboard() -> Dict:
    """Get dashboard data."""
    return analytics.get_dashboard_data()
