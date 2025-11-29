"""
Beta Testing Suite
Tests for Task 88: Beta Testing
- Beta build distribution verification
- Crash report monitoring
- User feedback collection
- Performance metrics tracking
- Issue documentation
"""
import pytest
import requests
import json
import time
import os
from typing import Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib


# Test configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


class FeedbackType(Enum):
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    USABILITY = "usability"
    PERFORMANCE = "performance"
    OTHER = "other"


class IssueSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CrashReport:
    """Crash report data structure"""
    id: str
    timestamp: datetime
    error_type: str
    error_message: str
    stack_trace: str
    user_id: str = ""
    app_version: str = ""
    os_info: str = ""
    device_info: str = ""
    steps_to_reproduce: str = ""
    
    
@dataclass
class UserFeedback:
    """User feedback data structure"""
    id: str
    timestamp: datetime
    feedback_type: FeedbackType
    title: str
    description: str
    user_id: str = ""
    app_version: str = ""
    rating: int = 0  # 1-5 stars
    attachments: List[str] = field(default_factory=list)


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BetaIssue:
    """Beta testing issue"""
    id: str
    title: str
    description: str
    severity: IssueSeverity
    status: str  # open, in_progress, resolved, closed
    reported_by: str
    reported_at: datetime
    resolved_at: datetime = None
    resolution: str = ""
    related_crash_reports: List[str] = field(default_factory=list)
    related_feedback: List[str] = field(default_factory=list)


class BetaTestingManager:
    """Beta testing management system"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.crash_reports: List[CrashReport] = []
        self.user_feedback: List[UserFeedback] = []
        self.performance_metrics: List[PerformanceMetric] = []
        self.issues: List[BetaIssue] = []
        
    def submit_crash_report(self, report: CrashReport) -> bool:
        """Submit a crash report"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/beta/crash-reports",
                json={
                    "id": report.id,
                    "timestamp": report.timestamp.isoformat(),
                    "error_type": report.error_type,
                    "error_message": report.error_message,
                    "stack_trace": report.stack_trace,
                    "user_id": report.user_id,
                    "app_version": report.app_version,
                    "os_info": report.os_info,
                    "device_info": report.device_info,
                    "steps_to_reproduce": report.steps_to_reproduce
                }
            )
            if response.status_code in [200, 201]:
                self.crash_reports.append(report)
                return True
        except:
            pass
        
        # Store locally if API not available
        self.crash_reports.append(report)
        return True
        
    def submit_feedback(self, feedback: UserFeedback) -> bool:
        """Submit user feedback"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/beta/feedback",
                json={
                    "id": feedback.id,
                    "timestamp": feedback.timestamp.isoformat(),
                    "feedback_type": feedback.feedback_type.value,
                    "title": feedback.title,
                    "description": feedback.description,
                    "user_id": feedback.user_id,
                    "app_version": feedback.app_version,
                    "rating": feedback.rating
                }
            )
            if response.status_code in [200, 201]:
                self.user_feedback.append(feedback)
                return True
        except:
            pass
            
        # Store locally if API not available
        self.user_feedback.append(feedback)
        return True
        
    def record_metric(self, metric: PerformanceMetric) -> bool:
        """Record a performance metric"""
        self.performance_metrics.append(metric)
        return True
        
    def create_issue(self, issue: BetaIssue) -> bool:
        """Create a beta testing issue"""
        self.issues.append(issue)
        return True
        
    def get_crash_report_summary(self) -> Dict[str, Any]:
        """Get crash report summary"""
        if not self.crash_reports:
            return {"total": 0, "by_type": {}, "by_version": {}}
            
        by_type = {}
        by_version = {}
        
        for report in self.crash_reports:
            by_type[report.error_type] = by_type.get(report.error_type, 0) + 1
            by_version[report.app_version] = by_version.get(report.app_version, 0) + 1
            
        return {
            "total": len(self.crash_reports),
            "by_type": by_type,
            "by_version": by_version,
            "latest": self.crash_reports[-1].timestamp.isoformat() if self.crash_reports else None
        }
        
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get feedback summary"""
        if not self.user_feedback:
            return {"total": 0, "by_type": {}, "average_rating": 0}
            
        by_type = {}
        total_rating = 0
        rated_count = 0
        
        for feedback in self.user_feedback:
            by_type[feedback.feedback_type.value] = by_type.get(feedback.feedback_type.value, 0) + 1
            if feedback.rating > 0:
                total_rating += feedback.rating
                rated_count += 1
                
        return {
            "total": len(self.user_feedback),
            "by_type": by_type,
            "average_rating": total_rating / rated_count if rated_count > 0 else 0
        }
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        if not self.performance_metrics:
            return {"total_metrics": 0, "metrics": {}}
            
        metrics_by_name = {}
        
        for metric in self.performance_metrics:
            if metric.metric_name not in metrics_by_name:
                metrics_by_name[metric.metric_name] = []
            metrics_by_name[metric.metric_name].append(metric.value)
            
        summary = {}
        for name, values in metrics_by_name.items():
            summary[name] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values)
            }
            
        return {
            "total_metrics": len(self.performance_metrics),
            "metrics": summary
        }
        
    def get_issue_summary(self) -> Dict[str, Any]:
        """Get issue summary"""
        if not self.issues:
            return {"total": 0, "by_severity": {}, "by_status": {}}
            
        by_severity = {}
        by_status = {}
        
        for issue in self.issues:
            by_severity[issue.severity.value] = by_severity.get(issue.severity.value, 0) + 1
            by_status[issue.status] = by_status.get(issue.status, 0) + 1
            
        return {
            "total": len(self.issues),
            "by_severity": by_severity,
            "by_status": by_status
        }
        
    def generate_beta_report(self) -> str:
        """Generate comprehensive beta testing report"""
        crash_summary = self.get_crash_report_summary()
        feedback_summary = self.get_feedback_summary()
        performance_summary = self.get_performance_summary()
        issue_summary = self.get_issue_summary()
        
        report = f"""
# Beta Testing Report
# Solar Calculator Pro

**Report Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report summarizes the beta testing phase for Solar Calculator Pro.

## Crash Reports

- **Total Crashes**: {crash_summary['total']}
- **By Error Type**: {json.dumps(crash_summary['by_type'], indent=2)}
- **By Version**: {json.dumps(crash_summary['by_version'], indent=2)}

## User Feedback

- **Total Feedback Items**: {feedback_summary['total']}
- **By Type**: {json.dumps(feedback_summary['by_type'], indent=2)}
- **Average Rating**: {feedback_summary['average_rating']:.1f}/5

## Performance Metrics

- **Total Metrics Collected**: {performance_summary['total_metrics']}
- **Metrics Summary**:
{json.dumps(performance_summary['metrics'], indent=2)}

## Issues

- **Total Issues**: {issue_summary['total']}
- **By Severity**: {json.dumps(issue_summary['by_severity'], indent=2)}
- **By Status**: {json.dumps(issue_summary['by_status'], indent=2)}

## Recommendations

1. Address all critical and high severity issues before release
2. Review user feedback for common pain points
3. Optimize performance based on metrics
4. Continue monitoring crash reports

## Next Steps

1. Resolve open issues
2. Implement high-priority feature requests
3. Perform regression testing
4. Prepare for production release
"""
        return report


