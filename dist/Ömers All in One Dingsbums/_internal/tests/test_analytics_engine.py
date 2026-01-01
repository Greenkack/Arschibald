"""
Unit Tests for Analytics Engine

Tests specific quota calculations, ratio descriptions, and edge cases
for the Employee Controlling System analytics engine.

Requirements: 10.1, 10.2, 11.1
"""

import sys
from pathlib import Path
from datetime import date, timedelta
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from controlling.analytics import AnalyticsEngine
from controlling.managers import (
    EmployeeManager,
    PositionManager,
    CriterionManager,
    PerformanceDataManager
)
from controlling.models import ReportType
from backend.core.database import SessionLocal, engine, Base


@pytest.fixture(scope="module")
def setup_database():
    """Setup database for all tests"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    """Create a database session for each test"""
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def analytics_engine(db_session):
    """Create an analytics engine instance"""
    return AnalyticsEngine(db_session)


@pytest.fixture
def test_employee(db_session):
    """Create a test employee with position"""
    pos_manager = PositionManager(db_session)
    emp_manager = EmployeeManager(db_session)

    # Create position
    import time
    position = pos_manager.create_position(
        name=f"Test_Position_{int(time.time() * 1000000)}",
        description="Test position"
    )

    # Create employee
    employee = emp_manager.create_employee(
        first_name="Test",
        last_name="Employee",
        city="Test City",
        birth_date=date(1990, 1, 1),
        position_id=position.id,
        start_date=date(2020, 1, 1)
    )

    return employee


class TestQuotaCalculations:
    """Test individual quota calculation methods"""

    def test_abschlussquote_normal_case(self, analytics_engine):
        """Test Abschlussquote with normal values"""
        result = analytics_engine.calculate_abschlussquote(
            verkauf=25,
            angefahrene_termine_gesamt=100
        )
        assert result == 25.0

    def test_abschlussquote_zero_denominator(self, analytics_engine):
        """Test Abschlussquote with zero denominator"""
        result = analytics_engine.calculate_abschlussquote(
            verkauf=10,
            angefahrene_termine_gesamt=0
        )
        assert result == 0.0

    def test_terminvereinbarungsquote_normal_case(self, analytics_engine):
        """Test Terminvereinbarungsquote with normal values"""
        result = analytics_engine.calculate_terminvereinbarungsquote(
            kunden_terminiert=50,
            getaetigte_anrufe_gesamt=200
        )
        assert result == 25.0

    def test_anfahrquote_perfect_attendance(self, analytics_engine):
        """Test Anfahrquote with 100% attendance"""
        result = analytics_engine.calculate_anfahrquote(
            angefahrene_termine=50,
            kunden_terminiert=50
        )
        assert result == 100.0

    def test_nicht_interessiert_quote(self, analytics_engine):
        """Test nicht interessierte Kunden Quote"""
        result = analytics_engine.calculate_nicht_interessiert_quote(
            storniert_kein_interesse=10,
            angefahrene_termine_gesamt=100
        )
        assert result == 10.0

    def test_technisch_nicht_machbar_quote(self, analytics_engine):
        """Test technisch nicht machbar Quote"""
        result = analytics_engine.calculate_technisch_nicht_machbar_quote(
            technisch_nicht_machbar=5,
            angefahrene_termine_gesamt=100
        )
        assert result == 5.0

    def test_nicht_erreicht_quote(self, analytics_engine):
        """Test Quote der nicht erreichten Kunden"""
        result = analytics_engine.calculate_nicht_erreicht_quote(
            nicht_erreicht=30,
            getaetigte_anrufe_gesamt=200
        )
        assert result == 15.0

    def test_folgetermin_quote(self, analytics_engine):
        """Test Quote für Folgetermine-Vereinbarungen"""
        result = analytics_engine.calculate_folgetermin_quote(
            folgetermin_gemacht=20,
            angefahrene_termine_gesamt=100
        )
        assert result == 20.0

    def test_angebot_quote(self, analytics_engine):
        """Test Quote für Angebote"""
        result = analytics_engine.calculate_angebot_quote(
            angebot_erhalten=40,
            angefahrene_termine_gesamt=100
        )
        assert result == 40.0

    def test_zu_teuer_quote(self, analytics_engine):
        """Test Quote für zu teuer"""
        result = analytics_engine.calculate_zu_teuer_quote(
            zu_teuer=15,
            angefahrene_termine_gesamt=100
        )
        assert result == 15.0

    def test_qc_bestanden_quote(self, analytics_engine):
        """Test Quote für QC bestanden"""
        result = analytics_engine.calculate_qc_bestanden_quote(
            qc_bestanden=20,
            verkauf=25
        )
        assert result == 80.0

    def test_qc_bestanden_quote_zero_sales(self, analytics_engine):
        """Test QC Quote with zero sales"""
        result = analytics_engine.calculate_qc_bestanden_quote(
            qc_bestanden=0,
            verkauf=0
        )
        assert result == 0.0


class TestRatioDescriptions:
    """Test ratio description generation"""

    def test_ratio_description_25_percent(self, analytics_engine):
        """Test ratio description for 25%"""
        result = analytics_engine.calculate_ratio_description(
            25.0,
            "Abschlussquote"
        )
        assert "4" in result
        assert "Verkauf" in result

    def test_ratio_description_10_percent(self, analytics_engine):
        """Test ratio description for 10%"""
        result = analytics_engine.calculate_ratio_description(
            10.0,
            "Terminvereinbarungsquote"
        )
        assert "10" in result
        assert "Termin" in result

    def test_ratio_description_zero_percent(self, analytics_engine):
        """Test ratio description for 0%"""
        result = analytics_engine.calculate_ratio_description(
            0.0,
            "Abschlussquote"
        )
        assert result == "keine Daten"

    def test_ratio_description_50_percent(self, analytics_engine):
        """Test ratio description for 50%"""
        result = analytics_engine.calculate_ratio_description(
            50.0,
            "Abschlussquote"
        )
        assert "2" in result

    def test_ratio_description_100_percent(self, analytics_engine):
        """Test ratio description for 100%"""
        result = analytics_engine.calculate_ratio_description(
            100.0,
            "Termine-Anfahrquote"
        )
        assert "1" in result

    def test_ratio_description_unknown_criterion(self, analytics_engine):
        """Test ratio description for unknown criterion"""
        result = analytics_engine.calculate_ratio_description(
            25.0,
            "Unknown Criterion"
        )
        assert "1 zu 4" in result


class TestCalculateQuotas:
    """Test the orchestrated calculate_quotas method"""

    def test_calculate_quotas_with_performance_data(
        self,
        db_session,
        analytics_engine,
        test_employee
    ):
        """Test calculate_quotas with actual performance data"""
        crit_manager = CriterionManager(db_session)
        perf_manager = PerformanceDataManager(db_session)

        # Create standard criteria if they don't exist
        from controlling.models import STANDARD_CRITERIA
        for crit_data in STANDARD_CRITERIA:
            try:
                crit_manager.create_criterion(
                    name=crit_data["name"],
                    description=crit_data["description"],
                    calculation_method=crit_data["calculation_method"],
                    is_standard=crit_data["is_standard"]
                )
            except Exception:
                pass  # Criterion already exists

        # Get criteria
        criteria = crit_manager.get_standard_criteria()
        criterion_map = {c.name: c for c in criteria}

        # Create performance data
        test_date = date.today()
        perf_manager.record_performance(
            employee_id=test_employee.id,
            criterion_id=criterion_map["Verkauf"].id,
            value=25,
            date=test_date
        )
        perf_manager.record_performance(
            employee_id=test_employee.id,
            criterion_id=criterion_map["Angefahrene Termine gesamt"].id,
            value=100,
            date=test_date
        )

        # Get performance data
        performance_data = perf_manager.get_performance_data(
            employee_id=test_employee.id,
            start_date=test_date,
            end_date=test_date
        )

        # Calculate quotas
        quotas = analytics_engine.calculate_quotas(performance_data)

        # Verify quotas
        assert "Abschlussquote" in quotas
        assert quotas["Abschlussquote"] == 25.0

    def test_calculate_quotas_empty_data(self, analytics_engine):
        """Test calculate_quotas with empty performance data"""
        quotas = analytics_engine.calculate_quotas([])

        # All quotas should be 0
        assert all(value == 0.0 for value in quotas.values())


class TestAggregateData:
    """Test data aggregation for different time periods"""

    def test_aggregate_data_daily(
        self,
        db_session,
        analytics_engine,
        test_employee
    ):
        """Test daily data aggregation"""
        crit_manager = CriterionManager(db_session)
        perf_manager = PerformanceDataManager(db_session)

        # Create standard criteria if they don't exist
        from controlling.models import STANDARD_CRITERIA
        for crit_data in STANDARD_CRITERIA:
            try:
                crit_manager.create_criterion(
                    name=crit_data["name"],
                    description=crit_data["description"],
                    calculation_method=crit_data["calculation_method"],
                    is_standard=crit_data["is_standard"]
                )
            except Exception:
                pass

        # Get criteria
        criteria = crit_manager.get_standard_criteria()
        criterion_map = {c.name: c for c in criteria}

        # Create performance data for today
        test_date = date.today()
        perf_manager.record_performance(
            employee_id=test_employee.id,
            criterion_id=criterion_map["Verkauf"].id,
            value=5,
            date=test_date
        )

        # Aggregate data
        result = analytics_engine.aggregate_data(
            employee_id=test_employee.id,
            period_type=ReportType.DAILY,
            start_date=test_date,
            end_date=test_date
        )

        # Verify result structure
        assert result["employee_id"] == test_employee.id
        assert result["period_type"] == "DAILY"
        assert "quotas" in result
        assert "ratios" in result
        assert "raw_data" in result

    def test_aggregate_data_invalid_employee(
        self,
        analytics_engine
    ):
        """Test aggregate_data with invalid employee ID"""
        with pytest.raises(ValueError, match="Employee with ID .* not found"):
            analytics_engine.aggregate_data(
                employee_id=99999,
                period_type=ReportType.DAILY
            )


class TestCalculateComparison:
    """Test multi-employee comparison"""

    def test_calculate_comparison_multiple_employees(
        self,
        db_session,
        analytics_engine
    ):
        """Test comparison with multiple employees"""
        pos_manager = PositionManager(db_session)
        emp_manager = EmployeeManager(db_session)

        # Create position
        import time
        position = pos_manager.create_position(
            name=f"Comp_Position_{int(time.time() * 1000000)}",
            description="Comparison test position"
        )

        # Create two employees
        employee1 = emp_manager.create_employee(
            first_name="Employee",
            last_name="One",
            city="City1",
            birth_date=date(1990, 1, 1),
            position_id=position.id,
            start_date=date(2020, 1, 1)
        )

        employee2 = emp_manager.create_employee(
            first_name="Employee",
            last_name="Two",
            city="City2",
            birth_date=date(1991, 1, 1),
            position_id=position.id,
            start_date=date(2020, 1, 1)
        )

        # Calculate comparison
        result = analytics_engine.calculate_comparison(
            employee_ids=[employee1.id, employee2.id],
            start_date=date(2020, 1, 1),
            end_date=date.today()
        )

        # Verify result structure
        assert "employees" in result
        assert len(result["employees"]) == 2
        assert result["employees"][0]["employee_id"] == employee1.id
        assert result["employees"][1]["employee_id"] == employee2.id

    def test_calculate_comparison_too_many_employees(
        self,
        analytics_engine
    ):
        """Test comparison with more than 10 employees"""
        employee_ids = list(range(1, 12))  # 11 employees

        with pytest.raises(
            ValueError,
            match="Comparison supports maximum 10 employees"
        ):
            analytics_engine.calculate_comparison(
                employee_ids=employee_ids,
                start_date=date(2020, 1, 1),
                end_date=date.today()
            )


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_zero_values_all_quotas(self, analytics_engine):
        """Test all quota calculations with zero values"""
        # All quotas should return 0.0 when denominators are 0
        assert analytics_engine.calculate_abschlussquote(0, 0) == 0.0
        assert analytics_engine.calculate_terminvereinbarungsquote(0, 0) == 0.0
        assert analytics_engine.calculate_anfahrquote(0, 0) == 0.0
        assert analytics_engine.calculate_nicht_interessiert_quote(0, 0) == 0.0
        assert analytics_engine.calculate_technisch_nicht_machbar_quote(
            0, 0
        ) == 0.0
        assert analytics_engine.calculate_nicht_erreicht_quote(0, 0) == 0.0
        assert analytics_engine.calculate_folgetermin_quote(0, 0) == 0.0
        assert analytics_engine.calculate_angebot_quote(0, 0) == 0.0
        assert analytics_engine.calculate_zu_teuer_quote(0, 0) == 0.0
        assert analytics_engine.calculate_qc_bestanden_quote(0, 0) == 0.0

    def test_very_small_percentages(self, analytics_engine):
        """Test quota calculations with very small percentages"""
        result = analytics_engine.calculate_abschlussquote(
            verkauf=1,
            angefahrene_termine_gesamt=1000
        )
        assert result == 0.1

    def test_very_large_percentages(self, analytics_engine):
        """Test quota calculations that exceed 100%"""
        # This shouldn't happen in practice, but test the calculation
        result = analytics_engine.calculate_qc_bestanden_quote(
            qc_bestanden=150,
            verkauf=100
        )
        assert result == 150.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
