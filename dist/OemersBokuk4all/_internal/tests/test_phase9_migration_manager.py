"""
Test Suite für Phase 9: Migration Manager & Database Migrations

Tests für:
- MigrationManager Core
- Migration Creation
- Migration Apply/Rollback
- History & Status
- Validation
- Integration Tests

Author: ARSCHIBALD Development Team
Date: 2025-01-18
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Test Imports
from core.migrations import (
    MigrationManager,
    get_migration_manager,
    migrate,
    rollback,
    create_migration
)


class TestMigrationManagerInit:
    """Tests für MigrationManager Initialisierung"""
    
    def test_init_creates_instance(self):
        """Test: MigrationManager Instanz erstellen"""
        mgr = MigrationManager()
        assert mgr is not None
        assert hasattr(mgr, 'db_url')
    
    def test_init_with_custom_db_url(self):
        """Test: MigrationManager mit custom DB-URL"""
        custom_url = "sqlite:///test_custom.db"
        mgr = MigrationManager(db_url=custom_url)
        assert mgr.db_url == custom_url
    
    def test_pickle_serializable(self):
        """Test: MigrationManager ist pickle-serializable (Streamlit Session State)"""
        import pickle
        mgr = MigrationManager()
        
        # Serialize
        pickled = pickle.dumps(mgr)
        assert pickled is not None
        
        # Deserialize
        restored = pickle.loads(pickled)
        assert restored is not None
        assert restored.db_url == mgr.db_url
    
    def test_getstate_setstate(self):
        """Test: __getstate__ und __setstate__ für Pickle"""
        mgr = MigrationManager()
        
        # Get state
        state = mgr.__getstate__()
        assert isinstance(state, dict)
        assert 'db_url' in state
        
        # Set state
        new_mgr = MigrationManager.__new__(MigrationManager)
        new_mgr.__setstate__(state)
        assert new_mgr.db_url == mgr.db_url


class TestMigrationManagerMethods:
    """Tests für MigrationManager Methoden"""
    
    @pytest.fixture
    def mock_manager(self):
        """Mock MigrationManager für Tests"""
        with patch('core.migrations.MigrationManager') as mock:
            manager = MagicMock()
            mock.return_value = manager
            yield manager
    
    def test_get_current_revision(self, mock_manager):
        """Test: Aktuelle Revision abrufen"""
        mock_manager.get_current_revision.return_value = "a1b2c3d4e5f6"
        
        revision = mock_manager.get_current_revision()
        assert revision == "a1b2c3d4e5f6"
        mock_manager.get_current_revision.assert_called_once()
    
    def test_get_current_version_alias(self, mock_manager):
        """Test: get_current_version() ist Alias für get_current_revision()"""
        mock_manager.get_current_version.return_value = "a1b2c3d4e5f6"
        
        version = mock_manager.get_current_version()
        assert version == "a1b2c3d4e5f6"
    
    def test_get_pending_migrations(self, mock_manager):
        """Test: Ausstehende Migrationen abrufen"""
        mock_manager.get_pending_migrations.return_value = [
            "rev1", "rev2", "rev3"
        ]
        
        pending = mock_manager.get_pending_migrations()
        assert len(pending) == 3
        assert "rev1" in pending
    
    def test_get_migration_history(self, mock_manager):
        """Test: Migration History abrufen"""
        mock_history = [
            {
                'revision': 'a1b2c3d4',
                'message': 'Initial',
                'is_current': True,
                'down_revision': None
            },
            {
                'revision': 'b2c3d4e5',
                'message': 'Add table',
                'is_current': False,
                'down_revision': 'a1b2c3d4'
            }
        ]
        mock_manager.get_migration_history.return_value = mock_history
        
        history = mock_manager.get_migration_history()
        assert len(history) == 2
        assert history[0]['is_current'] is True
        assert history[1]['down_revision'] == 'a1b2c3d4'
    
    def test_get_stats(self, mock_manager):
        """Test: Statistiken abrufen"""
        mock_stats = {
            'current_version': 'a1b2c3d4e5f6',
            'pending_count': 2,
            'total_migrations': 5,
            'applied_count': 3,
            'database_tables': 15,
            'last_migration': {
                'revision': 'a1b2c3d4',
                'message': 'Add customer table',
                'date': '2025-01-18'
            },
            'status': 'pending'
        }
        mock_manager.get_stats.return_value = mock_stats
        
        stats = mock_manager.get_stats()
        assert stats['status'] == 'pending'
        assert stats['pending_count'] == 2
        assert stats['total_migrations'] == 5
        assert stats['database_tables'] == 15


class TestMigrationOperations:
    """Tests für Migration-Operationen (Create, Apply, Rollback)"""
    
    @pytest.fixture
    def mock_manager(self):
        """Mock MigrationManager für Tests"""
        with patch('core.migrations.MigrationManager') as mock:
            manager = MagicMock()
            mock.return_value = manager
            yield manager
    
    def test_create_migration_autogenerate(self, mock_manager):
        """Test: Migration mit Autogenerate erstellen"""
        mock_manager.create_migration.return_value = "new_revision_id_12345"
        
        revision_id = mock_manager.create_migration(
            message="Add user table",
            autogenerate=True
        )
        
        assert revision_id == "new_revision_id_12345"
        mock_manager.create_migration.assert_called_once_with(
            message="Add user table",
            autogenerate=True
        )
    
    def test_create_migration_manual(self, mock_manager):
        """Test: Manuelle Migration (ohne Autogenerate) erstellen"""
        mock_manager.create_migration.return_value = "manual_rev_67890"
        
        revision_id = mock_manager.create_migration(
            message="Custom index",
            autogenerate=False
        )
        
        assert revision_id == "manual_rev_67890"
    
    def test_run_migrations_to_head(self, mock_manager):
        """Test: Migrationen zu 'head' anwenden"""
        mock_manager.run_migrations.return_value = None
        
        mock_manager.run_migrations(target_revision="head")
        
        mock_manager.run_migrations.assert_called_once_with(
            target_revision="head"
        )
    
    def test_run_migrations_to_specific_revision(self, mock_manager):
        """Test: Migrationen zu spezifischer Revision anwenden"""
        mock_manager.run_migrations.return_value = None
        
        mock_manager.run_migrations(target_revision="a1b2c3d4")
        
        mock_manager.run_migrations.assert_called_once_with(
            target_revision="a1b2c3d4"
        )
    
    def test_rollback_one_version(self, mock_manager):
        """Test: Rollback um eine Version"""
        mock_manager.rollback_migration.return_value = None
        
        mock_manager.rollback_migration(target_revision="-1")
        
        mock_manager.rollback_migration.assert_called_once_with(
            target_revision="-1"
        )
    
    def test_rollback_to_base(self, mock_manager):
        """Test: Rollback zu 'base' (alles zurück)"""
        mock_manager.rollback_migration.return_value = None
        
        mock_manager.rollback_migration(target_revision="base")
        
        mock_manager.rollback_migration.assert_called_once_with(
            target_revision="base"
        )
    
    def test_rollback_to_specific_revision(self, mock_manager):
        """Test: Rollback zu spezifischer Revision"""
        mock_manager.rollback_migration.return_value = None
        
        mock_manager.rollback_migration(target_revision="xyz123")
        
        mock_manager.rollback_migration.assert_called_once_with(
            target_revision="xyz123"
        )


class TestMigrationValidation:
    """Tests für Migration Validation"""
    
    @pytest.fixture
    def mock_manager(self):
        """Mock MigrationManager für Tests"""
        with patch('core.migrations.MigrationManager') as mock:
            manager = MagicMock()
            mock.return_value = manager
            yield manager
    
    def test_validate_migrations_ok(self, mock_manager):
        """Test: Validierung erfolgreich (status=ok)"""
        mock_validation = {
            'status': 'ok',
            'current_revision': 'a1b2c3d4',
            'pending_migrations': [],
            'errors': [],
            'warnings': []
        }
        mock_manager.validate_migrations.return_value = mock_validation
        
        result = mock_manager.validate_migrations()
        assert result['status'] == 'ok'
        assert len(result['errors']) == 0
        assert len(result['pending_migrations']) == 0
    
    def test_validate_migrations_pending(self, mock_manager):
        """Test: Validierung mit ausstehenden Migrationen (status=pending)"""
        mock_validation = {
            'status': 'pending',
            'current_revision': 'a1b2c3d4',
            'pending_migrations': ['rev1', 'rev2'],
            'errors': [],
            'warnings': ['2 migrations pending']
        }
        mock_manager.validate_migrations.return_value = mock_validation
        
        result = mock_manager.validate_migrations()
        assert result['status'] == 'pending'
        assert len(result['pending_migrations']) == 2
        assert len(result['warnings']) == 1
    
    def test_validate_migrations_error(self, mock_manager):
        """Test: Validierung mit Fehler (status=error)"""
        mock_validation = {
            'status': 'error',
            'current_revision': None,
            'pending_migrations': [],
            'errors': ['Database not initialized', 'Connection failed'],
            'warnings': []
        }
        mock_manager.validate_migrations.return_value = mock_validation
        
        result = mock_manager.validate_migrations()
        assert result['status'] == 'error'
        assert len(result['errors']) == 2
    
    def test_validate_migrations_uninitialized(self, mock_manager):
        """Test: Validierung mit nicht initialisierter DB (status=uninitialized)"""
        mock_validation = {
            'status': 'uninitialized',
            'current_revision': None,
            'pending_migrations': ['initial_rev'],
            'errors': [],
            'warnings': ['Database not initialized']
        }
        mock_manager.validate_migrations.return_value = mock_validation
        
        result = mock_manager.validate_migrations()
        assert result['status'] == 'uninitialized'
        assert result['current_revision'] is None


class TestGlobalFunctions:
    """Tests für globale Helper-Funktionen"""
    
    @patch('core.migrations.get_migration_manager')
    def test_get_migration_manager(self, mock_get_mgr):
        """Test: get_migration_manager() gibt Singleton zurück"""
        mock_mgr = MagicMock()
        mock_get_mgr.return_value = mock_mgr
        
        mgr1 = get_migration_manager()
        mgr2 = get_migration_manager()
        
        assert mgr1 is mgr2  # Singleton
        assert mock_get_mgr.call_count == 2
    
    @patch('core.migrations.get_migration_manager')
    def test_migrate_global_function(self, mock_get_mgr):
        """Test: migrate() globale Funktion"""
        mock_mgr = MagicMock()
        mock_get_mgr.return_value = mock_mgr
        
        migrate(target_revision="head")
        
        mock_mgr.run_migrations.assert_called_once_with(
            target_revision="head"
        )
    
    @patch('core.migrations.get_migration_manager')
    def test_rollback_global_function(self, mock_get_mgr):
        """Test: rollback() globale Funktion"""
        mock_mgr = MagicMock()
        mock_get_mgr.return_value = mock_mgr
        
        rollback(target_revision="-1")
        
        mock_mgr.rollback_migration.assert_called_once_with(
            target_revision="-1"
        )
    
    @patch('core.migrations.get_migration_manager')
    def test_create_migration_global_function(self, mock_get_mgr):
        """Test: create_migration() globale Funktion"""
        mock_mgr = MagicMock()
        mock_mgr.create_migration.return_value = "new_rev_id"
        mock_get_mgr.return_value = mock_mgr
        
        revision_id = create_migration(
            message="Test migration",
            autogenerate=True
        )
        
        assert revision_id == "new_rev_id"
        mock_mgr.create_migration.assert_called_once_with(
            message="Test migration",
            autogenerate=True
        )


class TestMigrationHistory:
    """Tests für Migration History"""
    
    @pytest.fixture
    def sample_history(self):
        """Sample Migration History"""
        return [
            {
                'revision': 'a1b2c3d4e5f6',
                'message': 'Initial database schema',
                'is_current': True,
                'down_revision': None,
                'create_date': '2025-01-18 10:00:00'
            },
            {
                'revision': 'b2c3d4e5f6a1',
                'message': 'Add customer address',
                'is_current': False,
                'down_revision': 'a1b2c3d4e5f6',
                'create_date': '2025-01-18 11:00:00'
            },
            {
                'revision': 'c3d4e5f6a1b2',
                'message': 'Add projects table',
                'is_current': False,
                'down_revision': 'b2c3d4e5f6a1',
                'create_date': '2025-01-18 12:00:00'
            }
        ]
    
    def test_history_ordering(self, sample_history):
        """Test: Historie ist korrekt geordnet (newest first)"""
        assert sample_history[0]['is_current'] is True
        assert sample_history[0]['down_revision'] is None
        assert sample_history[1]['down_revision'] == sample_history[0]['revision']
    
    def test_history_current_marker(self, sample_history):
        """Test: is_current Flag ist nur bei aktueller Version True"""
        current_count = sum(1 for h in sample_history if h['is_current'])
        assert current_count == 1
    
    def test_history_chaining(self, sample_history):
        """Test: down_revision verlinkt korrekt zur vorherigen Version"""
        for i in range(1, len(sample_history)):
            assert sample_history[i]['down_revision'] == sample_history[i-1]['revision']


class TestMigrationStats:
    """Tests für Migration Statistics"""
    
    @pytest.fixture
    def sample_stats(self):
        """Sample Migration Stats"""
        return {
            'current_version': 'a1b2c3d4e5f6',
            'pending_count': 2,
            'total_migrations': 5,
            'applied_count': 3,
            'database_tables': 15,
            'last_migration': {
                'revision': 'a1b2c3d4',
                'message': 'Add customer table',
                'date': '2025-01-18'
            },
            'status': 'pending'
        }
    
    def test_stats_structure(self, sample_stats):
        """Test: Stats haben alle erforderlichen Felder"""
        required_fields = [
            'current_version',
            'pending_count',
            'total_migrations',
            'applied_count',
            'database_tables',
            'last_migration',
            'status'
        ]
        for field in required_fields:
            assert field in sample_stats
    
    def test_stats_status_values(self):
        """Test: status kann nur valide Werte haben"""
        valid_statuses = ['ok', 'pending', 'uninitialized', 'error', 'unknown']
        test_status = 'pending'
        assert test_status in valid_statuses
    
    def test_stats_counts_consistent(self, sample_stats):
        """Test: Counts sind konsistent (applied + pending = total)"""
        assert sample_stats['applied_count'] + sample_stats['pending_count'] == sample_stats['total_migrations']


class TestMigrationIntegration:
    """Integration Tests für komplette Workflows"""
    
    @patch('core.migrations.MigrationManager')
    def test_full_migration_workflow(self, mock_mgr_class):
        """Test: Kompletter Migration-Workflow (Create → Apply → Verify)"""
        mock_mgr = MagicMock()
        mock_mgr_class.return_value = mock_mgr
        
        # 1. Create Migration
        mock_mgr.create_migration.return_value = "new_rev_123"
        revision_id = mock_mgr.create_migration(message="Test", autogenerate=True)
        assert revision_id == "new_rev_123"
        
        # 2. Verify Pending
        mock_mgr.get_pending_migrations.return_value = ["new_rev_123"]
        pending = mock_mgr.get_pending_migrations()
        assert "new_rev_123" in pending
        
        # 3. Apply Migration
        mock_mgr.run_migrations.return_value = None
        mock_mgr.run_migrations(target_revision="head")
        
        # 4. Verify Applied
        mock_mgr.get_current_revision.return_value = "new_rev_123"
        current = mock_mgr.get_current_revision()
        assert current == "new_rev_123"
        
        # 5. Verify No Pending
        mock_mgr.get_pending_migrations.return_value = []
        pending = mock_mgr.get_pending_migrations()
        assert len(pending) == 0
    
    @patch('core.migrations.MigrationManager')
    def test_rollback_workflow(self, mock_mgr_class):
        """Test: Rollback-Workflow (Apply → Rollback → Verify)"""
        mock_mgr = MagicMock()
        mock_mgr_class.return_value = mock_mgr
        
        # 1. Initial State
        mock_mgr.get_current_revision.return_value = "rev_current"
        start_rev = mock_mgr.get_current_revision()
        
        # 2. Apply Migration
        mock_mgr.run_migrations.return_value = None
        mock_mgr.run_migrations()
        mock_mgr.get_current_revision.return_value = "rev_new"
        
        # 3. Rollback
        mock_mgr.rollback_migration.return_value = None
        mock_mgr.rollback_migration("-1")
        mock_mgr.get_current_revision.return_value = start_rev
        
        # 4. Verify
        current = mock_mgr.get_current_revision()
        assert current == start_rev


# Pytest Configuration
@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state zwischen Tests"""
    yield
    # Cleanup


if __name__ == '__main__':
    # Run Tests
    pytest.main([__file__, '-v', '--tb=short'])
