"""
Admin Dashboard Service
Provides comprehensive system monitoring, health checks, usage statistics, and performance metrics
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import psutil
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class AdminDashboardService:
    """Service for admin dashboard data and system monitoring"""
    
    def __init__(self, db: Session):
        self.db = db
        self._cache = {}
        self._cache_ttl = 60  # seconds

    # System Health Monitoring
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get process info
            process = psutil.Process()
            process_memory = process.memory_info()
            
            # Determine health status
            health_status = "healthy"
            issues = []
            
            if cpu_percent > 80:
                health_status = "warning"
                issues.append("High CPU usage detected")
            
            if memory.percent > 85:
                health_status = "warning"
                issues.append("High memory usage detected")
            
            if disk.percent > 90:
                health_status = "critical"
                issues.append("Low disk space")
            
            return {
                "status": health_status,
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "status": "warning" if cpu_percent > 80 else "healthy"
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent,
                    "status": "warning" if memory.percent > 85 else "healthy"
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": disk.percent,
                    "status": "critical" if disk.percent > 90 else "warning" if disk.percent > 80 else "healthy"
                },
                "process": {
                    "memory_mb": round(process_memory.rss / (1024**2), 2),
                    "threads": process.num_threads(),
                    "connections": len(process.connections())
                },
                "issues": issues,
                "uptime_seconds": int((datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds())
            }
        except Exception as e:
            logger.error(f"Error getting system health: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_database_health(self) -> Dict[str, Any]:
        """Get database health and statistics"""
        try:
            # Test database connection
            self.db.execute("SELECT 1")
            
            # Get table statistics (simplified - would need actual table models)
            stats = {
                "status": "healthy",
                "connection": "active",
                "timestamp": datetime.now().isoformat(),
                "tables": {
                    "users": self._get_table_count("users"),
                    "projects": self._get_table_count("projects"),
                    "products": self._get_table_count("products"),
                    "customers": self._get_table_count("customers"),
                    "offers": self._get_table_count("offers")
                },
                "total_records": 0  # Would sum all tables
            }
            
            stats["total_records"] = sum(stats["tables"].values())
            
            return stats
        except Exception as e:
            logger.error(f"Error getting database health: {str(e)}")
            return {
                "status": "error",
                "connection": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _get_table_count(self, table_name: str) -> int:
        """Get count of records in a table"""
        try:
            # Simplified - would use actual models
            result = self.db.execute(f"SELECT COUNT(*) FROM {table_name}")
            return result.scalar() or 0
        except:
            return 0

    # Usage Statistics
    
    def get_usage_statistics(self, period: str = "today") -> Dict[str, Any]:
        """Get usage statistics for specified period"""
        try:
            start_date, end_date = self._get_period_dates(period)
            
            stats = {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "users": self._get_user_statistics(start_date, end_date),
                "projects": self._get_project_statistics(start_date, end_date),
                "calculations": self._get_calculation_statistics(start_date, end_date),
                "pdfs": self._get_pdf_statistics(start_date, end_date),
                "api": self._get_api_statistics(start_date, end_date)
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting usage statistics: {str(e)}")
            return {"error": str(e)}

    def _get_period_dates(self, period: str) -> tuple:
        """Get start and end dates for period"""
        end_date = datetime.now()
        
        if period == "today":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        elif period == "year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=1)
        
        return start_date, end_date

    def _get_user_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get user activity statistics"""
        try:
            # Simplified - would query actual user activity logs
            return {
                "total_users": 150,
                "active_users": 45,
                "new_users": 5,
                "login_count": 320,
                "average_session_duration_minutes": 25
            }
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            return {}

    def _get_project_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get project statistics"""
        try:
            # Simplified - would query actual project data
            return {
                "total_projects": 1250,
                "new_projects": 35,
                "completed_projects": 28,
                "active_projects": 180,
                "by_type": {
                    "solar": 800,
                    "heatpump": 300,
                    "combined": 150
                }
            }
        except Exception as e:
            logger.error(f"Error getting project statistics: {str(e)}")
            return {}

    def _get_calculation_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get calculation statistics"""
        try:
            # Simplified - would query actual calculation logs
            return {
                "total_calculations": 2500,
                "solar_calculations": 1800,
                "heatpump_calculations": 500,
                "combined_calculations": 200,
                "average_calculation_time_ms": 150,
                "failed_calculations": 12
            }
        except Exception as e:
            logger.error(f"Error getting calculation statistics: {str(e)}")
            return {}

    def _get_pdf_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get PDF generation statistics"""
        try:
            # Simplified - would query actual PDF generation logs
            return {
                "total_pdfs": 850,
                "standard_pv": 500,
                "extended_pv": 200,
                "heatpump": 100,
                "multi_pdf": 50,
                "average_generation_time_seconds": 3.5,
                "failed_generations": 8
            }
        except Exception as e:
            logger.error(f"Error getting PDF statistics: {str(e)}")
            return {}

    def _get_api_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get API usage statistics"""
        try:
            # Simplified - would query actual API logs
            return {
                "total_requests": 15000,
                "successful_requests": 14500,
                "failed_requests": 500,
                "average_response_time_ms": 120,
                "requests_by_endpoint": {
                    "/api/v1/solar/calculate": 3000,
                    "/api/v1/pdf/generate": 850,
                    "/api/v1/projects": 2500,
                    "/api/v1/products": 1800,
                    "other": 6850
                },
                "requests_by_status": {
                    "200": 14000,
                    "400": 300,
                    "401": 100,
                    "500": 100
                }
            }
        except Exception as e:
            logger.error(f"Error getting API statistics: {str(e)}")
            return {}

    # Performance Metrics
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "response_times": self._get_response_time_metrics(),
                "throughput": self._get_throughput_metrics(),
                "error_rates": self._get_error_rate_metrics(),
                "resource_usage": self._get_resource_usage_metrics(),
                "cache_performance": self._get_cache_performance_metrics()
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return {"error": str(e)}

    def _get_response_time_metrics(self) -> Dict[str, Any]:
        """Get response time metrics"""
        # Simplified - would query actual performance logs
        return {
            "average_ms": 120,
            "p50_ms": 100,
            "p95_ms": 250,
            "p99_ms": 500,
            "max_ms": 1200,
            "by_endpoint": {
                "solar_calculation": {"average_ms": 150, "p95_ms": 300},
                "pdf_generation": {"average_ms": 3500, "p95_ms": 5000},
                "database_queries": {"average_ms": 50, "p95_ms": 100}
            }
        }

    def _get_throughput_metrics(self) -> Dict[str, Any]:
        """Get throughput metrics"""
        # Simplified - would calculate from actual logs
        return {
            "requests_per_second": 25,
            "requests_per_minute": 1500,
            "requests_per_hour": 90000,
            "peak_rps": 45,
            "peak_time": "14:30"
        }

    def _get_error_rate_metrics(self) -> Dict[str, Any]:
        """Get error rate metrics"""
        # Simplified - would calculate from actual logs
        return {
            "error_rate_percent": 3.3,
            "total_errors": 500,
            "errors_by_type": {
                "validation_error": 200,
                "database_error": 100,
                "timeout_error": 50,
                "internal_error": 150
            },
            "errors_by_endpoint": {
                "/api/v1/solar/calculate": 150,
                "/api/v1/pdf/generate": 100,
                "other": 250
            }
        }

    def _get_resource_usage_metrics(self) -> Dict[str, Any]:
        """Get resource usage metrics over time"""
        # Simplified - would query historical data
        return {
            "cpu_usage_trend": [65, 70, 68, 72, 75, 70, 68],
            "memory_usage_trend": [55, 58, 60, 62, 65, 63, 60],
            "disk_io_trend": [120, 130, 125, 140, 135, 130, 128],
            "network_io_trend": [250, 280, 270, 300, 290, 280, 275]
        }

    def _get_cache_performance_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        # Simplified - would query actual cache statistics
        return {
            "hit_rate_percent": 85,
            "miss_rate_percent": 15,
            "total_hits": 8500,
            "total_misses": 1500,
            "cache_size_mb": 250,
            "eviction_count": 120
        }

    # User Activity Overview
    
    def get_user_activity_overview(self, limit: int = 100) -> Dict[str, Any]:
        """Get recent user activity overview"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "recent_logins": self._get_recent_logins(limit),
                "active_sessions": self._get_active_sessions(),
                "user_actions": self._get_recent_user_actions(limit),
                "top_users": self._get_top_users_by_activity()
            }
        except Exception as e:
            logger.error(f"Error getting user activity overview: {str(e)}")
            return {"error": str(e)}

    def _get_recent_logins(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent user logins"""
        # Simplified - would query actual login logs
        return [
            {
                "user_id": 1,
                "username": "john.doe@example.com",
                "login_time": (datetime.now() - timedelta(minutes=i*5)).isoformat(),
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0..."
            }
            for i in range(min(limit, 10))
        ]

    def _get_active_sessions(self) -> Dict[str, Any]:
        """Get active user sessions"""
        # Simplified - would query actual session data
        return {
            "total_active": 45,
            "by_role": {
                "admin": 5,
                "user": 35,
                "viewer": 5
            },
            "average_duration_minutes": 25
        }

    def _get_recent_user_actions(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent user actions"""
        # Simplified - would query actual activity logs
        actions = [
            "created_project",
            "generated_pdf",
            "updated_calculation",
            "deleted_project",
            "exported_data"
        ]
        
        return [
            {
                "user_id": i % 10 + 1,
                "username": f"user{i % 10 + 1}@example.com",
                "action": actions[i % len(actions)],
                "resource": "project" if i % 2 == 0 else "calculation",
                "timestamp": (datetime.now() - timedelta(minutes=i*2)).isoformat()
            }
            for i in range(min(limit, 20))
        ]

    def _get_top_users_by_activity(self) -> List[Dict[str, Any]]:
        """Get top users by activity"""
        # Simplified - would query actual activity data
        return [
            {
                "user_id": i,
                "username": f"user{i}@example.com",
                "action_count": 150 - (i * 10),
                "last_active": (datetime.now() - timedelta(hours=i)).isoformat()
            }
            for i in range(1, 11)
        ]

    # System Alerts
    
    def get_system_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get system alerts"""
        try:
            alerts = []
            
            # Check system health for alerts
            health = self.get_system_health()
            
            if health.get("cpu", {}).get("usage_percent", 0) > 80:
                alerts.append({
                    "id": 1,
                    "severity": "warning",
                    "type": "system",
                    "title": "High CPU Usage",
                    "message": f"CPU usage is at {health['cpu']['usage_percent']}%",
                    "timestamp": datetime.now().isoformat(),
                    "resolved": False
                })
            
            if health.get("memory", {}).get("usage_percent", 0) > 85:
                alerts.append({
                    "id": 2,
                    "severity": "warning",
                    "type": "system",
                    "title": "High Memory Usage",
                    "message": f"Memory usage is at {health['memory']['usage_percent']}%",
                    "timestamp": datetime.now().isoformat(),
                    "resolved": False
                })
            
            if health.get("disk", {}).get("usage_percent", 0) > 90:
                alerts.append({
                    "id": 3,
                    "severity": "critical",
                    "type": "system",
                    "title": "Low Disk Space",
                    "message": f"Disk usage is at {health['disk']['usage_percent']}%",
                    "timestamp": datetime.now().isoformat(),
                    "resolved": False
                })
            
            # Add database alerts
            db_health = self.get_database_health()
            if db_health.get("status") == "error":
                alerts.append({
                    "id": 4,
                    "severity": "critical",
                    "type": "database",
                    "title": "Database Connection Failed",
                    "message": db_health.get("error", "Unknown error"),
                    "timestamp": datetime.now().isoformat(),
                    "resolved": False
                })
            
            # Filter by severity if specified
            if severity:
                alerts = [a for a in alerts if a["severity"] == severity]
            
            return alerts
        except Exception as e:
            logger.error(f"Error getting system alerts: {str(e)}")
            return []

    def resolve_alert(self, alert_id: int) -> bool:
        """Resolve a system alert"""
        try:
            # Would update alert status in database
            logger.info(f"Alert {alert_id} resolved")
            return True
        except Exception as e:
            logger.error(f"Error resolving alert: {str(e)}")
            return False

    # Dashboard Summary
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "system_health": self.get_system_health(),
                "database_health": self.get_database_health(),
                "usage_statistics": self.get_usage_statistics("today"),
                "performance_metrics": self.get_performance_metrics(),
                "active_alerts": self.get_system_alerts(),
                "user_activity": self.get_user_activity_overview(limit=10)
            }
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {str(e)}")
            return {"error": str(e)}

    # Historical Data
    
    def get_historical_metrics(self, metric_type: str, period: str = "week") -> Dict[str, Any]:
        """Get historical metrics data"""
        try:
            start_date, end_date = self._get_period_dates(period)
            
            if metric_type == "system_health":
                return self._get_historical_system_health(start_date, end_date)
            elif metric_type == "usage":
                return self._get_historical_usage(start_date, end_date)
            elif metric_type == "performance":
                return self._get_historical_performance(start_date, end_date)
            else:
                return {"error": "Invalid metric type"}
        except Exception as e:
            logger.error(f"Error getting historical metrics: {str(e)}")
            return {"error": str(e)}

    def _get_historical_system_health(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get historical system health data"""
        # Simplified - would query actual historical data
        days = (end_date - start_date).days
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "data": [
                {
                    "timestamp": (start_date + timedelta(days=i)).isoformat(),
                    "cpu_percent": 65 + (i % 10),
                    "memory_percent": 55 + (i % 15),
                    "disk_percent": 70 + (i % 5)
                }
                for i in range(days + 1)
            ]
        }

    def _get_historical_usage(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get historical usage data"""
        # Simplified - would query actual historical data
        days = (end_date - start_date).days
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "data": [
                {
                    "date": (start_date + timedelta(days=i)).isoformat(),
                    "active_users": 40 + (i % 10),
                    "new_projects": 5 + (i % 3),
                    "calculations": 100 + (i % 20),
                    "pdfs_generated": 30 + (i % 10)
                }
                for i in range(days + 1)
            ]
        }

    def _get_historical_performance(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get historical performance data"""
        # Simplified - would query actual historical data
        days = (end_date - start_date).days
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "data": [
                {
                    "date": (start_date + timedelta(days=i)).isoformat(),
                    "avg_response_time_ms": 120 + (i % 30),
                    "requests_per_second": 20 + (i % 10),
                    "error_rate_percent": 2 + (i % 3)
                }
                for i in range(days + 1)
            ]
        }
