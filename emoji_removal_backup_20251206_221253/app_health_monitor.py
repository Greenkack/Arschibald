"""
Comprehensive Application Health Monitor

Real-time monitoring, error detection, and automatic fixing.
Integrates tracing, evaluation, and diagnostics.
"""

import os
import sys
import json
import time
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Try to import monitoring components
try:
    from app_tracing import app_tracer, initialize_tracing, shutdown_tracing
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False

try:
    from app_evaluation import evaluation_system
    EVALUATION_AVAILABLE = True
except ImportError:
    EVALUATION_AVAILABLE = False

try:
    from app_diagnostics import ApplicationScanner
    DIAGNOSTICS_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_AVAILABLE = False


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class HealthMetrics:
    """Overall application health metrics."""
    timestamp: str
    status: str  # HEALTHY, DEGRADED, CRITICAL, OFFLINE
    error_rate: float
    performance_score: float
    code_quality_score: float
    active_errors: int
    total_operations: int
    uptime_seconds: float
    memory_usage_mb: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ApplicationHealthMonitor:
    """
    Comprehensive health monitoring system.
    
    Combines:
    - OpenTelemetry tracing
    - Azure AI evaluation
    - Static code analysis
    - Runtime error tracking
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics_history: List[HealthMetrics] = []
        self.error_log: List[Dict] = []
        self.monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Initialize components
        if TRACING_AVAILABLE:
            initialize_tracing()
            logger.info("Tracing initialized")
        else:
            logger.warning("Tracing not available")
        
        if EVALUATION_AVAILABLE:
            logger.info("Evaluation system available")
        else:
            logger.warning("Evaluation system not available")
        
        if DIAGNOSTICS_AVAILABLE:
            logger.info("Diagnostics available")
        else:
            logger.warning("Diagnostics not available")
    
    def start_monitoring(self, interval_seconds: int = 60):
        """
        Start continuous health monitoring.
        
        Args:
            interval_seconds: How often to check health
        """
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self._monitor_thread.start()
        logger.info(f"Health monitoring started (interval: {interval_seconds}s)")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("🛑 Health monitoring stopped")
    
    def _monitor_loop(self, interval: int):
        """Continuous monitoring loop."""
        while self.monitoring_active:
            try:
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # Keep last 1000 metrics
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                
                # Alert on critical status
                if metrics.status == "CRITICAL":
                    self._alert_critical(metrics)
                
                # Auto-fix if enabled
                if os.environ.get("AUTO_FIX_ENABLED", "false").lower() == "true":
                    self._attempt_auto_fix()
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            time.sleep(interval)
    
    def collect_metrics(self) -> HealthMetrics:
        """Collect current health metrics."""
        
        # Get evaluation metrics
        error_rate = 0.0
        performance_score = 5.0
        active_errors = 0
        total_operations = 0
        
        if EVALUATION_AVAILABLE:
            try:
                health = evaluation_system.get_health_status()
                error_rate = health.get('error_rate', 0.0)
                active_errors = health.get('total_errors', 0)
                total_operations = health.get('total_operations', 0)
                
                # Calculate performance score
                perf_summary = evaluation_system.performance.get_summary()
                if perf_summary and len(perf_summary) > 0:
                    scores = [p.get('avg_score', 5.0) for p in perf_summary.values()]
                    performance_score = sum(scores) / len(scores) if scores else 5.0
            except Exception as e:
                logger.error(f"Error getting evaluation metrics: {e}")
        
        # Get code quality score from latest scan
        code_quality_score = 100.0
        if DIAGNOSTICS_AVAILABLE:
            report_file = Path("code_analysis_report.json")
            if report_file.exists():
                try:
                    with open(report_file, 'r') as f:
                        report = json.load(f)
                    
                    # Calculate quality score
                    total_issues = report.get('total_issues', 0)
                    critical = report.get('severity_breakdown', {}).get('CRITICAL', 0)
                    high = report.get('severity_breakdown', {}).get('HIGH', 0)
                    
                    # Deduct points for issues
                    code_quality_score = max(0, 100 - (critical * 10) - (high * 0.1))
                
                except Exception as e:
                    logger.error(f"Error reading diagnostics report: {e}")
        
        # Get memory usage
        memory_usage_mb = 0.0
        try:
            import psutil
            process = psutil.Process()
            memory_usage_mb = process.memory_info().rss / 1024 / 1024
        except ImportError:
            pass
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
        
        # Determine overall status
        status = self._determine_status(error_rate, performance_score, code_quality_score)
        
        # Calculate uptime
        uptime = time.time() - self.start_time
        
        return HealthMetrics(
            timestamp=datetime.now().isoformat(),
            status=status,
            error_rate=error_rate,
            performance_score=performance_score,
            code_quality_score=code_quality_score,
            active_errors=active_errors,
            total_operations=total_operations,
            uptime_seconds=uptime,
            memory_usage_mb=memory_usage_mb
        )
    
    def _determine_status(self, error_rate: float, performance_score: float, code_quality: float) -> str:
        """Determine overall health status."""
        
        # Critical conditions
        if error_rate > 0.10:  # > 10% errors
            return "CRITICAL"
        if performance_score < 2.0:  # Very slow
            return "CRITICAL"
        if code_quality < 50:  # Many critical issues
            return "CRITICAL"
        
        # Degraded conditions
        if error_rate > 0.05:  # > 5% errors
            return "DEGRADED"
        if performance_score < 3.0:  # Slow
            return "DEGRADED"
        if code_quality < 80:  # Some issues
            return "DEGRADED"
        
        return "HEALTHY"
    
    def _alert_critical(self, metrics: HealthMetrics):
        """Alert on critical status."""
        alert = {
            "timestamp": metrics.timestamp,
            "status": "CRITICAL",
            "error_rate": metrics.error_rate,
            "performance_score": metrics.performance_score,
            "code_quality_score": metrics.code_quality_score,
            "message": "Application in CRITICAL state"
        }
        
        self.error_log.append(alert)
        logger.critical(f"🚨 CRITICAL ALERT: {json.dumps(alert, indent=2)}")
        
        # Save alert to file
        alert_file = Path("alerts") / f"alert_{int(time.time())}.json"
        alert_file.parent.mkdir(exist_ok=True)
        with open(alert_file, 'w') as f:
            json.dump(alert, f, indent=2)
    
    def _attempt_auto_fix(self):
        """Attempt to automatically fix issues."""
        logger.info("Attempting auto-fix...")
        
        try:
            # Run diagnostics
            if DIAGNOSTICS_AVAILABLE:
                scanner = ApplicationScanner()
                report = scanner.scan_application()
                
                # Get critical issues
                critical = scanner.get_critical_issues()
                
                if critical:
                    logger.info(f"Found {len(critical)} critical issues to fix")
                    # Auto-fixer would run here
                    # For now, just log
                    for issue in critical[:5]:
                        logger.warning(f"  - {issue.file}:{issue.line} - {issue.message}")
        
        except Exception as e:
            logger.error(f"Error in auto-fix: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        current = self.collect_metrics()
        
        return {
            "current": current.to_dict(),
            "history_count": len(self.metrics_history),
            "recent_errors": len([m for m in self.metrics_history[-10:] if m.status in ("CRITICAL", "DEGRADED")]),
            "uptime_hours": current.uptime_seconds / 3600,
            "monitoring_active": self.monitoring_active
        }
    
    def generate_health_report(self, output_file: str = "health_report.json"):
        """Generate comprehensive health report."""
        
        current = self.collect_metrics()
        
        # Calculate trends
        recent = self.metrics_history[-10:] if self.metrics_history else []
        
        error_rate_trend = "stable"
        if len(recent) >= 2:
            if recent[-1].error_rate > recent[-2].error_rate * 1.5:
                error_rate_trend = "increasing"
            elif recent[-1].error_rate < recent[-2].error_rate * 0.5:
                error_rate_trend = "decreasing"
        
        performance_trend = "stable"
        if len(recent) >= 2:
            if recent[-1].performance_score > recent[-2].performance_score * 1.2:
                performance_trend = "improving"
            elif recent[-1].performance_score < recent[-2].performance_score * 0.8:
                performance_trend = "degrading"
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "current_status": current.to_dict(),
            "trends": {
                "error_rate": error_rate_trend,
                "performance": performance_trend
            },
            "recent_metrics": [m.to_dict() for m in recent],
            "alerts": self.error_log[-10:],
            "recommendations": self._generate_recommendations(current)
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Health report saved: {output_file}")
        
        return report
    
    def _generate_recommendations(self, metrics: HealthMetrics) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        if metrics.error_rate > 0.05:
            recommendations.append("High error rate detected - review error logs and add error handling")
        
        if metrics.performance_score < 3.0:
            recommendations.append("Performance degraded - review slow operations and optimize")
        
        if metrics.code_quality_score < 80:
            recommendations.append("Code quality issues detected - run app_diagnostics.py and fix issues")
        
        if metrics.memory_usage_mb > 1000:
            recommendations.append("High memory usage - check for memory leaks")
        
        if not recommendations:
            recommendations.append("All systems nominal - no action required")
        
        return recommendations
    
    def shutdown(self):
        """Shutdown health monitor."""
        self.stop_monitoring()
        
        if TRACING_AVAILABLE:
            shutdown_tracing()
        
        # Generate final report
        self.generate_health_report("health_report_final.json")
        
        logger.info("Health monitor shutdown complete")


# Global instance
health_monitor = ApplicationHealthMonitor()


def start_health_monitoring(interval: int = 60):
    """Start health monitoring."""
    health_monitor.start_monitoring(interval)


def stop_health_monitoring():
    """Stop health monitoring."""
    health_monitor.stop_monitoring()


def get_health_status() -> Dict[str, Any]:
    """Get current health status."""
    return health_monitor.get_health_status()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Application Health Monitor')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    parser.add_argument('--duration', type=int, default=0, help='How long to monitor (0 = forever)')
    parser.add_argument('--report', action='store_true', help='Generate report and exit')
    
    args = parser.parse_args()
    
    if args.report:
        # Just generate report
        report = health_monitor.generate_health_report()
        print(json.dumps(report, indent=2))
    else:
        # Start monitoring
        health_monitor.start_monitoring(args.interval)
        
        try:
            if args.duration > 0:
                time.sleep(args.duration)
            else:
                # Run forever
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        finally:
            health_monitor.shutdown()
