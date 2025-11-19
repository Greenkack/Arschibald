"""
Unit tests for DatabaseService

Tests CRUD operations, transactions, query optimization,
backup/restore, and error handling.
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime
from backend.services.database_service import (
    DatabaseService,
    DatabaseError,
    ConnectionError,
    TransactionError,
    QueryError
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')
    
    # Create test database with sample table
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE test_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def db_service(temp_db):
    """Create DatabaseService instance for testing"""
    service = DatabaseService(db_path=temp_db)
    yield service
    service.close()


class TestDatabaseService:
    """Test DatabaseService functionality"""
    
    def test_initialization(self, db_service):
        """Test service initialization"""
        assert db_service is not None
        assert len(db_service._connection_pool) > 0
        assert os.path.exists(db_service.db_path)
    
    def test_connection_pool(self, db_service):
        """Test connection pool management"""
        initial_size = len(db_service._connection_pool)
        
        with db_service.get_connection() as conn:
            assert conn is not None
            # Pool should have one less connection
            assert len(db_service._connection_pool) == initial_size - 1
        
        # Connection should be returned to pool
        assert len(db_service._connection_pool) == initial_size
    
    def test_create_record(self, db_service):
        """Test creating a record"""
        data = {'name': 'Test Item', 'value': 42}
        record_id = db_service.create('test_table', data)
        
        assert record_id > 0
        
        # Verify record was created
        record = db_service.read('test_table', record_id)
        assert record is not None
        assert record['name'] == 'Test Item'
        assert record['value'] == 42
    
    def test_read_record(self, db_service):
        """Test reading a record"""
        # Create test record
        data = {'name': 'Read Test', 'value': 100}
        record_id = db_service.create('test_table', data)
        
        # Read record
        record = db_service.read('test_table', record_id)
        assert record is not None
        assert record['id'] == record_id
        assert record['name'] == 'Read Test'
        assert record['value'] == 100
    
    def test_read_nonexistent_record(self, db_service):
        """Test reading non-existent record"""
        record = db_service.read('test_table', 99999)
        assert record is None
    
    def test_read_all_records(self, db_service):
        """Test reading all records"""
        # Create multiple records
        for i in range(5):
            db_service.create('test_table', {'name': f'Item {i}', 'value': i * 10})
        
        # Read all
        records = db_service.read_all('test_table')
        assert len(records) >= 5
    
    def test_read_all_with_filters(self, db_service):
        """Test reading with filters"""
        # Create test records
        db_service.create('test_table', {'name': 'Alpha', 'value': 10})
        db_service.create('test_table', {'name': 'Beta', 'value': 20})
        db_service.create('test_table', {'name': 'Alpha', 'value': 30})
        
        # Filter by name
        records = db_service.read_all('test_table', filters={'name': 'Alpha'})
        assert len(records) == 2
        assert all(r['name'] == 'Alpha' for r in records)
    
    def test_read_all_with_order_and_limit(self, db_service):
        """Test reading with order and limit"""
        # Create test records
        for i in range(10):
            db_service.create('test_table', {'name': f'Item {i}', 'value': i})
        
        # Read with order and limit
        records = db_service.read_all('test_table', order_by='value DESC', limit=3)
        assert len(records) == 3
        assert records[0]['value'] >= records[1]['value']
        assert records[1]['value'] >= records[2]['value']
    
    def test_update_record(self, db_service):
        """Test updating a record"""
        # Create record
        data = {'name': 'Original', 'value': 50}
        record_id = db_service.create('test_table', data)
        
        # Update record
        update_data = {'name': 'Updated', 'value': 75}
        success = db_service.update('test_table', record_id, update_data)
        assert success is True
        
        # Verify update
        record = db_service.read('test_table', record_id)
        assert record['name'] == 'Updated'
        assert record['value'] == 75
    
    def test_delete_record(self, db_service):
        """Test deleting a record"""
        # Create record
        data = {'name': 'To Delete', 'value': 99}
        record_id = db_service.create('test_table', data)
        
        # Delete record
        success = db_service.delete('test_table', record_id)
        assert success is True
        
        # Verify deletion
        record = db_service.read('test_table', record_id)
        assert record is None
    
    def test_transaction_commit(self, db_service):
        """Test transaction commit"""
        with db_service.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ('Trans1', 111))
            cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ('Trans2', 222))
        
        # Verify both records were committed
        records = db_service.read_all('test_table', filters={'value': 111})
        assert len(records) == 1
        records = db_service.read_all('test_table', filters={'value': 222})
        assert len(records) == 1
    
    def test_transaction_rollback(self, db_service):
        """Test transaction rollback on error"""
        try:
            with db_service.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO test_table (name, value) VALUES (?, ?)", ('Rollback', 333))
                # Force an error
                raise Exception("Test error")
        except TransactionError:
            pass
        
        # Verify record was not committed
        records = db_service.read_all('test_table', filters={'value': 333})
        assert len(records) == 0
    
    def test_execute_query(self, db_service):
        """Test custom query execution"""
        # Create test data
        db_service.create('test_table', {'name': 'Query Test', 'value': 500})
        
        # Execute custom query
        results = db_service.execute_query(
            "SELECT * FROM test_table WHERE value > ?",
            (400,)
        )
        
        assert len(results) > 0
        assert all(r['value'] > 400 for r in results)
    
    def test_execute_many(self, db_service):
        """Test batch insert"""
        data_list = [
            ('Batch1', 10),
            ('Batch2', 20),
            ('Batch3', 30)
        ]
        
        count = db_service.execute_many(
            "INSERT INTO test_table (name, value) VALUES (?, ?)",
            data_list
        )
        
        assert count == 3
        
        # Verify records
        records = db_service.read_all('test_table')
        assert len(records) >= 3
    
    def test_create_index(self, db_service):
        """Test index creation"""
        success = db_service.create_index('test_table', ['name'])
        assert success is True
        
        # Verify index was created
        analysis = db_service.analyze_table('test_table')
        index_names = [idx['name'] for idx in analysis['indexes']]
        assert any('name' in name for name in index_names)
    
    def test_analyze_table(self, db_service):
        """Test table analysis"""
        analysis = db_service.analyze_table('test_table')
        
        assert 'table' in analysis
        assert analysis['table'] == 'test_table'
        assert 'columns' in analysis
        assert 'indexes' in analysis
        assert 'row_count' in analysis
        assert len(analysis['columns']) > 0
    
    def test_optimize_database(self, db_service):
        """Test database optimization"""
        success = db_service.optimize_database()
        assert success is True
    
    def test_backup_database(self, db_service):
        """Test database backup"""
        # Create some test data
        db_service.create('test_table', {'name': 'Backup Test', 'value': 999})
        
        # Create backup
        backup_path = db_service.backup()
        
        assert os.path.exists(backup_path)
        assert backup_path.endswith('.db')
        
        # Verify backup contains data
        import sqlite3
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM test_table")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count > 0
    
    def test_restore_database(self, db_service, temp_db):
        """Test database restore"""
        # Create original data
        original_id = db_service.create('test_table', {'name': 'Original', 'value': 111})
        
        # Create backup
        backup_path = db_service.backup()
        
        # Modify database
        db_service.create('test_table', {'name': 'After Backup', 'value': 222})
        
        # Restore from backup
        success = db_service.restore(backup_path)
        assert success is True
        
        # Verify restoration
        record = db_service.read('test_table', original_id)
        assert record is not None
        
        # New record should not exist
        records = db_service.read_all('test_table', filters={'value': 222})
        assert len(records) == 0
    
    def test_list_backups(self, db_service):
        """Test listing backups"""
        # Create multiple backups
        backup1 = db_service.backup()
        backup2 = db_service.backup()
        
        # List backups
        backups = db_service.list_backups()
        
        assert len(backups) >= 2
        assert all('filename' in b for b in backups)
        assert all('path' in b for b in backups)
        assert all('size_mb' in b for b in backups)
        assert all('created_at' in b for b in backups)
    
    def test_health_check(self, db_service):
        """Test health check"""
        health = db_service.health_check()
        
        assert 'status' in health
        assert health['status'] == 'healthy'
        assert 'connection_pool_size' in health
        assert 'database_size_mb' in health
        assert 'timestamp' in health
    
    def test_get_table_list(self, db_service):
        """Test getting table list"""
        tables = db_service.get_table_list()
        
        assert isinstance(tables, list)
        assert 'test_table' in tables
    
    def test_context_manager(self, temp_db):
        """Test using service as context manager"""
        with DatabaseService(db_path=temp_db) as service:
            data = {'name': 'Context Test', 'value': 777}
            record_id = service.create('test_table', data)
            assert record_id > 0
        
        # Service should be closed after context
        assert len(service._connection_pool) == 0
    
    def test_singleton_instance(self):
        """Test singleton pattern"""
        from backend.services.database_service import get_database_service
        
        service1 = get_database_service()
        service2 = get_database_service()
        
        assert service1 is service2


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_table_name(self, db_service):
        """Test error on invalid table name"""
        with pytest.raises(DatabaseError):
            db_service.read('nonexistent_table', 1)
    
    def test_invalid_column_name(self, db_service):
        """Test error on invalid column name"""
        with pytest.raises(DatabaseError):
            db_service.create('test_table', {'invalid_column': 'value'})
    
    def test_restore_nonexistent_backup(self, db_service):
        """Test error on restoring non-existent backup"""
        with pytest.raises(DatabaseError):
            db_service.restore('/nonexistent/backup.db')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
