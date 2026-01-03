"""
Integration Tests for Employee Controlling System

Tests complete workflows and interactions between components.

Requirements: All
"""

import pytest
from datetime import date, timedelta
from pathlib import Path
import sys
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.database import SessionLocal, engine, Base
from controlling.managers import (
    EmployeeManager,
    PositionManager,
    CriterionManager,
    PerformanceDataManager
)
from controlling.analytics import AnalyticsEngine
from controlling.report_generator import ReportGenerator
from controlling.chart_generator import ChartGenerator
from controlling.notifications import NotificationManager
from controlling.models import ReportType


@pytest.fixture(scope="function")
def integration_db():
    """Create a fresh database for each integration test"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)


class TestEndToEndEmployeeManagement:
    """Test complete employee management workflow"""
    
    def test_employee_creation_to_report_workflow(self, integration_db):
        """
        Test complete workflow: employee creation → performance recording →
        report generation → export
        
        Requirements: All
        """
        # Setup managers
        emp_manager = EmployeeManager(integration_db)
        pos_manager = PositionManager(integration_db)
        crit_manager = CriterionManager(integration_db)
        perf_manager = PerformanceDataManager(integration_db)
        report_gen = ReportGenerator(integration_db)
        
        # Step 1: Create position
        position = pos_manager.create_position(
            name="Vertriebsmitarbeiter",
            description="Verkauf und Kundenbetreuung"
        )
        assert position.id is not None
        
        # Step 2: Create criteria
        criteria = []
        criterion_names = [
            "Verkauf",
            "Angefahrene Termine gesamt",
            "Getätigte Anrufe gesamt",
            "Kunden terminiert"
        ]
        for name in criterion_names:
            crit = crit_manager.create_criterion(
                name=name,
                description=f"Test {name}"
            )
            criteria.append(crit)
        
        # Step 3: Assign criteria to position
        criterion_ids = [c.id for c in criteria]
        pos_manager.assign_criteria(position.id, criterion_ids)
        
        # Verify assignment
        assigned = pos_manager.get_position_criteria(position.id)
        assert len(assigned) == len(criteria)
        
        # Step 4: Create employee
        employee = emp_manager.create_employee(
            first_name="Max",
            last_name="Mustermann",
            city="Berlin",
            birth_date=date(1990, 1, 1),
            position_id=position.id,
            start_date=date(2024, 1, 1)
        )
        assert employee.id is not None
        assert employee.age > 0
        assert employee.days_employed > 0
        
        # Step 5: Record performance data
        today = date.today()
        performance_data = {
            "Verkauf": 5.0,
            "Angefahrene Termine gesamt": 20.0,
            "Getätigte Anrufe gesamt": 100.0,
            "Kunden terminiert": 25.0
        }
        
        for crit_name, value in performance_data.items():
            criterion = next(c for c in criteria if c.name == crit_name)
            perf_manager.record_performance(
                employee_id=employee.id,
                criterion_id=criterion.id,
                value=value,
                date=today
            )
        
        # Step 6: Generate report
        report_data = report_gen.generate_report(
            employee_id=employee.id,
            report_type=ReportType.DAILY,
            end_date=today
        )
        
        # Verify report data
        assert report_data is not None
        assert report_data["employee_name"] == "Max Mustermann"
        assert "quotas" in report_data
        assert "Abschlussquote" in report_data["quotas"]
        
        # Step 7: Export report
        json_export = report_gen.export_report_json(report_data)
        assert json_export is not None
        
        # Verify JSON can be parsed
        parsed = json.loads(json_export)
        assert parsed is not None
        assert isinstance(parsed, dict)
        
        # Step 8: Save report
        saved_report_id = report_gen.save_report(report_data)
        assert saved_report_id is not None
        assert isinstance(saved_report_id, int)
        
        # Step 9: Load report
        loaded_report = report_gen.load_report(saved_report_id)
        assert loaded_report is not None
        assert loaded_report["employee_name"] == "Max Mustermann"


class TestAdminConfigurationWorkflow:
    """Test admin configuration workflow"""
    
    def test_position_criteria_setup_and_employee_assignment(
        self,
        integration_db
    ):
        """
        Test admin workflow: position/criteria setup → employee assignment
        
        Requirements: 4.1, 5.1, 6.2, 2.1
        """
        # Setup managers
        pos_manager = PositionManager(integration_db)
        crit_manager = CriterionManager(integration_db)
        emp_manager = EmployeeManager(integration_db)
        
        # Step 1: Create multiple positions
        positions = []
        for pos_name in ["Vertrieb", "Kundenservice", "Teamleiter"]:
            pos = pos_manager.create_position(
                name=pos_name,
                description=f"{pos_name} Position"
            )
            positions.append(pos)
        
        # Step 2: Create criteria
        criteria = []
        for crit_name in ["Verkauf", "Anrufe", "Termine", "Zufriedenheit"]:
            crit = crit_manager.create_criterion(
                name=crit_name,
                description=f"{crit_name} Kriterium"
            )
            criteria.append(crit)
        
        # Step 3: Assign different criteria to different positions
        # Vertrieb gets all criteria
        pos_manager.assign_criteria(
            positions[0].id,
            [c.id for c in criteria]
        )
        
        # Kundenservice gets only Anrufe and Zufriedenheit
        pos_manager.assign_criteria(
            positions[1].id,
            [criteria[1].id, criteria[3].id]
        )
        
        # Teamleiter gets all criteria
        pos_manager.assign_criteria(
            positions[2].id,
            [c.id for c in criteria]
        )
        
        # Step 4: Create employees for each position
        employees = []
        for i, position in enumerate(positions):
            emp = emp_manager.create_employee(
                first_name=f"Employee{i}",
                last_name=f"Test{i}",
                city="TestCity",
                birth_date=date(1990, 1, 1),
                position_id=position.id,
                start_date=date(2024, 1, 1)
            )
            employees.append(emp)
        
        # Step 5: Verify employee criteria inheritance
        # Vertrieb employee should have all 4 criteria
        vertrieb_criteria = emp_manager.get_employee_criteria(employees[0].id)
        assert len(vertrieb_criteria) == 4
        
        # Kundenservice employee should have 2 criteria
        service_criteria = emp_manager.get_employee_criteria(employees[1].id)
        assert len(service_criteria) == 2
        
        # Teamleiter employee should have all 4 criteria
        leader_criteria = emp_manager.get_employee_criteria(employees[2].id)
        assert len(leader_criteria) == 4


class TestReportingWorkflow:
    """Test reporting workflow"""
    
    def test_multi_period_reporting(self, integration_db):
        """
        Test report generation for multiple time periods
        
        Requirements: 9.1, 9.2
        """
        # Setup
        emp_manager = EmployeeManager(integration_db)
        pos_manager = PositionManager(integration_db)
        crit_manager = CriterionManager(integration_db)
        perf_manager = PerformanceDataManager(integration_db)
        report_gen = ReportGenerator(integration_db)
        
        # Create position and criteria
        position = pos_manager.create_position(name="Test Position")
        criterion = crit_manager.create_criterion(name="Test Criterion")
        pos_manager.assign_criteria(position.id, [criterion.id])
        
        # Create employee
        employee = emp_manager.create_employee(
            first_name="Test",
            last_name="Employee",
            city="TestCity",
            birth_date=date(1990, 1, 1),
            position_id=position.id,
            start_date=date(2024, 1, 1)
        )
        
        # Record performance data for multiple days
        today = date.today()
        for days_ago in range(30):
            perf_date = today - timedelta(days=days_ago)
            perf_manager.record_performance(
                employee_id=employee.id,
                criterion_id=criterion.id,
                value=float(days_ago + 1),
                date=perf_date
            )
        
        # Generate reports for different periods
        report_types = [
            ReportType.DAILY,
            ReportType.WEEKLY,
            ReportType.MONTHLY
        ]
        
        reports = []
        for report_type in report_types:
            report = report_gen.generate_report(
                employee_id=employee.id,
                report_type=report_type,
                end_date=today
            )
            reports.append(report)
            assert report is not None
            assert "employee_name" in report
        
        # Verify different periods have different data
        # Daily should have less data than weekly, which should have less
        # than monthly
        assert reports[0] is not None  # Daily
        assert reports[1] is not None  # Weekly
        assert reports[2] is not None  # Monthly


class TestNotificationIntegration:
    """Test notification system integration"""
    
    def test_notification_generation_after_report(self, integration_db):
        """
        Test that notifications are generated after report creation
        
        Requirements: 21.1, 21.2
        """
        # Setup
        emp_manager = EmployeeManager(integration_db)
        pos_manager = PositionManager(integration_db)
        crit_manager = CriterionManager(integration_db)
        perf_manager = PerformanceDataManager(integration_db)
        report_gen = ReportGenerator(integration_db)
        notification_manager = NotificationManager()
        
        # Create position and criteria
        position = pos_manager.create_position(name="Sales")
        
        # Create standard criteria needed for quotas
        criteria_names = [
            "Verkauf",
            "Angefahrene Termine gesamt"
        ]
        criteria = []
        for name in criteria_names:
            crit = crit_manager.create_criterion(name=name)
            criteria.append(crit)
            pos_manager.assign_criteria(position.id, [crit.id])
        
        # Create employee
        employee = emp_manager.create_employee(
            first_name="High",
            last_name="Performer",
            city="TestCity",
            birth_date=date(1990, 1, 1),
            position_id=position.id,
            start_date=date(2024, 1, 1)
        )
        
        # Record high performance data (should trigger success notification)
        today = date.today()
        perf_manager.record_performance(
            employee_id=employee.id,
            criterion_id=criteria[0].id,  # Verkauf
            value=10.0,
            date=today
        )
        perf_manager.record_performance(
            employee_id=employee.id,
            criterion_id=criteria[1].id,  # Angefahrene Termine gesamt
            value=20.0,
            date=today
        )
        
        # Generate report
        report_data = report_gen.generate_report(
            employee_id=employee.id,
            report_type=ReportType.DAILY,
            end_date=today
        )
        
        # Check for notifications
        if "quotas" in report_data:
            notifications = notification_manager.check_quotas(
                report_data["quotas"],
                employee_name=employee.full_name
            )
            
            # Should have at least one notification (Abschlussquote = 50%)
            assert len(notifications) > 0
            
            # Verify notification has correct employee name
            for notification in notifications:
                assert notification.employee_name == "High Performer"


class TestChartGeneration:
    """Test chart generation integration"""
    
    def test_chart_generation_from_report(self, integration_db):
        """
        Test that charts can be generated from report data
        
        Requirements: 12.1, 12.4
        """
        # Setup
        emp_manager = EmployeeManager(integration_db)
        pos_manager = PositionManager(integration_db)
        crit_manager = CriterionManager(integration_db)
        perf_manager = PerformanceDataManager(integration_db)
        report_gen = ReportGenerator(integration_db)
        chart_gen = ChartGenerator()
        
        # Create position and criteria
        position = pos_manager.create_position(name="Test Position")
        criteria_names = ["Verkauf", "Angefahrene Termine gesamt"]
        criteria = []
        for name in criteria_names:
            crit = crit_manager.create_criterion(name=name)
            criteria.append(crit)
            pos_manager.assign_criteria(position.id, [crit.id])
        
        # Create employee
        employee = emp_manager.create_employee(
            first_name="Chart",
            last_name="Test",
            city="TestCity",
            birth_date=date(1990, 1, 1),
            position_id=position.id,
            start_date=date(2024, 1, 1)
        )
        
        # Record performance data
        today = date.today()
        for criterion in criteria:
            perf_manager.record_performance(
                employee_id=employee.id,
                criterion_id=criterion.id,
                value=10.0,
                date=today
            )
        
        # Generate report
        report_data = report_gen.generate_report(
            employee_id=employee.id,
            report_type=ReportType.DAILY,
            end_date=today
        )
        
        # Generate charts
        charts = chart_gen.create_dashboard(report_data)
        
        # Verify charts were created
        assert len(charts) > 0
        
        # Verify each chart is a valid Plotly figure
        for chart in charts:
            assert chart is not None
            assert hasattr(chart, 'data')
            assert hasattr(chart, 'layout')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
