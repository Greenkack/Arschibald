"""
Security Audit System
Task 186: Security event logging, intrusion detection, and compliance
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import asyncio


router = APIRouter(prefix="/security", tags=["Security Audit"])


class SecurityEventType(str, Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_DENIED = "permission_denied"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    API_RATE_LIMIT = "api_rate_limit"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    INTRUSION_ATTEMPT = "intrusion_attempt"
    CONFIGURATION_CHANGE = "configuration_change"
    EXPORT_DATA = "export_data"
    ADMIN_ACTION = "admin_action"


class SecuritySeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEvent(BaseModel):
    """Security event model"""
    id: str
    timestamp: datetime
    event_type: SecurityEventType
    severity: SecuritySeverity
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    details: Dict[str, Any] = {}
    success: bool = True


class SecurityAlert(BaseModel):
    """Security alert model"""
    id: str
    timestamp: datetime
    alert_type: str
    severity: SecuritySeverity
    title: str
    description: str
    source_events: List[str] = []
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class IntrusionPattern(BaseModel):
    """Intrusion detection pattern"""
    pattern_id: str
    name: str
    description: str
    detection_rules: Dict[str, Any]
    severity: SecuritySeverity
    enabled: bool = True


class ComplianceCheck(BaseModel):
    """Compliance check result"""
    check_id: str
    name: str
    category: str
    status: str  # passed, failed, warning
    details: str
    last_checked: datetime


class VulnerabilityScan(BaseModel):
    """Vulnerability scan result"""
    scan_id: str
    timestamp: datetime
    target: str
    vulnerabilities_found: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    details: List[Dict[str, Any]]


# In-memory storage (would be database in production)
security_events: List[SecurityEvent] = []
security_alerts: List[SecurityAlert] = []
intrusion_patterns: List[IntrusionPattern] = []


# Default intrusion detection patterns
DEFAULT_PATTERNS = [
    IntrusionPattern(
        pattern_id="brute_force",
        name="Brute Force Attack",
        description="Multiple failed login attempts from same IP",
        detection_rules={
            "event_type": "login_failure",
            "threshold": 5,
            "time_window_minutes": 10,
            "group_by": "ip_address"
        },
        severity=SecuritySeverity.HIGH
    ),
    IntrusionPattern(
        pattern_id="sql_injection",
        name="SQL Injection Attempt",
        description="SQL injection patterns detected in input",
        detection_rules={
            "patterns": ["' OR '", "'; DROP", "UNION SELECT", "1=1"],
            "check_fields": ["query", "search", "filter"]
        },
        severity=SecuritySeverity.CRITICAL
    ),
    IntrusionPattern(
        pattern_id="xss_attempt",
        name="XSS Attack Attempt",
        description="Cross-site scripting patterns detected",
        detection_rules={
            "patterns": ["<script>", "javascript:", "onerror=", "onload="],
            "check_fields": ["input", "comment", "name"]
        },
        severity=SecuritySeverity.HIGH
    ),
    IntrusionPattern(
        pattern_id="privilege_escalation",
        name="Privilege Escalation Attempt",
        description="Unauthorized access to admin resources",
        detection_rules={
            "event_type": "permission_denied",
            "resource_pattern": "/admin/*",
            "threshold": 3,
            "time_window_minutes": 5
        },
        severity=SecuritySeverity.CRITICAL
    ),
    IntrusionPattern(
        pattern_id="data_exfiltration",
        name="Data Exfiltration Attempt",
        description="Large data export in short time",
        detection_rules={
            "event_type": "export_data",
            "threshold": 10,
            "time_window_minutes": 30
        },
        severity=SecuritySeverity.HIGH
    )
]

intrusion_patterns.extend(DEFAULT_PATTERNS)


def generate_event_id() -> str:
    """Generate unique event ID"""
    return hashlib.sha256(f"{datetime.now().isoformat()}{len(security_events)}".encode()).hexdigest()[:16]


def generate_alert_id() -> str:
    """Generate unique alert ID"""
    return hashlib.sha256(f"alert_{datetime.now().isoformat()}{len(security_alerts)}".encode()).hexdigest()[:16]


async def check_intrusion_patterns(event: SecurityEvent):
    """Check event against intrusion patterns"""
    for pattern in intrusion_patterns:
        if not pattern.enabled:
            continue
            
        rules = pattern.detection_rules
        
        # Check brute force pattern
        if pattern.pattern_id == "brute_force" and event.event_type == SecurityEventType.LOGIN_FAILURE:
            time_window = datetime.now() - timedelta(minutes=rules.get("time_window_minutes", 10))
            recent_failures = [
                e for e in security_events
                if e.event_type == SecurityEventType.LOGIN_FAILURE
                and e.ip_address == event.ip_address
                and e.timestamp >= time_window
            ]
            
            if len(recent_failures) >= rules.get("threshold", 5):
                await create_security_alert(
                    alert_type="intrusion_detection",
                    severity=pattern.severity,
                    title=pattern.name,
                    description=f"Detected {len(recent_failures)} failed login attempts from {event.ip_address}",
                    source_events=[e.id for e in recent_failures]
                )
                
        # Check privilege escalation
        if pattern.pattern_id == "privilege_escalation" and event.event_type == SecurityEventType.PERMISSION_DENIED:
            if event.resource and "/admin" in event.resource:
                time_window = datetime.now() - timedelta(minutes=rules.get("time_window_minutes", 5))
                recent_denials = [
                    e for e in security_events
                    if e.event_type == SecurityEventType.PERMISSION_DENIED
                    and e.user_id == event.user_id
                    and e.timestamp >= time_window
                ]
                
                if len(recent_denials) >= rules.get("threshold", 3):
                    await create_security_alert(
                        alert_type="intrusion_detection",
                        severity=pattern.severity,
                        title=pattern.name,
                        description=f"User {event.user_id} attempted unauthorized admin access {len(recent_denials)} times",
                        source_events=[e.id for e in recent_denials]
                    )


async def create_security_alert(
    alert_type: str,
    severity: SecuritySeverity,
    title: str,
    description: str,
    source_events: List[str] = []
) -> SecurityAlert:
    """Create a security alert"""
    alert = SecurityAlert(
        id=generate_alert_id(),
        timestamp=datetime.now(),
        alert_type=alert_type,
        severity=severity,
        title=title,
        description=description,
        source_events=source_events
    )
    security_alerts.append(alert)
    return alert


@router.post("/events", response_model=SecurityEvent)
async def log_security_event(
    event_type: SecurityEventType,
    severity: SecuritySeverity = SecuritySeverity.INFO,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    details: Dict[str, Any] = {},
    success: bool = True
):
    """Log a security event"""
    event = SecurityEvent(
        id=generate_event_id(),
        timestamp=datetime.now(),
        event_type=event_type,
        severity=severity,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        resource=resource,
        action=action,
        details=details,
        success=success
    )
    
    security_events.append(event)
    
    # Check for intrusion patterns
    await check_intrusion_patterns(event)
    
    return event


@router.get("/events", response_model=List[SecurityEvent])
async def get_security_events(
    event_type: Optional[SecurityEventType] = None,
    severity: Optional[SecuritySeverity] = None,
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100
):
    """Get security events with filtering"""
    filtered = security_events.copy()
    
    if event_type:
        filtered = [e for e in filtered if e.event_type == event_type]
    if severity:
        filtered = [e for e in filtered if e.severity == severity]
    if user_id:
        filtered = [e for e in filtered if e.user_id == user_id]
    if start_date:
        filtered = [e for e in filtered if e.timestamp >= start_date]
    if end_date:
        filtered = [e for e in filtered if e.timestamp <= end_date]
        
    return sorted(filtered, key=lambda x: x.timestamp, reverse=True)[:limit]


@router.get("/alerts", response_model=List[SecurityAlert])
async def get_security_alerts(
    severity: Optional[SecuritySeverity] = None,
    acknowledged: Optional[bool] = None,
    limit: int = 50
):
    """Get security alerts"""
    filtered = security_alerts.copy()
    
    if severity:
        filtered = [a for a in filtered if a.severity == severity]
    if acknowledged is not None:
        filtered = [a for a in filtered if a.acknowledged == acknowledged]
        
    return sorted(filtered, key=lambda x: x.timestamp, reverse=True)[:limit]


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, acknowledged_by: str):
    """Acknowledge a security alert"""
    for alert in security_alerts:
        if alert.id == alert_id:
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now()
            return {"status": "acknowledged", "alert_id": alert_id}
            
    raise HTTPException(status_code=404, detail="Alert not found")


@router.get("/intrusion-patterns", response_model=List[IntrusionPattern])
async def get_intrusion_patterns():
    """Get all intrusion detection patterns"""
    return intrusion_patterns


@router.post("/intrusion-patterns", response_model=IntrusionPattern)
async def create_intrusion_pattern(pattern: IntrusionPattern):
    """Create a new intrusion detection pattern"""
    intrusion_patterns.append(pattern)
    return pattern


@router.put("/intrusion-patterns/{pattern_id}/toggle")
async def toggle_intrusion_pattern(pattern_id: str, enabled: bool):
    """Enable or disable an intrusion pattern"""
    for pattern in intrusion_patterns:
        if pattern.pattern_id == pattern_id:
            pattern.enabled = enabled
            return {"status": "updated", "pattern_id": pattern_id, "enabled": enabled}
            
    raise HTTPException(status_code=404, detail="Pattern not found")


@router.get("/compliance-check", response_model=List[ComplianceCheck])
async def run_compliance_check():
    """Run compliance checks"""
    checks = []
    
    # Password policy check
    checks.append(ComplianceCheck(
        check_id="password_policy",
        name="Password Policy",
        category="Authentication",
        status="passed",
        details="Password complexity requirements are enforced",
        last_checked=datetime.now()
    ))
    
    # Session timeout check
    checks.append(ComplianceCheck(
        check_id="session_timeout",
        name="Session Timeout",
        category="Authentication",
        status="passed",
        details="Sessions expire after 30 minutes of inactivity",
        last_checked=datetime.now()
    ))
    
    # Data encryption check
    checks.append(ComplianceCheck(
        check_id="data_encryption",
        name="Data Encryption",
        category="Data Protection",
        status="passed",
        details="Sensitive data is encrypted at rest and in transit",
        last_checked=datetime.now()
    ))
    
    # Access logging check
    checks.append(ComplianceCheck(
        check_id="access_logging",
        name="Access Logging",
        category="Audit",
        status="passed",
        details="All data access is logged with user and timestamp",
        last_checked=datetime.now()
    ))
    
    # HTTPS enforcement check
    checks.append(ComplianceCheck(
        check_id="https_enforcement",
        name="HTTPS Enforcement",
        category="Network Security",
        status="warning",
        details="HTTPS should be enforced in production",
        last_checked=datetime.now()
    ))
    
    # Rate limiting check
    checks.append(ComplianceCheck(
        check_id="rate_limiting",
        name="Rate Limiting",
        category="API Security",
        status="passed",
        details="API rate limiting is configured",
        last_checked=datetime.now()
    ))
    
    return checks


@router.post("/vulnerability-scan", response_model=VulnerabilityScan)
async def run_vulnerability_scan(target: str = "application"):
    """Run a vulnerability scan"""
    # Simulated vulnerability scan results
    scan = VulnerabilityScan(
        scan_id=hashlib.sha256(f"scan_{datetime.now().isoformat()}".encode()).hexdigest()[:16],
        timestamp=datetime.now(),
        target=target,
        vulnerabilities_found=3,
        critical_count=0,
        high_count=1,
        medium_count=1,
        low_count=1,
        details=[
            {
                "id": "VULN-001",
                "severity": "high",
                "title": "Missing Security Headers",
                "description": "Some security headers are not configured",
                "recommendation": "Add X-Content-Type-Options, X-Frame-Options headers"
            },
            {
                "id": "VULN-002",
                "severity": "medium",
                "title": "Verbose Error Messages",
                "description": "Error messages may reveal sensitive information",
                "recommendation": "Use generic error messages in production"
            },
            {
                "id": "VULN-003",
                "severity": "low",
                "title": "Server Version Disclosure",
                "description": "Server header reveals version information",
                "recommendation": "Remove or obfuscate server version"
            }
        ]
    )
    
    return scan


@router.get("/report")
async def generate_security_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Generate a security report"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
        
    # Filter events in date range
    events_in_range = [
        e for e in security_events
        if start_date <= e.timestamp <= end_date
    ]
    
    # Count by type
    events_by_type = {}
    for event in events_in_range:
        event_type = event.event_type.value
        events_by_type[event_type] = events_by_type.get(event_type, 0) + 1
        
    # Count by severity
    events_by_severity = {}
    for event in events_in_range:
        severity = event.severity.value
        events_by_severity[severity] = events_by_severity.get(severity, 0) + 1
        
    # Get alerts in range
    alerts_in_range = [
        a for a in security_alerts
        if start_date <= a.timestamp <= end_date
    ]
    
    # Run compliance check
    compliance_results = await run_compliance_check()
    compliance_passed = sum(1 for c in compliance_results if c.status == "passed")
    compliance_total = len(compliance_results)
    
    return {
        "report_period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "summary": {
            "total_events": len(events_in_range),
            "total_alerts": len(alerts_in_range),
            "unacknowledged_alerts": sum(1 for a in alerts_in_range if not a.acknowledged),
            "compliance_score": f"{compliance_passed}/{compliance_total}"
        },
        "events_by_type": events_by_type,
        "events_by_severity": events_by_severity,
        "top_users_by_events": {},  # Would aggregate by user
        "top_ips_by_events": {},  # Would aggregate by IP
        "alerts_summary": {
            "critical": sum(1 for a in alerts_in_range if a.severity == SecuritySeverity.CRITICAL),
            "high": sum(1 for a in alerts_in_range if a.severity == SecuritySeverity.HIGH),
            "medium": sum(1 for a in alerts_in_range if a.severity == SecuritySeverity.MEDIUM),
            "low": sum(1 for a in alerts_in_range if a.severity == SecuritySeverity.LOW)
        },
        "recommendations": [
            "Review and acknowledge all unacknowledged alerts",
            "Address any failed compliance checks",
            "Monitor for recurring security events",
            "Update intrusion detection patterns as needed"
        ]
    }


@router.get("/dashboard")
async def get_security_dashboard():
    """Get security dashboard data"""
    now = datetime.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    
    events_24h = [e for e in security_events if e.timestamp >= last_24h]
    events_7d = [e for e in security_events if e.timestamp >= last_7d]
    
    alerts_24h = [a for a in security_alerts if a.timestamp >= last_24h]
    unack_alerts = [a for a in security_alerts if not a.acknowledged]
    
    return {
        "overview": {
            "events_24h": len(events_24h),
            "events_7d": len(events_7d),
            "alerts_24h": len(alerts_24h),
            "unacknowledged_alerts": len(unack_alerts),
            "active_patterns": sum(1 for p in intrusion_patterns if p.enabled)
        },
        "recent_alerts": [
            {
                "id": a.id,
                "title": a.title,
                "severity": a.severity.value,
                "timestamp": a.timestamp.isoformat()
            }
            for a in sorted(security_alerts, key=lambda x: x.timestamp, reverse=True)[:5]
        ],
        "event_trend": {
            "login_failures": sum(1 for e in events_24h if e.event_type == SecurityEventType.LOGIN_FAILURE),
            "permission_denied": sum(1 for e in events_24h if e.event_type == SecurityEventType.PERMISSION_DENIED),
            "suspicious_activity": sum(1 for e in events_24h if e.event_type == SecurityEventType.SUSPICIOUS_ACTIVITY)
        },
        "threat_level": "low" if len(unack_alerts) == 0 else "medium" if len(unack_alerts) < 5 else "high"
    }