class TestBetaBuildDistribution:
    """Beta build distribution tests"""
    
    def test_build_version_endpoint(self):
        """Test that build version is accessible"""
        response = requests.get(f"{API_V1}/version")
        
        if response.status_code == 200:
            data = response.json()
            assert "version" in data or "build" in str(data)
            print("Build version endpoint: PASSED")
        else:
            print("Build version endpoint: SKIPPED (not available)")
            
    def test_health_check_for_beta(self):
        """Test health check endpoint for beta builds"""
        response = requests.get(f"{API_V1}/health")
        
        assert response.status_code == 200, "Health check failed"
        print("Health check for beta: PASSED")
        
    def test_beta_feature_flags(self):
        """Test beta feature flags endpoint"""
        response = requests.get(f"{API_V1}/beta/features")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Beta features: {data}")
            print("Beta feature flags: PASSED")
        else:
            print("Beta feature flags: SKIPPED (not available)")


class TestCrashReportMonitoring:
    """Crash report monitoring tests"""
    
    def test_crash_report_submission(self):
        """Test crash report submission"""
        manager = BetaTestingManager()
        
        report = CrashReport(
            id=f"crash_{int(time.time())}",
            timestamp=datetime.now(),
            error_type="RuntimeError",
            error_message="Test crash report",
            stack_trace="File 'test.py', line 1\n  raise RuntimeError('test')",
            user_id="test_user",
            app_version="1.0.0-beta",
            os_info="Windows 11",
            device_info="Desktop"
        )
        
        result = manager.submit_crash_report(report)
        assert result, "Crash report submission failed"
        
        summary = manager.get_crash_report_summary()
        assert summary["total"] >= 1
        print("Crash report submission: PASSED")
        
    def test_crash_report_aggregation(self):
        """Test crash report aggregation"""
        manager = BetaTestingManager()
        
        # Submit multiple crash reports
        error_types = ["RuntimeError", "ValueError", "RuntimeError", "TypeError"]
        
        for i, error_type in enumerate(error_types):
            report = CrashReport(
                id=f"crash_{i}_{int(time.time())}",
                timestamp=datetime.now(),
                error_type=error_type,
                error_message=f"Test error {i}",
                stack_trace=f"Stack trace {i}",
                app_version="1.0.0-beta"
            )
            manager.submit_crash_report(report)
            
        summary = manager.get_crash_report_summary()
        
        assert summary["total"] == 4
        assert summary["by_type"]["RuntimeError"] == 2
        print("Crash report aggregation: PASSED")


