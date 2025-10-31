"""Example usage of Data Protection System - Task 9.3"""

from datetime import datetime, timedelta

from .database import get_db_manager
from .security import (
    PIIField,
    get_data_protection_manager,
    get_data_retention_policy,
    init_all_security_tables,
    log_data_access,
)


def example_pii_masking():
    """Example: Masking PII in data"""
    print("\n=== PII Masking Example ===\n")

    manager = get_data_protection_manager()

    # Mask email
    email = "john.doe@example.com"
    masked_email = manager.mask_email(email)
    print(f"Original email: {email}")
    print(f"Masked email: {masked_email}")

    # Mask phone
    phone = "555-123-4567"
    masked_phone = manager.mask_phone(phone)
    print(f"\nOriginal phone: {phone}")
    print(f"Masked phone: {masked_phone}")

    # Mask credit card
    card = "4532-1234-5678-9010"
    masked_card = manager.mask_credit_card(card)
    print(f"\nOriginal card: {card}")
    print(f"Masked card: {masked_card}")

    # Mask text with multiple PII
    text = "Contact John at john.doe@example.com or 555-123-4567"
    masked_text = manager.mask_pii(text)
    print(f"\nOriginal text: {text}")
    print(f"Masked text: {masked_text}")


def example_pii_identification():
    """Example: Identifying PII fields in data"""
    print("\n=== PII Identification Example ===\n")

    manager = get_data_protection_manager()

    # User data with PII
    user_data = {
        "user_id": "12345",
        "email": "john.doe@example.com",
        "phone": "555-123-4567",
        "name": "John Doe",
        "address": "123 Main St, City, State 12345",
        "ssn": "123-45-6789",
        "credit_card": "4532-1234-5678-9010",
        "status": "active",
        "created_at": "2024-01-01"
    }

    # Identify PII fields
    pii_fields = manager.identify_pii_fields(user_data)

    print("User data:")
    for key, value in user_data.items():
        print(f"  {key}: {value}")

    print("\nIdentified PII fields:")
    for field, field_type in pii_fields.items():
        print(f"  {field}: {field_type.value}")


def example_dict_masking():
    """Example: Masking PII in dictionaries"""
    print("\n=== Dictionary Masking Example ===\n")

    manager = get_data_protection_manager()

    # User data
    user_data = {
        "user_id": "12345",
        "email": "john.doe@example.com",
        "phone": "555-123-4567",
        "name": "John Doe",
        "status": "active"
    }

    print("Original data:")
    for key, value in user_data.items():
        print(f"  {key}: {value}")

    # Mask PII (auto-detect)
    masked_data = manager.mask_dict(user_data)

    print("\nMasked data (auto-detect):")
    for key, value in masked_data.items():
        print(f"  {key}: {value}")

    # Mask with specific PII fields
    pii_fields = {
        "email": PIIField.EMAIL,
        "phone": PIIField.PHONE,
        "name": PIIField.NAME
    }

    masked_data_specific = manager.mask_dict(user_data, pii_fields)

    print("\nMasked data (specific fields):")
    for key, value in masked_data_specific.items():
        print(f"  {key}: {value}")


def example_data_encryption():
    """Example: Encrypting and decrypting sensitive data"""
    print("\n=== Data Encryption Example ===\n")

    manager = get_data_protection_manager()

    # Sensitive data
    sensitive_data = "This is highly sensitive information"

    print(f"Original data: {sensitive_data}")

    # Encrypt
    encrypted = manager.encrypt_data(sensitive_data)
    print(f"Encrypted: {encrypted[:50]}...")

    # Decrypt
    decrypted = manager.decrypt_data(encrypted)
    print(f"Decrypted: {decrypted}")

    # Verify
    assert decrypted == sensitive_data
    print("\n✓ Encryption/decryption successful")


def example_data_access_logging():
    """Example: Logging data access for compliance"""
    print("\n=== Data Access Logging Example ===\n")

    # Initialize database
    init_all_security_tables()
    db_manager = get_db_manager()

    # Log data access
    print("Logging data access...")
    log_data_access(
        user_id="admin123",
        resource_type="users",
        resource_id="user456",
        action="READ",
        pii_fields=["email", "phone", "ssn"],
        ip_address="192.168.1.100",
        session_id="session789"
    )

    # Log another access
    log_data_access(
        user_id="admin123",
        resource_type="users",
        resource_id="user456",
        action="WRITE",
        pii_fields=["email"],
        ip_address="192.168.1.100",
        session_id="session789"
    )

    # Query logs
    from .security import DataAccessLog
    with db_manager.session_scope() as session:
        logs = session.query(DataAccessLog).filter(
            DataAccessLog.user_id == "admin123"
        ).all()

        print(f"\nFound {len(logs)} access logs:")
        for log in logs:
            print(f"  - {log.action} on {log.resource_type}:{log.resource_id}")
            print(f"    PII fields: {log.pii_fields_accessed}")
            print(f"    IP: {log.ip_address}")
            print(f"    Time: {log.timestamp}")


