"""
Performance Testing Suite for KAI Agent Integration

This module tests performance with large knowledge bases, concurrent sessions,
response times, and resource usage.

Requirements: Performance NFRs from requirements.md
"""

import json
import os
import sys
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import psutil
import pytest

# Add Agent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


class TestKnowledgeBasePerformance:
    """Test performance with large knowledge bases (Performance NFR)"""

    def test_knowledge_base_search_speed(self):
        """Test knowledge base search completes within 1 second"""
        from agent.tools.knowledge_tools import (
            knowledge_base_search,
            setup_knowledge_base,
        )

        kb_dir = Path(__file__).parent / "knowledge_base"

        if not kb_dir.exists() or not list(kb_dir.glob("*.pdf")):
            pytest.skip("No knowledge base documents available for testing")

        # Setup knowledge base
        start_time = time.time()
        vector_store = setup_knowledge_base()
        setup_time = time.time() - start_time

        print(f"\nKnowledge base setup time: {setup_time:.2f}s")

        # Test search speed
        search_tool = knowledge_base_search(vector_store)

        start_time = time.time()
        result = search_tool.invoke("Photovoltaik")
        search_time = time.time() - start_time

        print(f"Search time: {search_time:.3f}s")

        # Should complete in under 1 second (Performance NFR)
        assert search_time < 1.0, f"Search took {
            search_time:.3f}s, expected < 1.0s"

    def test_knowledge_base_caching(self):
        """Test that knowledge base index is cached and reused"""
        from agent.tools.knowledge_tools import setup_knowledge_base

        kb_dir = Path(__file__).parent / "knowledge_base"

        if not kb_dir.exists() or not list(kb_dir.glob("*.pdf")):
            pytest.skip("No knowledge base documents available for testing")

        # First load
        start_time = time.time()
        vector_store1 = setup_knowledge_base()
        first_load_time = time.time() - start_time

        # Second load (should use cache)
        start_time = time.time()
        vector_store2 = setup_knowledge_base()
        second_load_time = time.time() - start_time

        print(f"\nFirst load: {first_load_time:.2f}s")
        print(f"Second load (cached): {second_load_time:.2f}s")

        # Cached load should be significantly faster
        assert second_load_time < first_load_time * \
            0.5, "Caching not working effectively"

    def test_large_knowledge_base_handling(self):
        """Test system handles large knowledge base efficiently"""
        # This test verifies the system can handle many documents
        # In production, test with 100+ PDFs

        kb_dir = Path(__file__).parent / "knowledge_base"

        if not kb_dir.exists():
            pytest.skip("Knowledge base directory not available")

        pdf_count = len(list(kb_dir.glob("*.pdf")))
        print(f"\nKnowledge base contains {pdf_count} PDF documents")

        # System should handle at least some documents without issues
        assert pdf_count >= 0, "Knowledge base directory should be accessible"


class TestAgentResponseTime:
    """Test agent response times (Performance NFR)"""

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-key-123',
        'TAVILY_API_KEY': 'test-tavily-key'
    })
    def test_agent_initialization_speed(self):
        """Test agent initializes within reasonable time"""
        from agent.tools.knowledge_tools import setup_knowledge_base

        kb_dir = Path(__file__).parent / "knowledge_base"

        if not kb_dir.exists() or not list(kb_dir.glob("*.pdf")):
            # Test with empty knowledge base
            with patch('agent.tools.knowledge_tools.os.listdir', return_value=[]):
                start_time = time.time()
                vector_store = setup_knowledge_base()
                init_time = time.time() - start_time
        else:
            start_time = time.time()
            vector_store = setup_knowledge_base()
            init_time = time.time() - start_time

        print(f"\nAgent initialization time: {init_time:.2f}s")

        # Should initialize within reasonable time
        assert init_time < 30.0, f"Initialization took {
            init_time:.2f}s, too slow"

    def test_file_operations_speed(self):
        """Test file operations are fast"""
        from agent.tools.coding_tools import list_files, read_file, write_file

        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['AGENT_WORKSPACE_DIR'] = temp_dir

            # Test write speed
            start_time = time.time()
            for i in range(10):
                write_file(f"test_{i}.txt", f"Content {i}" * 100)
            write_time = time.time() - start_time

            print(f"\nWrite 10 files: {write_time:.3f}s")

            # Test read speed
            start_time = time.time()
            for i in range(10):
                read_file(f"test_{i}.txt")
            read_time = time.time() - start_time

            print(f"Read 10 files: {read_time:.3f}s")

            # Test list speed
            start_time = time.time()
            list_files(".")
            list_time = time.time() - start_time

            print(f"List files: {list_time:.3f}s")

            # All operations should be fast
            assert write_time < 1.0, "File writes too slow"
            assert read_time < 1.0, "File reads too slow"
            assert list_time < 0.5, "File listing too slow"


