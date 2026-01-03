"""
Unit Tests for Controlling Main UI

Tests the main user interface components for the Employee Controlling System.

Requirements: 8.1, 8.2, 9.1, 16.2
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date

# Mock streamlit before importing the module
import sys
sys.modules['streamlit'] = MagicMock()

from controlling_ui import (  # noqa: E402
    render_controlling_page,
    render_performance_entry_tab,
    render_report_generation_tab,
    render_archive_tab
)


class TestControllingUI:
    """Test suite for controlling UI components."""

    @patch('controlling_ui.st')
    @patch('controlling_ui.SessionLocal')
    def test_render_controlling_page_creates_tabs(self, mock_db, mock_st):
        """
        Test that main controlling page creates 3 tabs.

        Requirements: 9.1
        """
        # Setup
        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]

        # Execute
        render_controlling_page()

        # Verify
        mock_st.header.assert_called_once()
        mock_st.tabs.assert_called_once()
        tab_labels = mock_st.tabs.call_args[0][0]
        assert len(tab_labels) == 3
        assert "Leistungsdaten erfassen" in tab_labels[0]
        assert "Berichte erstellen" in tab_labels[1]
        assert "Archiv" in tab_labels[2]

    @patch('controlling_ui.st')
    @patch('controlling_ui.SessionLocal')
    @patch('controlling_ui.EmployeeManager')
    @patch('controlling_ui.PerformanceDataManager')
    def test_performance_entry_tab_displays_empty_state(
        self, mock_perf_mgr, mock_emp_mgr, mock_db, mock_st
    ):
        """
        Test performance entry tab shows warning when no employees exist.

        Requirements: 8.1
        """
        # Setup
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance

        mock_emp_instance = Mock()
        mock_emp_instance.list_employees.return_value = []
        mock_emp_mgr.return_value = mock_emp_instance

        # Execute
        render_performance_entry_tab()

        # Verify
        mock_st.warning.assert_called()
        call_args = str(mock_st.warning.call_args)
        assert "Keine Mitarbeiter" in call_args

    @patch('controlling_ui.st')
    @patch('controlling_ui.SessionLocal')
    @patch('controlling_ui.EmployeeManager')
    @patch('controlling_ui.ReportGenerator')
    @patch('controlling_ui.ChartGenerator')
    def test_report_generation_tab_displays_empty_state(
        self, mock_chart_gen, mock_report_gen, mock_emp_mgr, mock_db, mock_st
    ):
        """
        Test report generation tab shows warning when no employees exist.

        Requirements: 9.1
        """
        # Setup
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance

        mock_emp_instance = Mock()
        mock_emp_instance.list_employees.return_value = []
        mock_emp_mgr.return_value = mock_emp_instance

        # Mock columns
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]

        # Execute
        render_report_generation_tab()

        # Verify
        mock_st.warning.assert_called()
        call_args = str(mock_st.warning.call_args)
        assert "Keine Mitarbeiter" in call_args



    @patch('controlling_ui.st')
    @patch('controlling_ui.SessionLocal')
    @patch('controlling_ui.ReportGenerator')
    @patch('controlling_ui.ChartGenerator')
    def test_archive_tab_displays_empty_state(
        self, mock_chart_gen, mock_report_gen, mock_db, mock_st
    ):
        """
        Test archive tab shows info when no reports exist.

        Requirements: 9.1
        """
        # Setup
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance

        mock_report_gen_instance = Mock()
        mock_report_gen_instance.list_reports.return_value = []
        mock_report_gen.return_value = mock_report_gen_instance

        # Mock columns
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.selectbox.return_value = None
        mock_st.number_input.return_value = 20

        # Execute
        render_archive_tab()

        # Verify
        mock_st.info.assert_called()
        call_args = str(mock_st.info.call_args)
        assert "Keine gespeicherten Berichte" in call_args

    @patch('controlling_ui.st')
    @patch('controlling_ui.SessionLocal')
    @patch('controlling_ui.EmployeeManager')
    @patch('controlling_ui.PerformanceDataManager')
    def test_performance_entry_validates_numeric_input(
        self, mock_perf_mgr, mock_emp_mgr, mock_db, mock_st
    ):
        """
        Test that performance entry form validates numeric input.

        Requirements: 8.2
        """
        # Setup
        mock_db_instance = Mock()
        mock_db.return_value = mock_db_instance

        # Create mock employee with position and criteria
        mock_emp = Mock()
        mock_emp.id = 1
        mock_emp.full_name = "Test Employee"
        mock_emp.position = Mock()
        mock_emp.position.name = "Developer"

        mock_criterion = Mock()
        mock_criterion.id = 1
        mock_criterion.name = "Test Criterion"
        mock_criterion.description = "Test"

        mock_emp_instance = Mock()
        mock_emp_instance.list_employees.return_value = [mock_emp]
        mock_emp_instance.get_employee.return_value = mock_emp
        mock_emp_instance.get_employee_criteria.return_value = [mock_criterion]
        mock_emp_mgr.return_value = mock_emp_instance

        # Mock streamlit components
        mock_st.selectbox.return_value = 1
        mock_st.date_input.return_value = date.today()
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock()
        mock_st.number_input.return_value = 10.0  # Valid numeric input
        mock_st.form_submit_button.return_value = False

        # Execute
        render_performance_entry_tab()

        # Verify that number_input was called (validates numeric input)
        assert mock_st.number_input.called
        # Verify min_value parameter ensures non-negative values
        call_kwargs = mock_st.number_input.call_args[1]
        assert 'min_value' in call_kwargs
        assert call_kwargs['min_value'] == 0.0
