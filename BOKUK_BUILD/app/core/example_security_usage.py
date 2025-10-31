"""Example usage of Security & Access Control System"""

from core.database import get_db_manager
from core.security import (
    AuthenticationManager,
    AuthorizationManager,
    DataProtectionManager,
    SecurityEventType,
    SecurityMonitor,
    SecuritySeverity,
    create_default_roles_and_permissions,
    init_all_security_tables,
)


def example_authentication():
    """Example: User authentication"""
    print("\n=== Authentication Example ===\n")

    # Initialize
    init_all_security_tables()
    auth_manager = AuthenticationManager()

    # Register a new user
    print("1. Registering new user...")
    user = auth_manager.register_user(
        email="john.doe@example.com",
        password="SecurePass123!",
        username="johndoe",
        full_name="John Doe"
    )
    print(f"   User registered: {user.email}")

    # Authenticate user
    print("\n2. Authenticating user...")
    result = auth_manager.authenticate(
        email="john.doe@example.com",
        password="SecurePass123!",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0"
    )

    if result.status.value == "success":
        print("   Authentication successful!")
        print(f"   Session token: {result.session_token[:20]}...")
    else:
        print(f"   Authentication failed: {result.message}")

    # Validate session
    print("\n3. Validating session...")
    validated_user = auth_manager.session_manager.validate_session(
        result.session_token)
    if validated_user:
        print(f"   Session valid for user: {validated_user.email}")

    # Change password
    print("\n4. Changing password...")
    success = auth_manager.change_password(
        user_id=user.id,
        old_password="SecurePass123!",
        new_password="NewSecurePass456!"
    )
    print(f"   Password changed: {success}")

    # Logout
    print("\n5. Logging out...")
    auth_manager.logout(result.session_token)
    print("   User logged out")


def example_mfa():
    """Example: Multi-factor authentication"""
    print("\n=== MFA Example ===\n")

    init_all_security_tables()
    auth_manager = AuthenticationManager()

    # Register user
    user = auth_manager.register_user(
        email="jane.doe@example.com",
        password="SecurePass123!"
    )

    # Enable MFA
    print("1. Enabling MFA...")
    mfa_data = auth_manager.enable_mfa(user.id)
    print(f"   MFA Secret: {mfa_data['secret']}")
    print(f"   Provisioning URI: {mfa_data['provisioning_uri'][:50]}...")
    print("   (Scan QR code with authenticator app)")

    # Authenticate with MFA
    print("\n2. Authenticating with MFA...")
    result = auth_manager.authenticate(
        email="jane.doe@example.com",
        password="SecurePass123!"
    )

    if result.requires_mfa:
        print("   MFA required!")
        print("   Enter MFA token from authenticator app")
        # In real usage, get token from user input
        # mfa_token = input("MFA Token: ")
        # result = auth_manager.authenticate(
        #     email="jane.doe@example.com",
        #     password="SecurePass123!",
        #     mfa_token=mfa_token
        # )


