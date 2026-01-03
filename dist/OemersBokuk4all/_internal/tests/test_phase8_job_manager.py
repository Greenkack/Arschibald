"""
Test Suite für Phase 8: Job Manager & Background Tasks

Führe umfassende Tests für JobManager, Job, JobResult und Integration aus.
"""

import pytest
import sys
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.jobs import (
    Job, JobResult, JobManager, JobQueue, JobStatus, JobPriority,
    ErrorType, ProgressCallback
)


class TestJob:
    """Tests für Job Dataclass"""
    
    def test_job_creation(self):
        """Test Job-Erstellung"""
        job = Job(
            name="Test Job",
            function_name='test_func',
            args=(1, 2),
            kwargs={'x': 10},
            priority=JobPriority.HIGH
        )
        
        assert job.name == "Test Job"
        assert job.function_name == 'test_func'
        assert job.args == (1, 2)
        assert job.kwargs == {'x': 10}
        assert job.priority == JobPriority.HIGH
    
    def test_job_to_dict(self):
        """Test Job Serialisierung"""
        job = Job(
            name="Test Job",
            function_name='test_func',
            kwargs={'x': 10},
            max_retries=3,
            retry_delay=5
        )
        
        data = job.to_dict()
        
        assert data['name'] == "Test Job"
        assert data['function_name'] == 'test_func'
        assert data['kwargs'] == {'x': 10}
        assert data['max_retries'] == 3
        assert data['retry_delay'] == 5
    
    def test_job_from_dict(self):
        """Test Job Deserialisierung"""
        data = {
            'id': 'test-123',
            'name': 'Test Job',
            'function_name': 'test_func',
            'args': [1, 2],
            'kwargs': {'x': 10},
            'priority': JobPriority.HIGH,
            'scheduled_at': None,
            'timeout': 30,
            'retry_count': 0,
            'max_retries': 3,
            'retry_delay': 1,
            'retry_backoff': 2.0,
            'retry_jitter': True,
            'depends_on': [],
            'tags': ['test'],
            'created_by': 'test_user',
            'created_at': datetime.now().isoformat(),
            'metadata': {},
            'cron_expression': None
        }
        
        job = Job.from_dict(data)
        
        assert job.id == 'test-123'
        assert job.name == 'Test Job'
        assert job.function_name == 'test_func'
    
    def test_pickle_serialization(self):
        """Test Pickle-Serialisierung für Session State"""
        import pickle
        
        job = Job(
            name="Test Job",
            function_name='test_func',
            kwargs={'x': 10}
        )
        
        # Serialize
        pickled = pickle.dumps(job)
        
        # Deserialize
        job_restored = pickle.loads(pickled)
        
        assert job_restored.name == "Test Job"
        assert job_restored.function_name == 'test_func'
        assert job_restored.kwargs == {'x': 10}


class TestJobResult:
    """Tests für JobResult Dataclass"""
    
    def test_result_creation(self):
        """Test JobResult-Erstellung"""
        result = JobResult(
            job_id='job-123',
            status=JobStatus.COMPLETED,
            result={'success': True},
            duration_seconds=1.5
        )
        
        assert result.job_id == 'job-123'
        assert result.status == JobStatus.COMPLETED
        assert result.result == {'success': True}
        assert result.duration_seconds == 1.5
    
    def test_result_progress(self):
        """Test Progress-Tracking"""
        result = JobResult(
            job_id='job-123',
            status=JobStatus.RUNNING,
            progress=0.5,
            progress_message="Processing..."
        )
        
        assert result.progress == 0.5
        assert result.progress_message == "Processing..."
    
    def test_result_error(self):
        """Test Error-Tracking"""
        result = JobResult(
            job_id='job-123',
            status=JobStatus.FAILED,
            error="Division by zero",
            error_type=ErrorType.PERMANENT,
            traceback="Traceback (most recent call last)..."
        )
        
        assert result.error == "Division by zero"
        assert result.error_type == ErrorType.PERMANENT
        assert result.traceback.startswith("Traceback")


