"""Verification script for Data Protection System - Task 9.3"""

import sys
from datetime import datetime, timedelta

try:
    from .database import get_db_manager
    from .security import (
        DataAccessLog,
        DataProtectionManager,
        DataRetentionPolicy,
        PIIField,
        get_data_protection_manager,
        get_data_retention_policy,
        init_all_security_tables,
        log_data_access,
    )
except ImportError:
    from security import (
        DataAccessLog,
        PIIField,
        get_data_protection_manager,
        get_data_retention_policy,
        init_all_security_tables,
        log_data_access,
    )

    from database import get_db_manager


def verify_pii_masking() -> bool:
    """Verify PII masking functionality"""
    print("\n1. Testing PII Masking...")

    try:
        manager = get_data_protection_manager()

        # Test email masking
        email = "john.doe@example.com"
        masked_email = manager.mask_email(email)
        assert masked_email != email, "Email not masked"
        assert "@example.com" in masked_email, "Email domain not preserved"
        print("  ✓ Email masking works")

        # Test phone masking
        phone = "555-123-4567"
        masked_phone = manager.mask_phone(phone)
        assert masked_phone != phone, "Phone not masked"
        assert masked_phone.endswith(
            "4567"), "Phone last 4 digits not preserved"
        print("  ✓ Phone masking works")

        # Test credit card masking
        card = "4532-1234-5678-9010"
        masked_card = manager.mask_credit_card(card)
        assert masked_card != card, "Card not masked"
        assert masked_card.endswith("9010"), "Card last 4 digits not preserved"
        print("  ✓ Credit card masking works")

        # Test text masking
        text = "Contact me at john@example.com or 555-123-4567"
        masked_text = manager.mask_pii(text)
        assert "john@example.com" not in masked_text, "Email not masked in text"
        assert "555-123-4567" not in masked_text, "Phone not masked in text"
        print("  ✓ Text PII masking works")

        return True

    except Exception as e:
        print(f"  ✗ PII masking failed: {e}")
        return False


def verify_pii_identification() -> bool:
    """Verify PII field identification"""
    print("\n2. Testing PII Identification...")

    try:
        manager = get_data_protection_manager()

        # Test identification by field name
        data = {
            "user_email": "john@example.com",
            "phone_number": "555-123-4567",
            "user_name": "John Doe",
            "status": "active"
        }

        pii_fields = manager.identify_pii_fields(data)

        assert "user_email" in pii_fields, "Email field not identified"
        assert pii_fields["user_email"] == PIIField.EMAIL, "Email field type incorrect"
        print("  ✓ Email field identified")

        assert "phone_number" in pii_fields, "Phone field not identified"
        assert pii_fields["phone_number"] == PIIField.PHONE, "Phone field type incorrect"
        print("  ✓ Phone field identified")

        assert "status" not in pii_fields, "Non-PII field incorrectly identified"
        print("  ✓ Non-PII fields not identified")

        # Test identification by pattern
        data2 = {
            "contact": "john@example.com",
            "info": "555-123-4567"
        }

        pii_fields2 = manager.identify_pii_fields(data2)
        assert len(pii_fields2) > 0, "Pattern-based identification failed"
        print("  ✓ Pattern-based identification works")

        return True

    except Exception as e:
        print(f"  ✗ PII identification failed: {e}")
        return False


def verify_dict_masking() -> bool:
    """Verify dictionary masking"""
    print("\n3. Testing Dictionary Masking...")

    try:
        manager = get_data_protection_manager()

        data = {
            "user_id": "12345",
            "email": "john@example.com",
            "phone": "555-123-4567",
            "name": "John Doe",
            "status": "active"
        }

        # Auto-detect and mask
        masked = manager.mask_dict(data)

        assert masked["email"] != data["email"], "Email not masked in dict"
        assert masked["phone"] != data["phone"], "Phone not masked in dict"
        assert masked["user_id"] == data["user_id"], "Non-PII field changed"
        assert masked["status"] == data["status"], "Non-PII field changed"
        print("  ✓ Dictionary masking works")

        # Mask with specific fields
        pii_fields = {
            "email": PIIField.EMAIL,
            "phone": PIIField.PHONE,
            "name": PIIField.NAME
        }

        masked2 = manager.mask_dict(data, pii_fields)
        assert masked2["email"] != data["email"], "Email not masked"
        assert masked2["phone"] != data["phone"], "Phone not masked"
        print("  ✓ Dictionary masking with specific fields works")

        return True

    except Exception as e:
        print(f"  ✗ Dictionary masking failed: {e}")
        return False


def verify_encryption() -> bool:
    """Verify data encryption"""
    print("\n4. Testing Data Encryption...")

    try:
        manager = get_data_protection_manager()

        # Test encryption/decryption
        original = "sensitive data"
        encrypted = manager.encrypt_data(original)

        assert encrypted != original, "Data not encrypted"
        assert ":" in encrypted, "Encrypted format incorrect"
        print("  ✓ Data encryption works")

        decrypted = manager.decrypt_data(encrypted)
        assert decrypted == original, "Decryption failed"
        print("  ✓ Data decryption works")

        # Test empty string
        encrypted_empty = manager.encrypt_data("")
        assert encrypted_empty == "", "Empty string handling incorrect"
        print("  ✓ Empty string handling works")

        # Test invalid decryption
        invalid = "invalid:data"
        result = manager.decrypt_data(invalid)
        assert result == invalid, "Invalid data handling incorrect"
        print("  ✓ Invalid data handling works")

        return True

    except Exception as e:
        print(f"  ✗ Encryption failed: {e}")
        return False


