"""
Unit Tests for Admin Controlling Settings UI

Tests the admin UI components for the Employee Controlling System.

Requirements: 7.1, 7.2, 7.3
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date

# Mock streamlit before importing the module
import sys
sys.modules['streamlit'] = MagicMock()

from admin_controlling_settings_ui import (  # noqa: E402
    render_admin_controlling_settings,
    render_employee_management_tab,
    render_position_management_tab,
    render_criterion_management_tab,
    render_assignment_tab
)


class TestAdminControllingUI:
    """Test suite for admin controlling UI components."""

    @patch('admin_controlling_settings_ui.st')
    @patch('admin_controlling_settings_ui.SessionLocal')
    @patch('admin_controlling_settings_ui.EmployeeManager')
    @patch('admin_controlling_settings_ui.PositionManager')
    @patch('admin_controlling_settings_ui.CriterionManager')
    def test_render_admin_controlling_settings_creates_tabs(
        self, mock_crit_mgr, mock_pos_mgr, mock_emp_mgr, mock_db, mock_st
    ):
        """
        Test that main settings page creates 5 tabs (including notifications).

        Requirements: 7.1, 21.4
        """
        # Setup
        mock_st.tabs.return_value = [
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        ]
        # Mock columns to return context managers
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock()

        # Mock managers
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance

        mock_emp_instance = Mock()
        mock_emp_instance.list_employees.return_value = []
        mock_emp_mgr.return_value = mock_emp_instance

        mock_pos_instance = Mock()
        mock_pos_instance.list_positions.return_value = []
        mock_pos_mgr.return_value = mock_pos_instance

        mock_crit_instance = Mock()
        mock_crit_instance.list_criteria.return_value = []
        mock_crit_mgr.return_value = mock_crit_instance

        # Execute
        render_admin_controlling_settings()

        # Verify
        mock_st.header.assert_called_once()
        mock_st.tabs.assert_called_once()
        tab_labels = mock_st.tabs.call_args[0][0]
        assert len(tab_labels) == 5
        assert "Mitarbeiter" in tab_labels[0]
        assert "Positionen" in tab_labels[1]
        assert "Auswertungskriterien" in tab_labels[2]
        assert "Zuordnungen" in tab_labels[3]
        assert "Benachrichtigungen" in tab_labels[4]

    @patch('admin_controlling_settings_ui.st')
    @patch('admin_controlling_settings_ui.SessionLocal')
    @patch('admin_controlling_settings_ui.EmployeeManager')
    @patch('admin_controlling_settings_ui.PositionManager')
    def test_employee_tab_displays_empty_state(
        self, mock_pos_mgr, mock_emp_mgr, mock_db, mock_st
    ):
        """
        Test employee tab shows info message when no employees exist.

        Requirements: 7.2
        """
        # Setup
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance

        mock_emp_instance = Mock()
        mock_emp_instance.list_employees.return_value = []
        mock_emp_mgr.return_value = mock_emp_instance

        mock_pos_instance = Mock()
        mock_pos_instance.list_positions.return_value = []
        mock_pos_mgr.return_value = mock_pos_instance

        # Mock columns and form
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock()

        # Execute
        render_employee_management_tab()

        # Verify
        mock_st.info.assert_called()
        call_args = str(mock_st.info.call_args)
        assert "Keine Mitarbeiter" in call_args or "Keine Positionen" in call_args

    @patch('admin_controlling_settings_ui.st')
    @patch('admin_controlling_settings_ui.SessionLocal')
    @patch('admin_controlling_settings_ui.PositionManager')
    def test_position_tab_displays_empty_state(
        self, mock_pos_mgr, mock_db, mock_st
    ):
        """
        Test position tab shows info message when no positions exist.

        Requirements: 7.2
        """
        # Setup
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance

        mock_pos_instance = Mock()
        mock_pos_instance.list_positions.return_value = []
        mock_pos_mgr.return_value = mock_pos_instance

        # Execute
        render_position_management_tab()

        # Verify
        mock_st.info.assert_called()
        call_args = str(mock_st.info.call_args)
        assert "Keine Positionen" in call_args

    @patch('admin_controlling_settings_ui.st')
    @patch('admin_controlling_settings_ui.SessionLocal')
    @patch('admin_controlling_settings_ui.CriterionManager')
    def test_criterion_tab_displays_empty_state(
        self, mock_crit_mgr, mock_db, mock_st
    ):
        """
        Test criterion tab shows info message when no criteria exist.

        Requirements: 7.2
        """
        # Setup
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance

        mock_crit_instance = Mock()
        mock_crit_instance.list_criteria.return_value = []
        mock_crit_mgr.return_value = mock_crit_instance

        # Execute
        render_criterion_management_tab()

        # Verify
        mock_st.info.assert_called()
        call_args = str(mock_st.info.call_args)
        assert "Keine Kriterien" in call_args

    @patch('admin_controlling_settings_ui.st')
    @patch('admin_controlling_settings_ui.SessionLocal')
    @patch('admin_controlling_settings_ui.PositionManager')
    @patch('admin_controlling_settings_ui.CriterionManager')
    def test_assignment_tab_requires_positions(
        self, mock_crit_mgr, mock_pos_mgr, mock_db, mock_st
    ):
        """
        Test assignment tab shows warning when no positions exist.

        Requirements: 7.3
        """
        # Setup
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance

        mock_pos_instance = Mock()
        mock_pos_instance.list_positions.return_value = []
        mock_pos_mgr.return_value = mock_pos_instance

        mock_crit_instance = Mock()
        mock_crit_instance.list_criteria.return_value = []
        mock_crit_mgr.return_value = mock_crit_instance

        # Execute
        render_assignment_tab()

        # Verify
        mock_st.warning.assert_called()
        call_args = str(mock_st.warning.call_args)
        assert "Keine Positionen" in call_args

    @patch('admin_controlling_settings_ui.st')
    @patch('admin_controlling_settings_ui.SessionLocal')
    @patch('admin_controlling_settings_ui.PositionManager')
    @patch('admin_controlling_settings_ui.CriterionManager')
    def test_assignment_tab_requires_criteria(
        self, mock_crit_mgr, mock_pos_mgr, mock_db, mock_st
    ):
        """
        Test assignment tab shows warning when no criteria exist.

        Requirements: 7.3
        """
        # Setup
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance

        # Create a mock position
        mock_position = Mock()
        mock_position.id = 1
        mock_position.name = "Test Position"

        mock_pos_instance = Mock()
        mock_pos_instance.list_positions.return_value = [mock_position]
        mock_pos_mgr.return_value = mock_pos_instance

        mock_crit_instance = Mock()
        mock_crit_instance.list_criteria.return_value = []
        mock_crit_mgr.return_value = mock_crit_instance

        # Execute
        render_assignment_tab()

        # Verify
        mock_st.warning.assert_called()
        call_args = str(mock_st.warning.call_args)
        assert "Keine Kriterien" in call_args