class TestJobQueue:
    """Tests für JobQueue"""
    
    def test_queue_enqueue_dequeue(self):
        """Test Enqueue/Dequeue"""
        queue = JobQueue()
        
        job1 = Job(name="Job 1", priority=JobPriority.NORMAL)
        job2 = Job(name="Job 2", priority=JobPriority.HIGH)
        
        queue.enqueue(job1)
        queue.enqueue(job2)
        
        # High priority should be dequeued first
        dequeued = queue.dequeue()
        assert dequeued.name == "Job 2"
        
        dequeued = queue.dequeue()
        assert dequeued.name == "Job 1"
    
    def test_queue_priority_order(self):
        """Test Prioritäts-Reihenfolge"""
        queue = JobQueue()
        
        low_job = Job(name="Low", priority=JobPriority.LOW)
        normal_job = Job(name="Normal", priority=JobPriority.NORMAL)
        high_job = Job(name="High", priority=JobPriority.HIGH)
        critical_job = Job(name="Critical", priority=JobPriority.CRITICAL)
        
        # Enqueue in random order
        queue.enqueue(normal_job)
        queue.enqueue(low_job)
        queue.enqueue(critical_job)
        queue.enqueue(high_job)
        
        # Dequeue in priority order
        assert queue.dequeue().name == "Critical"
        assert queue.dequeue().name == "High"
        assert queue.dequeue().name == "Normal"
        assert queue.dequeue().name == "Low"
    
    def test_queue_size(self):
        """Test Queue Size"""
        queue = JobQueue()
        
        assert queue.size() == 0
        
        queue.enqueue(Job(name="Job 1"))
        assert queue.size() == 1
        
        queue.enqueue(Job(name="Job 2"))
        assert queue.size() == 2
        
        queue.dequeue()
        assert queue.size() == 1
    
    def test_queue_remove(self):
        """Test Job-Removal"""
        queue = JobQueue()
        
        job1 = Job(name="Job 1")
        job2 = Job(name="Job 2")
        
        queue.enqueue(job1)
        queue.enqueue(job2)
        
        # Remove job1
        removed = queue.remove(job1.id)
        assert removed == True
        assert queue.size() == 1
        
        # Try to remove again
        removed = queue.remove(job1.id)
        assert removed == False


class TestJobManager:
    """Tests für JobManager"""
    
    def test_manager_initialization(self):
        """Test JobManager Initialisierung"""
        mgr = JobManager(max_workers=2, auto_recover=False)
        
        assert mgr.max_workers == 2
        assert mgr.running == False
        assert len(mgr.workers) == 0
    
    def test_manager_start_stop(self):
        """Test Start/Stop Workers"""
        mgr = JobManager(max_workers=2, auto_recover=False)
        
        mgr.start()
        assert mgr.running == True
        assert len(mgr.workers) == 2
        
        time.sleep(0.1)
        
        mgr.stop()
        assert mgr.running == False
    
    def test_function_registration(self):
        """Test Funktions-Registrierung"""
        mgr = JobManager(max_workers=1, auto_recover=False)
        
        def my_func(x):
            return x * 2
        
        mgr.register_function('my_func', my_func)
        
        assert 'my_func' in mgr.function_registry
        assert mgr.function_registry['my_func'] == my_func
    
    def test_job_execution(self):
        """Test Job-Ausführung"""
        mgr = JobManager(max_workers=1, auto_recover=False)
        mgr.start()
        
        def double(x):
            return x * 2
        
        mgr.register_function('double', double)
        
        job = Job(
            name="Double Job",
            function_name='double',
            kwargs={'x': 21}
        )
        
        job_id = mgr.enqueue(job)
        
        # Wait for completion
        time.sleep(0.5)
        
        result = mgr.poll(job_id)
        
        assert result is not None
        assert result.status == JobStatus.COMPLETED
        assert result.result == 42
        
        mgr.stop()
    
    def test_job_retry(self):
        """Test Job-Retry"""
        mgr = JobManager(max_workers=1, auto_recover=False)
        mgr.start()
        
        attempt = {'count': 0}
        
        def flaky_func():
            attempt['count'] += 1
            if attempt['count'] < 3:
                raise Exception("Transient error")
            return "Success"
        
        mgr.register_function('flaky_func', flaky_func)
        
        job = Job(
            name="Flaky Job",
            function_name='flaky_func',
            max_retries=3,
            retry_delay=0.1,
            retry_backoff=1.0
        )
        
        job_id = mgr.enqueue(job)
        
        # Wait for retries
        time.sleep(1.5)
        
        result = mgr.poll(job_id)
        
        assert result.status == JobStatus.COMPLETED
        assert result.result == "Success"
        assert attempt['count'] == 3
        
        mgr.stop()
    
    def test_job_cancellation(self):
        """Test Job-Abbruch"""
        mgr = JobManager(max_workers=1, auto_recover=False)
        mgr.start()
        
        def slow_job():
            time.sleep(10)
            return "Done"
        
        mgr.register_function('slow_job', slow_job)
        
        job = Job(
            name="Slow Job",
            function_name='slow_job'
        )
        
        job_id = mgr.enqueue(job)
        
        # Let it start
        time.sleep(0.2)
        
        # Cancel
        cancelled = mgr.cancel(job_id)
        assert cancelled == True
        
        # Check result
        result = mgr.poll(job_id)
        assert result.status == JobStatus.CANCELLED
        
        mgr.stop()
    
    def test_job_dependencies(self):
        """Test Job-Dependencies"""
        mgr = JobManager(max_workers=2, auto_recover=False)
        mgr.start()
        
        def job1_func():
            return "Job1 Done"
        
        def job2_func():
            return "Job2 Done"
        
        def job3_func():
            return "Job3 Done (depends on 1 & 2)"
        
        mgr.register_function('job1_func', job1_func)
        mgr.register_function('job2_func', job2_func)
        mgr.register_function('job3_func', job3_func)
        
        job1 = Job(name="Job 1", function_name='job1_func')
        job2 = Job(name="Job 2", function_name='job2_func')
        
        job1_id = mgr.enqueue(job1)
        job2_id = mgr.enqueue(job2)
        
        # Job3 depends on Job1 & Job2
        job3 = Job(
            name="Job 3",
            function_name='job3_func',
            depends_on=[job1_id, job2_id]
        )
        job3_id = mgr.enqueue(job3)
        
        # Wait for all jobs
        time.sleep(1)
        
        result1 = mgr.poll(job1_id)
        result2 = mgr.poll(job2_id)
        result3 = mgr.poll(job3_id)
        
        assert result1.status == JobStatus.COMPLETED
        assert result2.status == JobStatus.COMPLETED
        assert result3.status == JobStatus.COMPLETED
        
        mgr.stop()
    
    def test_get_stats(self):
        """Test Statistik-Abruf"""
        mgr = JobManager(max_workers=2, auto_recover=False)
        mgr.start()
        
        def dummy_job():
            return "Done"
        
        mgr.register_function('dummy_job', dummy_job)
        
        # Enqueue some jobs
        for i in range(5):
            job = Job(name=f"Job {i}", function_name='dummy_job')
            mgr.enqueue(job)
        
        # Wait
        time.sleep(1)
        
        stats = mgr.get_stats()
        
        assert 'total' in stats
        assert 'pending' in stats
        assert 'running' in stats
        assert 'completed' in stats
        assert 'workers' in stats
        assert stats['workers'] == 2
        
        mgr.stop()
    
    def test_get_job_history(self):
        """Test Job-History"""
        mgr = JobManager(max_workers=1, auto_recover=False)
        mgr.start()
        
        def dummy_job():
            return "Done"
        
        mgr.register_function('dummy_job', dummy_job)
        
        # Enqueue jobs
        for i in range(3):
            job = Job(name=f"Job {i}", function_name='dummy_job')
            mgr.enqueue(job)
        
        # Wait
        time.sleep(1)
        
        history = mgr.get_job_history(limit=10)
        
        assert len(history) >= 3
        
        # Verify structure
        for job, result in history:
            assert isinstance(job, Job)
            assert isinstance(result, JobResult)
        
        mgr.stop()


