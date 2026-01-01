"""
Tests for State Management System
"""

import pytest
import streamlit as st
from theming.state_manager import (
    ThemeStateManager,
    SessionStateBackend,
    LocalStorageBackend,
    DatabaseBackend,
    StateBackend
)
import tempfile
import os
from pathlib import Path


class TestSessionStateBackend:
    """Tests for SessionStateBackend"""
    
    def setup_method(self):
        """Setup for each test"""
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        self.backend = SessionStateBackend()
    
    def test_save(self):
        """Test saving theme preference"""
        result = self.backend.save('user123', 'shadcn-dark')
        assert result == True
        
        # Verify it's in session state
        assert 'theme_preference_user123' in st.session_state
        data = st.session_state['theme_preference_user123']
        assert data['theme_name'] == 'shadcn-dark'
        assert data['backend'] == 'session'
    
    def test_load(self):
        """Test loading theme preference"""
        # Save first
        self.backend.save('user123', 'shadcn-dark')
        
        # Load
        theme = self.backend.load('user123')
        assert theme == 'shadcn-dark'
    
    def test_load_nonexistent(self):
        """Test loading non-existent preference"""
        theme = self.backend.load('nonexistent_user')
        assert theme is None
    
    def test_delete(self):
        """Test deleting theme preference"""
        # Save first
        self.backend.save('user123', 'shadcn-dark')
        
        # Delete
        result = self.backend.delete('user123')
        assert result == True
        
        # Verify it's gone
        assert 'theme_preference_user123' not in st.session_state
    
    def test_delete_nonexistent(self):
        """Test deleting non-existent preference"""
        result = self.backend.delete('nonexistent_user')
        assert result == False
    
    def test_exists(self):
        """Test checking existence"""
        # Should not exist initially
        assert self.backend.exists('user123') == False
        
        # Save
        self.backend.save('user123', 'shadcn-dark')
        
        # Should exist now
        assert self.backend.exists('user123') == True
        
        # Delete
        self.backend.delete('user123')
        
        # Should not exist anymore
        assert self.backend.exists('user123') == False


class TestLocalStorageBackend:
    """Tests for LocalStorageBackend"""
    
    def setup_method(self):
        """Setup for each test"""
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        self.backend = LocalStorageBackend()
    
    def test_save(self):
        """Test saving to local storage"""
        result = self.backend.save('user123', 'shadcn-dark')
        assert result == True
        
        # Verify it's in session state bridge
        assert 'user123' in st.session_state.ls_data
        assert st.session_state.ls_data['user123'] == 'shadcn-dark'
    
    def test_load(self):
        """Test loading from local storage"""
        # Save first
        self.backend.save('user123', 'shadcn-dark')
        
        # Load
        theme = self.backend.load('user123')
        assert theme == 'shadcn-dark'
    
    def test_delete(self):
        """Test deleting from local storage"""
        # Save first
        self.backend.save('user123', 'shadcn-dark')
        
        # Delete
        result = self.backend.delete('user123')
        assert result == True
        
        # Verify it's gone from bridge
        assert 'user123' not in st.session_state.ls_data
    
    def test_exists(self):
        """Test checking existence"""
        assert self.backend.exists('user123') == False
        
        self.backend.save('user123', 'shadcn-dark')
        assert self.backend.exists('user123') == True
        
        self.backend.delete('user123')
        assert self.backend.exists('user123') == False


