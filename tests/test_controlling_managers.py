"""
Unit Tests for Controlling System Managers

Tests CRUD operations and validation logic for all manager classes.

Requirements: 2.1, 3.1, 3.2, 4.1, 5.1
"""

import sys
from pathlib import Path
from datetime import date, timedelta
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from controlling.managers import (
    EmployeeManager,
    PositionManager,
    CriterionManager,
    PerformanceDataManager,
    ValidationError
)
from controlling.models import CalculationMethod
from backend.core.database import SessionLocal, engine, Base


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = SessionLocal()

    yield session

    # Cleanup
    session.close()
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)


def test_position_manager_create(db_session):
    """Test creating a position"""
    manager = PositionManager(db_session)

    position = manager.create_position(
        name="Sales Representative",
        description="Handles customer sales"
    )

    assert position.id is not None
    assert position.name == "Sales Representative"
    assert position.description == "Handles customer sales"
    assert position.is_active is True


def test_position_manager_duplicate_name(db_session):
    """Test that duplicate position names are rejected"""
    manager = PositionManager(db_session)

    manager.create_position(name="Manager")

    with pytest.raises(ValidationError, match="already exists"):
        manager.create_position(name="Manager")


def test_employee_manager_create(db_session):
    """Test creating an employee"""
    # First create a position
    pos_manager = PositionManager(db_session)
    position = pos_manager.create_position(name="Developer")

    # Create employee
    emp_manager = EmployeeManager(db_session)
    employee = emp_manager.create_employee(
        first_name="John",
        last_name="Doe",
        city="Berlin",
        birth_date=date(1990, 1, 1),
        position_id=position.id,
        start_date=date(2020, 1, 1)
    )

    assert employee.id is not None
    assert employee.first_name == "John"
    assert employee.last_name == "Doe"
    assert employee.full_name == "John Doe"
    assert employee.is_active is True


def test_employee_manager_validation(db_session):
    """Test employee validation"""
    pos_manager = PositionManager(db_session)
    position = pos_manager.create_position(name="Tester")

    emp_manager = EmployeeManager(db_session)

    # Test empty first name
    with pytest.raises(ValidationError, match="First name is required"):
        emp_manager.create_employee(
            first_name="",
            last_name="Doe",
            city="Berlin",
            birth_date=date(1990, 1, 1),
            position_id=position.id,
            start_date=date(2020, 1, 1)
        )

    # Test future birth date
    with pytest.raises(ValidationError, match="Birth date must be in the past"):
        emp_manager.create_employee(
            first_name="John",
            last_name="Doe",
            city="Berlin",
            birth_date=date.today() + timedelta(days=1),
            position_id=position.id,
            start_date=date(2020, 1, 1)
        )


def test_criterion_manager_create(db_session):
    """Test creating a criterion"""
    manager = CriterionManager(db_session)

    criterion = manager.create_criterion(
        name="Sales Count",
        description="Number of sales made",
        calculation_method=CalculationMethod.SUM
    )

    assert criterion.id is not None
    assert criterion.name == "Sales Count"
    assert criterion.calculation_method == CalculationMethod.SUM
    assert criterion.is_active is True


def test_position_criteria_assignment(db_session):
    """Test assigning criteria to positions"""
    pos_manager = PositionManager(db_session)
    crit_manager = CriterionManager(db_session)

    # Create position and criteria
    position = pos_manager.create_position(name="Sales Rep")
    criterion1 = crit_manager.create_criterion(name="Calls Made")
    criterion2 = crit_manager.create_criterion(name="Sales Closed")

    # Assign criteria
    pos_manager.assign_criteria(
        position.id,
        [criterion1.id, criterion2.id]
    )

    # Verify assignment
    assigned = pos_manager.get_position_criteria(position.id)
    assert len(assigned) == 2
    assert criterion1.id in [c.id for c in assigned]
    assert criterion2.id in [c.id for c in assigned]


def test_performance_data_manager(db_session):
    """Test recording performance data"""
    # Setup
    pos_manager = PositionManager(db_session)
    emp_manager = EmployeeManager(db_session)
    crit_manager = CriterionManager(db_session)
    perf_manager = PerformanceDataManager(db_session)

    position = pos_manager.create_position(name="Agent")
    employee = emp_manager.create_employee(
        first_name="Jane",
        last_name="Smith",
        city="Munich",
        birth_date=date(1985, 5, 15),
        position_id=position.id,
        start_date=date(2019, 3, 1)
    )
    criterion = crit_manager.create_criterion(name="Tasks Completed")

    # Record performance
    performance = perf_manager.record_performance(
        employee_id=employee.id,
        criterion_id=criterion.id,
        value=25.0,
        date=date.today()
    )

    assert performance.id is not None
    assert performance.value == 25.0
    assert performance.employee_id == employee.id


