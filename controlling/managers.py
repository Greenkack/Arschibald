"""
Controlling System Manager Classes

Provides CRUD operations and business logic for the Employee Controlling
System.

Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 5.1, 5.3, 5.4,
              6.2, 6.3, 8.3, 8.5
"""

import sys
import logging
from pathlib import Path
from datetime import date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from controlling.models import (  # noqa: E402
    Employee,
    Position,
    Criterion,
    PositionCriterion,
    PerformanceData,
    CalculationMethod
)

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


class EmployeeManager:
    """
    Manager for Employee CRUD operations.

    Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3
    """

    def __init__(self, db: Session):
        self.db = db

    def create_employee(
        self,
        first_name: str,
        last_name: str,
        city: str,
        birth_date: date,
        position_id: int,
        start_date: date,
        agent_name: Optional[str] = None
    ) -> Employee:
        """
        Create a new employee.

        Args:
            first_name: Employee's first name
            last_name: Employee's last name
            city: Employee's city of residence
            birth_date: Employee's birth date
            position_id: ID of the employee's position
            start_date: Employee's start date

        Returns:
            Created Employee instance

        Raises:
            ValidationError: If validation fails

        Requirements: 2.1
        """
        # Validate required fields
        if not first_name or not first_name.strip():
            raise ValidationError("First name is required")
        if not last_name or not last_name.strip():
            raise ValidationError("Last name is required")
        if not city or not city.strip():
            raise ValidationError("City is required")

        # Validate dates
        if birth_date >= date.today():
            raise ValidationError("Birth date must be in the past")
        if start_date > date.today():
            raise ValidationError("Start date cannot be in the future")

        # Validate position exists
        position = self.db.query(Position).filter(
            Position.id == position_id
        ).first()
        if not position:
            raise ValidationError(f"Position with ID {position_id} not found")

        # Create employee
        employee = Employee(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            agent_name=agent_name.strip() if agent_name else None,
            city=city.strip(),
            birth_date=birth_date,
            position_id=position_id,
            start_date=start_date
        )

        try:
            self.db.add(employee)
            self.db.commit()
            self.db.refresh(employee)
            logger.info(f"Created employee: {employee.full_name}")
            return employee
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create employee: {e}")
            raise

    def update_employee(
        self,
        employee_id: int,
        **kwargs
    ) -> Employee:
        """
        Update an existing employee.

        Args:
            employee_id: ID of the employee to update
            **kwargs: Fields to update

        Returns:
            Updated Employee instance

        Raises:
            ValidationError: If validation fails or employee not found

        Requirements: 3.2
        """
        employee = self.db.query(Employee).filter(
            Employee.id == employee_id
        ).first()

        if not employee:
            raise ValidationError(f"Employee with ID {employee_id} not found")

        # Validate and update fields
        for key, value in kwargs.items():
            if key in ['first_name', 'last_name', 'city']:
                if not value or not str(value).strip():
                    raise ValidationError(f"{key} cannot be empty")
                setattr(employee, key, str(value).strip())
            elif key == 'agent_name':
                # Agent name is optional
                setattr(employee, key, str(value).strip() if value else None)
            elif key == 'birth_date':
                if value >= date.today():
                    raise ValidationError("Birth date must be in the past")
                setattr(employee, key, value)
            elif key == 'start_date':
                if value > date.today():
                    raise ValidationError(
                        "Start date cannot be in the future"
                    )
                setattr(employee, key, value)
            elif key == 'position_id':
                position = self.db.query(Position).filter(
                    Position.id == value
                ).first()
                if not position:
                    raise ValidationError(
                        f"Position with ID {value} not found"
                    )
                setattr(employee, key, value)
            elif key == 'is_active':
                setattr(employee, key, value)

        try:
            self.db.commit()
            self.db.refresh(employee)
            logger.info(f"Updated employee: {employee.full_name}")
            return employee
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update employee: {e}")
            raise

    def delete_employee(self, employee_id: int) -> bool:
        """
        Delete (archive) an employee by setting is_active to False.

        Args:
            employee_id: ID of the employee to delete

        Returns:
            True if successful

        Raises:
            ValidationError: If employee not found

        Requirements: 3.3
        """
        employee = self.db.query(Employee).filter(
            Employee.id == employee_id
        ).first()

        if not employee:
            raise ValidationError(f"Employee with ID {employee_id} not found")

        try:
            employee.is_active = False
            self.db.commit()
            logger.info(f"Archived employee: {employee.full_name}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to archive employee: {e}")
            raise

    def get_employee(self, employee_id: int) -> Optional[Employee]:
        """
        Get an employee by ID.

        Args:
            employee_id: ID of the employee

        Returns:
            Employee instance or None if not found

        Requirements: 3.1
        """
        return self.db.query(Employee).filter(
            Employee.id == employee_id
        ).first()

    def list_employees(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Employee]:
        """
        List all active employees with optional filters.

        Args:
            filters: Optional dictionary of filters
                - position_id: Filter by position
                - name: Filter by name (partial match)
                - city: Filter by city (partial match)
                - include_inactive: Include inactive employees

        Returns:
            List of Employee instances

        Requirements: 3.1, 3.5
        """
        query = self.db.query(Employee)

        # Default: only active employees
        if not filters or not filters.get('include_inactive'):
            query = query.filter(Employee.is_active == True)  # noqa: E712

        if filters:
            if 'position_id' in filters:
                query = query.filter(
                    Employee.position_id == filters['position_id']
                )
            if 'name' in filters:
                name_filter = f"%{filters['name']}%"
                query = query.filter(
                    (Employee.first_name.ilike(name_filter)) |
                    (Employee.last_name.ilike(name_filter))
                )
            if 'city' in filters:
                query = query.filter(
                    Employee.city.ilike(f"%{filters['city']}%")
                )

        return query.all()

    def search_employees(self, query: str) -> List[Employee]:
        """
        Search for employees by name or city.

        Args:
            query: Search query string

        Returns:
            List of matching Employee instances

        Requirements: 3.4
        """
        search_filter = f"%{query}%"
        return self.db.query(Employee).filter(
            Employee.is_active == True,  # noqa: E712
            (Employee.first_name.ilike(search_filter)) |
            (Employee.last_name.ilike(search_filter)) |
            (Employee.city.ilike(search_filter))
        ).all()

    def get_employee_criteria(self, employee_id: int) -> List[Criterion]:
        """
        Get all criteria assigned to an employee through their position.

        Args:
            employee_id: ID of the employee

        Returns:
            List of Criterion instances

        Raises:
            ValidationError: If employee not found

        Requirements: 6.5
        """
        employee = self.get_employee(employee_id)
        if not employee:
            raise ValidationError(
                f"Employee with ID {employee_id} not found"
            )

        # Get criteria through position
        return self.db.query(Criterion).join(
            PositionCriterion,
            Criterion.id == PositionCriterion.criterion_id
        ).filter(
            PositionCriterion.position_id == employee.position_id,
            Criterion.is_active == True  # noqa: E712
        ).all()