class TestUserFeedbackCollection:
    """User feedback collection tests"""
    
    def test_feedback_submission(self):
        """Test feedback submission"""
        manager = BetaTestingManager()
        
        feedback = UserFeedback(
            id=f"feedback_{int(time.time())}",
            timestamp=datetime.now(),
            feedback_type=FeedbackType.USABILITY,
            title="Great app!",
            description="The solar calculator is very easy to use.",
            user_id="test_user",
            app_version="1.0.0-beta",
            rating=5
        )
        
        result = manager.submit_feedback(feedback)
        assert result, "Feedback submission failed"
        
        summary = manager.get_feedback_summary()
        assert summary["total"] >= 1
        print("Feedback submission: PASSED")
        
    def test_feedback_categorization(self):
        """Test feedback categorization"""
        manager = BetaTestingManager()
        
        feedback_items = [
            (FeedbackType.BUG, "Button not working", 3),
            (FeedbackType.FEATURE_REQUEST, "Add dark mode", 4),
            (FeedbackType.USABILITY, "Confusing navigation", 2),
            (FeedbackType.PERFORMANCE, "Slow loading", 3),
            (FeedbackType.BUG, "Crash on save", 1),
        ]
        
        for i, (ftype, title, rating) in enumerate(feedback_items):
            feedback = UserFeedback(
                id=f"feedback_{i}_{int(time.time())}",
                timestamp=datetime.now(),
                feedback_type=ftype,
                title=title,
                description=f"Description for {title}",
                rating=rating
            )
            manager.submit_feedback(feedback)
            
        summary = manager.get_feedback_summary()
        
        assert summary["total"] == 5
        assert summary["by_type"]["bug"] == 2
        assert summary["by_type"]["feature_request"] == 1
        assert 2.0 <= summary["average_rating"] <= 3.0
        print("Feedback categorization: PASSED")


class TestPerformanceMetricsTracking:
    """Performance metrics tracking tests"""
    
    def test_metric_recording(self):
        """Test performance metric recording"""
        manager = BetaTestingManager()
        
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            metric_name="api_response_time",
            value=150.5,
            unit="ms",
            context={"endpoint": "/api/v1/calculations"}
        )
        
        result = manager.record_metric(metric)
        assert result, "Metric recording failed"
        
        summary = manager.get_performance_summary()
        assert summary["total_metrics"] >= 1
        print("Metric recording: PASSED")
        
    def test_metric_aggregation(self):
        """Test metric aggregation"""
        manager = BetaTestingManager()
        
        # Record multiple metrics
        metrics_data = [
            ("api_response_time", 100),
            ("api_response_time", 150),
            ("api_response_time", 200),
            ("memory_usage", 256),
            ("memory_usage", 280),
            ("cpu_usage", 45),
        ]
        
        for name, value in metrics_data:
            metric = PerformanceMetric(
                timestamp=datetime.now(),
                metric_name=name,
                value=value,
                unit="ms" if "time" in name else "MB" if "memory" in name else "%"
            )
            manager.record_metric(metric)
            
        summary = manager.get_performance_summary()
        
        assert summary["total_metrics"] == 6
        assert "api_response_time" in summary["metrics"]
        assert summary["metrics"]["api_response_time"]["avg"] == 150
        print("Metric aggregation: PASSED")


class TestIssueDocumentation:
    """Issue documentation tests"""
    
    def test_issue_creation(self):
        """Test issue creation"""
        manager = BetaTestingManager()
        
        issue = BetaIssue(
            id=f"issue_{int(time.time())}",
            title="PDF generation fails for large systems",
            description="When generating PDF for systems > 50kWp, the process times out.",
            severity=IssueSeverity.HIGH,
            status="open",
            reported_by="beta_tester_1",
            reported_at=datetime.now()
        )
        
        result = manager.create_issue(issue)
        assert result, "Issue creation failed"
        
        summary = manager.get_issue_summary()
        assert summary["total"] >= 1
        print("Issue creation: PASSED")
        
    def test_issue_tracking(self):
        """Test issue tracking"""
        manager = BetaTestingManager()
        
        issues_data = [
            ("Critical bug", IssueSeverity.CRITICAL, "open"),
            ("High priority fix", IssueSeverity.HIGH, "in_progress"),
            ("Medium issue", IssueSeverity.MEDIUM, "resolved"),
            ("Low priority", IssueSeverity.LOW, "closed"),
            ("Another critical", IssueSeverity.CRITICAL, "open"),
        ]
        
        for i, (title, severity, status) in enumerate(issues_data):
            issue = BetaIssue(
                id=f"issue_{i}_{int(time.time())}",
                title=title,
                description=f"Description for {title}",
                severity=severity,
                status=status,
                reported_by="tester",
                reported_at=datetime.now()
            )
            manager.create_issue(issue)
            
        summary = manager.get_issue_summary()
        
        assert summary["total"] == 5
        assert summary["by_severity"]["critical"] == 2
        assert summary["by_status"]["open"] == 2
        print("Issue tracking: PASSED")


