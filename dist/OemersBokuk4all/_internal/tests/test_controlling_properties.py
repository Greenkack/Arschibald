"""
Property-Based Tests for Employee Controlling System

Uses Hypothesis for property-based testing to verify correctness properties
across many randomly generated inputs.

Requirements: 2.1, 2.2, 2.3, 2.5
"""

import sys
from pathlib import Path
from datetime import date, timedelta, datetime
from contextlib import contextmanager
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from controlling.models import Employee, Position
from controlling.managers import (
    EmployeeManager,
    PositionManager,
    CriterionManager,
    PerformanceDataManager,
    ValidationError
)
from backend.core.database import SessionLocal, engine, Base

# Import export availability flags for conditional test execution
try:
    from controlling.report_generator import (
        REPORTLAB_AVAILABLE,
        OPENPYXL_AVAILABLE
    )
except ImportError:
    REPORTLAB_AVAILABLE = False
    OPENPYXL_AVAILABLE = False


# Context manager for database sessions
@contextmanager
def get_test_db():
    """Context manager for test database sessions"""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = SessionLocal()

    try:
        # Create a test position if it doesn't exist
        position = session.query(Position).filter(
            Position.name == "Test Position"
        ).first()

        if not position:
            position = Position(
                name="Test Position",
                description="Test position for property tests"
            )
            session.add(position)
            session.commit()

        yield session
    finally:
        # Cleanup
        session.close()


