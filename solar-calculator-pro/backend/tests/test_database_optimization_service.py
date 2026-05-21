"""
Tests for Database Optimization Service

Tests all database optimization functionality including:
- Query analysis
- Index management
- Partitioning analysis
- Data archiving
- Vacuum and analyze operations
- Performance monitoring

Requirements: 8.4
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker

from ..services.database_optimization_service import DatabaseOptimizationService


@pytest.fixture
def test_engine():
    """Create test database engine"""
    engine = create_engine("sqlite:///:memory:")
    
    # Create test tables
    metadata = MetaData()
    
    # Users table
    users = Table(
        'users',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(100)),
        Column('email', String(100)),
        Column('created_at', DateTime)
    )
    
    # Orders table
    orders = Table(
        'orders',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer),
        Column('amount', Integer),
        Column('order_date', DateTime)
    )
    
    metadata.create_all(engine)
    
    # Insert test data
    with engine.connect() as conn:
        # Insert users
        for i in range(100):
            conn.execute(
                text("INSERT INTO users (name, email, created_at) VALUES (:name, :email, :created_at)"),
                {
                    "name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "created_at": datetime.now() - timedelta(days=i)
                }
            )
        
        # Insert orders
        for i in range(500):
            conn.execute(
                text("INSERT INTO orders (user_id, amount, order_date) VALUES (:user_id, :amount, :order_date)"),
                {
                    "user_id": i % 100,
                    "amount": 100 + i,
                    "order_date": datetime.now() - timedelta(days=i % 400)
                }
            )
        
        conn.commit()
    
    yield engine
    
    engine.dispose()


@pytest.fixture
def optimization_service(test_engine):
    """Create optimization service instance"""
    return DatabaseOptimizationService(test_engine)


# ==================== Query Optimization Tests ====================

def test_analyze_query(optimization_service):
    """Test query analysis"""
    query = "SELECT * FROM users WHERE email = 'user1@example.com'"
    
    result = optimization_service.analyze_query(query)
    
    assert "query" in result
    assert "execution_time_ms" in result
    assert "query_plan" in result
    assert "issues" in result
    assert "suggestions" in result
    assert result["query"] == query


def test_analyze_query_with_join(optimization_service):
    """Test query analysis with JOIN"""
    query = """
        SELECT u.name, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.id
    """
    
    result = optimization_service.analyze_query(query)
    
    assert "query" in result
    assert "execution_time_ms" in result
    assert isinstance(result["execution_time_ms"], (int, float))


def test_analyze_query_invalid(optimization_service):
    """Test query analysis with invalid query"""
    query = "SELECT * FROM nonexistent_table"
    
    result = optimization_service.analyze_query(query)
    
    assert "error" in result


# ==================== Index Management Tests ====================

def test_get_indexes(optimization_service):
    """Test getting all indexes"""
    indexes = optimization_service.get_indexes()
    
    assert isinstance(indexes, dict)
    assert "users" in indexes
    assert "orders" in indexes


def test_get_indexes_for_table(optimization_service):
    """Test getting indexes for specific table"""
    indexes = optimization_service.get_indexes("users")
    
    assert isinstance(indexes, dict)
    assert "users" in indexes
    assert isinstance(indexes["users"], list)


def test_analyze_index_usage(optimization_service):
    """Test index usage analysis"""
    result = optimization_service.analyze_index_usage("users")
    
    assert "table_name" in result
    assert "row_count" in result
    assert "indexes" in result
    assert "recommendations" in result
    assert result["table_name"] == "users"
    assert result["row_count"] == 100


def test_create_index(optimization_service):
    """Test creating an index"""
    result = optimization_service.create_index(
        table_name="users",
        columns=["email"]
    )
    
    assert result["success"] is True
    assert "index_name" in result
    assert result["table_name"] == "users"
    assert result["columns"] == ["email"]
    
    # Verify index was created
    indexes = optimization_service.get_indexes("users")
    index_names = [idx["name"] for idx in indexes["users"]]
    assert result["index_name"] in index_names


def test_create_unique_index(optimization_service):
    """Test creating a unique index"""
    result = optimization_service.create_index(
        table_name="users",
        columns=["email"],
        index_name="idx_users_email_unique",
        unique=True
    )
    
    assert result["success"] is True
    assert result["unique"] is True


def test_drop_index(optimization_service):
    """Test dropping an index"""
    # First create an index
    create_result = optimization_service.create_index(
        table_name="users",
        columns=["name"]
    )
    index_name = create_result["index_name"]
    
    # Then drop it
    drop_result = optimization_service.drop_index(index_name)
    
    assert drop_result["success"] is True
    assert drop_result["index_name"] == index_name


# ==================== Partitioning Tests ====================

def test_analyze_partitioning_candidates(optimization_service):
    """Test partitioning candidate analysis"""
    candidates = optimization_service.analyze_partitioning_candidates()
    
    assert isinstance(candidates, list)
    # With our test data (500 orders), orders table should be a candidate
    # if threshold is low enough


def test_partitioning_candidates_structure(optimization_service):
    """Test structure of partitioning candidates"""
    candidates = optimization_service.analyze_partitioning_candidates()
    
    for candidate in candidates:
        assert "table_name" in candidate
        assert "row_count" in candidate
        assert "partition_columns" in candidate
        assert "strategy" in candidate
        assert "reason" in candidate


# ==================== Archiving Tests ====================

def test_analyze_archiving_candidates(optimization_service):
    """Test archiving candidate analysis"""
    candidates = optimization_service.analyze_archiving_candidates(age_threshold_days=30)
    
    assert isinstance(candidates, list)
    # Should find old records in both tables


def test_archiving_candidates_structure(optimization_service):
    """Test structure of archiving candidates"""
    candidates = optimization_service.analyze_archiving_candidates(age_threshold_days=30)
    
    for candidate in candidates:
        assert "table_name" in candidate
        assert "date_column" in candidate
        assert "old_records_count" in candidate
        assert "threshold_date" in candidate
        assert "recommendation" in candidate


def test_archive_old_data(optimization_service, test_engine):
    """Test archiving old data"""
    threshold_date = datetime.now() - timedelta(days=30)
    
    result = optimization_service.archive_old_data(
        table_name="users",
        date_column="created_at",
        threshold_date=threshold_date
    )
    
    assert result["success"] is True
    assert "archived_count" in result
    assert result["archived_count"] > 0
    assert result["table_name"] == "users"
    assert result["archive_table"] == "users_archive"
    
    # Verify archive table exists and has data
    with test_engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM users_archive"))
        archive_count = result.scalar()
        assert archive_count > 0


# ==================== Vacuum and Analyze Tests ====================

def test_vacuum_database(optimization_service):
    """Test VACUUM operation"""
    result = optimization_service.vacuum_database()
    
    assert result["success"] is True
    assert "duration_seconds" in result
    assert "size_before_bytes" in result
    assert "size_after_bytes" in result
    assert "space_freed_bytes" in result
    assert "space_freed_mb" in result


def test_analyze_tables_all(optimization_service):
    """Test ANALYZE on all tables"""
    result = optimization_service.analyze_tables()
    
    assert result["success"] is True
    assert "duration_seconds" in result
    assert result["tables_analyzed"] == "all"


def test_analyze_tables_specific(optimization_service):
    """Test ANALYZE on specific tables"""
    result = optimization_service.analyze_tables(table_names=["users", "orders"])
    
    assert result["success"] is True
    assert "duration_seconds" in result
    assert result["tables_analyzed"] == ["users", "orders"]


def test_schedule_maintenance(optimization_service):
    """Test maintenance schedule configuration"""
    result = optimization_service.schedule_maintenance(
        vacuum_enabled=True,
        analyze_enabled=True,
        vacuum_schedule="weekly",
        analyze_schedule="daily"
    )
    
    assert "vacuum" in result
    assert "analyze" in result
    assert result["vacuum"]["enabled"] is True
    assert result["vacuum"]["schedule"] == "weekly"
    assert result["analyze"]["enabled"] is True
    assert result["analyze"]["schedule"] == "daily"


# ==================== Performance Monitoring Tests ====================

def test_get_performance_metrics(optimization_service):
    """Test getting performance metrics"""
    metrics = optimization_service.get_performance_metrics()
    
    assert "database_size_bytes" in metrics
    assert "database_size_mb" in metrics
    assert "table_count" in metrics
    assert "total_rows" in metrics
    assert "total_indexes" in metrics
    assert "table_statistics" in metrics
    assert "measured_at" in metrics
    
    # Verify table statistics
    assert metrics["table_count"] == 2  # users and orders
    assert metrics["total_rows"] == 600  # 100 users + 500 orders


def test_get_optimization_report(optimization_service):
    """Test generating optimization report"""
    report = optimization_service.get_optimization_report()
    
    assert "generated_at" in report
    assert "performance_metrics" in report
    assert "index_analysis" in report
    assert "partitioning_candidates" in report
    assert "archiving_candidates" in report
    assert "recommendations" in report
    
    # Verify performance metrics in report
    assert "database_size_mb" in report["performance_metrics"]
    assert "table_count" in report["performance_metrics"]
    
    # Verify index analysis for each table
    assert "users" in report["index_analysis"]
    assert "orders" in report["index_analysis"]


def test_optimization_report_recommendations(optimization_service):
    """Test optimization report recommendations"""
    report = optimization_service.get_optimization_report()
    
    assert isinstance(report["recommendations"], list)
    # Should have recommendations based on test data


# ==================== Integration Tests ====================

def test_full_optimization_workflow(optimization_service, test_engine):
    """Test complete optimization workflow"""
    # 1. Get initial metrics
    initial_metrics = optimization_service.get_performance_metrics()
    assert initial_metrics["total_rows"] == 600
    
    # 2. Create indexes
    email_index = optimization_service.create_index("users", ["email"])
    assert email_index["success"] is True
    
    user_id_index = optimization_service.create_index("orders", ["user_id"])
    assert user_id_index["success"] is True
    
    # 3. Analyze index usage
    users_analysis = optimization_service.analyze_index_usage("users")
    assert len(users_analysis["indexes"]) > 0
    
    # 4. Archive old data
    threshold = datetime.now() - timedelta(days=50)
    archive_result = optimization_service.archive_old_data(
        "users",
        "created_at",
        threshold
    )
    assert archive_result["success"] is True
    
    # 5. Run ANALYZE
    analyze_result = optimization_service.analyze_tables()
    assert analyze_result["success"] is True
    
    # 6. Run VACUUM
    vacuum_result = optimization_service.vacuum_database()
    assert vacuum_result["success"] is True
    
    # 7. Get final report
    final_report = optimization_service.get_optimization_report()
    assert "recommendations" in final_report


def test_error_handling(optimization_service):
    """Test error handling in various scenarios"""
    # Test with invalid table name
    result = optimization_service.analyze_index_usage("nonexistent_table")
    assert "error" in result
    
    # Test with invalid query
    result = optimization_service.analyze_query("INVALID SQL")
    assert "error" in result


# ==================== Performance Tests ====================

def test_query_analysis_performance(optimization_service):
    """Test query analysis performance"""
    query = "SELECT * FROM users WHERE id < 50"
    
    result = optimization_service.analyze_query(query)
    
    # Execution time should be reasonable
    assert result["execution_time_ms"] < 1000  # Less than 1 second


def test_index_creation_performance(optimization_service):
    """Test index creation performance"""
    import time
    
    start = time.time()
    result = optimization_service.create_index("orders", ["order_date"])
    duration = time.time() - start
    
    assert result["success"] is True
    assert duration < 5  # Should complete in less than 5 seconds


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