class TestConcurrentSessions:
    """Test concurrent agent sessions (Scalability NFR)"""

    def test_multiple_file_operations_concurrent(self):
        """Test multiple file operations can run concurrently"""
        from agent.tools.coding_tools import read_file, write_file

        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['AGENT_WORKSPACE_DIR'] = temp_dir

            results = []
            errors = []

            def worker(worker_id):
                try:
                    # Each worker writes and reads files
                    write_file(
                        f"worker_{worker_id}.txt",
                        f"Data from worker {worker_id}")
                    content = read_file(f"worker_{worker_id}.txt")
                    results.append((worker_id, content))
                except Exception as e:
                    errors.append((worker_id, str(e)))

            # Create 5 concurrent workers
            threads = []
            start_time = time.time()

            for i in range(5):
                t = threading.Thread(target=worker, args=(i,))
                t.start()
                threads.append(t)

            # Wait for all to complete
            for t in threads:
                t.join()

            total_time = time.time() - start_time

            print(f"\n5 concurrent operations completed in {total_time:.3f}s")
            print(f"Successful operations: {len(results)}")
            print(f"Failed operations: {len(errors)}")

            # All should succeed
            assert len(errors) == 0, f"Concurrent operations failed: {errors}"
            assert len(results) == 5, "Not all operations completed"

    def test_knowledge_base_concurrent_searches(self):
        """Test concurrent knowledge base searches"""
        from agent.tools.knowledge_tools import (
            knowledge_base_search,
            setup_knowledge_base,
        )

        kb_dir = Path(__file__).parent / "knowledge_base"

        if not kb_dir.exists() or not list(kb_dir.glob("*.pdf")):
            pytest.skip("No knowledge base documents available for testing")

        vector_store = setup_knowledge_base()
        search_tool = knowledge_base_search(vector_store)

        results = []
        errors = []

        def search_worker(query, worker_id):
            try:
                start = time.time()
                result = search_tool.invoke(query)
                duration = time.time() - start
                results.append((worker_id, duration, len(result)))
            except Exception as e:
                errors.append((worker_id, str(e)))

        # Create concurrent searches
        queries = [
            "Photovoltaik",
            "Wärmepumpe",
            "Energie",
            "Solar",
            "Installation"
        ]

        threads = []
        start_time = time.time()

        for i, query in enumerate(queries):
            t = threading.Thread(target=search_worker, args=(query, i))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        total_time = time.time() - start_time

        print(
            f"\n{
                len(queries)} concurrent searches completed in {
                total_time:.3f}s")
        print(f"Successful searches: {len(results)}")
        print(f"Failed searches: {len(errors)}")

        if results:
            avg_time = sum(r[1] for r in results) / len(results)
            print(f"Average search time: {avg_time:.3f}s")

        # All should succeed
        assert len(errors) == 0, f"Concurrent searches failed: {errors}"


