"""
Tests for Database Abstraction Layer
"""

import pytest
import tempfile
import os
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

from backend.core.database_abstraction import (
    DatabaseType,
    DatabaseConfig,
    DatabaseFactory,
    DatabaseManager,
    SQLiteAdapter,
    PostgreSQLAdapter,
    MySQLAdapter
)

Base = declarative_base()


class TestModel(Base):
    """Test model for database operations"""
    __tablename__ = "test_table"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    value = Column(Float)


class TestDatabaseConfig:
    """Test DatabaseConfig class"""
    
    def test_sqlite_connection_string(self):
        """Test SQLite connection string generation"""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path="/path/to/database.db"
        )
        
        assert config.get_connection_string() == "sqlite:////path/to/database.db"
    
    def test_postgresql_connection_string(self):
        """Test PostgreSQL connection string generation"""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            port=5432,
            database="testdb",
            username="user",
            password="pass"
        )
        
        expected = "postgresql://user:pass@localhost:5432/testdb"
        assert config.get_connection_string() == expected
    
    def test_mysql_connection_string(self):
        """Test MySQL connection string generation"""
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            host="localhost",
            port=3306,
            database="testdb",
            username="user",
            password="pass"
        )
        
        expected = "mysql+pymysql://user:pass@localhost:3306/testdb"
        assert config.get_connection_string() == expected
    
    def test_sqlite_missing_path(self):
        """Test SQLite with missing path raises error"""
        config = DatabaseConfig(db_type=DatabaseType.SQLITE)
        
        with pytest.raises(ValueError, match="SQLite path is required"):
            config.get_connection_string()
    
    def test_postgresql_missing_credentials(self):
        """Test PostgreSQL with missing credentials raises error"""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost"
        )
        
        with pytest.raises(ValueError, match="Host, database, username, and password are required"):
            config.get_connection_string()


class TestDatabaseFactory:
    """Test DatabaseFactory class"""
    
    def test_create_sqlite_adapter(self):
        """Test creating SQLite adapter"""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path=":memory:"
        )
        
        adapter = DatabaseFactory.create_adapter(config)
        assert isinstance(adapter, SQLiteAdapter)
    
    def test_create_postgresql_adapter(self):
        """Test creating PostgreSQL adapter"""
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="testdb",
            username="user",
            password="pass"
        )
        
        adapter = DatabaseFactory.create_adapter(config)
        assert isinstance(adapter, PostgreSQLAdapter)
    
    def test_create_mysql_adapter(self):
        """Test creating MySQL adapter"""
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            host="localhost",
            database="testdb",
            username="user",
            password="pass"
        )
        
        adapter = DatabaseFactory.create_adapter(config)
        assert isinstance(adapter, MySQLAdapter)


class TestSQLiteAdapter:
    """Test SQLite adapter"""
    
    @pytest.fixture
    def sqlite_config(self):
        """Create SQLite configuration"""
        return DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path=":memory:"
        )
    
    @pytest.fixture
    def sqlite_adapter(self, sqlite_config):
        """Create SQLite adapter"""
        return SQLiteAdapter(sqlite_config)
    
    def test_connect_disconnect(self, sqlite_adapter):
        """Test connecting and disconnecting"""
        sqlite_adapter.connect()
        assert sqlite_adapter.engine is not None
        assert sqlite_adapter.SessionLocal is not None
        
        sqlite_adapter.disconnect()
    
    def test_create_tables(self, sqlite_adapter):
        """Test creating tables"""
        sqlite_adapter.Base = Base
        sqlite_adapter.connect()
        sqlite_adapter.create_tables()
        
        # Verify table exists
        from sqlalchemy import inspect
        inspector = inspect(sqlite_adapter.engine)
        tables = inspector.get_table_names()
        assert "test_table" in tables
        
        sqlite_adapter.disconnect()
    
    def test_get_session(self, sqlite_adapter):
        """Test getting session"""
        sqlite_adapter.connect()
        session = sqlite_adapter.get_session()
        
        assert session is not None
        session.close()
        sqlite_adapter.disconnect()
    
    def test_execute_raw_sql(self, sqlite_adapter):
        """Test executing raw SQL"""
        sqlite_adapter.Base = Base
        sqlite_adapter.connect()
        sqlite_adapter.create_tables()
        
        # Insert data
        sqlite_adapter.execute_raw_sql(
            "INSERT INTO test_table (name, value) VALUES ('test', 123.45)"
        )
        
        # Query data
        result = sqlite_adapter.execute_raw_sql("SELECT * FROM test_table")
        assert len(result) == 1
        
        sqlite_adapter.disconnect()
    
    def test_backup_restore(self, sqlite_adapter):
        """Test backup and restore"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create database with data
            db_path = os.path.join(tmpdir, "test.db")
            backup_path = os.path.join(tmpdir, "backup.db")
            
            config = DatabaseConfig(
                db_type=DatabaseType.SQLITE,
                sqlite_path=db_path
            )
            adapter = SQLiteAdapter(config)
            adapter.Base = Base
            adapter.connect()
            adapter.create_tables()
            
            # Insert data
            session = adapter.get_session()
            session.add(TestModel(name="test", value=123.45))
            session.commit()
            session.close()
            
            adapter.disconnect()
            
            # Backup
            assert adapter.backup(backup_path)
            assert os.path.exists(backup_path)
            
            # Restore
            assert adapter.restore(backup_path)


class TestDatabaseManager:
    """Test DatabaseManager class"""
    
    @pytest.fixture
    def manager(self):
        """Create database manager"""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path=":memory:"
        )
        return DatabaseManager(config)
    
    def test_connect_disconnect(self, manager):
        """Test connecting and disconnecting"""
        manager.connect()
        assert manager._connected
        
        manager.disconnect()
        assert not manager._connected
    
    def test_get_session(self, manager):
        """Test getting session"""
        session = manager.get_session()
        assert session is not None
        assert manager._connected
        session.close()
        manager.disconnect()
    
    def test_context_manager(self):
        """Test using as context manager"""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path=":memory:"
        )
        
        with DatabaseManager(config) as manager:
            assert manager._connected
            session = manager.get_session()
            assert session is not None
            session.close()
        
        assert not manager._connected
    
    def test_get_database_type(self, manager):
        """Test getting database type"""
        assert manager.get_database_type() == DatabaseType.SQLITE


class TestDatabaseIntegration:
    """Integration tests for database operations"""
    
    def test_full_workflow(self):
        """Test complete database workflow"""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            sqlite_path=":memory:"
        )
        
        manager = DatabaseManager(config)
        manager.adapter.Base = Base
        
        # Connect
        manager.connect()
        
        # Create tables
        manager.create_tables()
        
        # Insert data
        session = manager.get_session()
        test_obj = TestModel(name="test", value=123.45)
        session.add(test_obj)
        session.commit()
        
        # Query data
        result = session.query(TestModel).filter_by(name="test").first()
        assert result is not None
        assert result.name == "test"
        assert result.value == 123.45
        
        # Update data
        result.value = 456.78
        session.commit()
        
        # Verify update
        updated = session.query(TestModel).filter_by(name="test").first()
        assert updated.value == 456.78
        
        # Delete data
        session.delete(updated)
        session.commit()
        
        # Verify deletion
        deleted = session.query(TestModel).filter_by(name="test").first()
        assert deleted is None
        
        session.close()
        manager.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
