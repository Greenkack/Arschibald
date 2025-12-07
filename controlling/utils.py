"""
Controlling System Utility Functions

Helper functions for accessing controlling data from other modules.

Requirements: Integration with PDF generation system
"""

import logging
from typing import Optional
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.database import SessionLocal  # noqa: E402
from controlling.models import Employee  # noqa: E402

logger = logging.getLogger(__name__)


def get_employee_by_id(employee_id: int) -> Optional[Employee]:
    """
    Get employee by ID.
    
    Args:
        employee_id: Employee ID
        
    Returns:
        Employee instance or None
    """
    db = SessionLocal()
    try:
        employee = db.query(Employee).filter(
            Employee.id == employee_id,
            Employee.is_active == True
        ).first()
        return employee
    except Exception as e:
        logger.error(f"Error fetching employee {employee_id}: {e}")
        return None
    finally:
        db.close()


def get_agent_name_by_employee_id(employee_id: int) -> Optional[str]:
    """
    Get agent name by employee ID.
    
    Args:
        employee_id: Employee ID
        
    Returns:
        Agent name or None
    """
    employee = get_employee_by_id(employee_id)
    if employee:
        return employee.agent_name
    return None


def get_all_active_employees():
    """
    Get all active employees.
    
    Returns:
        List of Employee instances
    """
    db = SessionLocal()
    try:
        employees = db.query(Employee).filter(
            Employee.is_active == True
        ).order_by(Employee.last_name, Employee.first_name).all()
        return employees
    except Exception as e:
        logger.error(f"Error fetching employees: {e}")
        return []
    finally:
        db.close()


def enrich_customer_data_with_agent_name(
    customer_data: dict,
    employee_id: Optional[int] = None
) -> dict:
    """
    Enrich customer data dictionary with agent_name field.
    
    This function adds the agent_name from the controlling system
    to customer_data for use in PDF generation.
    
    Args:
        customer_data: Customer data dictionary
        employee_id: Optional employee ID to look up agent name
        
    Returns:
        Enriched customer data dictionary with agent_name field
        
    Example:
        >>> customer_data = {'name': 'Max Mustermann'}
        >>> enriched = enrich_customer_data_with_agent_name(customer_data, employee_id=1)
        >>> print(enriched.get('agent_name'))
        'Agent Schmidt'
    """
    if not isinstance(customer_data, dict):
        customer_data = {}
    
    # Don't overwrite if already set
    if customer_data.get('agent_name'):
        return customer_data
    
    # Try to get agent name from employee_id
    if employee_id:
        agent_name = get_agent_name_by_employee_id(employee_id)
        if agent_name:
            customer_data['agent_name'] = agent_name
            logger.info(f"Added agent_name '{agent_name}' to customer_data")
    
    return customer_data
