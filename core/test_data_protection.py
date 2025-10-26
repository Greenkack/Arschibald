"""Tests for Data Protection System - Task 9.3"""

import json
from datetime import datetime, timedelta

import pytest

from .database import Base, get_db_manager
from .security import (
    DataAccessLog,
    DataProtectionManager,
    DataRetentionPolicy,
    PIIField,
    get_data_protection_manager,
    get_data_retention_policy,
    log_data_access,
)


@pytest.fixture
def db_manager():
    """Create test database manager"""
    manager = get_db_manager()
    Base.metadata.create_all(bind=manager.engine)
    yield manager
    Base.metadata.drop_all(bind=manager.engine)


@pytest.fixture
def data_protection_manager():
    """Create data protection manager"""
    return DataProtectionManager()


@pytest.fixture
def retention_policy(db_manager):
    """Create data retention policy"""
    return DataRetentionPolicy(db_manager)


class TestPIIMasking:
    """Test PII masking functionality"""

    def test_mask_email(self, data_protection_manager):
        """Test email masking"""
        email = "john.doe@example.com"
        masked = data_protection_manager.mask_email(email)

        assert masked != email
        assert "@example.com" in masked
        assert masked.startswith("j")
        assert masked[1] == "*"

    def test_mask_short_email(self, data_protection_manager):
        """Test masking short email"""
        email = "ab@example.com"
        masked = data_protection_manager.mask_email(email)

        assert masked != email
        assert "@example.com" in masked

    def test_mask_phone(self, data_protection_manager):
        """Test phone number masking"""
        phone = "555-123-4567"
        masked = data_protection_manager.mask_phone(phone)

        assert masked != phone
        assert masked.endswith("4567")
        assert "*" in masked

    def test_mask_credit_card(self, data_protection_manager):
        """Test credit card masking"""
        card = "4532-1234-5678-9010"
        masked = data_protection_manager.mask_credit_card(card)

        assert masked != card
        assert masked.endswith("9010")
        assert "*" in masked

    def test_mask_pii_text(self, data_protection_manager):
        """Test masking PII in text"""
        text = "Contact me at john@example.com or 555-123-4567"
        masked = data_protection_manager.mask_pii(text)

        assert masked != text
        assert "john@example.com" not in masked
        assert "555-123-4567" not in masked
        assert "*" in masked

    def test_mask_specific_field_type(self, data_protection_manager):
        """Test masking specific field type"""
        text = "Email: john@example.com, Phone: 555-123-4567"
        masked = data_protection_manager.mask_pii(text, PIIField.EMAIL)

        # Email should be masked
        assert "john@example.com" not in masked
        # Phone should NOT be masked (not specified)
        assert "555-123-4567" in masked


class TestPIIIdentification:
    """Test PII field identification"""

    def test_identify_email_field(self, data_protection_manager):
        """Test identifying email field"""
        data = {
            "user_email": "john@example.com",
            "name": "John Doe"
        }

        pii_fields = data_protection_manager.identify_pii_fields(data)

        assert "user_email" in pii_fields
        assert pii_fields["user_email"] == PIIField.EMAIL

    def test_identify_phone_field(self, data_protection_manager):
        """Test identifying phone field"""
        data = {
            "phone_number": "555-123-4567",
            "mobile": "555-987-6543"
        }

        pii_fields = data_protection_manager.identify_pii_fields(data)

        assert "phone_number" in pii_fields
        assert "mobile" in pii_fields
        assert pii_fields["phone_number"] == PIIField.PHONE

    def test_identify_by_pattern(self, data_protection_manager):
        """Test identifying PII by pattern matching"""
        data = {
            "contact": "john@example.com",
            "info": "Call 555-123-4567"
        }

        pii_fields = data_protection_manager.identify_pii_fields(data)

        assert "contact" in pii_fields
        assert "info" in pii_fields

    def test_identify_multiple_types(self, data_protection_manager):
        """Test identifying multiple PII types"""
        data = {
            "email": "john@example.com",
            "phone": "555-123-4567",
            "ssn": "123-45-6789",
            "credit_card": "4532-1234-5678-9010",
            "regular_field": "not pii"
        }

        pii_fields = data_protection_manager.identify_pii_fields(data)

        assert len(pii_fields) == 4
        assert "regular_field" not in pii_fields