def example_authorization():
    """Example: Role-based access control"""
    print("\n=== Authorization Example ===\n")

    init_all_security_tables()
    auth_manager = AuthenticationManager()
    authz_manager = AuthorizationManager()

    # Create user
    user = auth_manager.register_user(
        email="user@example.com",
        password="SecurePass123!"
    )

    # Create roles
    print("1. Creating roles...")
    admin_role = authz_manager.create_role(
        name="admin",
        description="Administrator with full access"
    )
    user_role = authz_manager.create_role(
        name="user",
        description="Standard user"
    )
    print("   Created roles: admin, user")

    # Create permissions
    print("\n2. Creating permissions...")
    read_perm = authz_manager.create_permission(
        name="users:read",
        resource="users",
        action="read",
        description="Read user information"
    )
    write_perm = authz_manager.create_permission(
        name="users:write",
        resource="users",
        action="write",
        description="Create and update users"
    )
    delete_perm = authz_manager.create_permission(
        name="users:delete",
        resource="users",
        action="delete",
        description="Delete users"
    )
    print("   Created permissions: users:read, users:write, users:delete")

    # Assign permissions to roles
    print("\n3. Assigning permissions to roles...")
    authz_manager.assign_permission_to_role(admin_role.id, read_perm.id)
    authz_manager.assign_permission_to_role(admin_role.id, write_perm.id)
    authz_manager.assign_permission_to_role(admin_role.id, delete_perm.id)
    authz_manager.assign_permission_to_role(user_role.id, read_perm.id)
    print("   Admin has all permissions, user has read only")

    # Assign role to user
    print("\n4. Assigning role to user...")
    authz_manager.assign_role_to_user(user.id, user_role.id)
    print("   User assigned 'user' role")

    # Check permissions
    print("\n5. Checking permissions...")
    permissions = authz_manager.get_user_permissions(user.id)
    print(f"   User permissions: {permissions}")

    has_read = authz_manager.has_permission(user.id, "users:read")
    has_delete = authz_manager.has_permission(user.id, "users:delete")
    print(f"   Can read users: {has_read}")
    print(f"   Can delete users: {has_delete}")


def example_data_protection():
    """Example: Data protection and PII masking"""
    print("\n=== Data Protection Example ===\n")

    data_protection = DataProtectionManager()

    # Mask PII
    print("1. Masking PII...")
    email = "john.doe@example.com"
    phone = "555-123-4567"
    card = "1234-5678-9012-3456"

    print(f"   Original email: {email}")
    print(f"   Masked email: {data_protection.mask_email(email)}")
    print(f"   Original phone: {phone}")
    print(f"   Masked phone: {data_protection.mask_phone(phone)}")
    print(f"   Original card: {card}")
    print(f"   Masked card: {data_protection.mask_credit_card(card)}")

    # Identify PII in data
    print("\n2. Identifying PII fields...")
    user_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "555-123-4567",
        "age": 30,
        "address": "123 Main St"
    }

    pii_fields = data_protection.identify_pii_fields(user_data)
    print(f"   PII fields found: {list(pii_fields.keys())}")

    # Mask dictionary
    print("\n3. Masking dictionary...")
    masked_data = data_protection.mask_dict(user_data)
    print(f"   Original: {user_data}")
    print(f"   Masked: {masked_data}")

    # Encrypt sensitive data
    print("\n4. Encrypting sensitive data...")
    sensitive = "Social Security Number: 123-45-6789"
    encrypted = data_protection.encrypt_data(sensitive)
    decrypted = data_protection.decrypt_data(encrypted)
    print(f"   Original: {sensitive}")
    print(f"   Encrypted: {encrypted[:50]}...")
    print(f"   Decrypted: {decrypted}")


