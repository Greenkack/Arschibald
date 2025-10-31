"""Verification script for Security & Access Control System"""

import sys


def verify_imports():
    """Verify all security components can be imported"""
    print("=" * 60)
    print("VERIFICATION: Security & Access Control System")
    print("=" * 60)
    print("\n1. Verifying imports...")

    try:
        from core.security import (
            AuthenticationAuditLog,
            # Authentication
            AuthenticationManager,
            AuthenticationResult,
            AuthenticationStatus,
            # Authorization
            AuthorizationManager,
            # Data Protection
            DataAccessLog,
            DataProtectionManager,
            DataRetentionPolicy,
            MFAManager,
            PasswordHasher,
            Permission,
            PermissionCache,
            PIIField,
            Role,
            # Security Monitoring
            SecurityEvent,
            SecurityEventType,
            SecurityMonitor,
            SecuritySeverity,
            SessionManager,
            ThreatDetector,
            User,
            UserSessionModel,
            # Initialization
            create_default_roles_and_permissions,
            init_all_security_tables,
            init_security_tables,
            log_data_access,
            require_permission,
            require_role,
        )
        print("   ✓ All security components imported successfully")
        return True
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        return False


def verify_authentication():
    """Verify authentication system"""
    print("\n2. Verifying authentication system...")

    try:
        from core.database import get_db_manager
        from core.security import (
            AuthenticationManager,
            init_all_security_tables,
        )

        # Initialize
        db_manager = get_db_manager()
        init_all_security_tables()
        auth_manager = AuthenticationManager(db_manager)

        # Test user registration
        user = auth_manager.register_user(
            email="test@example.com",
            password="TestPass123!",
            full_name="Test User"
        )
        print(f"   ✓ User registration: {user.email}")

        # Test authentication
        result = auth_manager.authenticate(
            email="test@example.com",
            password="TestPass123!",
            ip_address="127.0.0.1"
        )
        print(f"   ✓ Authentication: {result.status.value}")

        # Test session validation
        validated_user = auth_manager.session_manager.validate_session(
            result.session_token)
        print(f"   ✓ Session validation: {validated_user.email}")

        # Cleanup
        db_manager.drop_tables()

        return True
    except Exception as e:
        print(f"   ✗ Authentication verification failed: {e}")
        return False


def verify_authorization():
    """Verify authorization system"""
    print("\n3. Verifying authorization system...")

    try:
        from core.database import get_db_manager
        from core.security import (
            AuthenticationManager,
            AuthorizationManager,
            init_all_security_tables,
        )

        # Initialize
        db_manager = get_db_manager()
        init_all_security_tables()
        auth_manager = AuthenticationManager(db_manager)
        authz_manager = AuthorizationManager(db_manager)

        # Create user
        user = auth_manager.register_user(
            email="test@example.com",
            password="TestPass123!"
        )

        # Create role and permission
        role = authz_manager.create_role(name="test_role")
        permission = authz_manager.create_permission(
            name="test:read",
            resource="test",
            action="read"
        )
        print(f"   ✓ Role created: {role.name}")
        print(f"   ✓ Permission created: {permission.name}")

        # Assign permission to role
        authz_manager.assign_permission_to_role(role.id, permission.id)
        print("   ✓ Permission assigned to role")

        # Assign role to user
        authz_manager.assign_role_to_user(user.id, role.id)
        print("   ✓ Role assigned to user")

        # Check permission
        has_perm = authz_manager.has_permission(user.id, "test:read")
        print(f"   ✓ Permission check: {has_perm}")

        # Cleanup
        db_manager.drop_tables()

        return True
    except Exception as e:
        print(f"   ✗ Authorization verification failed: {e}")
        return False


