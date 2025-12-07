"""
Period Manager for Evaluation Periods

Manages CRUD operations for evaluation periods.
Provides functionality to create, read, update, delete, and list evaluation periods.
"""

import logging
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from controlling.models import (
    EvaluationPeriod,
    PeriodType,
    PeriodStatus,
    Employee
)

logger = logging.getLogger(__name__)


class PeriodManager:
    """
    Manager for handling evaluation periods.
    
    Provides CRUD operations and utility functions for managing
    time-based performance evaluation periods.
    """
    
    def __init__(self, db: Session):
        """Initialize PeriodManager with database session."""
        self.db = db
    
    def create_period(
        self,
        name: str,
        period_type: PeriodType,
        start_date: date,
        end_date: date,
        description: Optional[str] = None,
        employee_id: Optional[int] = None
    ) -> EvaluationPeriod:
        """
        Create a new evaluation period.
        
        Args:
            name: Name of the period (e.g., "Januar 2025", "Q1 2025")
            period_type: Type of period (MONTHLY, QUARTERLY, YEARLY, CUSTOM)
            start_date: Start date of the period
            end_date: End date of the period
            description: Optional description
            employee_id: Optional employee ID (None = all employees)
            
        Returns:
            Created EvaluationPeriod object
            
        Raises:
            ValueError: If dates are invalid or period overlaps with existing
        """
        # Validate dates
        if end_date < start_date:
            raise ValueError("End date must be after start date")
        
        # Check for overlapping periods for same employee
        overlapping = self._check_overlapping_periods(
            start_date, end_date, employee_id
        )
        
        if overlapping:
            logger.warning(
                f"Period overlaps with existing period: {overlapping.name}"
            )
            # Allow overlap but log warning
        
        # Create period
        period = EvaluationPeriod(
            name=name,
            description=description,
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
            status=PeriodStatus.ACTIVE,
            employee_id=employee_id
        )
        
        self.db.add(period)
        self.db.commit()
        self.db.refresh(period)
        
        logger.info(
            f"Created evaluation period: {period.name} "
            f"({period.start_date} - {period.end_date})"
        )
        
        return period
    
    def get_period(self, period_id: int) -> Optional[EvaluationPeriod]:
        """
        Get a specific evaluation period by ID.
        
        Args:
            period_id: ID of the period
            
        Returns:
            EvaluationPeriod object or None if not found
        """
        return self.db.query(EvaluationPeriod).filter(
            EvaluationPeriod.id == period_id
        ).first()
    
    def list_periods(
        self,
        employee_id: Optional[int] = None,
        status: Optional[PeriodStatus] = None,
        period_type: Optional[PeriodType] = None,
        include_global: bool = True
    ) -> List[EvaluationPeriod]:
        """
        List evaluation periods with optional filters.
        
        Args:
            employee_id: Filter by employee (None = all)
            status: Filter by status (None = all)
            period_type: Filter by type (None = all)
            include_global: Include periods not assigned to specific employee
            
        Returns:
            List of EvaluationPeriod objects
        """
        query = self.db.query(EvaluationPeriod)
        
        # Filter by employee
        if employee_id is not None:
            if include_global:
                # Show periods for this employee OR global periods
                query = query.filter(
                    or_(
                        EvaluationPeriod.employee_id == employee_id,
                        EvaluationPeriod.employee_id.is_(None)
                    )
                )
            else:
                query = query.filter(
                    EvaluationPeriod.employee_id == employee_id
                )
        
        # Filter by status
        if status is not None:
            query = query.filter(EvaluationPeriod.status == status)
        
        # Filter by type
        if period_type is not None:
            query = query.filter(EvaluationPeriod.period_type == period_type)
        
        # Order by start date (newest first)
        query = query.order_by(EvaluationPeriod.start_date.desc())
        
        return query.all()
    
    def update_period(
        self,
        period_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[PeriodStatus] = None
    ) -> Optional[EvaluationPeriod]:
        """
        Update an existing evaluation period.
        
        Args:
            period_id: ID of the period to update
            name: New name (None = no change)
            description: New description (None = no change)
            start_date: New start date (None = no change)
            end_date: New end date (None = no change)
            status: New status (None = no change)
            
        Returns:
            Updated EvaluationPeriod object or None if not found
            
        Raises:
            ValueError: If dates are invalid
        """
        period = self.get_period(period_id)
        
        if not period:
            logger.error(f"Period with ID {period_id} not found")
            return None
        
        # Update fields
        if name is not None:
            period.name = name
        
        if description is not None:
            period.description = description
        
        if start_date is not None:
            period.start_date = start_date
        
        if end_date is not None:
            period.end_date = end_date
        
        # Validate dates after update
        if period.end_date < period.start_date:
            raise ValueError("End date must be after start date")
        
        if status is not None:
            period.status = status
            
            # Set completion timestamp if status changed to COMPLETED
            if status == PeriodStatus.COMPLETED and period.completed_at is None:
                period.completed_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(period)
        
        logger.info(f"Updated evaluation period: {period.name}")
        
        return period
    
    def delete_period(self, period_id: int) -> bool:
        """
        Delete an evaluation period.
        
        Args:
            period_id: ID of the period to delete
            
        Returns:
            True if deleted, False if not found
            
        Note:
            This will also delete all associated performance data
            due to cascade delete.
        """
        period = self.get_period(period_id)
        
        if not period:
            logger.error(f"Period with ID {period_id} not found")
            return False
        
        # Log warning about cascade delete
        data_count = len(period.performance_data)
        if data_count > 0:
            logger.warning(
                f"Deleting period '{period.name}' will also delete "
                f"{data_count} performance data entries"
            )
        
        self.db.delete(period)
        self.db.commit()
        
        logger.info(f"Deleted evaluation period: {period.name}")
        
        return True
    
    def complete_period(self, period_id: int) -> Optional[EvaluationPeriod]:
        """
        Mark a period as completed.
        
        Args:
            period_id: ID of the period to complete
            
        Returns:
            Updated EvaluationPeriod object or None if not found
        """
        return self.update_period(
            period_id,
            status=PeriodStatus.COMPLETED
        )
    
    def archive_period(self, period_id: int) -> Optional[EvaluationPeriod]:
        """
        Archive a period.
        
        Args:
            period_id: ID of the period to archive
            
        Returns:
            Updated EvaluationPeriod object or None if not found
        """
        return self.update_period(
            period_id,
            status=PeriodStatus.ARCHIVED
        )
    
    def get_active_periods(
        self,
        employee_id: Optional[int] = None
    ) -> List[EvaluationPeriod]:
        """
        Get all active evaluation periods.
        
        Args:
            employee_id: Optional employee ID filter
            
        Returns:
            List of active EvaluationPeriod objects
        """
        return self.list_periods(
            employee_id=employee_id,
            status=PeriodStatus.ACTIVE
        )
    
    def get_current_period(
        self,
        employee_id: Optional[int] = None,
        reference_date: Optional[date] = None
    ) -> Optional[EvaluationPeriod]:
        """
        Get the current active period that includes the reference date.
        
        Args:
            employee_id: Optional employee ID filter
            reference_date: Date to check (default: today)
            
        Returns:
            EvaluationPeriod object or None if no matching period
        """
        if reference_date is None:
            reference_date = date.today()
        
        query = self.db.query(EvaluationPeriod).filter(
            EvaluationPeriod.status == PeriodStatus.ACTIVE,
            EvaluationPeriod.start_date <= reference_date,
            EvaluationPeriod.end_date >= reference_date
        )
        
        # Filter by employee
        if employee_id is not None:
            query = query.filter(
                or_(
                    EvaluationPeriod.employee_id == employee_id,
                    EvaluationPeriod.employee_id.is_(None)
                )
            )
        
        # Prefer employee-specific period over global
        periods = query.order_by(
            EvaluationPeriod.employee_id.desc()
        ).all()
        
        return periods[0] if periods else None
    
    def create_monthly_period(
        self,
        year: int,
        month: int,
        employee_id: Optional[int] = None
    ) -> EvaluationPeriod:
        """
        Create a monthly evaluation period.
        
        Args:
            year: Year
            month: Month (1-12)
            employee_id: Optional employee ID
            
        Returns:
            Created EvaluationPeriod object
        """
        # Calculate first and last day of month
        start_date = date(year, month, 1)
        
        # Last day of month
        if month == 12:
            end_date = date(year, 12, 31)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Month name in German
        month_names = [
            "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember"
        ]
        name = f"{month_names[month - 1]} {year}"
        
        return self.create_period(
            name=name,
            period_type=PeriodType.MONTHLY,
            start_date=start_date,
            end_date=end_date,
            employee_id=employee_id
        )
    
    def create_quarterly_period(
        self,
        year: int,
        quarter: int,
        employee_id: Optional[int] = None
    ) -> EvaluationPeriod:
        """
        Create a quarterly evaluation period.
        
        Args:
            year: Year
            quarter: Quarter (1-4)
            employee_id: Optional employee ID
            
        Returns:
            Created EvaluationPeriod object
            
        Raises:
            ValueError: If quarter is not 1-4
        """
        if quarter not in [1, 2, 3, 4]:
            raise ValueError("Quarter must be 1, 2, 3, or 4")
        
        # Calculate start and end dates
        start_month = (quarter - 1) * 3 + 1
        start_date = date(year, start_month, 1)
        
        end_month = start_month + 2
        if end_month == 12:
            end_date = date(year, 12, 31)
        else:
            end_date = date(year, end_month + 1, 1) - timedelta(days=1)
        
        name = f"Q{quarter} {year}"
        
        return self.create_period(
            name=name,
            period_type=PeriodType.QUARTERLY,
            start_date=start_date,
            end_date=end_date,
            employee_id=employee_id
        )
    
    def create_yearly_period(
        self,
        year: int,
        employee_id: Optional[int] = None
    ) -> EvaluationPeriod:
        """
        Create a yearly evaluation period.
        
        Args:
            year: Year
            employee_id: Optional employee ID
            
        Returns:
            Created EvaluationPeriod object
        """
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        name = f"Jahr {year}"
        
        return self.create_period(
            name=name,
            period_type=PeriodType.YEARLY,
            start_date=start_date,
            end_date=end_date,
            employee_id=employee_id
        )
    
    def _check_overlapping_periods(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[int] = None
    ) -> Optional[EvaluationPeriod]:
        """
        Check if there are overlapping periods.
        
        Args:
            start_date: Start date to check
            end_date: End date to check
            employee_id: Employee ID to check (None = global)
            
        Returns:
            First overlapping EvaluationPeriod or None
        """
        query = self.db.query(EvaluationPeriod).filter(
            EvaluationPeriod.status != PeriodStatus.ARCHIVED,
            or_(
                and_(
                    EvaluationPeriod.start_date <= start_date,
                    EvaluationPeriod.end_date >= start_date
                ),
                and_(
                    EvaluationPeriod.start_date <= end_date,
                    EvaluationPeriod.end_date >= end_date
                ),
                and_(
                    EvaluationPeriod.start_date >= start_date,
                    EvaluationPeriod.end_date <= end_date
                )
            )
        )
        
        # Check for same employee or global periods
        if employee_id is not None:
            query = query.filter(
                or_(
                    EvaluationPeriod.employee_id == employee_id,
                    EvaluationPeriod.employee_id.is_(None)
                )
            )
        else:
            query = query.filter(EvaluationPeriod.employee_id.is_(None))
        
        return query.first()
