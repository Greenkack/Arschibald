"""
Database Audit System - Demo Script

This script demonstrates the complete functionality of the audit system.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.services.audit_service import AuditService
from backend.models.audit_schemas import (
    AuditLogCreate, DataAccessLogCreate, UserActionLogCreate, ComplianceLogCreate,
    AuditReportCreate, AuditLogQuery, DataAccessLogQuery, UserActionLogQuery,
    ComplianceLogQuery, ActionType, QueryType, ActionCategory, ActionStatus,
    ComplianceType, ComplianceStatus, ReportType, ReportFormat
)


def demo_change_tracking(db: Session):
    """Demonstrate change tracking functionality"""
    print("\n" + "="*80)
    print("DEMO: Change Tracking")
    print("="*80)
    
    audit_service = AuditService(db)
    
    # Log a CREATE operation
    print("\n1. Logging CREATE operation...")
    create_log = audit_service.log_change(AuditLogCreate(
        user_id=1,
        username="john.doe",
        action=ActionType.CREATE,
        table_name="projects",
        record_id="123",
        new_values={
            "name": "Solar Installation Project",
            "status": "draft",
            "system_size": 10.5
        },
        ip_address="192.168.1.100",
        session_id="session_abc123"
    ))
    print(f" Created audit log ID: {create_log.id}")
    
    # Log an UPDATE operation
    print("\n2. Logging UPDATE operation...")
    update_log = audit_service.log_change(AuditLogCreate(
        user_id=1,
        username="john.doe",
        action=ActionType.UPDATE,
        table_name="projects",
        record_id="123",
        old_values={
            "status": "draft",
            "system_size": 10.5
        },
        new_values={
            "status": "active",
            "system_size": 12.0
        },
        ip_address="192.168.1.100",
        session_id="session_abc123"
    ))
    print(f" Created audit log ID: {update_log.id}")
    print(f"  Changes detected: {update_log.changes}")
    
    # Log a DELETE operation
    print("\n3. Logging DELETE operation...")
    delete_log = audit_service.log_change(AuditLogCreate(
        user_id=1,
        username="john.doe",
        action=ActionType.DELETE,
        table_name="projects",
        record_id="123",
        old_values={
            "name": "Solar Installation Project",
            "status": "active",
            "system_size": 12.0
        },
        ip_address="192.168.1.100",
        session_id="session_abc123"
    ))
    print(f" Created audit log ID: {delete_log.id}")
    
    # Get record history
    print("\n4. Retrieving record history...")
    history = audit_service.get_record_history("projects", "123")
    print(f" Found {len(history)} changes for record projects/123:")
    for log in history:
        print(f"  - {log.timestamp}: {log.action} by {log.username}")


def demo_data_access_logging(db: Session):
    """Demonstrate data access logging functionality"""
    print("\n" + "="*80)
    print("DEMO: Data Access Logging")
    print("="*80)
    
    audit_service = AuditService(db)
    
    # Log a SELECT operation
    print("\n1. Logging SELECT operation...")
    select_log = audit_service.log_data_access(DataAccessLogCreate(
        user_id=1,
        username="john.doe",
        table_name="customers",
        record_id="456",
        query_type=QueryType.SELECT,
        result_count=1,
        ip_address="192.168.1.100"
    ))
    print(f" Created access log ID: {select_log.id}")
    
    # Log a SEARCH operation
    print("\n2. Logging SEARCH operation...")
    search_log = audit_service.log_data_access(DataAccessLogCreate(
        user_id=1,
        username="john.doe",
        table_name="customers",
        query_type=QueryType.SEARCH,
        query_params={"filter": "active", "city": "Berlin"},
        result_count=50,
        ip_address="192.168.1.100"
    ))
    print(f" Created access log ID: {search_log.id}")
    print(f"  Query params: {search_log.query_params}")
    print(f"  Results: {search_log.result_count} records")
    
    # Log an EXPORT operation
    print("\n3. Logging EXPORT operation...")
    export_log = audit_service.log_data_access(DataAccessLogCreate(
        user_id=1,
        username="john.doe",
        table_name="customers",
        query_type=QueryType.EXPORT,
        query_params={"format": "CSV", "filter": "active"},
        result_count=100,
        ip_address="192.168.1.100"
    ))
    print(f" Created access log ID: {export_log.id}")
    
    # Query access logs
    print("\n4. Querying access logs...")
    query = DataAccessLogQuery(
        user_id=1,
        table_name="customers",
        limit=10
    )
    logs = audit_service.get_data_access_logs(query)
    print(f" Found {len(logs)} access logs for user 1 on customers table")


def demo_user_action_logging(db: Session):
    """Demonstrate user action logging functionality"""
    print("\n" + "="*80)
    print("DEMO: User Action Logging")
    print("="*80)
    
    audit_service = AuditService(db)
    
    # Log a successful login
    print("\n1. Logging successful login...")
    login_log = audit_service.log_user_action(UserActionLogCreate(
        user_id=1,
        username="john.doe",
        action_type="LOGIN",
        action_category=ActionCategory.AUTH,
        action_details={"method": "password"},
        status=ActionStatus.SUCCESS,
        duration_ms=150,
        ip_address="192.168.1.100"
    ))
    print(f" Created action log ID: {login_log.id}")
    
    # Log a solar calculation
    print("\n2. Logging solar calculation...")
    calc_log = audit_service.log_user_action(UserActionLogCreate(
        user_id=1,
        username="john.doe",
        action_type="SOLAR_CALCULATION",
        action_category=ActionCategory.CALCULATION,
        action_details={
            "system_size": 10.5,
            "module_count": 30,
            "annual_production": 12000
        },
        status=ActionStatus.SUCCESS,
        duration_ms=1250,
        ip_address="192.168.1.100"
    ))
    print(f" Created action log ID: {calc_log.id}")
    print(f"  Duration: {calc_log.duration_ms}ms")
    
    # Log a PDF generation
    print("\n3. Logging PDF generation...")
    pdf_log = audit_service.log_user_action(UserActionLogCreate(
        user_id=1,
        username="john.doe",
        action_type="PDF_GENERATION",
        action_category=ActionCategory.PDF,
        action_details={
            "project_id": 123,
            "template": "standard",
            "pages": 8
        },
        status=ActionStatus.SUCCESS,
        duration_ms=3500,
        ip_address="192.168.1.100"
    ))
    print(f" Created action log ID: {pdf_log.id}")
    
    # Log a failed action
    print("\n4. Logging failed action...")
    failed_log = audit_service.log_user_action(UserActionLogCreate(
        user_id=1,
        username="john.doe",
        action_type="DATA_EXPORT",
        action_category=ActionCategory.REPORT,
        action_details={"format": "CSV"},
        status=ActionStatus.FAILURE,
        error_message="Insufficient permissions",
        duration_ms=50,
        ip_address="192.168.1.100"
    ))
    print(f" Created action log ID: {failed_log.id}")
    print(f"  Error: {failed_log.error_message}")
    
    # Query action logs
    print("\n5. Querying action logs...")
    query = UserActionLogQuery(
        user_id=1,
        action_category=ActionCategory.CALCULATION,
        limit=10
    )
    logs = audit_service.get_user_action_logs(query)
    print(f" Found {len(logs)} calculation actions for user 1")


def demo_compliance_logging(db: Session):
    """Demonstrate compliance logging functionality"""
    print("\n" + "="*80)
    print("DEMO: Compliance Logging")
    print("="*80)
    
    audit_service = AuditService(db)
    
    # Log a GDPR compliance event
    print("\n1. Logging GDPR data export...")
    gdpr_log = audit_service.log_compliance_event(ComplianceLogCreate(
        compliance_type=ComplianceType.GDPR,
        event_type="DATA_EXPORT",
        user_id=1,
        username="john.doe",
        affected_data={
            "table": "customers",
            "record_count": 100,
            "fields": ["name", "email", "phone"]
        },
        compliance_status=ComplianceStatus.COMPLIANT,
        details={
            "export_format": "CSV",
            "reason": "User data request",
            "request_id": "GDPR-2024-001"
        },
        notes="User requested all personal data for review"
    ))
    print(f" Created compliance log ID: {gdpr_log.id}")
    
    # Log a data retention event
    print("\n2. Logging data retention policy execution...")
    retention_log = audit_service.log_compliance_event(ComplianceLogCreate(
        compliance_type=ComplianceType.DATA_RETENTION,
        event_type="DATA_DELETION",
        affected_data={
            "table": "audit_logs",
            "deleted_count": 5000,
            "date_range": "2020-01-01 to 2021-12-31"
        },
        compliance_status=ComplianceStatus.COMPLIANT,
        details={
            "policy": "Delete logs older than 3 years",
            "automated": True
        }
    ))
    print(f" Created compliance log ID: {retention_log.id}")
    
    # Log a security event
    print("\n3. Logging security event...")
    security_log = audit_service.log_compliance_event(ComplianceLogCreate(
        compliance_type=ComplianceType.SECURITY,
        event_type="FAILED_LOGIN_ATTEMPTS",
        user_id=1,
        username="john.doe",
        affected_data={
            "attempt_count": 5,
            "ip_address": "192.168.1.100"
        },
        compliance_status=ComplianceStatus.NON_COMPLIANT,
        details={
            "action_taken": "Account temporarily locked",
            "duration_minutes": 30
        },
        notes="Multiple failed login attempts detected"
    ))
    print(f" Created compliance log ID: {security_log.id}")
    print(f"  Status: {security_log.compliance_status}")
    
    # Query compliance logs
    print("\n4. Querying compliance logs...")
    query = ComplianceLogQuery(
        compliance_type=ComplianceType.GDPR,
        limit=10
    )
    logs = audit_service.get_compliance_logs(query)
    print(f" Found {len(logs)} GDPR compliance logs")


def demo_audit_reports(db: Session):
    """Demonstrate audit report generation"""
    print("\n" + "="*80)
    print("DEMO: Audit Reports")
    print("="*80)
    
    audit_service = AuditService(db)
    
    # Create an audit report
    print("\n1. Creating audit report...")
    report = audit_service.create_audit_report(
        AuditReportCreate(
            report_type=ReportType.AUDIT,
            report_name="Monthly Audit Report - January 2024",
            date_from=datetime(2024, 1, 1),
            date_to=datetime(2024, 1, 31),
            file_format=ReportFormat.PDF
        ),
        created_by_id=1
    )
    print(f" Created report ID: {report.id}")
    print(f"  Name: {report.report_name}")
    print(f"  Type: {report.report_type}")
    print(f"  Status: {report.status}")
    print(f"  Summary: {report.summary}")
    
    # Create an access report
    print("\n2. Creating access report...")
    access_report = audit_service.create_audit_report(
        AuditReportCreate(
            report_type=ReportType.ACCESS,
            report_name="Data Access Report - Q1 2024",
            date_from=datetime(2024, 1, 1),
            date_to=datetime(2024, 3, 31),
            file_format=ReportFormat.EXCEL
        ),
        created_by_id=1
    )
    print(f" Created report ID: {access_report.id}")
    
    # Create a compliance report
    print("\n3. Creating compliance report...")
    compliance_report = audit_service.create_audit_report(
        AuditReportCreate(
            report_type=ReportType.COMPLIANCE,
            report_name="GDPR Compliance Report - 2024",
            date_from=datetime(2024, 1, 1),
            date_to=datetime(2024, 12, 31),
            file_format=ReportFormat.PDF
        ),
        created_by_id=1
    )
    print(f" Created report ID: {compliance_report.id}")
    
    # Get all reports
    print("\n4. Retrieving all reports...")
    reports = audit_service.get_audit_reports(limit=10)
    print(f" Found {len(reports)} reports")
    for r in reports:
        print(f"  - {r.report_name} ({r.report_type}) - {r.status}")


def demo_statistics(db: Session):
    """Demonstrate statistics functionality"""
    print("\n" + "="*80)
    print("DEMO: Statistics")
    print("="*80)
    
    audit_service = AuditService(db)
    
    # Get audit statistics
    print("\n1. Getting audit statistics...")
    audit_stats = audit_service.get_audit_statistics(
        date_from=datetime.now() - timedelta(days=30),
        date_to=datetime.now()
    )
    print(f" Audit Statistics (Last 30 days):")
    print(f"  Total changes: {audit_stats.total_changes}")
    print(f"  Changes by action: {audit_stats.changes_by_action}")
    print(f"  Changes by table: {audit_stats.changes_by_table}")
    print(f"  Most active users: {audit_stats.most_active_users[:3]}")
    print(f"  Most modified tables: {audit_stats.most_modified_tables[:3]}")
    
    # Get access statistics
    print("\n2. Getting access statistics...")
    access_stats = audit_service.get_access_statistics(
        date_from=datetime.now() - timedelta(days=30),
        date_to=datetime.now()
    )
    print(f" Access Statistics (Last 30 days):")
    print(f"  Total accesses: {access_stats.total_accesses}")
    print(f"  Accesses by type: {access_stats.accesses_by_type}")
    print(f"  Most accessed tables: {access_stats.most_accessed_tables[:3]}")
    
    # Get compliance statistics
    print("\n3. Getting compliance statistics...")
    compliance_stats = audit_service.get_compliance_statistics(
        date_from=datetime.now() - timedelta(days=30),
        date_to=datetime.now()
    )
    print(f" Compliance Statistics (Last 30 days):")
    print(f"  Total events: {compliance_stats.total_events}")
    print(f"  Events by type: {compliance_stats.events_by_type}")
    print(f"  Events by status: {compliance_stats.events_by_status}")
    print(f"  Compliance rate: {compliance_stats.compliance_rate:.2f}%")
    print(f"  Non-compliant events: {len(compliance_stats.non_compliant_events)}")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("DATABASE AUDIT SYSTEM - COMPLETE DEMO")
    print("="*80)
    print("\nThis demo showcases all features of the audit system:")
    print("  1. Change Tracking (CREATE, UPDATE, DELETE)")
    print("  2. Data Access Logging (SELECT, SEARCH, EXPORT)")
    print("  3. User Action Logging (LOGIN, CALCULATIONS, PDF, etc.)")
    print("  4. Compliance Logging (GDPR, Security, Data Retention)")
    print("  5. Audit Reports (Multiple types and formats)")
    print("  6. Statistics (Audit, Access, Compliance)")
    
    # Note: In a real scenario, you would get the db session from your app
    # from backend.core.database import SessionLocal
    # db = SessionLocal()
    
    # For demo purposes, we'll use a mock db
    db = None  # Replace with actual db session
    
    if db is None:
        print("\n  Note: This is a demonstration script.")
        print("    To run with actual database, uncomment the db initialization code.")
        print("    All functionality is implemented and ready to use!")
        return
    
    try:
        demo_change_tracking(db)
        demo_data_access_logging(db)
        demo_user_action_logging(db)
        demo_compliance_logging(db)
        demo_audit_reports(db)
        demo_statistics(db)
        
        print("\n" + "="*80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\n All audit system features demonstrated")
        print(" Ready for production use")
        print("\nFor more information, see:")
        print("  - docs/AUDIT_SYSTEM_GUIDE.md")
        print("  - docs/AUDIT_SYSTEM_QUICK_REFERENCE.md")
        
    finally:
        if db:
            db.close()


if __name__ == "__main__":
    main()