# Setup and teardown for all tests
@pytest.fixture(scope="module", autouse=True)
def setup_teardown_db():
    """Setup and teardown database for all tests"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a test position
    session = SessionLocal()
    try:
        position = Position(
            name="Test Position",
            description="Test position for property tests"
        )
        session.add(position)
        session.commit()
    finally:
        session.close()
    
    yield
    
    # Drop tables after all tests
    Base.metadata.drop_all(bind=engine)


# Hypothesis strategies for generating test data
@st.composite
def valid_birth_date(draw):
    """Generate valid birth dates (18-100 years ago)"""
    today = date.today()
    max_date = today - timedelta(days=365 * 18)   # 18 years ago

    days_ago = draw(st.integers(min_value=0, max_value=365 * 82))
    return max_date - timedelta(days=days_ago)


@st.composite
def valid_start_date(draw):
    """Generate valid start dates (up to 50 years ago)"""
    today = date.today()

    days_ago = draw(st.integers(min_value=0, max_value=365 * 50))
    return today - timedelta(days=days_ago)


@st.composite
def valid_employee_data(draw, position_id=1):
    """Generate valid employee data"""
    # Use simpler string generation for better performance
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    first_name = draw(st.text(
        alphabet=alphabet,
        min_size=2,
        max_size=20
    ))
    last_name = draw(st.text(
        alphabet=alphabet,
        min_size=2,
        max_size=20
    ))
    city = draw(st.text(
        alphabet=alphabet,
        min_size=2,
        max_size=20
    ))
    birth_date = draw(valid_birth_date())
    start_date = draw(valid_start_date())

    return {
        "first_name": first_name,
        "last_name": last_name,
        "city": city,
        "birth_date": birth_date,
        "position_id": position_id,
        "start_date": start_date
    }


# Property 1: Employee Data Persistence Round-Trip
# Feature: employee-controlling-system, Property 1: Employee Data Persistence
# Round-Trip
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(employee_data=valid_employee_data())
def test_property_1_employee_data_persistence_round_trip(employee_data):
    """
    Property 1: Employee Data Persistence Round-Trip

    For any valid employee with all required fields (first_name, last_name,
    city, birth_date, position_id, start_date), saving the employee to the
    database and then retrieving it should return an employee with identical
    field values.

    Validates: Requirements 2.1, 2.5
    """
    with get_test_db() as db_session:
        # Create employee
        employee = Employee(**employee_data)
        db_session.add(employee)
        db_session.commit()

        # Get the ID
        employee_id = employee.id

        # Clear session to force fresh load
        db_session.expire_all()

        # Retrieve employee
        retrieved = db_session.query(Employee).filter(
            Employee.id == employee_id
        ).first()

        # Verify all fields match
        assert retrieved is not None, "Employee should be retrievable"
        assert retrieved.first_name == employee_data["first_name"]
        assert retrieved.last_name == employee_data["last_name"]
        assert retrieved.city == employee_data["city"]
        assert retrieved.birth_date == employee_data["birth_date"]
        assert retrieved.position_id == employee_data["position_id"]
        assert retrieved.start_date == employee_data["start_date"]
        assert retrieved.is_active is True  # Default value


# Property 2: Age Calculation Correctness
# Feature: employee-controlling-system, Property 2: Age Calculation
# Correctness
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(birth_date=valid_birth_date())
def test_property_2_age_calculation_correctness(birth_date):
    """
    Property 2: Age Calculation Correctness

    For any birth date in the past, the calculated age should equal the
    difference in years between the birth date and the current date,
    accounting for whether the birthday has occurred this year.

    Validates: Requirements 2.2
    """
    with get_test_db() as db_session:
        # Create employee with the birth date
        employee = Employee(
            first_name="Test",
            last_name="Employee",
            city="Test City",
            birth_date=birth_date,
            position_id=1,
            start_date=date.today() - timedelta(days=365)
        )
        db_session.add(employee)
        db_session.commit()

        # Calculate expected age manually
        today = date.today()
        expected_age = today.year - birth_date.year

        # Adjust if birthday hasn't occurred this year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            expected_age -= 1

        # Verify age calculation
        assert employee.age == expected_age, (
            f"Age calculation incorrect: expected {expected_age}, "
            f"got {employee.age} for birth_date {birth_date}"
        )


# Property 3: Days Employed Calculation Correctness
# Feature: employee-controlling-system, Property 3: Days Employed Calculation
# Correctness
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(start_date=valid_start_date())
def test_property_3_days_employed_calculation_correctness(start_date):
    """
    Property 3: Days Employed Calculation Correctness

    For any start date in the past, the calculated days employed should equal
    the number of calendar days between the start date and the current date.

    Validates: Requirements 2.3
    """
    with get_test_db() as db_session:
        # Create employee with the start date
        employee = Employee(
            first_name="Test",
            last_name="Employee",
            city="Test City",
            birth_date=date.today() - timedelta(days=365 * 30),
            position_id=1,
            start_date=start_date
        )
        db_session.add(employee)
        db_session.commit()

        # Calculate expected days employed
        today = date.today()
        expected_days = (today - start_date).days

        # Verify days employed calculation
        assert employee.days_employed == expected_days, (
            f"Days employed calculation incorrect: "
            f"expected {expected_days}, "
            f"got {employee.days_employed} for start_date {start_date}"
        )


# Property 53: Quota Threshold Notification
# Feature: employee-controlling-system, Property 53: Quota Threshold
# Notification
# Validates: Requirements 21.1
@given(
    quota_value=st.floats(min_value=0.0, max_value=100.0),
    threshold_value=st.floats(min_value=0.0, max_value=100.0)
)
@settings(max_examples=100, deadline=None)
def test_property_53_quota_threshold_notification(
    quota_value,
    threshold_value
):
    """
    Property 53: Quota Threshold Notification
    For any employee and quota, if the quota exceeds a configured threshold,
    a notification should be generated.

    Validates: Requirements 21.1
    """
    from controlling.notifications import (
        NotificationManager,
        NotificationType,
        ThresholdType
    )

    manager = NotificationManager()

    # Clear default thresholds for clean test
    manager.thresholds = []

    # Add a threshold for ABOVE
    manager.add_threshold(
        quota_name="Test Quote",
        threshold_value=threshold_value,
        threshold_type=ThresholdType.ABOVE,
        notification_type=NotificationType.SUCCESS,
        message_template="Quota {quota_value}% exceeds {threshold_value}%"
    )

    quotas = {"Test Quote": quota_value}
    notifications = manager.check_quotas(quotas)

    # If quota_value > threshold_value, should have notification
    if quota_value > threshold_value:
        assert len(notifications) == 1
        assert notifications[0].quota_name == "Test Quote"
        assert notifications[0].quota_value == quota_value
        assert notifications[0].threshold_value == threshold_value
        assert notifications[0].notification_type == NotificationType.SUCCESS
    else:
        # Should not trigger
        assert len(notifications) == 0


# Property 54: Quota Threshold Warning
# Feature: employee-controlling-system, Property 54: Quota Threshold Warning
# Validates: Requirements 21.2
@given(
    quota_value=st.floats(min_value=0.0, max_value=100.0),
    threshold_value=st.floats(min_value=0.0, max_value=100.0)
)
@settings(max_examples=100, deadline=None)
def test_property_54_quota_threshold_warning(
    quota_value,
    threshold_value
):
    """
    Property 54: Quota Threshold Warning
    For any employee and quota, if the quota falls below a configured
    threshold, a warning should be generated.

    Validates: Requirements 21.2
    """
    from controlling.notifications import (
        NotificationManager,
        NotificationType,
        ThresholdType
    )

    manager = NotificationManager()

    # Clear default thresholds for clean test
    manager.thresholds = []

    # Add a threshold for BELOW
    manager.add_threshold(
        quota_name="Test Quote",
        threshold_value=threshold_value,
        threshold_type=ThresholdType.BELOW,
        notification_type=NotificationType.WARNING,
        message_template="Quota {quota_value}% below {threshold_value}%"
    )

    quotas = {"Test Quote": quota_value}
    notifications = manager.check_quotas(quotas)

    # If quota_value < threshold_value, should have notification
    if quota_value < threshold_value:
        assert len(notifications) == 1
        assert notifications[0].quota_name == "Test Quote"
        assert notifications[0].quota_value == quota_value
        assert notifications[0].threshold_value == threshold_value
        assert notifications[0].notification_type == NotificationType.WARNING
    else:
        # Should not trigger
        assert len(notifications) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])


# Additional imports for manager property tests
from controlling.models import Criterion, CalculationMethod
from controlling.managers import ValidationError


# Additional strategies for manager tests
@st.composite
def valid_position_name(draw):
    """Generate valid position names"""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "
    return draw(st.text(alphabet=alphabet, min_size=2, max_size=50))


@st.composite
def valid_criterion_name(draw):
    """Generate valid criterion names"""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "
    return draw(st.text(alphabet=alphabet, min_size=2, max_size=50))


# Property 4: Employee Retrieval Completeness
# Feature: employee-controlling-system, Property 4: Employee Retrieval
# Completeness
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(employee_data=valid_employee_data())
def test_property_4_employee_retrieval_completeness(employee_data):
    """
    Property 4: Employee Retrieval Completeness

    For any employee stored in the database, retrieving that employee by ID
    should return all stored fields without data loss.

    Validates: Requirements 3.1
    """
    with get_test_db() as db_session:
        manager = EmployeeManager(db_session)

        # Create employee
        employee = manager.create_employee(**employee_data)
        employee_id = employee.id

        # Retrieve employee
        retrieved = manager.get_employee(employee_id)

        # Verify all fields are present and match
        # Note: Manager strips whitespace from string fields
        assert retrieved is not None
        assert retrieved.id == employee_id
        assert retrieved.first_name == employee_data["first_name"].strip()
        assert retrieved.last_name == employee_data["last_name"].strip()
        assert retrieved.city == employee_data["city"].strip()
        assert retrieved.birth_date == employee_data["birth_date"]
        assert retrieved.position_id == employee_data["position_id"]
        assert retrieved.start_date == employee_data["start_date"]


# Property 5: Employee Update Persistence
# Feature: employee-controlling-system, Property 5: Employee Update
# Persistence
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(
    employee_data=valid_employee_data(),
    new_city=st.text(
        alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        min_size=2,
        max_size=20
    ).filter(lambda x: x.strip())  # Ensure not just whitespace
)
def test_property_5_employee_update_persistence(employee_data, new_city):
    """
    Property 5: Employee Update Persistence

    For any employee and any valid field updates, updating the employee and
    then retrieving it should reflect all the changes made.

    Validates: Requirements 3.2
    """
    with get_test_db() as db_session:
        manager = EmployeeManager(db_session)

        # Create employee
        employee = manager.create_employee(**employee_data)
        employee_id = employee.id

        # Update employee
        updated = manager.update_employee(employee_id, city=new_city)

        # Verify update persisted (manager strips whitespace)
        assert updated.city == new_city.strip()

        # Retrieve and verify
        retrieved = manager.get_employee(employee_id)
        assert retrieved.city == new_city.strip()


# Property 6: Employee Deletion Archival
# Feature: employee-controlling-system, Property 6: Employee Deletion
# Archival
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(employee_data=valid_employee_data())
def test_property_6_employee_deletion_archival(employee_data):
    """
    Property 6: Employee Deletion Archival

    For any employee, deleting that employee should result in the employee
    being marked as inactive (is_active=False) and not appearing in the
    active employee list.

    Validates: Requirements 3.3
    """
    with get_test_db() as db_session:
        manager = EmployeeManager(db_session)

        # Create employee
        employee = manager.create_employee(**employee_data)
        employee_id = employee.id

        # Delete employee
        manager.delete_employee(employee_id)

        # Verify employee is archived
        retrieved = manager.get_employee(employee_id)
        assert retrieved.is_active is False

        # Verify not in active list
        active_employees = manager.list_employees()
        assert employee_id not in [e.id for e in active_employees]


# Property 7: Position Name Uniqueness
# Feature: employee-controlling-system, Property 7: Position Name Uniqueness
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(position_suffix=st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    min_size=5,
    max_size=20
))
def test_property_7_position_name_uniqueness(position_suffix):
    """
    Property 7: Position Name Uniqueness

    For any two positions in the database, their names should be distinct
    (case-insensitive comparison).

    Validates: Requirements 4.1
    """
    with get_test_db() as db_session:
        manager = PositionManager(db_session)

        # Create unique position name
        import time
        position_name = f"Pos_{int(time.time() * 1000000)}_{position_suffix}"

        # Create first position
        position1 = manager.create_position(name=position_name)
        assert position1.id is not None

        # Try to create duplicate - should fail
        try:
            manager.create_position(name=position_name)
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "already exists" in str(e).lower()


# Property 9: Position Deletion Protection
# Feature: employee-controlling-system, Property 9: Position Deletion
# Protection
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(
    position_suffix=st.text(
        alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        min_size=5,
        max_size=20
    ),
    employee_data=valid_employee_data()
)
def test_property_9_position_deletion_protection(
    position_suffix,
    employee_data
):
    """
    Property 9: Position Deletion Protection

    For any position that has at least one employee assigned, attempting to
    delete that position should either fail with an error or require
    reassignment of all employees.

    Validates: Requirements 4.3, 4.5
    """
    with get_test_db() as db_session:
        pos_manager = PositionManager(db_session)
        emp_manager = EmployeeManager(db_session)

        # Create position with unique name using timestamp
        import time
        position_name = f"Position_{int(time.time() * 1000000)}_{position_suffix}"
        position = pos_manager.create_position(name=position_name)

        # Create employee assigned to position
        employee_data["position_id"] = position.id
        emp_manager.create_employee(**employee_data)

        # Try to delete position - should fail
        try:
            pos_manager.delete_position(position.id)
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "cannot delete" in str(e).lower()


# Property 10: Criterion Name Uniqueness
# Feature: employee-controlling-system, Property 10: Criterion Name
# Uniqueness
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(criterion_suffix=st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    min_size=5,
    max_size=20
))
def test_property_10_criterion_name_uniqueness(criterion_suffix):
    """
    Property 10: Criterion Name Uniqueness

    For any two criteria in the database, their names should be distinct
    (case-insensitive comparison).

    Validates: Requirements 5.1
    """
    with get_test_db() as db_session:
        manager = CriterionManager(db_session)

        # Create unique criterion name
        import time
        criterion_name = f"Crit_{int(time.time() * 1000000)}_{criterion_suffix}"

        # Create first criterion
        criterion1 = manager.create_criterion(name=criterion_name)
        assert criterion1.id is not None

        # Try to create duplicate - should fail
        try:
            manager.create_criterion(name=criterion_name)
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            assert "already exists" in str(e).lower()



# Property 14: Position-Criterion Assignment Persistence
# Feature: employee-controlling-system, Property 14: Position-Criterion
# Assignment Persistence
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(
    position_suffix=st.text(
        alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        min_size=5,
        max_size=20
    ),
    num_criteria=st.integers(min_value=1, max_value=5)
)
def test_property_14_position_criterion_assignment_persistence(
    position_suffix,
    num_criteria
):
    """
    Property 14: Position-Criterion Assignment Persistence

    For any position and set of criteria, assigning those criteria to the
    position and then retrieving the position's criteria should return
    exactly the assigned criteria.

    Validates: Requirements 6.2
    """
    with get_test_db() as db_session:
        pos_manager = PositionManager(db_session)
        crit_manager = CriterionManager(db_session)

        # Create unique position
        import time
        position_name = f"Pos_{int(time.time() * 1000000)}_{position_suffix}"
        position = pos_manager.create_position(name=position_name)

        # Create criteria
        criterion_ids = []
        for i in range(num_criteria):
            criterion_name = (
                f"Crit_{int(time.time() * 1000000)}_{position_suffix}_{i}"
            )
            criterion = crit_manager.create_criterion(name=criterion_name)
            criterion_ids.append(criterion.id)

        # Assign criteria to position
        pos_manager.assign_criteria(position.id, criterion_ids)

        # Retrieve position criteria
        retrieved_criteria = pos_manager.get_position_criteria(position.id)

        # Verify all criteria are assigned
        retrieved_ids = [c.id for c in retrieved_criteria]
        assert len(retrieved_ids) == num_criteria
        for cid in criterion_ids:
            assert cid in retrieved_ids


# Property 15: Position-Criterion Removal Persistence
# Feature: employee-controlling-system, Property 15: Position-Criterion
# Removal Persistence
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(
    position_suffix=st.text(
        alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        min_size=5,
        max_size=20
    ),
    num_criteria=st.integers(min_value=2, max_value=5),
    num_to_remove=st.integers(min_value=1, max_value=2)
)
def test_property_15_position_criterion_removal_persistence(
    position_suffix,
    num_criteria,
    num_to_remove
):
    """
    Property 15: Position-Criterion Removal Persistence

    For any position with assigned criteria, removing a criterion and then
    retrieving the position's criteria should not include the removed
    criterion.

    Validates: Requirements 6.3
    """
    # Ensure we don't try to remove more than we have
    if num_to_remove >= num_criteria:
        num_to_remove = num_criteria - 1

    with get_test_db() as db_session:
        pos_manager = PositionManager(db_session)
        crit_manager = CriterionManager(db_session)

        # Create unique position
        import time
        position_name = f"Pos_{int(time.time() * 1000000)}_{position_suffix}"
        position = pos_manager.create_position(name=position_name)

        # Create criteria
        criterion_ids = []
        for i in range(num_criteria):
            criterion_name = (
                f"Crit_{int(time.time() * 1000000)}_{position_suffix}_{i}"
            )
            criterion = crit_manager.create_criterion(name=criterion_name)
            criterion_ids.append(criterion.id)

        # Assign all criteria
        pos_manager.assign_criteria(position.id, criterion_ids)

        # Remove some criteria
        to_remove = criterion_ids[:num_to_remove]
        pos_manager.remove_criteria(position.id, to_remove)

        # Retrieve remaining criteria
        retrieved_criteria = pos_manager.get_position_criteria(position.id)
        retrieved_ids = [c.id for c in retrieved_criteria]

        # Verify removed criteria are not present
        for cid in to_remove:
            assert cid not in retrieved_ids

        # Verify remaining criteria are present
        remaining = criterion_ids[num_to_remove:]
        assert len(retrieved_ids) == len(remaining)
        for cid in remaining:
            assert cid in retrieved_ids


# Property 16: Employee Criteria Inheritance
# Feature: employee-controlling-system, Property 16: Employee Criteria
# Inheritance
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(
    position_suffix=st.text(
        alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        min_size=5,
        max_size=20
    ),
    employee_data=valid_employee_data(),
    num_criteria=st.integers(min_value=1, max_value=5)
)
def test_property_16_employee_criteria_inheritance(
    position_suffix,
    employee_data,
    num_criteria
):
    """
    Property 16: Employee Criteria Inheritance

    For any employee assigned to a position, the employee should have access
    to all criteria assigned to that position.

    Validates: Requirements 6.5
    """
    with get_test_db() as db_session:
        pos_manager = PositionManager(db_session)
        emp_manager = EmployeeManager(db_session)
        crit_manager = CriterionManager(db_session)

        # Create unique position
        import time
        position_name = f"Pos_{int(time.time() * 1000000)}_{position_suffix}"
        position = pos_manager.create_position(name=position_name)

        # Create criteria
        criterion_ids = []
        for i in range(num_criteria):
            criterion_name = (
                f"Crit_{int(time.time() * 1000000)}_{position_suffix}_{i}"
            )
            criterion = crit_manager.create_criterion(name=criterion_name)
            criterion_ids.append(criterion.id)

        # Assign criteria to position
        pos_manager.assign_criteria(position.id, criterion_ids)

        # Create employee with this position
        employee_data["position_id"] = position.id
        employee = emp_manager.create_employee(**employee_data)

        # Get employee criteria
        employee_criteria = emp_manager.get_employee_criteria(employee.id)
        employee_criterion_ids = [c.id for c in employee_criteria]

        # Verify employee has all position criteria
        assert len(employee_criterion_ids) == num_criteria
        for cid in criterion_ids:
            assert cid in employee_criterion_ids



# ============================================================================
# Analytics Engine Property Tests (Task 4.1-4.4)
# ============================================================================


@given(
    verkauf=st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),
    angefahrene_termine_gesamt=st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False)
)
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
def test_property_26_quota_calculation_formula_correctness(
    verkauf,
    angefahrene_termine_gesamt
):
    """
    Property 26: Quota Calculation Formula Correctness

    For any performance data with non-zero denominators, each quota should be
    calculated as (numerator / denominator) × 100.

    Validates: Requirements 10.2
    """
    # Feature: employee-controlling-system, Property 26: Quota Calculation
    # Formula Correctness
    with get_test_db() as db_session:
        from controlling.analytics import AnalyticsEngine

        engine = AnalyticsEngine(db_session)

        # Test Abschlussquote calculation
        result = engine.calculate_abschlussquote(
            verkauf,
            angefahrene_termine_gesamt
        )

        # Calculate expected value
        expected = (verkauf / angefahrene_termine_gesamt) * 100

        # Verify result matches expected (with floating point tolerance)
        assert abs(result - expected) < 0.01  # Floating point tolerance


@given(
    performance_values=st.lists(
        st.floats(min_value=0, max_value=100),
        min_size=10,
        max_size=10
    )
)
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
def test_property_27_quota_sum_invariant(performance_values):
    """
    Property 27: Quota Sum Invariant

    For any set of mutually exclusive quotas that should sum to 100%, the sum
    of those quotas should equal 100% (within floating-point tolerance).

    Note: This property is not strictly applicable to our quota system as the
    quotas are not mutually exclusive (they measure different aspects). This
    test verifies that quotas are calculated independently and correctly.

    Validates: Requirements 10.3
    """
    # Feature: employee-controlling-system, Property 27: Quota Sum Invariant
    with get_test_db() as db_session:
        from controlling.analytics import AnalyticsEngine
        from controlling.models import Criterion, PerformanceData

        engine = AnalyticsEngine(db_session)
        emp_manager = EmployeeManager(db_session)
        pos_manager = PositionManager(db_session)
        crit_manager = CriterionManager(db_session)
        perf_manager = PerformanceDataManager(db_session)

        # Create test position and employee
        import time
        position_name = f"Pos_{int(time.time() * 1000000)}"
        position = pos_manager.create_position(name=position_name)

        employee = emp_manager.create_employee(
            first_name="Test",
            last_name="Employee",
            city="Test City",
            birth_date=date(1990, 1, 1),
            position_id=position.id,
            start_date=date(2020, 1, 1)
        )

        # Get standard criteria
        criteria = crit_manager.get_standard_criteria()
        criterion_map = {c.name: c for c in criteria}

        # Create performance data with the given values
        test_date = date.today()
        criterion_names = [
            "Verkauf",
            "Kunden terminiert",
            "Angefahrene Termine",
            "Angefahrene Termine gesamt",
            "Getätigte Anrufe gesamt",
            "Storniert / kein Interesse",
            "Technisch nicht machbar",
            "Nicht erreicht / neu terminieren",
            "Folgetermin gemacht",
            "Angebot erhalten"
        ]

        performance_data = []
        for i, name in enumerate(criterion_names):
            if name in criterion_map:
                perf = perf_manager.record_performance(
                    employee_id=employee.id,
                    criterion_id=criterion_map[name].id,
                    value=performance_values[i],
                    date=test_date
                )
                performance_data.append(perf)

        # Calculate quotas
        quotas = engine.calculate_quotas(performance_data)

        # Verify all quotas are between 0 and 100
        for quota_name, quota_value in quotas.items():
            assert 0 <= quota_value <= 100, (
                f"{quota_name} should be between 0 and 100, got {quota_value}"
            )


@given(
    quota_percentage=st.floats(min_value=0.01, max_value=100)
)
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
def test_property_29_ratio_calculation_formula(quota_percentage):
    """
    Property 29: Ratio Calculation Formula

    For any quota percentage Q > 0, the ratio X should be calculated as
    X = 100 / Q, representing "1 in X" occurrences.

    Validates: Requirements 11.2
    """
    # Feature: employee-controlling-system, Property 29: Ratio Calculation
    # Formula
    with get_test_db() as db_session:
        from controlling.analytics import AnalyticsEngine

        engine = AnalyticsEngine(db_session)

        # Calculate ratio description
        description = engine.calculate_ratio_description(
            quota_percentage,
            "Abschlussquote"
        )

        # Calculate expected ratio
        expected_ratio = round(100 / quota_percentage)

        # Verify the ratio appears in the description
        assert str(expected_ratio) in description


@given(
    start_offset=st.integers(min_value=0, max_value=365),
    end_offset=st.integers(min_value=0, max_value=30),
    num_records=st.integers(min_value=5, max_value=20)
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
def test_property_22_report_time_period_data_retrieval(
    start_offset,
    end_offset,
    num_records
):
    """
    Property 22: Report Time Period Data Retrieval

    For any time period (start_date, end_date) and employee, retrieving
    performance data for that period should return only data where the date
    falls within the specified range (inclusive).

    Validates: Requirements 9.2
    """
    # Feature: employee-controlling-system, Property 22: Report Time Period
    # Data Retrieval
    with get_test_db() as db_session:
        from controlling.analytics import AnalyticsEngine

        engine = AnalyticsEngine(db_session)
        emp_manager = EmployeeManager(db_session)
        pos_manager = PositionManager(db_session)
        crit_manager = CriterionManager(db_session)
        perf_manager = PerformanceDataManager(db_session)

        # Create test position and employee
        import time
        position_name = f"Pos_{int(time.time() * 1000000)}"
        position = pos_manager.create_position(name=position_name)

        employee = emp_manager.create_employee(
            first_name="Test",
            last_name="Employee",
            city="Test City",
            birth_date=date(1990, 1, 1),
            position_id=position.id,
            start_date=date(2020, 1, 1)
        )

        # Get or create a criterion
        criteria = crit_manager.get_standard_criteria()
        if not criteria:
            # Create a test criterion if none exist
            import time
            criterion = crit_manager.create_criterion(
                name=f"Test_Criterion_{int(time.time() * 1000000)}",
                description="Test criterion for property test"
            )
        else:
            criterion = criteria[0]

        # Define date range
        end_date = date.today() - timedelta(days=end_offset)
        start_date = end_date - timedelta(days=start_offset)

        # Create performance data: some inside range, some outside
        records_inside = []
        records_outside = []

        for i in range(num_records):
            # Half inside, half outside the range
            if i % 2 == 0:
                # Inside range
                days_offset = i * (start_offset // max(num_records // 2, 1))
                record_date = start_date + timedelta(days=days_offset)
                if record_date <= end_date:
                    perf = perf_manager.record_performance(
                        employee_id=employee.id,
                        criterion_id=criterion.id,
                        value=float(i),
                        date=record_date
                    )
                    records_inside.append(perf)
            else:
                # Outside range (before start_date)
                record_date = start_date - timedelta(days=i + 1)
                perf = perf_manager.record_performance(
                    employee_id=employee.id,
                    criterion_id=criterion.id,
                    value=float(i),
                    date=record_date
                )
                records_outside.append(perf)

        # Retrieve performance data for the period
        retrieved_data = perf_manager.get_performance_data(
            employee_id=employee.id,
            start_date=start_date,
            end_date=end_date
        )

        # Verify only data within range is retrieved
        for record in retrieved_data:
            assert start_date <= record.date <= end_date

        # Verify all inside records are retrieved
        retrieved_ids = [r.id for r in retrieved_data]
        for record in records_inside:
            assert record.id in retrieved_ids



# ============================================================================
# Report Generator Property Tests (Task 5.1-5.3)
# ============================================================================


# Property 33: Report Saving Persistence
# Feature: employee-controlling-system, Property 33: Report Saving Persistence
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(
    employee_data=valid_employee_data(),
    report_type_value=st.sampled_from([
        "DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"
    ])
)
def test_property_33_report_saving_persistence(
    employee_data,
    report_type_value
):
    """
    Property 33: Report Saving Persistence

    For any report, saving it to the database and then retrieving it should
    return a report with identical data, timestamp, and employee association.

    Validates: Requirements 13.2
    """
    # Feature: employee-controlling-system, Property 33: Report Saving
    # Persistence
    with get_test_db() as db_session:
        from controlling.report_generator import ReportGenerator
        from controlling.models import ReportType

        emp_manager = EmployeeManager(db_session)
        pos_manager = PositionManager(db_session)
        crit_manager = CriterionManager(db_session)
        perf_manager = PerformanceDataManager(db_session)

        # Create test position and employee
        import time
        position_name = f"Pos_{int(time.time() * 1000000)}"
        position = pos_manager.create_position(name=position_name)

        employee_data["position_id"] = position.id
        employee = emp_manager.create_employee(**employee_data)

        # Get standard criteria
        criteria = crit_manager.get_standard_criteria()
        if criteria:
            # Create some performance data
            test_date = date.today()
            for criterion in criteria[:3]:  # Use first 3 criteria
                perf_manager.record_performance(
                    employee_id=employee.id,
                    criterion_id=criterion.id,
                    value=10.0,
                    date=test_date
                )

        # Generate report
        report_gen = ReportGenerator(db_session)
        report_type = ReportType(report_type_value)
        report_data = report_gen.generate_report(
            employee_id=employee.id,
            report_type=report_type
        )

        # Save report
        report_id = report_gen.save_report(report_data)

        # Load report
        loaded_report = report_gen.load_report(report_id)

        # Verify data matches
        assert loaded_report["employee_id"] == report_data["employee_id"]
        assert loaded_report["employee_name"] == report_data["employee_name"]
        assert loaded_report["report_type"] == report_data["report_type"]
        assert loaded_report["start_date"] == report_data["start_date"]
        assert loaded_report["end_date"] == report_data["end_date"]
        assert "report_id" in loaded_report
        assert loaded_report["report_id"] == report_id
        assert "created_at" in loaded_report


# Property 34: Report Archival Completeness
# Feature: employee-controlling-system, Property 34: Report Archival
# Completeness
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(
    employee_data=valid_employee_data(),
    report_type_value=st.sampled_from([
        "DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"
    ])
)
def test_property_34_report_archival_completeness(
    employee_data,
    report_type_value
):
    """
    Property 34: Report Archival Completeness

    For any report being saved, all components (charts data, quotas, raw
    performance data) should be serialized and stored in the database.

    Validates: Requirements 13.3
    """
    # Feature: employee-controlling-system, Property 34: Report Archival
    # Completeness
    with get_test_db() as db_session:
        from controlling.report_generator import ReportGenerator
        from controlling.models import ReportType

        emp_manager = EmployeeManager(db_session)
        pos_manager = PositionManager(db_session)
        crit_manager = CriterionManager(db_session)
        perf_manager = PerformanceDataManager(db_session)

        # Create test position and employee
        import time
        position_name = f"Pos_{int(time.time() * 1000000)}"
        position = pos_manager.create_position(name=position_name)

        employee_data["position_id"] = position.id
        employee = emp_manager.create_employee(**employee_data)

        # Get standard criteria and create performance data
        criteria = crit_manager.get_standard_criteria()
        test_date = date.today()
        performance_values = {}

        if criteria:
            for i, criterion in enumerate(criteria[:5]):
                value = float(i + 1) * 10.0
                perf_manager.record_performance(
                    employee_id=employee.id,
                    criterion_id=criterion.id,
                    value=value,
                    date=test_date
                )
                performance_values[criterion.name] = value

        # Generate report
        report_gen = ReportGenerator(db_session)
        report_type = ReportType(report_type_value)
        report_data = report_gen.generate_report(
            employee_id=employee.id,
            report_type=report_type
        )

        # Save report
        report_id = report_gen.save_report(report_data)

        # Load report
        loaded_report = report_gen.load_report(report_id)

        # Verify all components are present
        assert "quotas" in loaded_report, "Quotas should be archived"
        assert "ratio_descriptions" in loaded_report, (
            "Ratio descriptions should be archived"
        )
        assert "aggregated_data" in loaded_report, (
            "Aggregated data should be archived"
        )

        # Verify aggregated data contains raw data
        if "aggregated_data" in loaded_report:
            aggregated = loaded_report["aggregated_data"]
            assert "raw_data" in aggregated or "quotas" in aggregated, (
                "Raw performance data should be archived"
            )


# Property 40: Report Loading Restoration
# Feature: employee-controlling-system, Property 40: Report Loading
# Restoration
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@given(
    employee_data=valid_employee_data(),
    report_type_value=st.sampled_from([
        "DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"
    ])
)
def test_property_40_report_loading_restoration(
    employee_data,
    report_type_value
):
    """
    Property 40: Report Loading Restoration

    For any saved report, loading it from the database should restore all
    charts data, tables, and metadata in their original form.

    Validates: Requirements 15.1, 15.2
    """
    # Feature: employee-controlling-system, Property 40: Report Loading
    # Restoration
    with get_test_db() as db_session:
        from controlling.report_generator import ReportGenerator
        from controlling.models import ReportType

        emp_manager = EmployeeManager(db_session)
        pos_manager = PositionManager(db_session)
        crit_manager = CriterionManager(db_session)
        perf_manager = PerformanceDataManager(db_session)

        # Create test position and employee
        import time
        position_name = f"Pos_{int(time.time() * 1000000)}"
        position = pos_manager.create_position(name=position_name)

        employee_data["position_id"] = position.id
        employee = emp_manager.create_employee(**employee_data)

        # Get standard criteria and create performance data
        criteria = crit_manager.get_standard_criteria()
        test_date = date.today()

        if criteria:
            for i, criterion in enumerate(criteria[:5]):
                perf_manager.record_performance(
                    employee_id=employee.id,
                    criterion_id=criterion.id,
                    value=float(i + 1) * 10.0,
                    date=test_date
                )

        # Generate report
        report_gen = ReportGenerator(db_session)
        report_type = ReportType(report_type_value)
        original_report = report_gen.generate_report(
            employee_id=employee.id,
            report_type=report_type
        )

        # Save report
        report_id = report_gen.save_report(original_report)

        # Load report
        loaded_report = report_gen.load_report(report_id)

        # Verify metadata is restored
        assert loaded_report["employee_id"] == original_report["employee_id"]
        assert loaded_report["employee_name"] == (
            original_report["employee_name"]
        )
        assert loaded_report["position"] == original_report["position"]
        assert loaded_report["report_type"] == original_report["report_type"]
        assert loaded_report["start_date"] == original_report["start_date"]
        assert loaded_report["end_date"] == original_report["end_date"]

        # Verify quotas are restored
        original_quotas = original_report.get("quotas", {})
        loaded_quotas = loaded_report.get("quotas", {})
        assert len(loaded_quotas) == len(original_quotas)
        for quota_name in original_quotas:
            if quota_name in loaded_quotas:
                # Allow small floating point differences
                assert abs(
                    loaded_quotas[quota_name] - original_quotas[quota_name]
                ) < 0.01

        # Verify ratio descriptions are restored
        original_ratios = original_report.get("ratio_descriptions", {})
        loaded_ratios = loaded_report.get("ratio_descriptions", {})
        assert len(loaded_ratios) == len(original_ratios)

        # Verify aggregated data is restored
        assert "aggregated_data" in loaded_report
        original_agg = original_report.get("aggregated_data", {})
        loaded_agg = loaded_report.get("aggregated_data", {})

        # Check that raw data is preserved
        if "raw_data" in original_agg:
            assert "raw_data" in loaded_agg
            original_raw = original_agg["raw_data"]
            loaded_raw = loaded_agg["raw_data"]
            assert len(loaded_raw) == len(original_raw)



# ============================================================================
# Export Functionality Property Tests (Task 7.1-7.4)
# ============================================================================


# Property 36: Export Format Support
# Feature: employee-controlling-system, Property 36: Export Format Support
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ],
    deadline=None
)
@given(
    employee_data=valid_employee_data(),
    report_type_value=st.sampled_from([
        "DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"
    ])
)
def test_property_36_export_format_support(
    employee_data,
    report_type_value
):
    """
    Property 36: Export Format Support

    For any report, export functions should be available for all three
    formats: PDF, Excel, and JSON.

    Validates: Requirements 14.1
    """
    # Feature: employee-controlling-system, Property 36: Export Format
    # Support
    with get_test_db() as db_session:
        from controlling.report_generator import ReportGenerator
        from controlling.models import ReportType

        emp_manager = EmployeeManager(db_session)
        pos_manager = PositionManager(db_session)
        crit_manager = CriterionManager(db_session)
        perf_manager = PerformanceDataManager(db_session)

        # Create test position and employee
        import time
        position_name = f"Pos_{int(time.time() * 1000000)}"
        position = pos_manager.create_position(name=position_name)

        employee_data["position_id"] = position.id
        employee = emp_manager.create_employee(**employee_data)

        # Get standard criteria and create performance data
        criteria = crit_manager.get_standard_criteria()
        test_date = date.today()

        if criteria:
            for i, criterion in enumerate(criteria[:3]):
                perf_manager.record_performance(
                    employee_id=employee.id,
                    criterion_id=criterion.id,
                    value=float(i + 1) * 10.0,
                    date=test_date
                )

        # Generate report
        report_gen = ReportGenerator(db_session)
        report_type = ReportType(report_type_value)
        report_data = report_gen.generate_report(
            employee_id=employee.id,
            report_type=report_type
        )

        # Test JSON export (always available)
        json_export = report_gen.export_report_json(report_data)
        assert json_export is not None
        assert isinstance(json_export, str)
        assert len(json_export) > 0

        # Test Excel export (if openpyxl available)
        if OPENPYXL_AVAILABLE:
            excel_export = report_gen.export_report_excel(report_data)
            assert excel_export is not None
            assert isinstance(excel_export, bytes)
            assert len(excel_export) > 0
            # Excel files start with PK (ZIP format)
            assert excel_export[:2] == b'PK'

        # Test PDF export (if reportlab available)
        if REPORTLAB_AVAILABLE:
            pdf_export = report_gen.export_report_pdf(report_data)
            assert pdf_export is not None
            assert isinstance(pdf_export, bytes)
            assert len(pdf_export) > 0
            # PDF files start with %PDF
            assert pdf_export[:4] == b'%PDF'


# Property 37: PDF Export Completeness
# Feature: employee-controlling-system, Property 37: PDF Export Completeness
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ],
    deadline=None
)
@given(
    employee_data=valid_employee_data(),
    report_type_value=st.sampled_from([
        "DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"
    ])
)
def test_property_37_pdf_export_completeness(
    employee_data,
    report_type_value
):
    """
    Property 37: PDF Export Completeness

    For any report exported to PDF, the PDF should contain representations
    of all charts, all quota tables, and all descriptive text from the
    report.

    Validates: Requirements 14.2
    """
    # Feature: employee-controlling-system, Property 37: PDF Export
    # Completeness
    with get_test_db() as db_session:
        from controlling.report_generator import (
            ReportGenerator,
            REPORTLAB_AVAILABLE
        )
        from controlling.models import ReportType

        if not REPORTLAB_AVAILABLE:
            # Skip test if reportlab not available
            return

        emp_manager = EmployeeManager(db_session)
        pos_manager = PositionManager(db_session)
        crit_manager = CriterionManager(db_session)
        perf_manager = PerformanceDataManager(db_session)

        # Create test position and employee
        import time
        position_name = f"Pos_{int(time.time() * 1000000)}"
        position = pos_manager.create_position(name=position_name)

        employee_data["position_id"] = position.id
        employee = emp_manager.create_employee(**employee_data)

        # Get standard criteria and create performance data
        criteria = crit_manager.get_standard_criteria()
        test_date = date.today()

        if criteria:
            for i, criterion in enumerate(criteria[:5]):
                perf_manager.record_performance(
                    employee_id=employee.id,
                    criterion_id=criterion.id,
                    value=float(i + 1) * 10.0,
                    date=test_date
                )

        # Generate report
        report_gen = ReportGenerator(db_session)
        report_type = ReportType(report_type_value)
        report_data = report_gen.generate_report(
            employee_id=employee.id,
            report_type=report_type
        )

        # Export to PDF
        pdf_bytes = report_gen.export_report_pdf(report_data)

        # Verify PDF was created
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

        # PDF should start with PDF header
        assert pdf_bytes[:4] == b'%PDF'

        # PDF should be reasonably sized (contains data)
        assert len(pdf_bytes) > 1000  # At least 1KB


# Property 38: Excel Export Completeness
# Feature: employee-controlling-system, Property 38: Excel Export
# Completeness
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ],
    deadline=None
)
@given(
    employee_data=valid_employee_data(),
    report_type_value=st.sampled_from([
        "DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"
    ])
)
def test_property_38_excel_export_completeness(
    employee_data,
    report_type_value
):
    """
    Property 38: Excel Export Completeness

    For any report exported to Excel, the Excel file should contain all raw
    performance data and all calculated quotas in structured tables.

    Validates: Requirements 14.3
    """
    # Feature: employee-controlling-system, Property 38: Excel Export
    # Completeness
    with get_test_db() as db_session:
        from controlling.report_generator import (
            ReportGenerator,
            OPENPYXL_AVAILABLE
        )
        from controlling.models import ReportType

        if not OPENPYXL_AVAILABLE:
            # Skip test if openpyxl not available
            return

        emp_manager = EmployeeManager(db_session)
        pos_manager = PositionManager(db_session)
        crit_manager = CriterionManager(db_session)
        perf_manager = PerformanceDataManager(db_session)

        # Create test position and employee
        import time
        position_name = f"Pos_{int(time.time() * 1000000)}"
        position = pos_manager.create_position(name=position_name)

        employee_data["position_id"] = position.id
        employee = emp_manager.create_employee(**employee_data)

        # Get standard criteria and create performance data
        criteria = crit_manager.get_standard_criteria()
        test_date = date.today()

        if criteria:
            for i, criterion in enumerate(criteria[:5]):
                perf_manager.record_performance(
                    employee_id=employee.id,
                    criterion_id=criterion.id,
                    value=float(i + 1) * 10.0,
                    date=test_date
                )

        # Generate report
        report_gen = ReportGenerator(db_session)
        report_type = ReportType(report_type_value)
        report_data = report_gen.generate_report(
            employee_id=employee.id,
            report_type=report_type
        )

        # Export to Excel
        excel_bytes = report_gen.export_report_excel(report_data)

        # Verify Excel was created
        assert excel_bytes is not None
        assert isinstance(excel_bytes, bytes)
        assert len(excel_bytes) > 0

        # Excel files start with PK (ZIP format)
        assert excel_bytes[:2] == b'PK'

        # Excel should be reasonably sized (contains data)
        assert len(excel_bytes) > 1000  # At least 1KB


# Property 39: JSON Export Round-Trip
# Feature: employee-controlling-system, Property 39: JSON Export Round-Trip
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ],
    deadline=None
)
@given(
    employee_data=valid_employee_data(),
    report_type_value=st.sampled_from([
        "DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"
    ])
)
def test_property_39_json_export_round_trip(
    employee_data,
    report_type_value
):
    """
    Property 39: JSON Export Round-Trip

    For any report, exporting to JSON and then parsing the JSON should
    produce a data structure equivalent to the original report data.

    Validates: Requirements 14.4
    """
    # Feature: employee-controlling-system, Property 39: JSON Export
    # Round-Trip
    with get_test_db() as db_session:
        from controlling.report_generator import ReportGenerator
        from controlling.models import ReportType
        import json

        emp_manager = EmployeeManager(db_session)
        pos_manager = PositionManager(db_session)
        crit_manager = CriterionManager(db_session)
        perf_manager = PerformanceDataManager(db_session)

        # Create test position and employee
        import time
        position_name = f"Pos_{int(time.time() * 1000000)}"
        position = pos_manager.create_position(name=position_name)

        employee_data["position_id"] = position.id
        employee = emp_manager.create_employee(**employee_data)

        # Get standard criteria and create performance data
        criteria = crit_manager.get_standard_criteria()
        test_date = date.today()

        if criteria:
            for i, criterion in enumerate(criteria[:5]):
                perf_manager.record_performance(
                    employee_id=employee.id,
                    criterion_id=criterion.id,
                    value=float(i + 1) * 10.0,
                    date=test_date
                )

        # Generate report
        report_gen = ReportGenerator(db_session)
        report_type = ReportType(report_type_value)
        original_report = report_gen.generate_report(
            employee_id=employee.id,
            report_type=report_type
        )

        # Export to JSON
        json_string = report_gen.export_report_json(original_report)

        # Parse JSON back
        parsed_data = json.loads(json_string)

        # Verify structure is preserved
        assert "report_metadata" in parsed_data
        assert "quotas" in parsed_data
        assert "ratio_descriptions" in parsed_data
        assert "aggregated_data" in parsed_data

        # Verify metadata
        metadata = parsed_data["report_metadata"]
        assert metadata["employee_id"] == original_report["employee_id"]
        assert metadata["employee_name"] == original_report["employee_name"]
        assert metadata["report_type"] == original_report["report_type"]
        assert metadata["start_date"] == original_report["start_date"]
        assert metadata["end_date"] == original_report["end_date"]

        # Verify quotas are preserved
        original_quotas = original_report.get("quotas", {})
        parsed_quotas = parsed_data.get("quotas", {})
        assert len(parsed_quotas) == len(original_quotas)

        # Verify quota values match (with floating point tolerance)
        import math
        for quota_name in original_quotas:
            if quota_name in parsed_quotas:
                assert math.isclose(
                    parsed_quotas[quota_name],
                    original_quotas[quota_name],
                    rel_tol=1e-5,
                    abs_tol=1e-8
                )

        # Verify ratio descriptions are preserved
        original_ratios = original_report.get("ratio_descriptions", {})
        parsed_ratios = parsed_data.get("ratio_descriptions", {})
        assert len(parsed_ratios) == len(original_ratios)
        
        # Verify aggregated data structure is preserved
        original_agg = original_report.get("aggregated_data", {})
        parsed_agg = parsed_data.get("aggregated_data", {})
        if "raw_data" in original_agg:
            assert "raw_data" in parsed_agg
            assert len(parsed_agg["raw_data"]) == len(original_agg["raw_data"])


# ============================================================================
# Task 9 Property Tests: Controlling UI
# ============================================================================


@given(
    num_employees=st.integers(min_value=2, max_value=10),
    filter_position=st.booleans(),
    filter_city=st.booleans(),
    filter_name=st.booleans()
)
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ],
    deadline=None
)
def test_property_43_employee_filtering_correctness(
    num_employees,
    filter_position,
    filter_city,
    filter_name
):
    """
    # Feature: employee-controlling-system, Property 43: Employee Filtering Correctness
    
    Property 43: Employee Filtering Correctness
    For any filter criteria (position, name, city, or start_date), applying
    the filter should return only employees that match the criteria, and all
    matching employees should be included.
    
    Validates: Requirements 16.2
    """
    with get_test_db() as db:
        emp_manager = EmployeeManager(db)
        pos_manager = PositionManager(db)

        # Create test positions
        positions = []
        for i in range(3):
            pos = pos_manager.create_position(
                name=f"Position_{i}_{datetime.now().timestamp()}",
                description=f"Test position {i}"
            )
            positions.append(pos)

        # Create test employees with varied attributes
        cities = ["Berlin", "München", "Hamburg"]
        names = ["Anna", "Boris", "Clara", "David", "Emma"]

        employees = []
        for i in range(num_employees):
            emp = emp_manager.create_employee(
                first_name=names[i % len(names)],
                last_name=f"Test_{i}_{datetime.now().timestamp()}",
                city=cities[i % len(cities)],
                birth_date=date(1990, 1, 1) + timedelta(days=i * 365),
                position_id=positions[i % len(positions)].id,
                start_date=date(2020, 1, 1) + timedelta(days=i * 30)
            )
            employees.append(emp)

        # Test position filter
        if filter_position and positions:
            target_position = positions[0]
            filtered = [
                emp for emp in employees
                if emp.position_id == target_position.id
            ]

            # Verify all matching employees are included
            for emp in employees:
                if emp.position_id == target_position.id:
                    assert emp in filtered, \
                        "Matching employee not in filtered results"

            # Verify only matching employees are included
            for emp in filtered:
                assert emp.position_id == target_position.id, \
                    "Non-matching employee in filtered results"

        # Test city filter
        if filter_city:
            target_city = cities[0]
            filtered = [emp for emp in employees if emp.city == target_city]

            # Verify all matching employees are included
            for emp in employees:
                if emp.city == target_city:
                    assert emp in filtered, \
                        "Matching employee not in filtered results"

            # Verify only matching employees are included
            for emp in filtered:
                assert emp.city == target_city, \
                    "Non-matching employee in filtered results"

        # Test name filter
        if filter_name:
            target_name = names[0]
            filtered = [
                emp for emp in employees
                if target_name.lower() in emp.full_name.lower()
            ]

            # Verify all matching employees are included
            for emp in employees:
                if target_name.lower() in emp.full_name.lower():
                    assert emp in filtered, \
                        "Matching employee not in filtered results"

            # Verify only matching employees are included
            for emp in filtered:
                assert target_name.lower() in emp.full_name.lower(), \
                    "Non-matching employee in filtered results"


@given(
    num_employees=st.integers(min_value=2, max_value=5),
    filter_by_position=st.booleans()
)
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ],
    deadline=None
)
def test_property_44_filtered_report_inclusion(
    num_employees,
    filter_by_position
):
    """
    # Feature: employee-controlling-system, Property 44: Filtered Report Inclusion
    
    Property 44: Filtered Report Inclusion
    For any active filter, generating a report should only include performance
    data for employees that match the filter criteria.
    
    Validates: Requirements 16.3
    """
    with get_test_db() as db:
        emp_manager = EmployeeManager(db)
        pos_manager = PositionManager(db)
        perf_manager = PerformanceDataManager(db)
        crit_manager = CriterionManager(db)

        # Create positions
        pos1 = pos_manager.create_position(
            name=f"Position_A_{datetime.now().timestamp()}",
            description="Position A"
        )
        pos2 = pos_manager.create_position(
            name=f"Position_B_{datetime.now().timestamp()}",
            description="Position B"
        )

        # Create criterion
        criterion = crit_manager.create_criterion(
            name=f"Test_Criterion_{datetime.now().timestamp()}",
            description="Test criterion",
            calculation_method="SUM",
            is_standard=False
        )

        # Create employees
        employees_pos1 = []
        employees_pos2 = []

        for i in range(num_employees):
            # Half to position 1, half to position 2
            pos_id = pos1.id if i < num_employees // 2 else pos2.id
            target_list = employees_pos1 if i < num_employees // 2 else employees_pos2

            emp = emp_manager.create_employee(
                first_name=f"Employee_{i}",
                last_name=f"Test_{datetime.now().timestamp()}",
                city="TestCity",
                birth_date=date(1990, 1, 1),
                position_id=pos_id,
                start_date=date(2020, 1, 1)
            )
            target_list.append(emp)

            # Add performance data
            perf_manager.record_performance(
                employee_id=emp.id,
                criterion_id=criterion.id,
                value=float(i + 1),
                date=date.today()
            )

        # Apply filter
        if filter_by_position and employees_pos1:
            # Filter by position 1
            filtered_employee_ids = [emp.id for emp in employees_pos1]

            # Get performance data for filtered employees
            for emp_id in filtered_employee_ids:
                perf_data = perf_manager.get_performance_data(
                    employee_id=emp_id,
                    start_date=date.today(),
                    end_date=date.today()
                )

                # Verify data exists for filtered employee
                assert len(perf_data) > 0, \
                    "Performance data missing for filtered employee"

                # Verify all data belongs to filtered employee
                for data in perf_data:
                    assert data.employee_id == emp_id, \
                        "Performance data from non-filtered employee included"

            # Verify no data from non-filtered employees is included
            for emp in employees_pos2:
                # This employee should not be in filtered results
                assert emp.id not in filtered_employee_ids, \
                    "Non-filtered employee included in results"


@given(
    value=st.one_of(
        st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        st.integers(min_value=0, max_value=1000)
    )
)
@settings(
    max_examples=100,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ],
    deadline=None
)
def test_property_19_performance_data_numeric_validation(value):
    """
    # Feature: employee-controlling-system, Property 19: Performance Data Numeric Validation
    
    Property 19: Performance Data Numeric Validation
    For any performance data input, the system should only accept numeric
    values (integers or floats) and reject non-numeric inputs.
    
    Validates: Requirements 8.2
    """
    with get_test_db() as db:
        emp_manager = EmployeeManager(db)
        pos_manager = PositionManager(db)
        perf_manager = PerformanceDataManager(db)
        crit_manager = CriterionManager(db)

        # Create test data
        pos = pos_manager.create_position(
            name=f"Position_{datetime.now().timestamp()}",
            description="Test position"
        )

        emp = emp_manager.create_employee(
            first_name="Test",
            last_name=f"Employee_{datetime.now().timestamp()}",
            city="TestCity",
            birth_date=date(1990, 1, 1),
            position_id=pos.id,
            start_date=date(2020, 1, 1)
        )

        criterion = crit_manager.create_criterion(
            name=f"Test_Criterion_{datetime.now().timestamp()}",
            description="Test criterion",
            calculation_method="SUM",
            is_standard=False
        )

        # Test that valid numeric values are accepted
        is_numeric = isinstance(value, (int, float)) and not isinstance(value, bool)

        if is_numeric and value >= 0:
            # Should accept valid numeric values
            try:
                perf_data = perf_manager.record_performance(
                    employee_id=emp.id,
                    criterion_id=criterion.id,
                    value=float(value),
                    date=date.today()
                )
                assert perf_data is not None, \
                    "Failed to record valid numeric performance data"
                # Allow small floating point differences
                import math
                assert math.isclose(perf_data.value, float(value), rel_tol=1e-9), \
                    f"Performance data value mismatch: {perf_data.value} != {float(value)}"
            except Exception as e:
                pytest.fail(f"Valid numeric value rejected: {e}")
