"""
CRM Integration Package
Module für die Integration zwischen verschiedenen Systemkomponenten.
"""

from .data_input_bridge import (
    extract_customer_data_from_session,
    extract_project_data_from_session,
    check_duplicate_customer)

__all__ = [
    'extract_customer_data_from_session',
    'extract_project_data_from_session',
    'check_duplicate_customer',
]