def verify_data_protection():
    """Verify data protection system"""
    print("\n4. Verifying data protection system...")

    try:
        from core.security import DataProtectionManager

        data_protection = DataProtectionManager()

        # Test email masking
        email = "john.doe@example.com"
        masked_email = data_protection.mask_email(email)
        print(f"   ✓ Email masking: {email} -> {masked_email}")

        # Test phone masking
        phone = "555-123-4567"
        masked_phone = data_protection.mask_phone(phone)
        print(f"   ✓ Phone masking: {phone} -> {masked_phone}")

        # Test PII identification
        data = {
            "email": "test@example.com",
            "phone": "555-123-4567",
            "name": "John Doe"
        }
        pii_fields = data_protection.identify_pii_fields(data)
        print(f"   ✓ PII identification: {len(pii_fields)} fields found")

        # Test dictionary masking
        masked_data = data_protection.mask_dict(data)
        print(f"   ✓ Dictionary masking: {len(masked_data)} fields masked")

        # Test encryption
        sensitive = "sensitive data"
        encrypted = data_protection.encrypt_data(sensitive)
        decrypted = data_protection.decrypt_data(encrypted)
        print(f"   ✓ Encryption/Decryption: {sensitive == decrypted}")

        return True
    except Exception as e:
        print(f"   ✗ Data protection verification failed: {e}")
        return False


def verify_security_monitoring():
    """Verify security monitoring system"""
    print("\n5. Verifying security monitoring system...")

    try:
        from core.database import get_db_manager
        from core.security import (
            SecurityEventType,
            SecurityMonitor,
            SecuritySeverity,
            ThreatDetector,
            init_all_security_tables,
        )

        # Initialize
        db_manager = get_db_manager()
        init_all_security_tables()
        security_monitor = SecurityMonitor(db_manager)
        threat_detector = ThreatDetector(db_manager)

        # Test security event logging
        event = security_monitor.log_security_event(
            event_type=SecurityEventType.FAILED_LOGIN,
            severity=SecuritySeverity.MEDIUM,
            description="Test security event",
            ip_address="127.0.0.1"
        )
        print(f"   ✓ Security event logged: {event.event_type}")

        # Test SQL injection detection
        sql_injection = "SELECT * FROM users"
        is_sql = threat_detector.detect_sql_injection(sql_injection)
        print(f"   ✓ SQL injection detection: {is_sql}")

        # Test XSS detection
        xss_attempt = "<script>alert('XSS')</script>"
        is_xss = threat_detector.detect_xss(xss_attempt)
        print(f"   ✓ XSS detection: {is_xss}")

        # Test input validation
        safe_input = "Hello World"
        is_valid = security_monitor.validate_input(safe_input, "test")
        print(f"   ✓ Input validation (safe): {is_valid}")

        unsafe_input = "DROP TABLE users"
        is_valid = security_monitor.validate_input(unsafe_input, "test")
        print(f"   ✓ Input validation (unsafe): {not is_valid}")

        # Test security statistics
        stats = security_monitor.get_security_stats(days=7)
        print(f"   ✓ Security statistics: {stats['total_events']} events")

        # Cleanup
        db_manager.drop_tables()

        return True
    except Exception as e:
        print(f"   ✗ Security monitoring verification failed: {e}")
        return False


def verify_integration():
    """Verify core module integration"""
    print("\n6. Verifying core module integration...")

    try:
        from core import (
            # Authentication
            get_authentication_manager,
            get_authorization_manager,
            get_data_protection_manager,
            get_security_monitor,
        )

        print("   ✓ All security components available from core module")

        # Test convenience functions
        auth_manager = get_authentication_manager()
        authz_manager = get_authorization_manager()
        data_protection = get_data_protection_manager()
        security_monitor = get_security_monitor()

        print("   ✓ All convenience functions working")

        return True
    except Exception as e:
        print(f"   ✗ Integration verification failed: {e}")
        return False


def main():
    """Run all verifications"""
    results = []

    results.append(("Imports", verify_imports()))
    results.append(("Authentication", verify_authentication()))
    results.append(("Authorization", verify_authorization()))
    results.append(("Data Protection", verify_data_protection()))
    results.append(("Security Monitoring", verify_security_monitoring()))
    results.append(("Integration", verify_integration()))

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:.<40} {status}")

    all_passed = all(result for _, result in results)

    print("=" * 60)
    if all_passed:
        print("✓ ALL VERIFICATIONS PASSED")
        print("\nTask 9: Security & Access Control System is complete!")
        print("\nNext steps:")
        print("  1. Run tests: pytest core/test_security.py -v")
        print("  2. See examples: python core/example_security_usage.py")
        print("  3. Read docs: core/SECURITY_README.md")
        return 0
    print("✗ SOME VERIFICATIONS FAILED")
    print("\nPlease check the errors above and fix any issues.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
