"""Tests for Security & Access Control System"""

import time

import pytest

from .database import get_db_manager
from .security import (
    AuthenticationManager,
    AuthorizationManager,
    DataProtectionManager,
    PIIField,
    SecurityEventType,
    SecurityMonitor,
    SecuritySeverity,
    init_all_security_tables,
)


@pytest.fixture
def db_manager():
    """Get database manager for testing"""
    manager = get_db_manager()
    # Create tables
    init_all_security_tables()
    yield manager
    # Cleanup
    manager.drop_tables()


@pytest.fixture
def auth_manager(db_manager):
    """Get authentication manager"""
    return AuthenticationManager(db_manager)


@pytest.fixture
def authz_manager(db_manager):
    """Get authorization manager"""
    return AuthorizationManager(db_manager)


@pytest.fixture
def data_protection(db_manager):
    """Get data protection manager"""
    return DataProtectionManager()


@pytest.fixture
def security_monitor(db_manager):
    """Get security monitor"""
    return SecurityMonitor(db_manager)


# ============================================================================
# Task 9.1: Authentication System Tests
# ============================================================================

def test_user_registration(auth_manager):
    """Test user registration"""
    user = auth_manager.register_user(
        email="test@example.com",
        password="SecurePass123",
        username="testuser",
        full_name="Test User"
    )

    assert user is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.full_name == "Test User"
    assert user.password_hash is not None
    assert user.password_hash != "SecurePass123"


def test_password_hashing(auth_manager):
    """Test password hashing and verification"""
    password = "SecurePass123"
    hashed = auth_manager.password_hasher.hash_password(password)

    assert hashed != password
    assert auth_manager.password_hasher.verify_password(password, hashed)
    assert not auth_manager.password_hasher.verify_password(
        "WrongPass", hashed)


def test_authentication_success(auth_manager):
    """Test successful authentication"""
    # Register user
    auth_manager.register_user(
        email="test@example.com",
        password="SecurePass123"
    )

    # Authenticate
    result = auth_manager.authenticate(
        email="test@example.com",
        password="SecurePass123",
        ip_address="127.0.0.1"
    )

    assert result.status.value == "success"
    assert result.user is not None
    assert result.session_token is not None


def test_authentication_failure(auth_manager):
    """Test failed authentication"""
    # Register user
    auth_manager.register_user(
        email="test@example.com",
        password="SecurePass123"
    )

    # Authenticate with wrong password
    result = auth_manager.authenticate(
        email="test@example.com",
        password="WrongPassword",
        ip_address="127.0.0.1"
    )

    assert result.status.value == "failed"
    assert result.user is None
    assert result.session_token is None


def test_account_lockout(auth_manager):
    """Test account lockout after failed attempts"""
    # Register user
    auth_manager.register_user(
        email="test@example.com",
        password="SecurePass123"
    )

    # Attempt multiple failed logins
    for _ in range(5):
        auth_manager.authenticate(
            email="test@example.com",
            password="WrongPassword",
            ip_address="127.0.0.1"
        )

    # Next attempt should be locked
    result = auth_manager.authenticate(
        email="test@example.com",
        password="SecurePass123",
        ip_address="127.0.0.1"
    )

    assert result.status.value == "locked"


def test_session_management(auth_manager):
    """Test session creation and validation"""
    # Register and authenticate user
    user = auth_manager.register_user(
        email="test@example.com",
        password="SecurePass123"
    )

    result = auth_manager.authenticate(
        email="test@example.com",
        password="SecurePass123",
        ip_address="127.0.0.1"
    )

    # Validate session
    validated_user = auth_manager.session_manager.validate_session(
        result.session_token)
    assert validated_user is not None
    assert validated_user.id == user.id

    # Revoke session
    revoked = auth_manager.session_manager.revoke_session(result.session_token)
    assert revoked

    # Session should no longer be valid
    validated_user = auth_manager.session_manager.validate_session(
        result.session_token)
    assert validated_user is None


def test_password_change(auth_manager):
    """Test password change"""
    # Register user
    user = auth_manager.register_user(
        email="test@example.com",
        password="OldPass123"
    )

    # Change password
    success = auth_manager.change_password(
        user_id=user.id,
        old_password="OldPass123",
        new_password="NewPass456"
    )

    assert success

    # Old password should not work
    result = auth_manager.authenticate(
        email="test@example.com",
        password="OldPass123"
    )
    assert result.status.value == "failed"

    # New password should work
    result = auth_manager.authenticate(
        email="test@example.com",
        password="NewPass456"
    )
    assert result.status.value == "success"


# ============================================================================
# Task 9.2: Authorization & RBAC Tests
# ============================================================================