def verify_access_logging() -> bool:
    """Verify data access logging"""
    print("\n5. Testing Data Access Logging...")

    try:
        # Initialize database
        init_all_security_tables()
        db_manager = get_db_manager()

        # Log access
        log_data_access(
            user_id="test_user",
            resource_type="users",
            resource_id="user123",
            action="READ",
            pii_fields=["email", "phone"],
            ip_address="192.168.1.100",
            session_id="session123"
        )
        print("  ✓ Access logging works")

        # Verify log was created
        with db_manager.session_scope() as session:
            log = session.query(DataAccessLog).filter(
                DataAccessLog.user_id == "test_user"
            ).first()

            assert log is not None, "Access log not created"
            assert log.resource_type == "users", "Resource type incorrect"
            assert log.resource_id == "user123", "Resource ID incorrect"
            assert log.action == "READ", "Action incorrect"
            print("  ✓ Access log created correctly")

            # Check PII fields
            import json
            pii_fields = json.loads(log.pii_fields_accessed)
            assert "email" in pii_fields, "PII fields not logged"
            assert "phone" in pii_fields, "PII fields not logged"
            print("  ✓ PII fields logged correctly")

        return True

    except Exception as e:
        print(f"  ✗ Access logging failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_retention_policy() -> bool:
    """Verify data retention policies"""
    print("\n6. Testing Data Retention Policies...")

    try:
        policy = get_data_retention_policy()

        # Set policies
        policy.set_policy("users", 365)
        policy.set_policy("sessions", 30)
        policy.set_policy("audit_logs", 90)
        print("  ✓ Setting retention policies works")

        # Get policies
        assert policy.get_policy("users") == 365, "User policy incorrect"
        assert policy.get_policy("sessions") == 30, "Session policy incorrect"
        assert policy.get_policy(
            "audit_logs") == 90, "Audit log policy incorrect"
        print("  ✓ Getting retention policies works")

        # Test cleanup
        init_all_security_tables()
        db_manager = get_db_manager()

        # Create old log
        old_date = datetime.utcnow() - timedelta(days=200)
        with db_manager.session_scope() as session:
            old_log = DataAccessLog(
                user_id="old_user",
                resource_type="users",
                resource_id="user999",
                action="READ",
                timestamp=old_date
            )
            session.add(old_log)

        # Set policy and cleanup
        policy.set_policy("data_access_logs", 180)
        count = policy.cleanup_expired_data("data_access_logs", DataAccessLog)

        assert count >= 1, "Cleanup did not remove expired data"
        print("  ✓ Data cleanup works")

        return True

    except Exception as e:
        print(f"  ✗ Retention policy failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_integration() -> bool:
    """Verify complete integration"""
    print("\n7. Testing Complete Integration...")

    try:
        # Initialize
        init_all_security_tables()
        manager = get_data_protection_manager()
        policy = get_data_retention_policy()

        # User data with PII
        user_data = {
            "user_id": "12345",
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "ssn": "123-45-6789",
            "status": "active"
        }

        # 1. Identify PII
        pii_fields = manager.identify_pii_fields(user_data)
        assert len(pii_fields) > 0, "PII identification failed"
        print("  ✓ PII identification in workflow")

        # 2. Encrypt sensitive data
        encrypted_ssn = manager.encrypt_data(user_data["ssn"])
        assert encrypted_ssn != user_data["ssn"], "Encryption failed"
        print("  ✓ Encryption in workflow")

        # 3. Log access
        log_data_access(
            user_id="admin",
            resource_type="users",
            resource_id=user_data["user_id"],
            action="WRITE",
            pii_fields=list(pii_fields.keys())
        )
        print("  ✓ Access logging in workflow")

        # 4. Mask for display
        masked_data = manager.mask_dict(user_data, pii_fields)
        assert masked_data["email"] != user_data["email"], "Masking failed"
        print("  ✓ Masking in workflow")

        # 5. Set retention policy
        policy.set_policy("data_access_logs", 180)
        print("  ✓ Retention policy in workflow")

        print("  ✓ Complete integration works")
        return True

    except Exception as e:
        print(f"  ✗ Integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verifications"""
    print("=" * 60)
    print("Data Protection System Verification - Task 9.3")
    print("=" * 60)

    results = {
        "PII Masking": verify_pii_masking(),
        "PII Identification": verify_pii_identification(),
        "Dictionary Masking": verify_dict_masking(),
        "Data Encryption": verify_encryption(),
        "Access Logging": verify_access_logging(),
        "Retention Policy": verify_retention_policy(),
        "Integration": verify_integration()
    }

    print("\n" + "=" * 60)
    print("Verification Results")
    print("=" * 60)

    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test:.<40} {status}")

    print("=" * 60)

    all_passed = all(results.values())

    if all_passed:
        print("\n✓ All verifications passed!")
        print("\nTask 9.3 Requirements Met:")
        print("  ✓ PII field identification and masking")
        print("  ✓ Data encryption for sensitive information")
        print("  ✓ Data retention policies with automatic cleanup")
        print("  ✓ Data access logging for compliance")
        return 0
    print("\n✗ Some verifications failed")
    failed = [test for test, passed in results.items() if not passed]
    print(f"\nFailed tests: {', '.join(failed)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
