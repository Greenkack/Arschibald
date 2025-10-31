"""Tests for Session Recovery System"""

import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from .session import FormState, NavigationEntry, UserSession
from .session_recovery import (
    SessionRecoveryManager,
    clear_recovery_errors,
    get_recovery_manager,
    get_recovery_status,
    recover_session_after_refresh,
)


class TestSessionRecoveryManager:
    """Test SessionRecoveryManager class"""

    def test_create_recovery_manager(self):
        """Test creating recovery manager"""
        manager = SessionRecoveryManager()

        assert manager.recovery_attempts == 0
        assert manager.max_recovery_attempts == 3
        assert manager.validation_errors == {}

    def test_validate_form_data_required_fields(self):
        """Test form data validation with required fields"""
        manager = SessionRecoveryManager()

        schema = {
            'name': {'required': True, 'type': 'string'},
            'email': {'required': True, 'type': 'string'}
        }

        # Missing required field
        data = {'name': 'John'}
        errors = manager._validate_form_data(data, schema)

        assert 'email' in errors
        assert any('required' in err.lower() for err in errors['email'])

    def test_validate_form_data_type_validation(self):
        """Test form data type validation"""
        manager = SessionRecoveryManager()

        schema = {
            'age': {'type': 'number'},
            'active': {'type': 'boolean'}
        }

        # Wrong types
        data = {'age': 'not a number', 'active': 'not a boolean'}
        errors = manager._validate_form_data(data, schema)

        assert 'age' in errors
        assert 'active' in errors

    def test_validate_form_data_min_max_validation(self):
        """Test form data min/max validation"""
        manager = SessionRecoveryManager()

        schema = {
            'age': {'type': 'number', 'min': 18, 'max': 100}
        }

        # Below minimum
        data = {'age': 15}
        errors = manager._validate_form_data(data, schema)
        assert 'age' in errors

        # Above maximum
        data = {'age': 150}
        errors = manager._validate_form_data(data, schema)
        assert 'age' in errors

        # Valid
        data = {'age': 25}
        errors = manager._validate_form_data(data, schema)
        assert 'age' not in errors

    def test_validate_form_data_length_validation(self):
        """Test form data length validation"""
        manager = SessionRecoveryManager()

        schema = {
            'username': {'type': 'string', 'minLength': 3, 'maxLength': 20}
        }

        # Too short
        data = {'username': 'ab'}
        errors = manager._validate_form_data(data, schema)
        assert 'username' in errors

        # Too long
        data = {'username': 'a' * 25}
        errors = manager._validate_form_data(data, schema)
        assert 'username' in errors

        # Valid
        data = {'username': 'john_doe'}
        errors = manager._validate_form_data(data, schema)
        assert 'username' not in errors

    @patch('core.session_repository.SessionRepository')
    def test_recover_from_database_success(self, mock_repo_class):
        """Test successful session recovery from database"""
        manager = SessionRecoveryManager()

        # Mock repository
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        session_id = str(uuid.uuid4())
        session_data = {
            'session_id': session_id,
            'user_id': 'user123',
            'current_page': 'dashboard',
            'page_params': {'id': '456'},
            'navigation_history': [],
            'form_states': {},
            'dirty_forms': [],
            'form_snapshots': {},
            'cache_keys': [],
            'cache_dependencies': {},
            'roles': [],
            'permissions': [],
            'theme': 'auto',
            'language': 'en',
            'timezone': 'UTC',
            'preferences': {},
            'page_views': {},
            'interaction_count': 0,
            'session_start': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'version': 1
        }

        mock_repo.get_session.return_value = session_data

        # Recover session
        session = manager._recover_from_database(session_id)

        assert session is not None
        assert session.session_id == session_id
        assert session.user_id == 'user123'
        assert session.current_page == 'dashboard'

    @patch('core.session_repository.SessionRepository')
    def test_recover_from_database_not_found(self, mock_repo_class):
        """Test session recovery when session not found"""
        manager = SessionRecoveryManager()

        # Mock repository
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.get_session.return_value = None

        session_id = str(uuid.uuid4())

        # Recover session
        session = manager._recover_from_database(session_id)

        assert session is None

    def test_recover_and_validate_forms_with_valid_data(self):
        """Test form recovery with valid data"""
        manager = SessionRecoveryManager()

        # Create session with form data
        session = UserSession(session_id=str(uuid.uuid4()))
        form_state = FormState(
            form_id='contact_form',
            data={'name': 'John Doe', 'email': 'john@example.com'},
            validation_schema={
                'name': {'required': True, 'type': 'string'},
                'email': {'required': True, 'type': 'string'}
            }
        )
        session.form_states['contact_form'] = form_state

        # Recover and validate
        manager._recover_and_validate_forms(session)

        # Should have no validation errors
        assert len(manager.validation_errors) == 0

    def test_recover_and_validate_forms_with_invalid_data(self):
        """Test form recovery with invalid data"""
        manager = SessionRecoveryManager()

        # Create session with invalid form data
        session = UserSession(session_id=str(uuid.uuid4()))
        form_state = FormState(
            form_id='contact_form',
            data={'name': 'John Doe'},  # Missing required email
            validation_schema={
                'name': {'required': True, 'type': 'string'},
                'email': {'required': True, 'type': 'string'}
            }
        )
        session.form_states['contact_form'] = form_state

        # Recover and validate
        manager._recover_and_validate_forms(session)

        # Should have validation errors
        assert 'contact_form' in manager.validation_errors
        assert len(manager.validation_errors['contact_form']) > 0

    def test_recover_navigation_state(self):
        """Test navigation state recovery"""
        manager = SessionRecoveryManager()

        # Create session with navigation state
        session = UserSession(session_id=str(uuid.uuid4()))
        session.current_page = 'dashboard'
        session.page_params = {'filter': 'active', 'sort': 'date'}
        session.navigation_history = [
            NavigationEntry(
                page='home',
                params={},
                timestamp=datetime.now() - timedelta(minutes=5)
            ),
            NavigationEntry(
                page='dashboard',
                params={'filter': 'active'},
                timestamp=datetime.now()
            )
        ]

        # Recover navigation state (without Streamlit, should not raise error)
        manager._recover_navigation_state(session)

        # Should complete without errors
        assert True

    def test_recover_cache_keys(self):
        """Test cache key recovery"""
        manager = SessionRecoveryManager()

        # Create session with cache keys
        session = UserSession(session_id=str(uuid.uuid4()))
        session.cache_keys = {'key1', 'key2', 'key3'}
        session.cache_dependencies = {
            'key1': {'dep1', 'dep2'},
            'key2': {'dep3'}
        }

        # Recover cache keys (without Streamlit, should not raise error)
        manager._recover_cache_keys(session)

        # Should complete without errors
        assert True

    def test_get_recovery_status(self):
        """Test getting recovery status"""
        manager = SessionRecoveryManager()

        # Initial status
        status = manager.get_recovery_status()

        assert status['recovery_attempts'] == 0
        assert status['max_attempts'] == 3
        assert status['has_errors'] is False

        # Add validation errors
        manager.validation_errors = {'form1': ['error1']}

        status = manager.get_recovery_status()
        assert status['has_errors'] is True

    def test_clear_validation_errors(self):
        """Test clearing validation errors"""
        manager = SessionRecoveryManager()

        # Add errors
        manager.validation_errors = {'form1': ['error1'], 'form2': ['error2']}

        # Clear errors
        manager.clear_validation_errors()

        assert len(manager.validation_errors) == 0


