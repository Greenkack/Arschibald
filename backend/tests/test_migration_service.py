"""
Tests for Migration Service
Task 235: Data Migration Implementation

Comprehensive tests for:
- SQLite to new database migration
- Data validation during migration
- Migration progress tracking
- Rollback functionality
- Backup before migration
"""

import pytest
import os
import sqlite3
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

from backend.services.migration_service import (
    MigrationService,
    MigrationStatus,
    MigrationProgress,
    MigrationReport,
    DataType,
    DataValidator
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def source_db(temp_dir):
    """Create source database with test data"""
    db_path = os.path.join(temp_dir, "source.db")
    conn = sqlite3.connect(db_path)
    
    # Create user_settings table
    conn.execute("""
        CREATE TABLE user_settings (
            user_id TEXT PRIMARY KEY,
            theme TEXT,
            language TEXT,
            notifications INTEGER
        )
    """)
    conn.execute(
        "INSERT INTO user_settings VALUES (?, ?, ?, ?)",
        ("user1", "dark", "de", 1)
    )
    conn.execute(
        "INSERT INTO user_settings VALUES (?, ?, ?, ?)",
        ("user2", "light", "en", 0)
    )
    
    # Create projects table
    conn.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            project_id TEXT,
            name TEXT,
            description TEXT,
            created_at TEXT
        )
    """)
    conn.execute(
        "INSERT INTO projects VALUES (?, ?, ?, ?, ?)",
        (1, "proj1", "Solar Project 1", "Test project", datetime.now().isoformat())
    )
    conn.execute(
        "INSERT INTO projects VALUES (?, ?, ?, ?, ?)",
        (2, "proj2", "Heat Pump Project", "Another test", datetime.now().isoformat())
    )
    
    # Create customers table
    conn.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            customer_id TEXT,
            name TEXT,
            email TEXT,
            phone TEXT
        )
    """)
    conn.execute(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?)",
        (1, "cust1", "Max Mustermann", "max@example.com", "+49123456789")
    )
    
    # Create products table
    conn.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            product_id TEXT,
            name TEXT,
            category TEXT,
            price REAL
        )
    """)
    conn.execute(
        "INSERT INTO products VALUES (?, ?, ?, ?, ?)",
        (1, "prod1", "Solar Panel 400W", "pv_modules", 299.99)
    )
    conn.execute(
        "INSERT INTO products VALUES (?, ?, ?, ?, ?)",
        (2, "prod2", "Inverter 10kW", "inverters", 1499.99)
    )
    
    # Create price_matrices table
    conn.execute("""
        CREATE TABLE price_matrices (
            id INTEGER PRIMARY KEY,
            matrix_id TEXT,
            name TEXT,
            version TEXT,
            data TEXT
        )
    """)
    conn.execute(
        "INSERT INTO price_matrices VALUES (?, ?, ?, ?, ?)",
        (1, "matrix1", "Standard Prices", "1.0", '{"modules": [100, 200, 300]}')
    )
    
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def target_db(temp_dir):
    """Create empty target database"""
    db_path = os.path.join(temp_dir, "target.db")
    return db_path


@pytest.fixture
def backup_dir(temp_dir):
    """Create backup directory"""
    backup_path = os.path.join(temp_dir, "backups")
    os.makedirs(backup_path, exist_ok=True)
    return backup_path


class TestDataValidator:
    """Tests for DataValidator class"""
    
    def test_validate_user_settings_valid(self):
        """Test validation of valid user settings"""
        data = {"user_id": "user1", "theme": "dark"}
        errors = DataValidator.validate_user_settings(data)
        assert len(errors) == 0
    
    def test_validate_user_settings_missing_id(self):
        """Test validation of user settings without user_id"""
        data = {"theme": "dark"}
        errors = DataValidator.validate_user_settings(data)
        assert len(errors) == 1
        assert "user_id" in errors[0]
    
    def test_validate_project_valid(self):
        """Test validation of valid project"""
        data = {"project_id": "proj1", "name": "Test Project"}
        errors = DataValidator.validate_project(data)
        assert len(errors) == 0
    
    def test_validate_project_missing_fields(self):
        """Test validation of project with missing fields"""
        data = {"description": "Test"}
        errors = DataValidator.validate_project(data)
        assert len(errors) == 2
    
    def test_validate_customer_valid(self):
        """Test validation of valid customer"""
        data = {"customer_id": "cust1", "name": "Test Customer"}
        errors = DataValidator.validate_customer(data)
        assert len(errors) == 0
    
    def test_validate_customer_with_id(self):
        """Test validation of customer with id instead of customer_id"""
        data = {"id": 1, "name": "Test Customer"}
        errors = DataValidator.validate_customer(data)
        assert len(errors) == 0
    
    def test_validate_product_valid(self):
        """Test validation of valid product"""
        data = {"product_id": "prod1", "name": "Test Product"}
        errors = DataValidator.validate_product(data)
        assert len(errors) == 0
    
    def test_validate_price_matrix_valid(self):
        """Test validation of valid price matrix"""
        data = {"matrix_id": "matrix1", "name": "Test Matrix"}
        errors = DataValidator.validate_price_matrix(data)
        assert len(errors) == 0


class TestMigrationService:
    """Tests for MigrationService class"""
    
    def test_init(self, source_db, target_db, backup_dir):
        """Test service initialization"""
        service = MigrationService(source_db, target_db, backup_dir)
        assert service.source_db_path == source_db
        assert service.target_db_path == target_db
        assert service.backup_dir == backup_dir
    
    def test_generate_migration_id(self, source_db, target_db, backup_dir):
        """Test migration ID generation"""
        service = MigrationService(source_db, target_db, backup_dir)
        migration_id = service.generate_migration_id()
        
        assert migration_id.startswith("migration_")
        assert len(migration_id) > 20
    
    def test_create_backup(self, source_db, target_db, backup_dir):
        """Test backup creation"""
        service = MigrationService(source_db, target_db, backup_dir)
        backup_path = service.create_backup()
        
        assert os.path.exists(backup_path)
        assert backup_path.startswith(backup_dir)
        assert backup_path.endswith(".db")
    
    def test_rollback(self, source_db, target_db, backup_dir):
        """Test rollback functionality"""
        service = MigrationService(source_db, target_db, backup_dir)
        backup_path = service.create_backup()
        
        # Modify source database
        conn = sqlite3.connect(source_db)
        conn.execute("DELETE FROM user_settings")
        conn.commit()
        conn.close()
        
        # Verify deletion
        conn = sqlite3.connect(source_db)
        cursor = conn.execute("SELECT COUNT(*) FROM user_settings")
        assert cursor.fetchone()[0] == 0
        conn.close()
        
        # Rollback
        success = service.rollback(backup_path)
        assert success
        
        # Verify rollback
        conn = sqlite3.connect(source_db)
        cursor = conn.execute("SELECT COUNT(*) FROM user_settings")
        assert cursor.fetchone()[0] == 2
        conn.close()
    
    def test_migrate_user_settings(self, source_db, target_db, backup_dir):
        """Test user settings migration"""
        service = MigrationService(source_db, target_db, backup_dir)
        progress = service.migrate_user_settings()
        
        assert progress.status == MigrationStatus.COMPLETED
        assert progress.total_records == 2
        assert progress.migrated_records == 2
        assert progress.failed_records == 0
    
    def test_migrate_projects(self, source_db, target_db, backup_dir):
        """Test projects migration"""
        service = MigrationService(source_db, target_db, backup_dir)
        progress = service.migrate_projects()
        
        assert progress.status == MigrationStatus.COMPLETED
        assert progress.total_records == 2
        assert progress.migrated_records == 2
        assert progress.failed_records == 0
    
    def test_migrate_customers(self, source_db, target_db, backup_dir):
        """Test customers migration"""
        service = MigrationService(source_db, target_db, backup_dir)
        progress = service.migrate_customers()
        
        assert progress.status == MigrationStatus.COMPLETED
        assert progress.total_records == 1
        assert progress.migrated_records == 1
        assert progress.failed_records == 0
    
    def test_migrate_products(self, source_db, target_db, backup_dir):
        """Test products migration"""
        service = MigrationService(source_db, target_db, backup_dir)
        progress = service.migrate_products()
        
        assert progress.status == MigrationStatus.COMPLETED
        assert progress.total_records == 2
        assert progress.migrated_records == 2
        assert progress.failed_records == 0
    
    def test_migrate_price_matrices(self, source_db, target_db, backup_dir):
        """Test price matrices migration"""
        service = MigrationService(source_db, target_db, backup_dir)
        progress = service.migrate_price_matrices()
        
        assert progress.status == MigrationStatus.COMPLETED
        assert progress.total_records == 1
        assert progress.migrated_records == 1
        assert progress.failed_records == 0
    
    def test_run_full_migration(self, source_db, target_db, backup_dir):
        """Test full migration"""
        service = MigrationService(source_db, target_db, backup_dir)
        report = service.run_full_migration()
        
        assert report.overall_status == MigrationStatus.COMPLETED
        assert report.total_records == 8  # 2+2+1+2+1
        assert report.migrated_records == 8
        assert report.failed_records == 0
        assert report.backup_path is not None
        assert os.path.exists(report.backup_path)
    
    def test_generate_report(self, source_db, target_db, backup_dir):
        """Test report generation"""
        service = MigrationService(source_db, target_db, backup_dir)
        service.run_full_migration()
        report = service.generate_report()
        
        assert "migration_id" in report
        assert "source_db" in report
        assert "target_db" in report
        assert "overall_status" in report
        assert "progress" in report
    
    def test_save_report(self, source_db, target_db, backup_dir, temp_dir):
        """Test saving report to file"""
        service = MigrationService(source_db, target_db, backup_dir)
        service.run_full_migration()
        
        report_path = os.path.join(temp_dir, "migration_report.json")
        service.save_report(report_path)
        
        assert os.path.exists(report_path)
    
    def test_progress_callback(self, source_db, target_db, backup_dir):
        """Test progress callback functionality"""
        service = MigrationService(source_db, target_db, backup_dir)
        
        progress_updates = []
        
        def callback(progress: MigrationProgress):
            progress_updates.append(progress.migrated_records)
        
        service.add_progress_callback(callback)
        service.migrate_user_settings()
        
        assert len(progress_updates) > 0
    
    def test_migration_with_empty_tables(self, temp_dir):
        """Test migration with empty source tables"""
        source_db = os.path.join(temp_dir, "empty_source.db")
        target_db = os.path.join(temp_dir, "empty_target.db")
        backup_dir = os.path.join(temp_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create empty source database
        conn = sqlite3.connect(source_db)
        conn.execute("CREATE TABLE user_settings (user_id TEXT PRIMARY KEY)")
        conn.commit()
        conn.close()
        
        service = MigrationService(source_db, target_db, backup_dir)
        progress = service.migrate_user_settings()
        
        assert progress.status == MigrationStatus.COMPLETED
        assert progress.total_records == 0
        assert progress.migrated_records == 0
    
    def test_migration_preserves_data_integrity(self, source_db, target_db, backup_dir):
        """Test that migration preserves data integrity"""
        service = MigrationService(source_db, target_db, backup_dir)
        service.run_full_migration()
        
        # Verify data in target database
        conn = sqlite3.connect(target_db)
        conn.row_factory = sqlite3.Row
        
        # Check user_settings
        cursor = conn.execute("SELECT * FROM user_settings WHERE user_id = 'user1'")
        row = cursor.fetchone()
        assert row is not None
        assert dict(row)["theme"] == "dark"
        assert dict(row)["language"] == "de"
        
        # Check projects
        cursor = conn.execute("SELECT * FROM projects WHERE project_id = 'proj1'")
        row = cursor.fetchone()
        assert row is not None
        assert dict(row)["name"] == "Solar Project 1"
        
        # Check customers
        cursor = conn.execute("SELECT * FROM customers WHERE customer_id = 'cust1'")
        row = cursor.fetchone()
        assert row is not None
        assert dict(row)["name"] == "Max Mustermann"
        
        # Check products
        cursor = conn.execute("SELECT * FROM products WHERE product_id = 'prod1'")
        row = cursor.fetchone()
        assert row is not None
        assert dict(row)["price"] == 299.99
        
        conn.close()


class TestMigrationProgress:
    """Tests for MigrationProgress dataclass"""
    
    def test_progress_percent_calculation(self):
        """Test progress percentage calculation"""
        progress = MigrationProgress(
            data_type="test",
            total_records=100,
            migrated_records=50
        )
        assert progress.progress_percent == 50.0
    
    def test_progress_percent_zero_total(self):
        """Test progress percentage with zero total"""
        progress = MigrationProgress(
            data_type="test",
            total_records=0,
            migrated_records=0
        )
        assert progress.progress_percent == 0.0


class TestMigrationReport:
    """Tests for MigrationReport dataclass"""
    
    def test_report_to_dict(self):
        """Test report conversion to dictionary"""
        report = MigrationReport(
            migration_id="test_123",
            source_db="/path/to/source.db",
            target_db="/path/to/target.db",
            started_at=datetime.now().isoformat()
        )
        
        report_dict = report.to_dict()
        
        assert report_dict["migration_id"] == "test_123"
        assert report_dict["source_db"] == "/path/to/source.db"
        assert report_dict["target_db"] == "/path/to/target.db"
        assert "started_at" in report_dict


class TestEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_nonexistent_source_db(self, temp_dir):
        """Test handling of nonexistent source database"""
        source_db = os.path.join(temp_dir, "nonexistent.db")
        target_db = os.path.join(temp_dir, "target.db")
        backup_dir = os.path.join(temp_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        service = MigrationService(source_db, target_db, backup_dir)
        
        # Backup should return empty string
        backup_path = service.create_backup()
        assert backup_path == ""
    
    def test_rollback_nonexistent_backup(self, source_db, target_db, backup_dir):
        """Test rollback with nonexistent backup"""
        service = MigrationService(source_db, target_db, backup_dir)
        
        success = service.rollback("/nonexistent/backup.db")
        assert not success
    
    def test_migration_with_special_characters(self, temp_dir):
        """Test migration with special characters in data"""
        source_db = os.path.join(temp_dir, "special_source.db")
        target_db = os.path.join(temp_dir, "special_target.db")
        backup_dir = os.path.join(temp_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create source with special characters
        conn = sqlite3.connect(source_db)
        conn.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                customer_id TEXT,
                name TEXT
            )
        """)
        conn.execute(
            "INSERT INTO customers VALUES (?, ?, ?)",
            (1, "cust1", "Müller & Söhne GmbH")
        )
        conn.commit()
        conn.close()
        
        service = MigrationService(source_db, target_db, backup_dir)
        progress = service.migrate_customers()
        
        assert progress.status == MigrationStatus.COMPLETED
        assert progress.migrated_records == 1
        
        # Verify special characters preserved
        conn = sqlite3.connect(target_db)
        cursor = conn.execute("SELECT name FROM customers WHERE customer_id = 'cust1'")
        row = cursor.fetchone()
        assert row[0] == "Müller & Söhne GmbH"
        conn.close()
    
    def test_migration_with_json_data(self, temp_dir):
        """Test migration with JSON data in columns"""
        source_db = os.path.join(temp_dir, "json_source.db")
        target_db = os.path.join(temp_dir, "json_target.db")
        backup_dir = os.path.join(temp_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create source with JSON data
        conn = sqlite3.connect(source_db)
        conn.execute("""
            CREATE TABLE price_matrices (
                id INTEGER PRIMARY KEY,
                matrix_id TEXT,
                data TEXT
            )
        """)
        json_data = '{"prices": [100, 200, 300], "currency": "EUR"}'
        conn.execute(
            "INSERT INTO price_matrices VALUES (?, ?, ?)",
            (1, "matrix1", json_data)
        )
        conn.commit()
        conn.close()
        
        service = MigrationService(source_db, target_db, backup_dir)
        progress = service.migrate_price_matrices()
        
        assert progress.status == MigrationStatus.COMPLETED
        
        # Verify JSON preserved
        conn = sqlite3.connect(target_db)
        cursor = conn.execute("SELECT data FROM price_matrices WHERE matrix_id = 'matrix1'")
        row = cursor.fetchone()
        assert row[0] == json_data
        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