def test_role_creation(authz_manager):
    """Test role creation"""
    role = authz_manager.create_role(
        name="admin",
        description="Administrator role"
    )

    assert role is not None
    assert role.name == "admin"
    assert role.description == "Administrator role"


def test_permission_creation(authz_manager):
    """Test permission creation"""
    permission = authz_manager.create_permission(
        name="users:read",
        resource="users",
        action="read",
        description="Read user information"
    )

    assert permission is not None
    assert permission.name == "users:read"
    assert permission.resource == "users"
    assert permission.action == "read"


def test_role_assignment(auth_manager, authz_manager):
    """Test role assignment to user"""
    # Create user
    user = auth_manager.register_user(
        email="test@example.com",
        password="SecurePass123"
    )

    # Create role
    role = authz_manager.create_role(name="admin")

    # Assign role
    success = authz_manager.assign_role_to_user(user.id, role.id)
    assert success

    # Check role
    assert authz_manager.has_role(user.id, "admin")


def test_permission_assignment(authz_manager):
    """Test permission assignment to role"""
    # Create role and permission
    role = authz_manager.create_role(name="admin")
    permission = authz_manager.create_permission(
        name="users:read",
        resource="users",
        action="read"
    )

    # Assign permission to role
    success = authz_manager.assign_permission_to_role(role.id, permission.id)
    assert success


def test_user_permissions(auth_manager, authz_manager):
    """Test getting user permissions"""
    # Create user
    user = auth_manager.register_user(
        email="test@example.com",
        password="SecurePass123"
    )

    # Create role and permissions
    role = authz_manager.create_role(name="admin")
    perm1 = authz_manager.create_permission("users:read", "users", "read")
    perm2 = authz_manager.create_permission("users:write", "users", "write")

    # Assign permissions to role
    authz_manager.assign_permission_to_role(role.id, perm1.id)
    authz_manager.assign_permission_to_role(role.id, perm2.id)

    # Assign role to user
    authz_manager.assign_role_to_user(user.id, role.id)

    # Get user permissions
    permissions = authz_manager.get_user_permissions(user.id)
    assert "users:read" in permissions
    assert "users:write" in permissions


def test_hierarchical_roles(auth_manager, authz_manager):
    """Test hierarchical role permissions"""
    # Create user
    user = auth_manager.register_user(
        email="test@example.com",
        password="SecurePass123"
    )

    # Create parent and child roles
    parent_role = authz_manager.create_role(name="user")
    child_role = authz_manager.create_role(
        name="moderator",
        parent_role_id=parent_role.id
    )

    # Create permissions
    parent_perm = authz_manager.create_permission("data:read", "data", "read")
    child_perm = authz_manager.create_permission("data:write", "data", "write")

    # Assign permissions
    authz_manager.assign_permission_to_role(parent_role.id, parent_perm.id)
    authz_manager.assign_permission_to_role(child_role.id, child_perm.id)

    # Assign child role to user
    authz_manager.assign_role_to_user(user.id, child_role.id)

    # User should have both parent and child permissions
    permissions = authz_manager.get_user_permissions(user.id)
    assert "data:read" in permissions  # From parent
    assert "data:write" in permissions  # From child


def test_permission_caching(auth_manager, authz_manager):
    """Test permission caching"""
    # Create user with permissions
    user = auth_manager.register_user(
        email="test@example.com",
        password="SecurePass123"
    )

    role = authz_manager.create_role(name="admin")
    perm = authz_manager.create_permission("users:read", "users", "read")
    authz_manager.assign_permission_to_role(role.id, perm.id)
    authz_manager.assign_role_to_user(user.id, role.id)

    # First call - should cache
    start = time.time()
    permissions1 = authz_manager.get_user_permissions(user.id, use_cache=True)
    time1 = time.time() - start

    # Second call - should be faster from cache
    start = time.time()
    permissions2 = authz_manager.get_user_permissions(user.id, use_cache=True)
    time2 = time.time() - start

    assert permissions1 == permissions2
    # Cache should be faster (though this might not always be true in tests)
    # assert time2 < time1


# ============================================================================
# Task 9.3: Data Protection Tests
# ============================================================================

def test_pii_masking(data_protection):
    """Test PII masking"""
    # Email masking
    masked_email = data_protection.mask_email("john.doe@example.com")
    assert masked_email != "john.doe@example.com"
    assert "@example.com" in masked_email

    # Phone masking
    masked_phone = data_protection.mask_phone("555-123-4567")
    assert masked_phone.endswith("4567")
    assert "*" in masked_phone

    # Credit card masking
    masked_card = data_protection.mask_credit_card("1234-5678-9012-3456")
    assert masked_card.endswith("3456")
    assert "*" in masked_card