class TestDictMasking:
    """Test dictionary masking"""

    def test_mask_dict_auto_detect(self, data_protection_manager):
        """Test masking dictionary with auto-detection"""
        data = {
            "email": "john@example.com",
            "phone": "555-123-4567",
            "name": "John Doe",
            "age": 30
        }

        masked = data_protection_manager.mask_dict(data)

        assert masked["email"] != data["email"]
        assert masked["phone"] != data["phone"]
        # Name not auto-masked by pattern
        assert masked["name"] == data["name"]
        assert masked["age"] == data["age"]

    def test_mask_dict_with_pii_fields(self, data_protection_manager):
        """Test masking dictionary with specified PII fields"""
        data = {
            "email": "john@example.com",
            "phone": "555-123-4567",
            "name": "John Doe"
        }

        pii_fields = {
            "email": PIIField.EMAIL,
            "phone": PIIField.PHONE,
            "name": PIIField.NAME
        }

        masked = data_protection_manager.mask_dict(data, pii_fields)

        assert masked["email"] != data["email"]
        assert masked["phone"] != data["phone"]
        # Name is masked because we specified it
        assert masked["name"] != data["name"]

    def test_mask_dict_preserves_non_pii(self, data_protection_manager):
        """Test that non-PII fields are preserved"""
        data = {
            "email": "john@example.com",
            "user_id": "12345",
            "status": "active",
            "count": 42
        }

        masked = data_protection_manager.mask_dict(data)

        assert masked["user_id"] == data["user_id"]
        assert masked["status"] == data["status"]
        assert masked["count"] == data["count"]


class TestDataEncryption:
    """Test data encryption"""

    def test_encrypt_decrypt(self, data_protection_manager):
        """Test encryption and decryption"""
        original = "sensitive data"
        encrypted = data_protection_manager.encrypt_data(original)

        assert encrypted != original
        assert ":" in encrypted  # signature:data format

        decrypted = data_protection_manager.decrypt_data(encrypted)
        assert decrypted == original

    def test_encrypt_empty_string(self, data_protection_manager):
        """Test encrypting empty string"""
        encrypted = data_protection_manager.encrypt_data("")
        assert encrypted == ""

    def test_decrypt_invalid_data(self, data_protection_manager):
        """Test decrypting invalid data"""
        invalid = "invalid:data"
        result = data_protection_manager.decrypt_data(invalid)

        # Should return original on failure
        assert result == invalid

    def test_decrypt_tampered_data(self, data_protection_manager):
        """Test decrypting tampered data"""
        original = "sensitive data"
        encrypted = data_protection_manager.encrypt_data(original)

        # Tamper with the data
        parts = encrypted.split(":")
        tampered = parts[0] + ":tampered"

        result = data_protection_manager.decrypt_data(tampered)

        # Should fail verification and return tampered data
        assert result == tampered


class TestDataAccessLogging:
    """Test data access logging"""

    def test_log_data_access(self, db_manager):
        """Test logging data access"""
        log_data_access(
            user_id="user123",
            resource_type="users",
            resource_id="user456",
            action="READ",
            pii_fields=["email", "phone"],
            ip_address="192.168.1.1",
            session_id="session123"
        )

        # Verify log was created
        with db_manager.session_scope() as session:
            log = session.query(DataAccessLog).filter(
                DataAccessLog.user_id == "user123"
            ).first()

            assert log is not None
            assert log.resource_type == "users"
            assert log.resource_id == "user456"
            assert log.action == "READ"
            assert log.ip_address == "192.168.1.1"
            assert log.session_id == "session123"

            # Check PII fields
            pii_fields = json.loads(log.pii_fields_accessed)
            assert "email" in pii_fields
            assert "phone" in pii_fields

    def test_log_data_access_without_pii(self, db_manager):
        """Test logging data access without PII fields"""
        log_data_access(
            user_id="user123",
            resource_type="products",
            resource_id="prod456",
            action="WRITE"
        )

        with db_manager.session_scope() as session:
            log = session.query(DataAccessLog).filter(
                DataAccessLog.resource_type == "products"
            ).first()

            assert log is not None
            assert log.pii_fields_accessed is None

    def test_query_access_logs_by_user(self, db_manager):
        """Test querying access logs by user"""
        # Create multiple logs
        for i in range(3):
            log_data_access(
                user_id="user123",
                resource_type="users",
                resource_id=f"user{i}",
                action="READ"
            )

        with db_manager.session_scope() as session:
            logs = session.query(DataAccessLog).filter(
                DataAccessLog.user_id == "user123"
            ).all()

            assert len(logs) == 3

    def test_query_access_logs_by_resource(self, db_manager):
        """Test querying access logs by resource"""
        log_data_access(
            user_id="user123",
            resource_type="users",
            resource_id="user456",
            action="READ"
        )

        log_data_access(
            user_id="user789",
            resource_type="users",
            resource_id="user456",
            action="WRITE"
        )

        with db_manager.session_scope() as session:
            logs = session.query(DataAccessLog).filter(
                DataAccessLog.resource_id == "user456"
            ).all()

            assert len(logs) == 2