class PositionManager:
    """
    Manager for Position CRUD operations.

    Requirements: 4.1, 4.2, 4.3, 6.2, 6.3
    """

    def __init__(self, db: Session):
        self.db = db

    def create_position(
        self,
        name: str,
        description: Optional[str] = None
    ) -> Position:
        """
        Create a new position.

        Args:
            name: Position name (must be unique)
            description: Optional position description

        Returns:
            Created Position instance

        Raises:
            ValidationError: If validation fails

        Requirements: 4.1
        """
        # Validate name
        if not name or not name.strip():
            raise ValidationError("Position name is required")

        # Check for duplicate name (case-insensitive)
        existing = self.db.query(Position).filter(
            Position.name.ilike(name.strip())
        ).first()
        if existing:
            raise ValidationError(
                f"Position with name '{name}' already exists"
            )

        # Create position
        position = Position(
            name=name.strip(),
            description=description.strip() if description else None
        )

        try:
            self.db.add(position)
            self.db.commit()
            self.db.refresh(position)
            logger.info(f"Created position: {position.name}")
            return position
        except IntegrityError:
            self.db.rollback()
            raise ValidationError(
                f"Position with name '{name}' already exists"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create position: {e}")
            raise

    def update_position(
        self,
        position_id: int,
        **kwargs
    ) -> Position:
        """
        Update an existing position.

        Args:
            position_id: ID of the position to update
            **kwargs: Fields to update

        Returns:
            Updated Position instance

        Raises:
            ValidationError: If validation fails or position not found

        Requirements: 4.2
        """
        position = self.db.query(Position).filter(
            Position.id == position_id
        ).first()

        if not position:
            raise ValidationError(
                f"Position with ID {position_id} not found"
            )

        # Validate and update fields
        for key, value in kwargs.items():
            if key == 'name':
                if not value or not str(value).strip():
                    raise ValidationError("Position name cannot be empty")
                # Check for duplicate name
                existing = self.db.query(Position).filter(
                    Position.name.ilike(str(value).strip()),
                    Position.id != position_id
                ).first()
                if existing:
                    raise ValidationError(
                        f"Position with name '{value}' already exists"
                    )
                setattr(position, key, str(value).strip())
            elif key == 'description':
                setattr(
                    position,
                    key,
                    str(value).strip() if value else None
                )
            elif key == 'is_active':
                setattr(position, key, value)

        try:
            self.db.commit()
            self.db.refresh(position)
            logger.info(f"Updated position: {position.name}")
            return position
        except IntegrityError:
            self.db.rollback()
            raise ValidationError("Position name must be unique")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update position: {e}")
            raise

    def delete_position(self, position_id: int) -> bool:
        """
        Delete a position if no employees are assigned.

        Args:
            position_id: ID of the position to delete

        Returns:
            True if successful

        Raises:
            ValidationError: If position not found or has employees

        Requirements: 4.3, 4.5
        """
        position = self.db.query(Position).filter(
            Position.id == position_id
        ).first()

        if not position:
            raise ValidationError(
                f"Position with ID {position_id} not found"
            )

        # Check if any employees are assigned
        employee_count = self.db.query(Employee).filter(
            Employee.position_id == position_id,
            Employee.is_active == True  # noqa: E712
        ).count()

        if employee_count > 0:
            raise ValidationError(
                f"Cannot delete position '{position.name}': "
                f"{employee_count} employee(s) are assigned to this position"
            )

        try:
            self.db.delete(position)
            self.db.commit()
            logger.info(f"Deleted position: {position.name}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete position: {e}")
            raise

    def get_position(self, position_id: int) -> Optional[Position]:
        """
        Get a position by ID.

        Args:
            position_id: ID of the position

        Returns:
            Position instance or None if not found
        """
        return self.db.query(Position).filter(
            Position.id == position_id
        ).first()

    def list_positions(self) -> List[Position]:
        """
        List all active positions.

        Returns:
            List of Position instances
        """
        return self.db.query(Position).filter(
            Position.is_active == True  # noqa: E712
        ).all()

    def assign_criteria(
        self,
        position_id: int,
        criterion_ids: List[int]
    ) -> bool:
        """
        Assign criteria to a position.

        Args:
            position_id: ID of the position
            criterion_ids: List of criterion IDs to assign

        Returns:
            True if successful

        Raises:
            ValidationError: If position or criteria not found

        Requirements: 6.2
        """
        position = self.get_position(position_id)
        if not position:
            raise ValidationError(
                f"Position with ID {position_id} not found"
            )

        try:
            for criterion_id in criterion_ids:
                # Check if criterion exists
                criterion = self.db.query(Criterion).filter(
                    Criterion.id == criterion_id
                ).first()
                if not criterion:
                    raise ValidationError(
                        f"Criterion with ID {criterion_id} not found"
                    )

                # Check if already assigned
                existing = self.db.query(PositionCriterion).filter(
                    PositionCriterion.position_id == position_id,
                    PositionCriterion.criterion_id == criterion_id
                ).first()

                if not existing:
                    assignment = PositionCriterion(
                        position_id=position_id,
                        criterion_id=criterion_id
                    )
                    self.db.add(assignment)

            self.db.commit()
            logger.info(
                f"Assigned {len(criterion_ids)} criteria to "
                f"position: {position.name}"
            )
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to assign criteria: {e}")
            raise

    def remove_criteria(
        self,
        position_id: int,
        criterion_ids: List[int]
    ) -> bool:
        """
        Remove criteria from a position.

        Args:
            position_id: ID of the position
            criterion_ids: List of criterion IDs to remove

        Returns:
            True if successful

        Raises:
            ValidationError: If position not found

        Requirements: 6.3
        """
        position = self.get_position(position_id)
        if not position:
            raise ValidationError(
                f"Position with ID {position_id} not found"
            )

        try:
            for criterion_id in criterion_ids:
                self.db.query(PositionCriterion).filter(
                    PositionCriterion.position_id == position_id,
                    PositionCriterion.criterion_id == criterion_id
                ).delete()

            self.db.commit()
            logger.info(
                f"Removed {len(criterion_ids)} criteria from "
                f"position: {position.name}"
            )
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to remove criteria: {e}")
            raise

    def get_position_criteria(self, position_id: int) -> List[Criterion]:
        """
        Get all criteria assigned to a position.

        Args:
            position_id: ID of the position

        Returns:
            List of Criterion instances

        Requirements: 6.1
        """
        return self.db.query(Criterion).join(
            PositionCriterion,
            Criterion.id == PositionCriterion.criterion_id
        ).filter(
            PositionCriterion.position_id == position_id,
            Criterion.is_active == True  # noqa: E712
        ).all()


class CriterionManager:
    """
    Manager for Criterion CRUD operations.

    Requirements: 5.1, 5.3, 5.4
    """

    def __init__(self, db: Session):
        self.db = db

    def create_criterion(
        self,
        name: str,
        description: Optional[str] = None,
        calculation_method: CalculationMethod = CalculationMethod.SUM,
        is_standard: bool = False
    ) -> Criterion:
        """
        Create a new criterion.

        Args:
            name: Criterion name (must be unique)
            description: Optional criterion description
            calculation_method: Calculation method for the criterion
            is_standard: Whether this is a standard criterion

        Returns:
            Created Criterion instance

        Raises:
            ValidationError: If validation fails

        Requirements: 5.1
        """
        # Validate name
        if not name or not name.strip():
            raise ValidationError("Criterion name is required")

        # Check for duplicate name (case-insensitive)
        existing = self.db.query(Criterion).filter(
            Criterion.name.ilike(name.strip())
        ).first()
        if existing:
            raise ValidationError(
                f"Criterion with name '{name}' already exists"
            )

        # Create criterion
        criterion = Criterion(
            name=name.strip(),
            description=description.strip() if description else None,
            calculation_method=calculation_method,
            is_standard=is_standard
        )

        try:
            self.db.add(criterion)
            self.db.commit()
            self.db.refresh(criterion)
            logger.info(f"Created criterion: {criterion.name}")
            return criterion
        except IntegrityError:
            self.db.rollback()
            raise ValidationError(
                f"Criterion with name '{name}' already exists"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create criterion: {e}")
            raise

    def update_criterion(
        self,
        criterion_id: int,
        **kwargs
    ) -> Criterion:
        """
        Update an existing criterion.

        Args:
            criterion_id: ID of the criterion to update
            **kwargs: Fields to update

        Returns:
            Updated Criterion instance

        Raises:
            ValidationError: If validation fails or criterion not found

        Requirements: 5.3
        """
        criterion = self.db.query(Criterion).filter(
            Criterion.id == criterion_id
        ).first()

        if not criterion:
            raise ValidationError(
                f"Criterion with ID {criterion_id} not found"
            )

        # Validate and update fields
        for key, value in kwargs.items():
            if key == 'name':
                if not value or not str(value).strip():
                    raise ValidationError("Criterion name cannot be empty")
                # Check for duplicate name
                existing = self.db.query(Criterion).filter(
                    Criterion.name.ilike(str(value).strip()),
                    Criterion.id != criterion_id
                ).first()
                if existing:
                    raise ValidationError(
                        f"Criterion with name '{value}' already exists"
                    )
                setattr(criterion, key, str(value).strip())
            elif key == 'description':
                setattr(
                    criterion,
                    key,
                    str(value).strip() if value else None
                )
            elif key == 'calculation_method':
                if isinstance(value, str):
                    value = CalculationMethod[value]
                setattr(criterion, key, value)
            elif key in ['is_standard', 'is_active']:
                setattr(criterion, key, value)

        try:
            self.db.commit()
            self.db.refresh(criterion)
            logger.info(f"Updated criterion: {criterion.name}")
            return criterion
        except IntegrityError:
            self.db.rollback()
            raise ValidationError("Criterion name must be unique")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update criterion: {e}")
            raise

    def delete_criterion(self, criterion_id: int) -> bool:
        """
        Delete a criterion if not assigned to any positions.

        Args:
            criterion_id: ID of the criterion to delete

        Returns:
            True if successful

        Raises:
            ValidationError: If criterion not found or is assigned

        Requirements: 5.4
        """
        criterion = self.db.query(Criterion).filter(
            Criterion.id == criterion_id
        ).first()

        if not criterion:
            raise ValidationError(
                f"Criterion with ID {criterion_id} not found"
            )

        # Check if assigned to any positions
        assignment_count = self.db.query(PositionCriterion).filter(
            PositionCriterion.criterion_id == criterion_id
        ).count()

        if assignment_count > 0:
            raise ValidationError(
                f"Cannot delete criterion '{criterion.name}': "
                f"it is assigned to {assignment_count} position(s)"
            )

        try:
            self.db.delete(criterion)
            self.db.commit()
            logger.info(f"Deleted criterion: {criterion.name}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete criterion: {e}")
            raise

    def get_criterion(self, criterion_id: int) -> Optional[Criterion]:
        """
        Get a criterion by ID.

        Args:
            criterion_id: ID of the criterion

        Returns:
            Criterion instance or None if not found
        """
        return self.db.query(Criterion).filter(
            Criterion.id == criterion_id
        ).first()

    def list_criteria(self) -> List[Criterion]:
        """
        List all active criteria.

        Returns:
            List of Criterion instances
        """
        return self.db.query(Criterion).filter(
            Criterion.is_active == True  # noqa: E712
        ).all()

    def get_standard_criteria(self) -> List[Criterion]:
        """
        Get all standard criteria.

        Returns:
            List of standard Criterion instances

        Requirements: 5.2
        """
        return self.db.query(Criterion).filter(
            Criterion.is_standard == True,  # noqa: E712
            Criterion.is_active == True  # noqa: E712
        ).all()


class PerformanceDataManager:
    """
    Manager for PerformanceData operations.

    Requirements: 8.3, 8.5
    """

    def __init__(self, db: Session):
        self.db = db

    def record_performance(
        self,
        employee_id: int,
        criterion_id: int,
        value: float,
        date: date,
        period_id: Optional[int] = None
    ) -> PerformanceData:
        """
        Record performance data for an employee.

        Args:
            employee_id: ID of the employee
            criterion_id: ID of the criterion
            value: Performance value (must be numeric)
            date: Date of the performance data
            period_id: Optional ID of the evaluation period

        Returns:
            Created PerformanceData instance

        Raises:
            ValidationError: If validation fails

        Requirements: 8.3, 8.5
        """
        # Validate employee exists
        employee = self.db.query(Employee).filter(
            Employee.id == employee_id
        ).first()
        if not employee:
            raise ValidationError(
                f"Employee with ID {employee_id} not found"
            )

        # Validate criterion exists
        criterion = self.db.query(Criterion).filter(
            Criterion.id == criterion_id
        ).first()
        if not criterion:
            raise ValidationError(
                f"Criterion with ID {criterion_id} not found"
            )

        # Validate value is numeric
        try:
            value = float(value)
            if value < 0:
                raise ValidationError("Performance value cannot be negative")
        except (TypeError, ValueError):
            raise ValidationError("Performance value must be numeric")

        # Create performance data
        performance = PerformanceData(
            employee_id=employee_id,
            criterion_id=criterion_id,
            value=value,
            date=date,
            period_id=period_id
        )

        try:
            self.db.add(performance)
            self.db.commit()
            self.db.refresh(performance)
            logger.info(
                f"Recorded performance for employee {employee_id}: "
                f"{criterion.name} = {value}"
            )
            return performance
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to record performance: {e}")
            raise

    def update_performance(
        self,
        performance_id: int,
        value: float
    ) -> PerformanceData:
        """
        Update performance data value.

        Args:
            performance_id: ID of the performance data
            value: New performance value

        Returns:
            Updated PerformanceData instance

        Raises:
            ValidationError: If validation fails
        """
        performance = self.db.query(PerformanceData).filter(
            PerformanceData.id == performance_id
        ).first()

        if not performance:
            raise ValidationError(
                f"Performance data with ID {performance_id} not found"
            )

        # Validate value is numeric
        try:
            value = float(value)
            if value < 0:
                raise ValidationError("Performance value cannot be negative")
        except (TypeError, ValueError):
            raise ValidationError("Performance value must be numeric")

        try:
            performance.value = value
            self.db.commit()
            self.db.refresh(performance)
            logger.info(f"Updated performance data ID {performance_id}")
            return performance
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update performance: {e}")
            raise

    def get_performance_data(
        self,
        employee_id: int,
        start_date: date,
        end_date: date,
        criterion_ids: Optional[List[int]] = None
    ) -> List[PerformanceData]:
        """
        Get performance data for an employee within a date range.

        Args:
            employee_id: ID of the employee
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            criterion_ids: Optional list of criterion IDs to filter

        Returns:
            List of PerformanceData instances

        Requirements: 9.2
        """
        query = self.db.query(PerformanceData).filter(
            PerformanceData.employee_id == employee_id,
            PerformanceData.date >= start_date,
            PerformanceData.date <= end_date
        )

        if criterion_ids:
            query = query.filter(
                PerformanceData.criterion_id.in_(criterion_ids)
            )

        return query.all()

    def bulk_record_performance(
        self,
        employee_id: int,
        data_dict: Dict[int, float],
        date: date
    ) -> List[PerformanceData]:
        """
        Record multiple performance data entries at once.

        Args:
            employee_id: ID of the employee
            data_dict: Dictionary mapping criterion_id to value
            date: Date of the performance data

        Returns:
            List of created PerformanceData instances

        Raises:
            ValidationError: If validation fails
        """
        # Validate employee exists
        employee = self.db.query(Employee).filter(
            Employee.id == employee_id
        ).first()
        if not employee:
            raise ValidationError(
                f"Employee with ID {employee_id} not found"
            )

        performance_list = []

        try:
            for criterion_id, value in data_dict.items():
                # Validate criterion exists
                criterion = self.db.query(Criterion).filter(
                    Criterion.id == criterion_id
                ).first()
                if not criterion:
                    raise ValidationError(
                        f"Criterion with ID {criterion_id} not found"
                    )

                # Validate value
                try:
                    value = float(value)
                    if value < 0:
                        raise ValidationError(
                            "Performance value cannot be negative"
                        )
                except (TypeError, ValueError):
                    raise ValidationError(
                        "Performance value must be numeric"
                    )

                performance = PerformanceData(
                    employee_id=employee_id,
                    criterion_id=criterion_id,
                    value=value,
                    date=date
                )
                self.db.add(performance)
                performance_list.append(performance)

            self.db.commit()
            for p in performance_list:
                self.db.refresh(p)

            logger.info(
                f"Bulk recorded {len(performance_list)} performance entries "
                f"for employee {employee_id}"
            )
            return performance_list
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to bulk record performance: {e}")
            raise