class TestCoreIntegration:
    """Tests für Core Integration"""
    
    def test_get_job_manager(self):
        """Test get_job_manager aus core_integration"""
        from core_integration import get_job_manager, is_feature_enabled
        
        if not is_feature_enabled('jobs'):
            pytest.skip("Jobs feature disabled")
        
        job_mgr = get_job_manager()
        
        assert job_mgr is not None
        assert isinstance(job_mgr, JobManager)
    
    def test_queue_job(self):
        """Test queue_job Funktion"""
        from core_integration import queue_job, get_job_manager, is_feature_enabled
        
        if not is_feature_enabled('jobs'):
            pytest.skip("Jobs feature disabled")
        
        job_mgr = get_job_manager()
        
        def test_func(x):
            return x * 2
        
        job_mgr.register_function('test_func', test_func)
        
        job_id = queue_job(
            job_type='test_func',
            data={'x': 21},
            priority=JobPriority.NORMAL
        )
        
        assert job_id is not None
        
        # Wait
        time.sleep(0.5)
        
        result = job_mgr.poll(job_id)
        assert result is not None


class TestProgressCallback:
    """Tests für ProgressCallback"""
    
    def test_progress_update(self):
        """Test Progress-Update"""
        result = JobResult(job_id='test-123')
        
        def update_callback(r):
            pass
        
        callback = ProgressCallback(result, update_callback)
        
        callback.update(0.5, "Processing...")
        
        assert result.progress == 0.5
        assert result.progress_message == "Processing..."
    
    def test_progress_details(self):
        """Test Progress-Details"""
        result = JobResult(job_id='test-123')
        
        callback = ProgressCallback(result, lambda r: None)
        
        callback.update(
            progress=0.75,
            message="Almost done",
            details={'items_processed': 75, 'items_total': 100}
        )
        
        assert result.progress == 0.75
        assert result.progress_details['items_processed'] == 75


def run_tests():
    """Führe alle Tests aus"""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_tests()