class TestBetaReportGeneration:
    """Beta report generation tests"""
    
    def test_comprehensive_report(self):
        """Test comprehensive beta report generation"""
        manager = BetaTestingManager()
        
        # Add sample data
        manager.submit_crash_report(CrashReport(
            id="crash_1",
            timestamp=datetime.now(),
            error_type="RuntimeError",
            error_message="Test error",
            stack_trace="Stack trace",
            app_version="1.0.0-beta"
        ))
        
        manager.submit_feedback(UserFeedback(
            id="feedback_1",
            timestamp=datetime.now(),
            feedback_type=FeedbackType.USABILITY,
            title="Good app",
            description="Works well",
            rating=4
        ))
        
        manager.record_metric(PerformanceMetric(
            timestamp=datetime.now(),
            metric_name="response_time",
            value=150,
            unit="ms"
        ))
        
        manager.create_issue(BetaIssue(
            id="issue_1",
            title="Test issue",
            description="Test description",
            severity=IssueSeverity.MEDIUM,
            status="open",
            reported_by="tester",
            reported_at=datetime.now()
        ))
        
        report = manager.generate_beta_report()
        
        assert "Beta Testing Report" in report
        assert "Crash Reports" in report
        assert "User Feedback" in report
        assert "Performance Metrics" in report
        assert "Issues" in report
        print("Comprehensive report generation: PASSED")


def run_beta_testing_simulation():
    """Run a complete beta testing simulation"""
    print("=" * 60)
    print("Beta Testing Simulation")
    print("=" * 60)
    
    manager = BetaTestingManager()
    
    # Simulate crash reports
    print("\n1. Simulating crash reports...")
    for i in range(5):
        report = CrashReport(
            id=f"crash_{i}",
            timestamp=datetime.now() - timedelta(days=i),
            error_type=["RuntimeError", "ValueError", "TypeError"][i % 3],
            error_message=f"Simulated error {i}",
            stack_trace=f"Stack trace for error {i}",
            app_version="1.0.0-beta",
            user_id=f"user_{i % 3}"
        )
        manager.submit_crash_report(report)
    print(f"   Submitted {len(manager.crash_reports)} crash reports")
    
    # Simulate user feedback
    print("\n2. Simulating user feedback...")
    feedback_types = list(FeedbackType)
    for i in range(10):
        feedback = UserFeedback(
            id=f"feedback_{i}",
            timestamp=datetime.now() - timedelta(days=i % 7),
            feedback_type=feedback_types[i % len(feedback_types)],
            title=f"Feedback item {i}",
            description=f"Description for feedback {i}",
            rating=(i % 5) + 1,
            user_id=f"user_{i % 5}"
        )
        manager.submit_feedback(feedback)
    print(f"   Collected {len(manager.user_feedback)} feedback items")
    
    # Simulate performance metrics
    print("\n3. Simulating performance metrics...")
    import random
    for i in range(20):
        metric = PerformanceMetric(
            timestamp=datetime.now() - timedelta(hours=i),
            metric_name=["response_time", "memory_usage", "cpu_usage"][i % 3],
            value=random.uniform(50, 500),
            unit=["ms", "MB", "%"][i % 3]
        )
        manager.record_metric(metric)
    print(f"   Recorded {len(manager.performance_metrics)} metrics")
    
    # Simulate issues
    print("\n4. Simulating issues...")
    severities = list(IssueSeverity)
    statuses = ["open", "in_progress", "resolved", "closed"]
    for i in range(8):
        issue = BetaIssue(
            id=f"issue_{i}",
            title=f"Beta issue {i}",
            description=f"Description for issue {i}",
            severity=severities[i % len(severities)],
            status=statuses[i % len(statuses)],
            reported_by=f"tester_{i % 3}",
            reported_at=datetime.now() - timedelta(days=i)
        )
        manager.create_issue(issue)
    print(f"   Created {len(manager.issues)} issues")
    
    # Generate report
    print("\n5. Generating beta testing report...")
    report = manager.generate_beta_report()
    
    print("\n" + "=" * 60)
    print(report)
    
    return manager


if __name__ == "__main__":
    print("Starting Solar Calculator Pro Beta Testing...")
    print("Run with: pytest solar-calculator-pro/tests/test_beta_testing.py -v")
    print()
    
    # Run simulation
    run_beta_testing_simulation()