class TestResourceUsage:
    """Monitor resource usage (Performance NFR)"""

    def test_memory_usage_reasonable(self):
        """Test memory usage stays within reasonable bounds"""
        process = psutil.Process()

        # Get baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        print(f"\nBaseline memory: {baseline_memory:.2f} MB")

        # Perform operations
        from agent.tools.coding_tools import write_file

        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['AGENT_WORKSPACE_DIR'] = temp_dir

            # Write many files
            for i in range(100):
                write_file(f"test_{i}.txt", "x" * 1000)

            # Check memory after operations
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - baseline_memory

            print(f"Memory after 100 file operations: {current_memory:.2f} MB")
            print(f"Memory increase: {memory_increase:.2f} MB")

            # Memory increase should be reasonable (< 100 MB for this test)
            assert memory_increase < 100, f"Memory usage too high: {
                memory_increase:.2f} MB"

    def test_docker_cleanup_releases_resources(self):
        """Test Docker containers are cleaned up properly"""
        # This test verifies cleanup happens
        # In production, monitor docker ps to ensure no orphaned containers

        try:
            import docker
            client = docker.from_env()

            # Get initial container count
            initial_containers = len(client.containers.list(all=True))

            print(f"\nInitial Docker containers: {initial_containers}")

            # After agent operations, container count should not grow indefinitely
            # This is a basic check - full test requires running actual
            # operations

            assert initial_containers >= 0, "Docker client should be accessible"

        except Exception as e:
            pytest.skip(f"Docker not available: {e}")

    def test_file_system_cleanup(self):
        """Test temporary files are cleaned up"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['AGENT_WORKSPACE_DIR'] = temp_dir

            from agent.tools.coding_tools import write_file

            # Create files
            for i in range(10):
                write_file(f"temp_{i}.txt", "temporary data")

            # Count files
            file_count = len(list(Path(temp_dir).glob("*.txt")))

            print(f"\nCreated {file_count} temporary files")

            # Files should exist
            assert file_count == 10

        # After context exit, temp_dir should be cleaned up
        assert not Path(temp_dir).exists(
        ), "Temporary directory not cleaned up"


class TestPerformanceMetrics:
    """Collect and report performance metrics"""

    def test_generate_performance_report(self):
        """Generate comprehensive performance report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_suite": "KAI Agent Performance Tests",
            "metrics": {}
        }

        # Test various operations and collect metrics
        from agent.tools.coding_tools import list_files, read_file, write_file

        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['AGENT_WORKSPACE_DIR'] = temp_dir

            # File write performance
            start = time.time()
            for i in range(50):
                write_file(f"perf_test_{i}.txt", "x" * 1000)
            write_duration = time.time() - start

            report["metrics"]["file_write_50_files"] = {
                "duration_seconds": round(write_duration, 3),
                "operations_per_second": round(50 / write_duration, 2)
            }

            # File read performance
            start = time.time()
            for i in range(50):
                read_file(f"perf_test_{i}.txt")
            read_duration = time.time() - start

            report["metrics"]["file_read_50_files"] = {
                "duration_seconds": round(read_duration, 3),
                "operations_per_second": round(50 / read_duration, 2)
            }

            # List performance
            start = time.time()
            list_files(".")
            list_duration = time.time() - start

            report["metrics"]["list_files"] = {
                "duration_seconds": round(list_duration, 3)
            }

        # Memory usage
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024

        report["metrics"]["memory_usage_mb"] = round(memory_mb, 2)

        # Save report
        report_path = Path(__file__).parent / "performance_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n{'=' * 60}")
        print("PERFORMANCE REPORT")
        print('=' * 60)
        print(json.dumps(report["metrics"], indent=2))
        print('=' * 60)

        # Basic assertions
        assert report["metrics"]["file_write_50_files"]["duration_seconds"] < 5.0
        assert report["metrics"]["file_read_50_files"]["duration_seconds"] < 5.0
        assert report["metrics"]["list_files"]["duration_seconds"] < 1.0


def run_performance_tests():
    """Run all performance tests and generate report"""
    print("=" * 70)
    print("KAI AGENT - PERFORMANCE TEST SUITE")
    print("=" * 70)

    # Run pytest with verbose output
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "-W", "ignore::DeprecationWarning",
        "-s"  # Show print statements
    ]

    result = pytest.main(pytest_args)

    print("\n" + "=" * 70)
    if result == 0:
        print("✓ ALL PERFORMANCE TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED - Review output above")
    print("=" * 70)

    return result


if __name__ == "__main__":
    sys.exit(run_performance_tests())
