"""
Tests for Monitoring Service

Tests post-release monitoring functionality including performance tracking,
crash reporting, feedback collection, and update adoption.
"""

import pytest
from datetime import datetime, timedelta
from backend.services.monitoring_service import MonitoringService


class TestPerformanceMonitoring:
    """Test performance monitoring functionality"""
    
    def test_track_performance_metric(self, db_session):
        """Test tracking a performance metric"""
        service = MonitoringService(db_session)
        
        metric = service.track_performance_metric(
            metric_name='api_response_time',
            value=125.5,
            unit='ms',
            metadata={'endpoint': '/api/v1/solar/calculate'}
        )
        
        assert metric['metric_name'] == 'api_response_time'
        assert metric['value'] == 125.5
        assert metric['unit'] == 'ms'
        assert 'timestamp' in metric
        assert metric['metadata']['endpoint'] == '/api/v1/solar/calculate'
    
    def test_get_performance_summary(self, db_session):
        """Test getting performance summary"""
        service = MonitoringService(db_session)
        
        summary = service.get_performance_summary()
        
        assert 'period' in summary
        assert 'system' in summary
        assert 'platform' in summary
        assert 'metrics' in summary
        
        # Check system metrics
        assert 'cpu_percent' in summary['system']
        assert 'memory_percent' in summary['system']
        assert 'disk_percent' in summary['system']
        
        # Check platform info
        assert 'system' in summary['platform']
        assert 'machine' in summary['platform']
    
    def test_get_performance_trends(self, db_session):
        """Test getting performance trends"""
        service = MonitoringService(db_session)
        
        trends = service.get_performance_trends('api_response_time', days=7)
        
        assert trends['metric_name'] == 'api_response_time'
        assert trends['period_days'] == 7
        assert 'start_date' in trends
        assert 'end_date' in trends
        assert 'trend' in trends
        assert trends['trend'] in ['improving', 'degrading', 'stable']


class TestCrashReporting:
    """Test crash reporting functionality"""
    
    def test_report_crash(self, db_session):
        """Test reporting a crash"""
        service = MonitoringService(db_session)
        
        crash_report = service.report_crash(
            error_type='TypeError',
            error_message='Cannot read property of undefined',
            stack_trace='Error: TypeError\n  at function1\n  at function2',
            user_id=123,
            app_version='1.0.0',
            metadata={'os': 'Windows 10', 'browser': 'Chrome'}
        )
        
        assert crash_report['error_type'] == 'TypeError'
        assert crash_report['error_message'] == 'Cannot read property of undefined'
        assert crash_report['user_id'] == 123
        assert crash_report['app_version'] == '1.0.0'
        assert crash_report['status'] == 'new'
        assert 'id' in crash_report
        assert 'timestamp' in crash_report
    
    def test_get_crash_statistics(self, db_session):
        """Test getting crash statistics"""
        service = MonitoringService(db_session)
        
        stats = service.get_crash_statistics(days=7)
        
        assert 'period_days' in stats
        assert 'total_crashes' in stats
        assert 'unique_errors' in stats
        assert 'affected_users' in stats
        assert 'crash_free_rate' in stats
        assert 'most_common_errors' in stats
        assert 'crashes_by_version' in stats
        assert 'crashes_by_platform' in stats
        
        # Crash-free rate should be between 0 and 100
        assert 0 <= stats['crash_free_rate'] <= 100
    
    def test_get_crash_reports(self, db_session):
        """Test getting crash reports"""
        service = MonitoringService(db_session)
        
        reports = service.get_crash_reports(status='new', days=7, limit=100)
        
        assert isinstance(reports, list)


class TestUserFeedback:
    """Test user feedback functionality"""
    
    def test_submit_feedback(self, db_session):
        """Test submitting user feedback"""
        service = MonitoringService(db_session)
        
        feedback = service.submit_feedback(
            user_id=123,
            feedback_type='feature_request',
            title='Add dark mode',
            description='Would love to have a dark mode option',
            rating=5,
            metadata={'page': 'settings'}
        )
        
        assert feedback['user_id'] == 123
        assert feedback['feedback_type'] == 'feature_request'
        assert feedback['title'] == 'Add dark mode'
        assert feedback['rating'] == 5
        assert feedback['status'] == 'new'
        assert 'id' in feedback
        assert 'timestamp' in feedback
    
    def test_get_feedback_summary(self, db_session):
        """Test getting feedback summary"""
        service = MonitoringService(db_session)
        
        summary = service.get_feedback_summary(days=30)
        
        assert 'period_days' in summary
        assert 'total_feedback' in summary
        assert 'by_type' in summary
        assert 'average_rating' in summary
        assert 'sentiment' in summary
        
        # Check feedback types
        assert 'bug' in summary['by_type']
        assert 'feature_request' in summary['by_type']
        assert 'improvement' in summary['by_type']
        assert 'praise' in summary['by_type']
        
        # Sentiment should be valid
        assert summary['sentiment'] in ['positive', 'neutral', 'negative']