def example_data_retention():
    """Example: Data retention policies"""
    print("\n=== Data Retention Policy Example ===\n")

    # Initialize database
    init_all_security_tables()

    policy = get_data_retention_policy()

    # Set retention policies
    print("Setting retention policies...")
    policy.set_policy("users", 365)  # 1 year
    policy.set_policy("sessions", 30)  # 30 days
    policy.set_policy("audit_logs", 90)  # 90 days
    policy.set_policy("data_access_logs", 180)  # 180 days

    # Get policies
    print("\nRetention policies:")
    for resource_type in [
        "users",
        "sessions",
        "audit_logs",
            "data_access_logs"]:
        days = policy.get_policy(resource_type)
        print(f"  {resource_type}: {days} days")

    # Simulate cleanup
    print("\nSimulating cleanup of expired data...")
    from .security import DataAccessLog

    # Create old log
    db_manager = get_db_manager()
    old_date = datetime.utcnow() - timedelta(days=200)

    with db_manager.session_scope() as session:
        old_log = DataAccessLog(
            user_id="user123",
            resource_type="users",
            resource_id="user456",
            action="READ",
            timestamp=old_date
        )
        session.add(old_log)

    # Clean up
    count = policy.cleanup_expired_data("data_access_logs", DataAccessLog)
    print(f"Cleaned up {count} expired records")


def example_complete_workflow():
    """Example: Complete data protection workflow"""
    print("\n=== Complete Data Protection Workflow ===\n")

    # Initialize
    init_all_security_tables()
    manager = get_data_protection_manager()

    # 1. Receive user data
    user_data = {
        "user_id": "12345",
        "email": "john.doe@example.com",
        "phone": "555-123-4567",
        "name": "John Doe",
        "ssn": "123-45-6789",
        "address": "123 Main St",
        "status": "active"
    }

    print("Step 1: Received user data")
    print(f"  User ID: {user_data['user_id']}")

    # 2. Identify PII fields
    pii_fields = manager.identify_pii_fields(user_data)
    print(f"\nStep 2: Identified {len(pii_fields)} PII fields")
    for field in pii_fields.keys():
        print(f"  - {field}")

    # 3. Encrypt sensitive fields
    encrypted_ssn = manager.encrypt_data(user_data["ssn"])
    print("\nStep 3: Encrypted SSN")
    print(f"  Original: {user_data['ssn']}")
    print(f"  Encrypted: {encrypted_ssn[:30]}...")

    # 4. Log data access
    log_data_access(
        user_id="admin123",
        resource_type="users",
        resource_id=user_data["user_id"],
        action="READ",
        pii_fields=list(pii_fields.keys()),
        ip_address="192.168.1.100"
    )
    print("\nStep 4: Logged data access")

    # 5. Mask PII for display/logging
    masked_data = manager.mask_dict(user_data, pii_fields)
    print("\nStep 5: Masked data for display:")
    for key, value in masked_data.items():
        if key in pii_fields:
            print(f"  {key}: {value} (masked)")
        else:
            print(f"  {key}: {value}")

    # 6. Decrypt when needed
    decrypted_ssn = manager.decrypt_data(encrypted_ssn)
    print("\nStep 6: Decrypted SSN when needed")
    print(f"  Decrypted: {decrypted_ssn}")

    print("\n✓ Complete workflow executed successfully")


def example_logging_best_practices():
    """Example: Best practices for logging with PII protection"""
    print("\n=== Logging Best Practices Example ===\n")

    manager = get_data_protection_manager()

    # User data
    user_data = {
        "user_id": "12345",
        "email": "john.doe@example.com",
        "phone": "555-123-4567",
        "action": "login"
    }

    # BAD: Logging raw PII
    print("❌ BAD: Logging raw PII")
    print(f"  User {user_data['email']} logged in from {user_data['phone']}")

    # GOOD: Mask PII before logging
    print("\n✓ GOOD: Mask PII before logging")
    masked_email = manager.mask_email(user_data["email"])
    masked_phone = manager.mask_phone(user_data["phone"])
    print(f"  User {masked_email} logged in from {masked_phone}")

    # BETTER: Use structured logging with automatic masking
    print("\n✓ BETTER: Structured logging with masking")
    pii_fields = manager.identify_pii_fields(user_data)
    masked_data = manager.mask_dict(user_data, pii_fields)
    print(f"  Event: {masked_data}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("Data Protection System Examples - Task 9.3")
    print("=" * 60)

    try:
        example_pii_masking()
        example_pii_identification()
        example_dict_masking()
        example_data_encryption()
        example_data_access_logging()
        example_data_retention()
        example_complete_workflow()
        example_logging_best_practices()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