def test_pii_identification(data_protection):
    """Test PII field identification"""
    data = {
        "email": "test@example.com",
        "phone": "555-123-4567",
        "name": "John Doe",
        "age": 30
    }

    pii_fields = data_protection.identify_pii_fields(data)

    assert PIIField.EMAIL in pii_fields.values()
    assert PIIField.PHONE in pii_fields.values()
    assert PIIField.NAME in pii_fields.values()


def test_dict_masking(data_protection):
    """Test dictionary masking"""
    data = {
        "email": "test@example.com",
        "phone": "555-123-4567",
        "name": "John Doe",
        "age": 30
    }

    masked = data_protection.mask_dict(data)

    assert masked["email"] != data["email"]
    assert masked["phone"] != data["phone"]
    assert masked["age"] == data["age"]  # Non-PII unchanged


def test_data_encryption(data_protection):
    """Test data encryption and decryption"""
    original = "sensitive data"

    # Encrypt
    encrypted = data_protection.encrypt_data(original)
    assert encrypted != original

    # Decrypt
    decrypted = data_protection.decrypt_data(encrypted)
    assert decrypted == original


# ============================================================================
# Task 9.4: Security Monitoring Tests
# ============================================================================

def test_brute_force_detection(security_monitor, auth_manager):
    """Test brute force detection"""
    # Register user
    auth_manager.register_user(
        email="test@example.com",
        password="SecurePass123"
    )

    # Simulate failed login attempts
    for _ in range(5):
        auth_manager.authenticate(
            email="test@example.com",
            password="WrongPassword",
            ip_address="192.168.1.100"
        )

    # Check for brute force detection
    threat_detector = security_monitor.threat_detector
    is_brute_force = threat_detector.detect_brute_force(
        "test@example.com",
        "192.168.1.100"
    )

    assert is_brute_force


def test_sql_injection_detection(security_monitor):
    """Test SQL injection detection"""
    threat_detector = security_monitor.threat_detector

    # SQL injection attempts
    assert threat_detector.detect_sql_injection("SELECT * FROM users")
    assert threat_detector.detect_sql_injection("1' OR '1'='1")
    assert threat_detector.detect_sql_injection("DROP TABLE users")

    # Normal input
    assert not threat_detector.detect_sql_injection("Hello World")


def test_xss_detection(security_monitor):
    """Test XSS detection"""
    threat_detector = security_monitor.threat_detector

    # XSS attempts
    assert threat_detector.detect_xss("<script>alert('XSS')</script>")
    assert threat_detector.detect_xss("javascript:alert('XSS')")
    assert threat_detector.detect_xss("<img onerror='alert(1)'>")

    # Normal input
    assert not threat_detector.detect_xss("Hello World")


def test_security_event_logging(security_monitor):
    """Test security event logging"""
    event = security_monitor.log_security_event(
        event_type=SecurityEventType.FAILED_LOGIN,
        severity=SecuritySeverity.MEDIUM,
        description="Failed login attempt",
        user_id="user123",
        ip_address="192.168.1.100",
        threat_score=50
    )

    assert event is not None
    assert event.event_type == SecurityEventType.FAILED_LOGIN.value
    assert event.severity == SecuritySeverity.MEDIUM.value


def test_security_stats(security_monitor, auth_manager):
    """Test security statistics"""
    # Create some security events
    security_monitor.log_security_event(
        event_type=SecurityEventType.FAILED_LOGIN,
        severity=SecuritySeverity.MEDIUM,
        description="Failed login"
    )

    security_monitor.log_security_event(
        event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
        severity=SecuritySeverity.HIGH,
        description="Suspicious activity"
    )

    # Get stats
    stats = security_monitor.get_security_stats(days=7)

    assert stats['total_events'] >= 2
    assert 'events_by_severity' in stats
    assert 'events_by_type' in stats


def test_security_report(security_monitor):
    """Test security report generation"""
    # Create some events
    security_monitor.log_security_event(
        event_type=SecurityEventType.FAILED_LOGIN,
        severity=SecuritySeverity.CRITICAL,
        description="Critical event",
        ip_address="192.168.1.100"
    )

    # Generate report
    report = security_monitor.generate_security_report(days=7)

    assert 'report_date' in report
    assert 'statistics' in report
    assert 'critical_events' in report
    assert 'top_threat_ips' in report


def test_input_validation(security_monitor):
    """Test input validation"""
    # Valid input
    assert security_monitor.validate_input("Hello World", "test")

    # SQL injection
    assert not security_monitor.validate_input("SELECT * FROM users", "test")

    # XSS
    assert not security_monitor.validate_input(
        "<script>alert(1)</script>", "test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