def example_security_monitoring():
    """Example: Security monitoring and threat detection"""
    print("\n=== Security Monitoring Example ===\n")

    init_all_security_tables()
    security_monitor = SecurityMonitor()

    # Log security event
    print("1. Logging security event...")
    event = security_monitor.log_security_event(
        event_type=SecurityEventType.FAILED_LOGIN,
        severity=SecuritySeverity.MEDIUM,
        description="Failed login attempt from suspicious IP",
        user_id="user123",
        ip_address="192.168.1.100",
        threat_score=60,
        action_taken="IP flagged for monitoring"
    )
    print(f"   Event logged: {event.event_type} (severity: {event.severity})")

    # Detect SQL injection
    print("\n2. Detecting SQL injection...")
    malicious_input = "SELECT * FROM users WHERE id = 1"
    is_sql_injection = security_monitor.threat_detector.detect_sql_injection(
        malicious_input)
    print(f"   Input: {malicious_input}")
    print(f"   SQL injection detected: {is_sql_injection}")

    # Detect XSS
    print("\n3. Detecting XSS...")
    xss_input = "<script>alert('XSS')</script>"
    is_xss = security_monitor.threat_detector.detect_xss(xss_input)
    print(f"   Input: {xss_input}")
    print(f"   XSS detected: {is_xss}")

    # Validate input
    print("\n4. Validating user input...")
    safe_input = "Hello World"
    unsafe_input = "DROP TABLE users"

    print(f"   Input: {safe_input}")
    print(
        f"   Valid: {
            security_monitor.validate_input(
                safe_input,
                'user_comment')}")
    print(f"   Input: {unsafe_input}")
    print(
        f"   Valid: {
            security_monitor.validate_input(
                unsafe_input,
                'user_comment')}")

    # Get security statistics
    print("\n5. Getting security statistics...")
    stats = security_monitor.get_security_stats(days=7)
    print(f"   Total events (last 7 days): {stats['total_events']}")
    print(f"   Events by severity: {stats['events_by_severity']}")
    print(f"   Unresolved events: {stats['unresolved_events']}")

    # Generate security report
    print("\n6. Generating security report...")
    report = security_monitor.generate_security_report(days=30)
    print(f"   Report period: {report['period_days']} days")
    print(f"   Total events: {report['statistics']['total_events']}")
    print(f"   Critical events: {len(report['critical_events'])}")


def example_complete_workflow():
    """Example: Complete security workflow"""
    print("\n=== Complete Security Workflow ===\n")

    # Initialize
    init_all_security_tables()
    create_default_roles_and_permissions()

    auth_manager = AuthenticationManager()
    authz_manager = AuthorizationManager()
    data_protection = DataProtectionManager()
    security_monitor = SecurityMonitor()

    # 1. Register user
    print("1. User Registration")
    user = auth_manager.register_user(
        email="admin@example.com",
        password="AdminPass123!",
        full_name="Admin User"
    )
    print(f"   ✓ User registered: {user.email}")

    # 2. Assign admin role
    print("\n2. Role Assignment")
    # Get admin role (created by create_default_roles_and_permissions)
    roles = authz_manager.get_user_roles(user.id)
    if not any(r.name == "admin" for r in roles):
        # Find admin role
        with get_db_manager().session_scope() as session:
            from .security import Role
            admin_role = session.query(Role).filter(
                Role.name == "admin").first()
            if admin_role:
                authz_manager.assign_role_to_user(user.id, admin_role.id)
                print("   ✓ Admin role assigned")

    # 3. Authenticate
    print("\n3. Authentication")
    result = auth_manager.authenticate(
        email="admin@example.com",
        password="AdminPass123!",
        ip_address="192.168.1.100"
    )
    print(f"   ✓ Authentication: {result.status.value}")

    # 4. Check permissions
    print("\n4. Authorization Check")
    permissions = authz_manager.get_user_permissions(user.id)
    print(f"   ✓ User has {len(permissions)} permissions")
    print(
        f"   ✓ Can delete users: {
            authz_manager.has_permission(
                user.id,
                'users:delete')}")

    # 5. Handle sensitive data
    print("\n5. Data Protection")
    sensitive_data = {
        "email": "admin@example.com",
        "phone": "555-123-4567",
        "role": "admin"
    }
    masked_data = data_protection.mask_dict(sensitive_data)
    print(f"   ✓ Original: {sensitive_data}")
    print(f"   ✓ Masked: {masked_data}")

    # 6. Monitor security
    print("\n6. Security Monitoring")
    stats = security_monitor.get_security_stats(days=1)
    print(f"   ✓ Security events today: {stats['total_events']}")
    print(f"   ✓ Failed logins: {stats['failed_logins']}")

    print("\n✓ Complete workflow executed successfully!")


if __name__ == "__main__":
    print("=" * 60)
    print("Security & Access Control System - Example Usage")
    print("=" * 60)

    # Run examples
    example_authentication()
    example_mfa()
    example_authorization()
    example_data_protection()
    example_security_monitoring()
    example_complete_workflow()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
