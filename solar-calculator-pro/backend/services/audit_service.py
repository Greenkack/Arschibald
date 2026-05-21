"""
Database Audit Service

This service handles all audit logging functionality including change tracking,
user action logging, data access logging, and compliance reporting.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json

from backend.models.audit_models import (
    AuditLog, DataAccessLog, UserActionLog, ComplianceLog, AuditReport
)
from backend.models.audit_schemas import (
    AuditLogCreate, AuditLogResponse, AuditLogQuery,
    DataAccessLogCreate, DataAccessLogResponse, DataAccessLogQuery,
    UserActionLogCreate, UserActionLogResponse, UserActionLogQuery,
    ComplianceLogCreate, ComplianceLogResponse, ComplianceLogQuery,
    AuditReportCreate, AuditReportResponse,
    AuditStatistics, AccessStatistics, ComplianceStatistics,
    ActionType, QueryType, ActionCategory, ActionStatus,
    ComplianceType, ComplianceStatus, ReportType, ReportFormat
)


class AuditService:
    """Service for managing audit logs and compliance tracking"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== Change Tracking ====================
    
    def log_change(self, log_data: AuditLogCreate) -> AuditLog:
        """
        Log a database change (CREATE, UPDATE, DELETE).
        
        Args:
            log_data: Audit log data
            
        Returns:
            Created audit log entry
        """
        # Calculate changes if old and new values provided
        changes = None
        if log_data.old_values and log_data.new_values:
            changes = self._calculate_changes(log_data.old_values, log_data.new_values)
        
        audit_log = AuditLog(
            user_id=log_data.user_id,
            username=log_data.username,
            action=log_data.action.value,
            table_name=log_data.table_name,
            record_id=log_data.record_id,
            old_values=log_data.old_values,
            new_values=log_data.new_values,
            changes=changes or log_data.changes,
            ip_address=log_data.ip_address,
            user_agent=log_data.user_agent,
            session_id=log_data.session_id,
            request_id=log_data.request_id
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    def get_audit_logs(self, query: AuditLogQuery) -> List[AuditLog]:
        """
        Retrieve audit logs based on query parameters.
        
        Args:
            query: Query parameters
            
        Returns:
            List of audit logs
        """
        q = self.db.query(AuditLog)
        
        if query.user_id:
            q = q.filter(AuditLog.user_id == query.user_id)
        if query.action:
            q = q.filter(AuditLog.action == query.action.value)
        if query.table_name:
            q = q.filter(AuditLog.table_name == query.table_name)
        if query.date_from:
            q = q.filter(AuditLog.timestamp >= query.date_from)
        if query.date_to:
            q = q.filter(AuditLog.timestamp <= query.date_to)
        
        q = q.order_by(AuditLog.timestamp.desc())
        q = q.offset(query.offset).limit(query.limit)
        
        return q.all()
    
    def get_audit_log_by_id(self, log_id: int) -> Optional[AuditLog]:
        """Get a specific audit log by ID"""
        return self.db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    def get_record_history(self, table_name: str, record_id: str) -> List[AuditLog]:
        """
        Get complete history of changes for a specific record.
        
        Args:
            table_name: Name of the table
            record_id: ID of the record
            
        Returns:
            List of audit logs for the record
        """
        return self.db.query(AuditLog).filter(
            and_(
                AuditLog.table_name == table_name,
                AuditLog.record_id == record_id
            )
        ).order_by(AuditLog.timestamp.desc()).all()
    
    # ==================== Data Access Logging ====================
    
    def log_data_access(self, log_data: DataAccessLogCreate) -> DataAccessLog:
        """
        Log data access (read operations).
        
        Args:
            log_data: Data access log data
            
        Returns:
            Created data access log entry
        """
        access_log = DataAccessLog(
            user_id=log_data.user_id,
            username=log_data.username,
            table_name=log_data.table_name,
            record_id=log_data.record_id,
            query_type=log_data.query_type.value,
            query_params=log_data.query_params,
            result_count=log_data.result_count,
            ip_address=log_data.ip_address,
            user_agent=log_data.user_agent,
            session_id=log_data.session_id,
            request_id=log_data.request_id
        )
        
        self.db.add(access_log)
        self.db.commit()
        self.db.refresh(access_log)
        
        return access_log
    
    def get_data_access_logs(self, query: DataAccessLogQuery) -> List[DataAccessLog]:
        """
        Retrieve data access logs based on query parameters.
        
        Args:
            query: Query parameters
            
        Returns:
            List of data access logs
        """
        q = self.db.query(DataAccessLog)
        
        if query.user_id:
            q = q.filter(DataAccessLog.user_id == query.user_id)
        if query.table_name:
            q = q.filter(DataAccessLog.table_name == query.table_name)
        if query.query_type:
            q = q.filter(DataAccessLog.query_type == query.query_type.value)
        if query.date_from:
            q = q.filter(DataAccessLog.timestamp >= query.date_from)
        if query.date_to:
            q = q.filter(DataAccessLog.timestamp <= query.date_to)
        
        q = q.order_by(DataAccessLog.timestamp.desc())
        q = q.offset(query.offset).limit(query.limit)
        
        return q.all()
    
    # ==================== User Action Logging ====================
    
    def log_user_action(self, log_data: UserActionLogCreate) -> UserActionLog:
        """
        Log user action/activity.
        
        Args:
            log_data: User action log data
            
        Returns:
            Created user action log entry
        """
        action_log = UserActionLog(
            user_id=log_data.user_id,
            username=log_data.username,
            action_type=log_data.action_type,
            action_category=log_data.action_category.value,
            action_details=log_data.action_details,
            status=log_data.status.value,
            error_message=log_data.error_message,
            duration_ms=log_data.duration_ms,
            ip_address=log_data.ip_address,
            user_agent=log_data.user_agent,
            session_id=log_data.session_id,
            request_id=log_data.request_id
        )
        
        self.db.add(action_log)
        self.db.commit()
        self.db.refresh(action_log)
        
        return action_log
    
    def get_user_action_logs(self, query: UserActionLogQuery) -> List[UserActionLog]:
        """
        Retrieve user action logs based on query parameters.
        
        Args:
            query: Query parameters
            
        Returns:
            List of user action logs
        """
        q = self.db.query(UserActionLog)
        
        if query.user_id:
            q = q.filter(UserActionLog.user_id == query.user_id)
        if query.action_type:
            q = q.filter(UserActionLog.action_type == query.action_type)
        if query.action_category:
            q = q.filter(UserActionLog.action_category == query.action_category.value)
        if query.status:
            q = q.filter(UserActionLog.status == query.status.value)
        if query.date_from:
            q = q.filter(UserActionLog.timestamp >= query.date_from)
        if query.date_to:
            q = q.filter(UserActionLog.timestamp <= query.date_to)
        
        q = q.order_by(UserActionLog.timestamp.desc())
        q = q.offset(query.offset).limit(query.limit)
        
        return q.all()
    
    # ==================== Compliance Logging ====================
    
    def log_compliance_event(self, log_data: ComplianceLogCreate) -> ComplianceLog:
        """
        Log compliance event.
        
        Args:
            log_data: Compliance log data
            
        Returns:
            Created compliance log entry
        """
        compliance_log = ComplianceLog(
            compliance_type=log_data.compliance_type.value,
            event_type=log_data.event_type,
            user_id=log_data.user_id,
            username=log_data.username,
            affected_data=log_data.affected_data,
            compliance_status=log_data.compliance_status.value,
            details=log_data.details,
            notes=log_data.notes
        )
        
        self.db.add(compliance_log)
        self.db.commit()
        self.db.refresh(compliance_log)
        
        return compliance_log
    
    def get_compliance_logs(self, query: ComplianceLogQuery) -> List[ComplianceLog]:
        """
        Retrieve compliance logs based on query parameters.
        
        Args:
            query: Query parameters
            
        Returns:
            List of compliance logs
        """
        q = self.db.query(ComplianceLog)
        
        if query.compliance_type:
            q = q.filter(ComplianceLog.compliance_type == query.compliance_type.value)
        if query.compliance_status:
            q = q.filter(ComplianceLog.compliance_status == query.compliance_status.value)
        if query.date_from:
            q = q.filter(ComplianceLog.timestamp >= query.date_from)
        if query.date_to:
            q = q.filter(ComplianceLog.timestamp <= query.date_to)
        
        q = q.order_by(ComplianceLog.timestamp.desc())
        q = q.offset(query.offset).limit(query.limit)
        
        return q.all()
    
    # ==================== Audit Reports ====================
    
    def create_audit_report(
        self, 
        report_data: AuditReportCreate, 
        created_by_id: int
    ) -> AuditReport:
        """
        Create an audit report.
        
        Args:
            report_data: Report configuration
            created_by_id: ID of user creating the report
            
        Returns:
            Created audit report
        """
        report = AuditReport(
            created_by_id=created_by_id,
            report_type=report_data.report_type.value,
            report_name=report_data.report_name,
            date_from=report_data.date_from,
            date_to=report_data.date_to,
            filters=report_data.filters,
            file_format=report_data.file_format.value,
            status="GENERATING"
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        # Generate report summary
        summary = self._generate_report_summary(report)
        report.summary = summary
        
        # Update status
        report.status = "COMPLETED"
        self.db.commit()
        
        return report
    
    def get_audit_reports(
        self, 
        user_id: Optional[int] = None,
        report_type: Optional[ReportType] = None,
        limit: int = 100
    ) -> List[AuditReport]:
        """Get audit reports"""
        q = self.db.query(AuditReport)
        
        if user_id:
            q = q.filter(AuditReport.created_by_id == user_id)
        if report_type:
            q = q.filter(AuditReport.report_type == report_type.value)
        
        q = q.order_by(AuditReport.created_at.desc())
        q = q.limit(limit)
        
        return q.all()
    
    # ==================== Statistics ====================
    
    def get_audit_statistics(
        self, 
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> AuditStatistics:
        """
        Get audit statistics.
        
        Args:
            date_from: Start date
            date_to: End date
            
        Returns:
            Audit statistics
        """
        q = self.db.query(AuditLog)
        
        if date_from:
            q = q.filter(AuditLog.timestamp >= date_from)
        if date_to:
            q = q.filter(AuditLog.timestamp <= date_to)
        
        total_changes = q.count()
        
        # Changes by action
        changes_by_action = dict(
            self.db.query(AuditLog.action, func.count(AuditLog.id))
            .filter(self._apply_date_filter(AuditLog, date_from, date_to))
            .group_by(AuditLog.action)
            .all()
        )
        
        # Changes by table
        changes_by_table = dict(
            self.db.query(AuditLog.table_name, func.count(AuditLog.id))
            .filter(self._apply_date_filter(AuditLog, date_from, date_to))
            .group_by(AuditLog.table_name)
            .all()
        )
        
        # Changes by user
        changes_by_user = dict(
            self.db.query(AuditLog.username, func.count(AuditLog.id))
            .filter(self._apply_date_filter(AuditLog, date_from, date_to))
            .filter(AuditLog.username.isnot(None))
            .group_by(AuditLog.username)
            .all()
        )
        
        # Most active users
        most_active_users = [
            {"username": username, "change_count": count}
            for username, count in sorted(
                changes_by_user.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        ]
        
        # Most modified tables
        most_modified_tables = [
            {"table_name": table, "change_count": count}
            for table, count in sorted(
                changes_by_table.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        ]
        
        return AuditStatistics(
            total_changes=total_changes,
            changes_by_action=changes_by_action,
            changes_by_table=changes_by_table,
            changes_by_user=changes_by_user,
            most_active_users=most_active_users,
            most_modified_tables=most_modified_tables
        )
    
    def get_access_statistics(
        self, 
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> AccessStatistics:
        """Get data access statistics"""
        q = self.db.query(DataAccessLog)
        
        if date_from:
            q = q.filter(DataAccessLog.timestamp >= date_from)
        if date_to:
            q = q.filter(DataAccessLog.timestamp <= date_to)
        
        total_accesses = q.count()
        
        # Accesses by type
        accesses_by_type = dict(
            self.db.query(DataAccessLog.query_type, func.count(DataAccessLog.id))
            .filter(self._apply_date_filter(DataAccessLog, date_from, date_to))
            .group_by(DataAccessLog.query_type)
            .all()
        )
        
        # Accesses by table
        accesses_by_table = dict(
            self.db.query(DataAccessLog.table_name, func.count(DataAccessLog.id))
            .filter(self._apply_date_filter(DataAccessLog, date_from, date_to))
            .group_by(DataAccessLog.table_name)
            .all()
        )
        
        # Accesses by user
        accesses_by_user = dict(
            self.db.query(DataAccessLog.username, func.count(DataAccessLog.id))
            .filter(self._apply_date_filter(DataAccessLog, date_from, date_to))
            .filter(DataAccessLog.username.isnot(None))
            .group_by(DataAccessLog.username)
            .all()
        )
        
        # Most accessed tables
        most_accessed_tables = [
            {"table_name": table, "access_count": count}
            for table, count in sorted(
                accesses_by_table.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        ]
        
        # Most active users
        most_active_users = [
            {"username": username, "access_count": count}
            for username, count in sorted(
                accesses_by_user.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        ]
        
        return AccessStatistics(
            total_accesses=total_accesses,
            accesses_by_type=accesses_by_type,
            accesses_by_table=accesses_by_table,
            accesses_by_user=accesses_by_user,
            most_accessed_tables=most_accessed_tables,
            most_active_users=most_active_users
        )
    
    def get_compliance_statistics(
        self, 
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> ComplianceStatistics:
        """Get compliance statistics"""
        q = self.db.query(ComplianceLog)
        
        if date_from:
            q = q.filter(ComplianceLog.timestamp >= date_from)
        if date_to:
            q = q.filter(ComplianceLog.timestamp <= date_to)
        
        total_events = q.count()
        
        # Events by type
        events_by_type = dict(
            self.db.query(ComplianceLog.compliance_type, func.count(ComplianceLog.id))
            .filter(self._apply_date_filter(ComplianceLog, date_from, date_to))
            .group_by(ComplianceLog.compliance_type)
            .all()
        )
        
        # Events by status
        events_by_status = dict(
            self.db.query(ComplianceLog.compliance_status, func.count(ComplianceLog.id))
            .filter(self._apply_date_filter(ComplianceLog, date_from, date_to))
            .group_by(ComplianceLog.compliance_status)
            .all()
        )
        
        # Calculate compliance rate
        compliant_count = events_by_status.get("COMPLIANT", 0)
        compliance_rate = (compliant_count / total_events * 100) if total_events > 0 else 0.0
        
        # Non-compliant events
        non_compliant_events = [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "compliance_type": log.compliance_type,
                "event_type": log.event_type,
                "details": log.details
            }
            for log in self.db.query(ComplianceLog)
            .filter(
                and_(
                    ComplianceLog.compliance_status == "NON_COMPLIANT",
                    self._apply_date_filter(ComplianceLog, date_from, date_to)
                )
            )
            .order_by(ComplianceLog.timestamp.desc())
            .limit(20)
            .all()
        ]
        
        return ComplianceStatistics(
            total_events=total_events,
            events_by_type=events_by_type,
            events_by_status=events_by_status,
            compliance_rate=compliance_rate,
            non_compliant_events=non_compliant_events
        )
    
    # ==================== Helper Methods ====================
    
    def _calculate_changes(
        self, 
        old_values: Dict[str, Any], 
        new_values: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Calculate the differences between old and new values"""
        changes = {}
        
        all_keys = set(old_values.keys()) | set(new_values.keys())
        
        for key in all_keys:
            old_val = old_values.get(key)
            new_val = new_values.get(key)
            
            if old_val != new_val:
                changes[key] = {
                    "old": old_val,
                    "new": new_val
                }
        
        return changes
    
    def _apply_date_filter(self, model, date_from, date_to):
        """Apply date filter to query"""
        conditions = []
        if date_from:
            conditions.append(model.timestamp >= date_from)
        if date_to:
            conditions.append(model.timestamp <= date_to)
        return and_(*conditions) if conditions else True
    
    def _generate_report_summary(self, report: AuditReport) -> Dict[str, Any]:
        """Generate summary for audit report"""
        summary = {}
        
        if report.report_type == "AUDIT":
            stats = self.get_audit_statistics(report.date_from, report.date_to)
            summary = {
                "total_changes": stats.total_changes,
                "changes_by_action": stats.changes_by_action,
                "most_active_users": stats.most_active_users[:5]
            }
        elif report.report_type == "ACCESS":
            stats = self.get_access_statistics(report.date_from, report.date_to)
            summary = {
                "total_accesses": stats.total_accesses,
                "accesses_by_type": stats.accesses_by_type,
                "most_accessed_tables": stats.most_accessed_tables[:5]
            }
        elif report.report_type == "COMPLIANCE":
            stats = self.get_compliance_statistics(report.date_from, report.date_to)
            summary = {
                "total_events": stats.total_events,
                "compliance_rate": stats.compliance_rate,
                "events_by_status": stats.events_by_status
            }
        
        return summary