class TestSessionRecoveryFunctions:
    """Test module-level recovery functions"""

    def test_get_recovery_manager(self):
        """Test getting global recovery manager"""
        manager1 = get_recovery_manager()
        manager2 = get_recovery_manager()

        # Should return same instance
        assert manager1 is manager2

    def test_get_recovery_status_function(self):
        """Test get_recovery_status function"""
        status = get_recovery_status()

        assert 'recovery_attempts' in status
        assert 'max_attempts' in status
        assert 'has_errors' in status

    def test_clear_recovery_errors_function(self):
        """Test clear_recovery_errors function"""
        manager = get_recovery_manager()
        manager.validation_errors = {'form1': ['error1']}

        clear_recovery_errors()

        assert len(manager.validation_errors) == 0


class TestSessionRecoveryIntegration:
    """Integration tests for session recovery"""

    @patch('core.session.bootstrap_session')
    def test_recover_session_after_refresh_no_session_id(
        self,
        mock_bootstrap
    ):
        """Test recovery when no session ID is available"""
        # Mock bootstrap to return new session
        new_session = UserSession(session_id=str(uuid.uuid4()))
        mock_bootstrap.return_value = new_session

        # Recover without session ID
        session = recover_session_after_refresh()

        # Should create new session
        mock_bootstrap.assert_called_once()

    @patch('core.session_repository.SessionRepository')
    def test_recover_session_after_refresh_with_session_id(
            self, mock_repo_class):
        """Test recovery with valid session ID"""
        # Mock repository
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        session_id = str(uuid.uuid4())
        session_data = {
            'session_id': session_id,
            'user_id': 'user123',
            'current_page': 'home',
            'page_params': {},
            'navigation_history': [],
            'form_states': {},
            'dirty_forms': [],
            'form_snapshots': {},
            'cache_keys': [],
            'cache_dependencies': {},
            'roles': [],
            'permissions': [],
            'theme': 'auto',
            'language': 'en',
            'timezone': 'UTC',
            'preferences': {},
            'page_views': {},
            'interaction_count': 0,
            'session_start': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'version': 1
        }

        mock_repo.get_session.return_value = session_data

        # Recover session
        session = recover_session_after_refresh(session_id=session_id)

        assert session is not None
        assert session.session_id == session_id

    @patch('core.session_repository.SessionRepository')
    def test_recover_session_with_form_validation(self, mock_repo_class):
        """Test recovery with form validation"""
        # Mock repository
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        session_id = str(uuid.uuid4())

        # Create session data with form that has validation errors
        form_state_data = {
            'form_id': 'test_form',
            'data': {'name': 'John'},  # Missing required email
            'errors': {},
            'warnings': {},
            'validation_schema': {
                'name': {'required': True, 'type': 'string'},
                'email': {'required': True, 'type': 'string'}
            },
            'snapshots': [],
            'current_snapshot_index': -1,
            'max_snapshots': 50,
            'is_dirty': False,
            'last_saved': None,
            'auto_save': True,
            'save_debounce_ms': 500,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'version': 1
        }

        session_data = {
            'session_id': session_id,
            'user_id': 'user123',
            'current_page': 'home',
            'page_params': {},
            'navigation_history': [],
            'form_states': {'test_form': form_state_data},
            'dirty_forms': [],
            'form_snapshots': {},
            'cache_keys': [],
            'cache_dependencies': {},
            'roles': [],
            'permissions': [],
            'theme': 'auto',
            'language': 'en',
            'timezone': 'UTC',
            'preferences': {},
            'page_views': {},
            'interaction_count': 0,
            'session_start': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'version': 1
        }

        mock_repo.get_session.return_value = session_data

        # Recover session with validation
        session = recover_session_after_refresh(
            session_id=session_id,
            validate_forms=True
        )

        assert session is not None

        # Check that validation errors were detected
        status = get_recovery_status()
        assert status['has_errors'] is True

    @patch('core.session_repository.SessionRepository')
    def test_recover_session_with_navigation_history(self, mock_repo_class):
        """Test recovery with navigation history"""
        # Mock repository
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        session_id = str(uuid.uuid4())

        # Create session data with navigation history
        nav_entry = {
            'page': 'dashboard',
            'params': {'filter': 'active'},
            'timestamp': datetime.now().isoformat()
        }

        session_data = {
            'session_id': session_id,
            'user_id': 'user123',
            'current_page': 'dashboard',
            'page_params': {'filter': 'active'},
            'navigation_history': [nav_entry],
            'form_states': {},
            'dirty_forms': [],
            'form_snapshots': {},
            'cache_keys': [],
            'cache_dependencies': {},
            'roles': [],
            'permissions': [],
            'theme': 'auto',
            'language': 'en',
            'timezone': 'UTC',
            'preferences': {},
            'page_views': {'dashboard': 5},
            'interaction_count': 10,
            'session_start': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'version': 1
        }

        mock_repo.get_session.return_value = session_data

        # Recover session
        session = recover_session_after_refresh(session_id=session_id)

        assert session is not None
        assert session.current_page == 'dashboard'
        assert session.page_params == {'filter': 'active'}
        assert len(session.navigation_history) == 1

    @patch('core.session_repository.SessionRepository')
    def test_recover_session_with_cache_keys(self, mock_repo_class):
        """Test recovery with cache keys"""
        # Mock repository
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        session_id = str(uuid.uuid4())

        # Create session data with cache keys
        session_data = {
            'session_id': session_id,
            'user_id': 'user123',
            'current_page': 'home',
            'page_params': {},
            'navigation_history': [],
            'form_states': {},
            'dirty_forms': [],
            'form_snapshots': {},
            'cache_keys': ['key1', 'key2', 'key3'],
            'cache_dependencies': {
                'key1': ['dep1', 'dep2'],
                'key2': ['dep3']
            },
            'roles': [],
            'permissions': [],
            'theme': 'auto',
            'language': 'en',
            'timezone': 'UTC',
            'preferences': {},
            'page_views': {},
            'interaction_count': 0,
            'session_start': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'version': 1
        }

        mock_repo.get_session.return_value = session_data

        # Recover session
        session = recover_session_after_refresh(session_id=session_id)

        assert session is not None
        assert len(session.cache_keys) == 3
        assert 'key1' in session.cache_keys
        assert len(session.cache_dependencies) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
