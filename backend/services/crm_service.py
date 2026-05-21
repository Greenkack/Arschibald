"""
CRM Service

This service wraps the legacy CRM modules and provides
a clean API interface for CRM operations including customer management,
offer tracking, task management, note management, and communication history.
"""

import sys
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, date

# Add parent directory to path to import CRM modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.core.base_service import BaseService, HealthCheckResult, ServiceStatus
from backend.core.error_wrapper import handle_service_errors, ErrorContext
from backend.core.logging_decorator import log_service_call


class CRMService(BaseService):
    """
    Service wrapper for CRM functionality.
    
    Wraps the legacy CRM modules and provides:
    - Customer management
    - Offer tracking
    - Task management
    - Note and communication history management
    - Input validation
    - Error handling and logging
    - Health checks
    """
    
    def __init__(self):
        super().__init__("crm_management")
        self._offer_tracker = None
        self._task_manager = None
        self._note_manager = None
        self._database_module = None
        
    def initialize(self) -> None:
        """Initialize the service and load legacy CRM modules"""
        try:
            # Import the legacy CRM modules
            from crm.features import offer_tracker, task_manager, note_manager
            import database
            
            self._offer_tracker = offer_tracker
            self._task_manager = task_manager
            self._note_manager = note_manager
            self._database_module = database
            
            self._set_legacy_module(offer_tracker)
            self._set_initialized(True)
            self.logger.info("CRM Service initialized successfully")
        except ImportError as e:
            self.logger.error(f"Failed to import CRM modules: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize CRM Service: {e}")
            raise
    
    def health_check(self) -> HealthCheckResult:
        """Perform health check on the service"""
        if not self.is_initialized:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="Service not initialized"
            )
        
        if not all([self._offer_tracker, self._task_manager, self._note_manager]):
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message="CRM modules not loaded"
            )
        
        # Check if database is available
        try:
            conn = self._database_module.get_db_connection()
            if not conn:
                return HealthCheckResult(
                    status=ServiceStatus.DEGRADED,
                    message="Database not available"
                )
            conn.close()
        except Exception as e:
            return HealthCheckResult(
                status=ServiceStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}"
            )
        
        return HealthCheckResult(
            status=ServiceStatus.HEALTHY,
            message="CRM Service is healthy"
        )
    
    # ==================== Customer Management ====================
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="get_customer", resource_type="customer"))
    def get_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get a customer by ID"""
        self._ensure_initialized()
        
        conn = self._database_module.get_db_connection()
        if not conn:
            raise RuntimeError("Database connection failed")
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        finally:
            conn.close()
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="list_customers", resource_type="customer"))
    def list_customers(
        self,
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all customers with optional search"""
        self._ensure_initialized()
        
        conn = self._database_module.get_db_connection()
        if not conn:
            raise RuntimeError("Database connection failed")
        
        try:
            cursor = conn.cursor()
            
            if search:
                query = """
                    SELECT * FROM customers 
                    WHERE first_name LIKE ? OR last_name LIKE ? OR company_name LIKE ? OR email LIKE ?
                    ORDER BY id DESC LIMIT ? OFFSET ?
                """
                search_pattern = f"%{search}%"
                cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, limit, offset))
            else:
                query = "SELECT * FROM customers ORDER BY id DESC LIMIT ? OFFSET ?"
                cursor.execute(query, (limit, offset))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="create_customer", resource_type="customer"))
    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer"""
        self._ensure_initialized()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name']
        for field in required_fields:
            if field not in customer_data or not customer_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        conn = self._database_module.get_db_connection()
        if not conn:
            raise RuntimeError("Database connection failed")
        
        try:
            cursor = conn.cursor()
            
            # Build INSERT statement dynamically
            fields = list(customer_data.keys())
            placeholders = ', '.join(['?' for _ in fields])
            field_names = ', '.join(fields)
            values = [customer_data[f] for f in fields]
            
            query = f"INSERT INTO customers ({field_names}) VALUES ({placeholders})"
            cursor.execute(query, values)
            conn.commit()
            
            customer_id = cursor.lastrowid
            return self.get_customer(customer_id)
        finally:
            conn.close()
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="update_customer", resource_type="customer"))
    def update_customer(self, customer_id: int, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing customer"""
        self._ensure_initialized()
        
        # Check if customer exists
        existing = self.get_customer(customer_id)
        if not existing:
            raise ValueError(f"Customer with ID {customer_id} not found")
        
        conn = self._database_module.get_db_connection()
        if not conn:
            raise RuntimeError("Database connection failed")
        
        try:
            cursor = conn.cursor()
            
            # Build UPDATE statement dynamically
            fields = list(customer_data.keys())
            set_clause = ', '.join([f"{f} = ?" for f in fields])
            values = [customer_data[f] for f in fields]
            values.append(customer_id)
            
            query = f"UPDATE customers SET {set_clause} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            return self.get_customer(customer_id)
        finally:
            conn.close()
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="delete_customer", resource_type="customer"))
    def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer"""
        self._ensure_initialized()
        
        conn = self._database_module.get_db_connection()
        if not conn:
            raise RuntimeError("Database connection failed")
        
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            conn.commit()
            
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    # ==================== Offer Tracking ====================
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="get_offer_status", resource_type="offer"))
    def get_offer_status(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Get offer status for a project"""
        self._ensure_initialized()
        
        conn = self._database_module.get_db_connection()
        if not conn:
            raise RuntimeError("Database connection failed")
        
        try:
            return self._offer_tracker.get_offer_status(conn, project_id)
        finally:
            conn.close()
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="update_offer_status", resource_type="offer"))
    def update_offer_status(
        self,
        project_id: int,
        new_status: str,
        **kwargs
    ) -> bool:
        """Update offer status"""
        self._ensure_initialized()
        
        # Validate status
        valid_statuses = ['draft', 'sent', 'accepted', 'rejected']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        conn = self._database_module.get_db_connection()
        if not conn:
            raise RuntimeError("Database connection failed")
        
        try:
            return self._offer_tracker.update_offer_status(conn, project_id, new_status, **kwargs)
        finally:
            conn.close()
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="list_offers", resource_type="offer"))
    def list_offers(
        self,
        status_filter: Optional[str] = None,
        include_customer_info: bool = True
    ) -> List[Dict[str, Any]]:
        """List all offers with optional status filter"""
        self._ensure_initialized()
        
        conn = self._database_module.get_db_connection()
        if not conn:
            raise RuntimeError("Database connection failed")
        
        try:
            return self._offer_tracker.get_all_offers(conn, status_filter, include_customer_info)
        finally:
            conn.close()
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="get_pending_follow_ups", resource_type="offer"))
    def get_pending_follow_ups(self) -> List[Dict[str, Any]]:
        """Get all offers with pending follow-ups"""
        self._ensure_initialized()
        
        conn = self._database_module.get_db_connection()
        if not conn:
            raise RuntimeError("Database connection failed")
        
        try:
            return self._offer_tracker.get_pending_follow_ups(conn)
        finally:
            conn.close()
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="mark_follow_up_completed", resource_type="offer"))
    def mark_follow_up_completed(self, project_id: int) -> bool:
        """Mark a follow-up as completed"""
        self._ensure_initialized()
        
        conn = self._database_module.get_db_connection()
        if not conn:
            raise RuntimeError("Database connection failed")
        
        try:
            return self._offer_tracker.mark_follow_up_completed(conn, project_id)
        finally:
            conn.close()
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="get_offer_statistics", resource_type="offer"))
    def get_offer_statistics(self) -> Dict[str, Any]:
        """Get offer statistics"""
        self._ensure_initialized()
        
        conn = self._database_module.get_db_connection()
        if not conn:
            raise RuntimeError("Database connection failed")
        
        try:
            return self._offer_tracker.get_offer_statistics(conn)
        finally:
            conn.close()
    
    # ==================== Task Management ====================
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="create_task", resource_type="task"))
    def create_task(self, task_data: Dict[str, Any]) -> Optional[int]:
        """Create a new task"""
        self._ensure_initialized()
        
        # Validate required fields
        if 'title' not in task_data or not task_data['title']:
            raise ValueError("Task title is required")
        
        # Convert date string to date object if needed
        if 'due_date' in task_data and isinstance(task_data['due_date'], str):
            task_data['due_date'] = datetime.fromisoformat(task_data['due_date']).date()
        
        return self._task_manager.create_task(**task_data)
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="get_task", resource_type="task"))
    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get a task by ID"""
        self._ensure_initialized()
        return self._task_manager.get_task(task_id)
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="update_task", resource_type="task"))
    def update_task(self, task_id: int, task_data: Dict[str, Any]) -> bool:
        """Update a task"""
        self._ensure_initialized()
        
        # Convert date string to date object if needed
        if 'due_date' in task_data and isinstance(task_data['due_date'], str):
            task_data['due_date'] = datetime.fromisoformat(task_data['due_date']).date()
        
        return self._task_manager.update_task(task_id, **task_data)
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="delete_task", resource_type="task"))
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        self._ensure_initialized()
        return self._task_manager.delete_task(task_id)
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="list_tasks", resource_type="task"))
    def list_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List tasks with optional filters"""
        self._ensure_initialized()
        
        if filters is None:
            filters = {}
        
        return self._task_manager.get_all_tasks(**filters)
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="get_overdue_tasks", resource_type="task"))
    def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """Get all overdue tasks"""
        self._ensure_initialized()
        return self._task_manager.get_overdue_tasks()
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="mark_task_completed", resource_type="task"))
    def mark_task_completed(self, task_id: int) -> bool:
        """Mark a task as completed"""
        self._ensure_initialized()
        return self._task_manager.mark_task_completed(task_id)
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="get_task_statistics", resource_type="task"))
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        self._ensure_initialized()
        return self._task_manager.get_task_statistics()
    
    # ==================== Note and Communication History ====================
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="create_activity", resource_type="activity"))
    def create_activity(self, activity_data: Dict[str, Any]) -> Optional[int]:
        """Create a new activity/note"""
        self._ensure_initialized()
        
        # Validate required fields
        required_fields = ['customer_id', 'activity_type', 'title']
        for field in required_fields:
            if field not in activity_data or activity_data[field] is None:
                raise ValueError(f"Missing required field: {field}")
        
        return self._note_manager.create_activity(**activity_data)
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="get_activity", resource_type="activity"))
    def get_activity(self, activity_id: int) -> Optional[Dict[str, Any]]:
        """Get an activity by ID"""
        self._ensure_initialized()
        return self._note_manager.get_activity(activity_id)
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="update_activity", resource_type="activity"))
    def update_activity(self, activity_id: int, activity_data: Dict[str, Any]) -> bool:
        """Update an activity"""
        self._ensure_initialized()
        return self._note_manager.update_activity(activity_id, **activity_data)
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="delete_activity", resource_type="activity"))
    def delete_activity(self, activity_id: int) -> bool:
        """Delete an activity"""
        self._ensure_initialized()
        return self._note_manager.delete_activity(activity_id)
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="get_customer_activities", resource_type="activity"))
    def get_customer_activities(
        self,
        customer_id: int,
        activity_type: Optional[str] = None,
        include_archived: bool = False,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all activities for a customer"""
        self._ensure_initialized()
        return self._note_manager.get_customer_activities(
            customer_id, activity_type, include_archived, limit
        )
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="search_activities", resource_type="activity"))
    def search_activities(
        self,
        search_term: str,
        customer_id: Optional[int] = None,
        activity_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search activities"""
        self._ensure_initialized()
        return self._note_manager.search_activities(
            search_term, customer_id, activity_type, limit
        )
    
    @log_service_call
    @handle_service_errors(ErrorContext(operation="get_activity_statistics", resource_type="activity"))
    def get_activity_statistics(self, customer_id: int) -> Dict[str, Any]:
        """Get activity statistics for a customer"""
        self._ensure_initialized()
        return self._note_manager.get_activity_statistics(customer_id)


# Singleton instance
_crm_service_instance: Optional[CRMService] = None


def get_crm_service() -> CRMService:
    """Get or create the CRM service singleton instance"""
    global _crm_service_instance
    
    if _crm_service_instance is None:
        _crm_service_instance = CRMService()
        _crm_service_instance.initialize()
    
    return _crm_service_instance