class TestDataRetentionPolicy:
    """Test data retention policy"""

    def test_set_policy(self, retention_policy):
        """Test setting retention policy"""
        retention_policy.set_policy("users", 90)

        policy = retention_policy.get_policy("users")
        assert policy == 90

    def test_get_nonexistent_policy(self, retention_policy):
        """Test getting non-existent policy"""
        policy = retention_policy.get_policy("nonexistent")
        assert policy is None

    def test_cleanup_expired_data(self, retention_policy, db_manager):
        """Test cleaning up expired data"""
        # Set retention policy
        retention_policy.set_policy("data_access_logs", 7)

        # Create old logs
        old_date = datetime.utcnow() - timedelta(days=10)
        recent_date = datetime.utcnow() - timedelta(days=3)

        with db_manager.session_scope() as session:
            # Old log (should be deleted)
            old_log = DataAccessLog(
                user_id="user123",
                resource_type="users",
                resource_id="user456",
                action="READ",
                timestamp=old_date
            )
            session.add(old_log)

            # Recent log (should be kept)
            recent_log = DataAccessLog(
                user_id="user789",
                resource_type="users",
                resource_id="user012",
                action="READ",
                timestamp=recent_date
            )
            session.add(recent_log)

        # Clean up expired data
        count = retention_policy.cleanup_expired_data(
            "data_access_logs", DataAccessLog)

        assert count == 1

        # Verify only recent log remains
        with db_manager.session_scope() as session:
            remaining = session.query(DataAccessLog).all()
            assert len(remaining) == 1
            assert remaining[0].user_id == "user789"

    def test_cleanup_without_policy(self, retention_policy, db_manager):
        """Test cleanup without policy returns 0"""
        count = retention_policy.cleanup_expired_data(
            "unknown_type", DataAccessLog)
        assert count == 0


class TestIntegration:
    """Integration tests for data protection"""

    def test_full_pii_protection_workflow(
            self, data_protection_manager, db_manager):
        """Test complete PII protection workflow"""
        # Original data with PII
        user_data = {
            "user_id": "12345",
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "name": "John Doe",
            "address": "123 Main St",
            "status": "active"
        }

        # 1. Identify PII fields
        pii_fields = data_protection_manager.identify_pii_fields(user_data)
        assert len(pii_fields) > 0

        # 2. Mask PII for logging
        masked_data = data_protection_manager.mask_dict(user_data, pii_fields)
        assert masked_data["email"] != user_data["email"]
        assert masked_data["phone"] != user_data["phone"]

        # 3. Log data access with PII fields
        log_data_access(
            user_id="admin123",
            resource_type="users",
            resource_id=user_data["user_id"],
            action="READ",
            pii_fields=list(pii_fields.keys())
        )

        # 4. Verify log was created
        with db_manager.session_scope() as session:
            log = session.query(DataAccessLog).filter(
                DataAccessLog.resource_id == user_data["user_id"]
            ).first()

            assert log is not None
            pii_accessed = json.loads(log.pii_fields_accessed)
            assert "email" in pii_accessed

    def test_encryption_with_masking(self, data_protection_manager):
        """Test combining encryption with masking"""
        sensitive_data = "john.doe@example.com"

        # Encrypt
        encrypted = data_protection_manager.encrypt_data(sensitive_data)
        assert encrypted != sensitive_data

        # Decrypt
        decrypted = data_protection_manager.decrypt_data(encrypted)
        assert decrypted == sensitive_data

        # Mask
        masked = data_protection_manager.mask_email(decrypted)
        assert masked != decrypted
        assert "@" in masked


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_get_data_protection_manager(self):
        """Test getting data protection manager"""
        manager = get_data_protection_manager()
        assert isinstance(manager, DataProtectionManager)

    def test_get_data_retention_policy(self):
        """Test getting data retention policy"""
        policy = get_data_retention_policy()
        assert isinstance(policy, DataRetentionPolicy)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