class TestDatabaseBackend:
    """Tests for DatabaseBackend"""
    
    def setup_method(self):
        """Setup for each test"""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_preferences.db')
        self.backend = DatabaseBackend(self.db_path)
    
    def teardown_method(self):
        """Cleanup after each test"""
        # Remove temporary database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_save(self):
        """Test saving to database"""
        result = self.backend.save('user123', 'shadcn-dark')
        assert result == True
    
    def test_save_with_metadata(self):
        """Test saving with metadata"""
        metadata = {'device': 'desktop', 'browser': 'chrome'}
        result = self.backend.save('user123', 'shadcn-dark', metadata)
        assert result == True
    
    def test_load(self):
        """Test loading from database"""
        # Save first
        self.backend.save('user123', 'shadcn-dark')
        
        # Load
        theme = self.backend.load('user123')
        assert theme == 'shadcn-dark'
    
    def test_load_nonexistent(self):
        """Test loading non-existent preference"""
        theme = self.backend.load('nonexistent_user')
        assert theme is None
    
    def test_update(self):
        """Test updating existing preference"""
        # Save initial
        self.backend.save('user123', 'shadcn-dark')
        
        # Update
        self.backend.save('user123', 'shadcn-ocean')
        
        # Verify update
        theme = self.backend.load('user123')
        assert theme == 'shadcn-ocean'
    
    def test_delete(self):
        """Test deleting from database"""
        # Save first
        self.backend.save('user123', 'shadcn-dark')
        
        # Delete
        result = self.backend.delete('user123')
        assert result == True
        
        # Verify it's gone
        theme = self.backend.load('user123')
        assert theme is None
    
    def test_exists(self):
        """Test checking existence"""
        assert self.backend.exists('user123') == False
        
        self.backend.save('user123', 'shadcn-dark')
        assert self.backend.exists('user123') == True
        
        self.backend.delete('user123')
        assert self.backend.exists('user123') == False
    
    def test_get_all_preferences(self):
        """Test getting all preferences"""
        # Save multiple preferences
        self.backend.save('user1', 'shadcn-dark')
        self.backend.save('user2', 'shadcn-ocean')
        self.backend.save('user3', 'shadcn-forest')
        
        # Get all
        all_prefs = self.backend.get_all_preferences()
        
        assert len(all_prefs) == 3
        
        # Verify data
        user_ids = [p['user_id'] for p in all_prefs]
        assert 'user1' in user_ids
        assert 'user2' in user_ids
        assert 'user3' in user_ids


class TestThemeStateManager:
    """Tests for ThemeStateManager"""
    
    def setup_method(self):
        """Setup for each test"""
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_preferences.db')
        
        # Initialize manager with all backends
        self.manager = ThemeStateManager(
            backends=['session', 'local_storage', 'database'],
            db_path=self.db_path
        )
    
    def teardown_method(self):
        """Cleanup after each test"""
        # Remove temporary database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """Test manager initialization"""
        assert len(self.manager.backends) == 3
        assert 'session' in self.manager.backends
        assert 'local_storage' in self.manager.backends
        assert 'database' in self.manager.backends
    
    def test_save_theme_preference(self):
        """Test saving theme preference"""
        results = self.manager.save_theme_preference('user123', 'shadcn-dark')
        
        # All backends should succeed
        assert results['session'] == True
        assert results['local_storage'] == True
        assert results['database'] == True
    
    def test_save_to_specific_backends(self):
        """Test saving to specific backends"""
        results = self.manager.save_theme_preference(
            'user123',
            'shadcn-dark',
            backends=['session', 'database']
        )
        
        # Only specified backends should be in results
        assert 'session' in results
        assert 'database' in results
        assert 'local_storage' not in results
    
    def test_load_theme_preference(self):
        """Test loading theme preference"""
        # Save first
        self.manager.save_theme_preference('user123', 'shadcn-dark')
        
        # Load
        theme = self.manager.load_theme_preference('user123')
        assert theme == 'shadcn-dark'
    
    def test_load_with_priority(self):
        """Test loading with backend priority"""
        # Save different themes to different backends
        self.manager.backends['session'].save('user123', 'shadcn-dark')
        self.manager.backends['database'].save('user123', 'shadcn-ocean')
        
        # Load with session priority (should get shadcn-dark)
        theme = self.manager.load_theme_preference(
            'user123',
            backends=['session', 'database']
        )
        assert theme == 'shadcn-dark'
        
        # Load with database priority (should get shadcn-ocean)
        theme = self.manager.load_theme_preference(
            'user123',
            backends=['database', 'session']
        )
        assert theme == 'shadcn-ocean'
    
    def test_load_nonexistent(self):
        """Test loading non-existent preference"""
        theme = self.manager.load_theme_preference('nonexistent_user')
        assert theme is None
    
    def test_delete_theme_preference(self):
        """Test deleting theme preference"""
        # Save first
        self.manager.save_theme_preference('user123', 'shadcn-dark')
        
        # Delete
        results = self.manager.delete_theme_preference('user123')
        
        # All backends should succeed
        assert results['session'] == True
        assert results['local_storage'] == True
        assert results['database'] == True
        
        # Verify it's gone
        theme = self.manager.load_theme_preference('user123')
        assert theme is None
    
    def test_sync_across_backends(self):
        """Test syncing across backends"""
        # Save to database only
        self.manager.backends['database'].save('user123', 'shadcn-dark')
        
        # Sync from database to other backends
        results = self.manager.sync_across_backends('user123', 'database')
        
        # Other backends should now have the theme
        assert self.manager.backends['session'].load('user123') == 'shadcn-dark'
        assert self.manager.backends['local_storage'].load('user123') == 'shadcn-dark'
    
    def test_recover_state(self):
        """Test state recovery"""
        # Save to database (most persistent)
        self.manager.backends['database'].save('user123', 'shadcn-dark')
        
        # Clear session state
        self.manager.backends['session'].delete('user123')
        
        # Recover
        recovered = self.manager.recover_state('user123')
        assert recovered == 'shadcn-dark'
        
        # Should also sync to other backends
        assert self.manager.backends['session'].load('user123') == 'shadcn-dark'
    
    def test_recover_state_no_data(self):
        """Test state recovery with no data"""
        recovered = self.manager.recover_state('nonexistent_user')
        assert recovered is None
    
    def test_get_backend_status(self):
        """Test getting backend status"""
        status = self.manager.get_backend_status()
        
        assert len(status) == 3
        assert 'session' in status
        assert 'local_storage' in status
        assert 'database' in status
        
        # All should be available
        for backend_name, info in status.items():
            assert info['available'] == True
            assert 'type' in info