def test_performance_data_validation(db_session):
    """Test performance data validation"""
    pos_manager = PositionManager(db_session)
    emp_manager = EmployeeManager(db_session)
    crit_manager = CriterionManager(db_session)
    perf_manager = PerformanceDataManager(db_session)

    position = pos_manager.create_position(name="Worker")
    employee = emp_manager.create_employee(
        first_name="Bob",
        last_name="Jones",
        city="Hamburg",
        birth_date=date(1992, 8, 20),
        position_id=position.id,
        start_date=date(2021, 1, 1)
    )
    criterion = crit_manager.create_criterion(name="Hours Worked")

    # Test negative value
    with pytest.raises(ValidationError, match="cannot be negative"):
        perf_manager.record_performance(
            employee_id=employee.id,
            criterion_id=criterion.id,
            value=-5.0,
            date=date.today()
        )

    # Test non-numeric value
    with pytest.raises(ValidationError, match="must be numeric"):
        perf_manager.record_performance(
            employee_id=employee.id,
            criterion_id=criterion.id,
            value="invalid",
            date=date.today()
        )


def test_employee_delete_archives(db_session):
    """Test that deleting an employee archives it"""
    pos_manager = PositionManager(db_session)
    emp_manager = EmployeeManager(db_session)

    position = pos_manager.create_position(name="Analyst")
    employee = emp_manager.create_employee(
        first_name="Alice",
        last_name="Brown",
        city="Frankfurt",
        birth_date=date(1988, 3, 10),
        position_id=position.id,
        start_date=date(2018, 6, 1)
    )

    # Delete employee
    emp_manager.delete_employee(employee.id)

    # Verify employee is archived
    retrieved = emp_manager.get_employee(employee.id)
    assert retrieved.is_active is False

    # Verify not in active list
    active_employees = emp_manager.list_employees()
    assert employee.id not in [e.id for e in active_employees]


def test_position_delete_protection(db_session):
    """Test that positions with employees cannot be deleted"""
    pos_manager = PositionManager(db_session)
    emp_manager = EmployeeManager(db_session)

    position = pos_manager.create_position(name="Engineer")
    emp_manager.create_employee(
        first_name="Charlie",
        last_name="Davis",
        city="Stuttgart",
        birth_date=date(1991, 11, 5),
        position_id=position.id,
        start_date=date(2020, 9, 1)
    )

    # Try to delete position with employee
    with pytest.raises(ValidationError, match="Cannot delete position"):
        pos_manager.delete_position(position.id)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])



def test_employee_criteria_inheritance(db_session):
    """Test that employees inherit criteria from their position"""
    pos_manager = PositionManager(db_session)
    emp_manager = EmployeeManager(db_session)
    crit_manager = CriterionManager(db_session)

    # Create position
    position = pos_manager.create_position(name="Sales Agent")

    # Create criteria
    criterion1 = crit_manager.create_criterion(name="Calls Made")
    criterion2 = crit_manager.create_criterion(name="Sales Closed")
    criterion3 = crit_manager.create_criterion(name="Meetings Held")

    # Assign criteria to position
    pos_manager.assign_criteria(
        position.id,
        [criterion1.id, criterion2.id, criterion3.id]
    )

    # Create employee with this position
    employee = emp_manager.create_employee(
        first_name="John",
        last_name="Seller",
        city="New York",
        birth_date=date(1990, 5, 15),
        position_id=position.id,
        start_date=date(2020, 1, 1)
    )

    # Get employee criteria
    employee_criteria = emp_manager.get_employee_criteria(employee.id)

    # Verify employee has all position criteria
    assert len(employee_criteria) == 3
    criterion_ids = [c.id for c in employee_criteria]
    assert criterion1.id in criterion_ids
    assert criterion2.id in criterion_ids
    assert criterion3.id in criterion_ids


def test_position_criteria_assignment_prevents_duplicates(db_session):
    """Test that assigning the same criterion twice doesn't create duplicates"""
    pos_manager = PositionManager(db_session)
    crit_manager = CriterionManager(db_session)

    # Create position and criterion
    position = pos_manager.create_position(name="Manager")
    criterion = crit_manager.create_criterion(name="Reports Reviewed")

    # Assign criterion twice
    pos_manager.assign_criteria(position.id, [criterion.id])
    pos_manager.assign_criteria(position.id, [criterion.id])

    # Verify only one assignment exists
    criteria = pos_manager.get_position_criteria(position.id)
    assert len(criteria) == 1
    assert criteria[0].id == criterion.id


def test_position_criteria_removal(db_session):
    """Test removing criteria from a position"""
    pos_manager = PositionManager(db_session)
    crit_manager = CriterionManager(db_session)

    # Create position and criteria
    position = pos_manager.create_position(name="Coordinator")
    criterion1 = crit_manager.create_criterion(name="Tasks Completed")
    criterion2 = crit_manager.create_criterion(name="Emails Sent")

    # Assign both criteria
    pos_manager.assign_criteria(position.id, [criterion1.id, criterion2.id])

    # Verify both assigned
    criteria = pos_manager.get_position_criteria(position.id)
    assert len(criteria) == 2

    # Remove one criterion
    pos_manager.remove_criteria(position.id, [criterion1.id])

    # Verify only one remains
    criteria = pos_manager.get_position_criteria(position.id)
    assert len(criteria) == 1
    assert criteria[0].id == criterion2.id