class TestUpdateAdoption:
    """Test update adoption tracking"""
    
    def test_track_update_adoption(self, db_session):
        """Test tracking update adoption"""
        service = MonitoringService(db_session)
        
        update_record = service.track_update_adoption(
            user_id=123,
            from_version='1.0.0',
            to_version='1.1.0',
            update_method='auto',
            success=True,
            duration_seconds=45.2
        )
        
        assert update_record['user_id'] == 123
        assert update_record['from_version'] == '1.0.0'
        assert update_record['to_version'] == '1.1.0'
        assert update_record['update_method'] == 'auto'
        assert update_record['success'] is True
        assert update_record['duration_seconds'] == 45.2
        assert 'timestamp' in update_record
    
    def test_get_update_adoption_stats(self, db_session):
        """Test getting update adoption statistics"""
        service = MonitoringService(db_session)
        
        stats = service.get_update_adoption_stats('1.1.0')
        
        assert stats['version'] == '1.1.0'
        assert 'total_users' in stats
        assert 'updated_users' in stats
        assert 'adoption_rate' in stats
        assert 'update_methods' in stats
        assert 'success_rate' in stats
        
        # Rates should be between 0 and 100
        assert 0 <= stats['adoption_rate'] <= 100
        assert 0 <= stats['success_rate'] <= 100
    
    def test_get_version_distribution(self, db_session):
        """Test getting version distribution"""
        service = MonitoringService(db_session)
        
        distribution = service.get_version_distribution()
        
        assert 'total_users' in distribution
        assert 'versions' in distribution
        assert 'latest_version' in distribution
        assert 'outdated_users' in distribution
        assert 'outdated_percentage' in distribution


class TestImprovementPlanning:
    """Test improvement planning functionality"""
    
    def test_analyze_improvement_opportunities(self, db_session):
        """Test analyzing improvement opportunities"""
        service = MonitoringService(db_session)
        
        opportunities = service.analyze_improvement_opportunities(days=30)
        
        assert 'high_priority' in opportunities
        assert 'medium_priority' in opportunities
        assert 'low_priority' in opportunities
        assert 'quick_wins' in opportunities
        assert 'long_term' in opportunities
        
        # Each priority level should be a list
        assert isinstance(opportunities['high_priority'], list)
        assert isinstance(opportunities['medium_priority'], list)
    
    def test_create_improvement_roadmap(self, db_session):
        """Test creating improvement roadmap"""
        service = MonitoringService(db_session)
        
        opportunities = {
            'high_priority': [
                {
                    'type': 'stability',
                    'title': 'Fix critical bug',
                    'impact': 'high',
                    'effort': 'medium'
                }
            ],
            'medium_priority': []
        }
        
        roadmap = service.create_improvement_roadmap(opportunities)
        
        assert 'created_at' in roadmap
        assert 'quarters' in roadmap
        assert 'themes' in roadmap
        
        # Check quarters
        assert 'Q1' in roadmap['quarters']
        assert 'Q2' in roadmap['quarters']
        assert 'Q3' in roadmap['quarters']
        assert 'Q4' in roadmap['quarters']
        
        # Check themes
        assert 'stability' in roadmap['themes']
        assert 'performance' in roadmap['themes']
        assert 'features' in roadmap['themes']


class TestHealthStatus:
    """Test health status functionality"""
    
    def test_get_health_status(self, db_session):
        """Test getting health status"""
        service = MonitoringService(db_session)
        
        health = service.get_health_status()
        
        assert 'status' in health
        assert 'timestamp' in health
        assert 'issues' in health
        assert 'metrics' in health
        
        # Status should be valid
        assert health['status'] in ['healthy', 'degraded', 'critical']
        
        # Issues should be a list
        assert isinstance(health['issues'], list)
        
        # Metrics should contain key values
        assert 'crash_free_rate' in health['metrics']
        assert 'cpu_percent' in health['metrics']
        assert 'memory_percent' in health['metrics']


# Fixtures
@pytest.fixture
def db_session():
    """Mock database session"""
    class MockSession:
        def add(self, obj):
            pass
        
        def commit(self):
            pass
        
        def refresh(self, obj):
            pass
        
        def query(self, model):
            return self
        
        def filter(self, *args):
            return self
        
        def first(self):
            return None
        
        def all(self):
            return []
    
    return MockSession()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