class TestIntegration:
    """Integration tests"""
    
    def setup_method(self):
        """Setup for each test"""
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_preferences.db')
        
        self.manager = ThemeStateManager(
            backends=['session', 'local_storage', 'database'],
            db_path=self.db_path
        )
    
    def teardown_method(self):
        """Cleanup after each test"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_full_workflow(self):
        """Test complete workflow"""
        user_id = 'test_user'
        
        # 1. Save theme
        results = self.manager.save_theme_preference(user_id, 'shadcn-dark')
        assert all(results.values())
        
        # 2. Load theme
        theme = self.manager.load_theme_preference(user_id)
        assert theme == 'shadcn-dark'
        
        # 3. Update theme
        results = self.manager.save_theme_preference(user_id, 'shadcn-ocean')
        assert all(results.values())
        
        # 4. Verify update
        theme = self.manager.load_theme_preference(user_id)
        assert theme == 'shadcn-ocean'
        
        # 5. Delete theme
        results = self.manager.delete_theme_preference(user_id)
        assert all(results.values())
        
        # 6. Verify deletion
        theme = self.manager.load_theme_preference(user_id)
        assert theme is None
    
    def test_multi_user(self):
        """Test multiple users"""
        # Save themes for multiple users
        self.manager.save_theme_preference('user1', 'shadcn-dark')
        self.manager.save_theme_preference('user2', 'shadcn-ocean')
        self.manager.save_theme_preference('user3', 'shadcn-forest')
        
        # Verify each user has correct theme
        assert self.manager.load_theme_preference('user1') == 'shadcn-dark'
        assert self.manager.load_theme_preference('user2') == 'shadcn-ocean'
        assert self.manager.load_theme_preference('user3') == 'shadcn-forest'
    
    def test_backend_failure_fallback(self):
        """Test fallback when backend fails"""
        # Save to all backends
        self.manager.save_theme_preference('user123', 'shadcn-dark')
        
        # Simulate session backend failure by clearing it
        self.manager.backends['session'].delete('user123')
        
        # Should still load from other backends
        theme = self.manager.load_theme_preference('user123')
        assert theme == 'shadcn-dark'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
