"""
Encryption Service Tests

Comprehensive tests for the encryption system.

Requirements: 11.3
"""

import pytest
import os
import tempfile
from datetime import datetime, timedelta

from ..services.encryption_service import EncryptionService, get_encryption_service
from ..core.encryption import (
    EncryptionManager,
    DatabaseEncryption,
    FileEncryption,
    CommunicationEncryption,
    KeyManager,
    EncryptionAudit
)


@pytest.fixture
def encryption_service():
    """Create encryption service for testing."""
    return EncryptionService()


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestEncryptionManager:
    """Test EncryptionManager class."""
    
    def test_encrypt_decrypt_string(self):
        """Test string encryption and decryption."""
        manager = EncryptionManager()
        original = "test_data"
        
        encrypted = manager.encrypt_string(original)
        assert encrypted != original
        
        decrypted = manager.decrypt_string(encrypted)
        assert decrypted == original
    
    def test_encrypt_decrypt_bytes(self):
        """Test bytes encryption and decryption."""
        manager = EncryptionManager()
        original = b"test_data_bytes"
        
        encrypted = manager.encrypt(original)
        assert encrypted != original
        
        decrypted = manager.decrypt(encrypted)
        assert decrypted == original
    
    def test_encrypt_decrypt_dict(self):
        """Test dictionary encryption and decryption."""
        manager = EncryptionManager()
        original = {"key": "value", "number": 123}
        
        encrypted = manager.encrypt_dict(original)
        assert isinstance(encrypted, str)
        
        decrypted = manager.decrypt_dict(encrypted)
        assert decrypted == original
    
    def test_derive_key(self):
        """Test key derivation from password."""
        manager = EncryptionManager()
        password = "test_password"
        
        key1, salt1 = manager.derive_key(password)
        key2, salt2 = manager.derive_key(password, salt1)
        
        assert key1 == key2
        assert salt1 == salt2
    
    def test_key_rotation(self):
        """Test master key rotation."""
        manager = EncryptionManager()
        old_key = manager.get_master_key()
        
        new_key = manager.rotate_key()
        
        assert new_key != old_key
        assert manager.get_master_key() == new_key


class TestDatabaseEncryption:
    """Test DatabaseEncryption class."""
    
    def test_encrypt_decrypt_field(self):
        """Test field encryption and decryption."""
        manager = EncryptionManager()
        db_encryption = DatabaseEncryption(manager)
        
        original = "sensitive_data"
        encrypted = db_encryption.encrypt_field(original, "test_field")
        assert encrypted != original
        
        decrypted = db_encryption.decrypt_field(encrypted, "test_field")
        assert decrypted == original
    
    def test_encrypt_decrypt_row(self):
        """Test row encryption and decryption."""
        manager = EncryptionManager()
        db_encryption = DatabaseEncryption(manager)
        
        row_data = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890"
        }
        encrypted_fields = ["email", "phone"]
        
        encrypted_row = db_encryption.encrypt_row(row_data, encrypted_fields)
        assert encrypted_row["email"] != row_data["email"]
        assert encrypted_row["phone"] != row_data["phone"]
        assert encrypted_row["name"] == row_data["name"]  # Not encrypted
        
        decrypted_row = db_encryption.decrypt_row(encrypted_row, encrypted_fields)
        assert decrypted_row == row_data
    
    def test_encrypt_none_value(self):
        """Test encrypting None value."""
        manager = EncryptionManager()
        db_encryption = DatabaseEncryption(manager)
        
        encrypted = db_encryption.encrypt_field(None, "test_field")
        assert encrypted is None


class TestFileEncryption:
    """Test FileEncryption class."""
    
    def test_encrypt_decrypt_file_memory(self):
        """Test file encryption/decryption in memory."""
        manager = EncryptionManager()
        file_encryption = FileEncryption(manager)
        
        original_data = b"This is test file content"
        
        encrypted_data = file_encryption.encrypt_file_in_memory(original_data)
        assert encrypted_data != original_data
        
        decrypted_data = file_encryption.decrypt_file_in_memory(encrypted_data)
        assert decrypted_data == original_data
    
    def test_encrypt_decrypt_file_disk(self, temp_dir):
        """Test file encryption/decryption on disk."""
        manager = EncryptionManager()
        file_encryption = FileEncryption(manager)
        
        # Create test file
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'wb') as f:
            f.write(b"Test file content")
        
        # Encrypt file
        encrypted_file = file_encryption.encrypt_file(test_file)
        assert os.path.exists(encrypted_file)
        
        # Decrypt file
        decrypted_file = file_encryption.decrypt_file(encrypted_file)
        assert os.path.exists(decrypted_file)
        
        # Verify content
        with open(decrypted_file, 'rb') as f:
            content = f.read()
        assert content == b"Test file content"


class TestCommunicationEncryption:
    """Test CommunicationEncryption class."""
    
    def test_encrypt_decrypt_payload(self):
        """Test payload encryption and decryption."""
        manager = EncryptionManager()
        comm_encryption = CommunicationEncryption(manager)
        
        payload = {"user_id": 123, "action": "test"}
        
        encrypted_payload = comm_encryption.encrypt_payload(payload)
        assert encrypted_payload["encrypted"] is True
        assert "data" in encrypted_payload
        assert "timestamp" in encrypted_payload
        
        decrypted_payload = comm_encryption.decrypt_payload(encrypted_payload)
        assert decrypted_payload == payload
    
    def test_encrypt_decrypt_websocket_message(self):
        """Test WebSocket message encryption and decryption."""
        manager = EncryptionManager()
        comm_encryption = CommunicationEncryption(manager)
        
        message = "Test WebSocket message"
        
        encrypted_message = comm_encryption.encrypt_websocket_message(message)
        assert encrypted_message != message
        
        decrypted_message = comm_encryption.decrypt_websocket_message(encrypted_message)
        assert decrypted_message == message


class TestKeyManager:
    """Test KeyManager class."""
    
    def test_generate_key(self, temp_dir):
        """Test key generation."""
        key_manager = KeyManager(temp_dir)
        
        key = key_manager.generate_key("test_key")
        assert key is not None
        assert len(key) > 0
    
    def test_store_load_key(self, temp_dir):
        """Test key storage and loading."""
        key_manager = KeyManager(temp_dir)
        
        key = key_manager.generate_key("test_key")
        key_manager.store_key("test_key", key, encrypted=False)
        
        loaded_key = key_manager.load_key("test_key", encrypted=False)
        assert loaded_key == key
    
    def test_list_keys(self, temp_dir):
        """Test listing keys."""
        key_manager = KeyManager(temp_dir)
        
        key_manager.generate_key("key1")
        key_manager.store_key("key1", key_manager._keys["key1"], encrypted=False)
        
        key_manager.generate_key("key2")
        key_manager.store_key("key2", key_manager._keys["key2"], encrypted=False)
        
        keys = key_manager.list_keys()
        assert "key1" in keys
        assert "key2" in keys
    
    def test_delete_key(self, temp_dir):
        """Test key deletion."""
        key_manager = KeyManager(temp_dir)
        
        key = key_manager.generate_key("test_key")
        key_manager.store_key("test_key", key, encrypted=False)
        
        assert "test_key" in key_manager.list_keys()
        
        key_manager.delete_key("test_key")
        assert "test_key" not in key_manager.list_keys()
    
    def test_rotate_key(self, temp_dir):
        """Test key rotation."""
        key_manager = KeyManager(temp_dir)
        
        old_key = key_manager.generate_key("test_key")
        key_manager.store_key("test_key", old_key, encrypted=False)
        
        new_key = key_manager.rotate_key("test_key")
        
        assert new_key != old_key
        assert key_manager._keys["test_key"] == new_key


class TestEncryptionAudit:
    """Test EncryptionAudit class."""
    
    def test_log_operation(self, temp_dir):
        """Test logging an operation."""
        audit_log_path = os.path.join(temp_dir, "audit.log")
        audit = EncryptionAudit(audit_log_path)
        
        audit.log_operation(
            operation="encrypt_field",
            data_type="database",
            user_id="test_user",
            success=True,
            metadata={"field_name": "email"}
        )
        
        assert os.path.exists(audit_log_path)
    
    def test_get_audit_log(self, temp_dir):
        """Test retrieving audit logs."""
        audit_log_path = os.path.join(temp_dir, "audit.log")
        audit = EncryptionAudit(audit_log_path)
        
        # Log some operations
        audit.log_operation("encrypt_field", "database", "user1", True)
        audit.log_operation("decrypt_field", "database", "user2", True)
        audit.log_operation("encrypt_file", "file", "user1", False, error="Test error")
        
        # Get all logs
        logs = audit.get_audit_log()
        assert len(logs) == 3
        
        # Filter by operation
        encrypt_logs = audit.get_audit_log(operation="encrypt_field")
        assert len(encrypt_logs) == 1
        
        # Filter by user
        user1_logs = audit.get_audit_log(user_id="user1")
        assert len(user1_logs) == 2
    
    def test_get_statistics(self, temp_dir):
        """Test getting audit statistics."""
        audit_log_path = os.path.join(temp_dir, "audit.log")
        audit = EncryptionAudit(audit_log_path)
        
        # Log some operations
        audit.log_operation("encrypt_field", "database", "user1", True)
        audit.log_operation("decrypt_field", "database", "user1", True)
        audit.log_operation("encrypt_file", "file", "user1", False)
        
        stats = audit.get_statistics()
        
        assert stats["total_operations"] == 3
        assert stats["successful_operations"] == 2
        assert stats["failed_operations"] == 1
        assert "encrypt_field" in stats["operations_by_type"]
        assert "database" in stats["operations_by_data_type"]


class TestEncryptionService:
    """Test EncryptionService class."""
    
    def test_encrypt_decrypt_database_field(self, encryption_service):
        """Test database field encryption via service."""
        original = "test_data"
        
        encrypted = encryption_service.encrypt_database_field(
            value=original,
            field_name="test_field",
            user_id="test_user"
        )
        assert encrypted != original
        
        decrypted = encryption_service.decrypt_database_field(
            encrypted_value=encrypted,
            field_name="test_field",
            user_id="test_user"
        )
        assert decrypted == original
    
    def test_encrypt_decrypt_database_row(self, encryption_service):
        """Test database row encryption via service."""
        row_data = {
            "id": 1,
            "email": "test@example.com",
            "phone": "+1234567890"
        }
        encrypted_fields = ["email", "phone"]
        
        encrypted_row = encryption_service.encrypt_database_row(
            row_data=row_data,
            encrypted_fields=encrypted_fields,
            user_id="test_user"
        )
        
        decrypted_row = encryption_service.decrypt_database_row(
            row_data=encrypted_row,
            encrypted_fields=encrypted_fields,
            user_id="test_user"
        )
        
        assert decrypted_row == row_data
    
    def test_encrypt_decrypt_file_data(self, encryption_service):
        """Test file data encryption via service."""
        file_data = b"Test file content"
        
        encrypted_data = encryption_service.encrypt_file_data(
            file_data=file_data,
            user_id="test_user"
        )
        assert encrypted_data != file_data
        
        decrypted_data = encryption_service.decrypt_file_data(
            encrypted_data=encrypted_data,
            user_id="test_user"
        )
        assert decrypted_data == file_data
    
    def test_encrypt_decrypt_api_payload(self, encryption_service):
        """Test API payload encryption via service."""
        payload = {"key": "value", "number": 123}
        
        encrypted_payload = encryption_service.encrypt_api_payload(
            payload=payload,
            user_id="test_user"
        )
        
        decrypted_payload = encryption_service.decrypt_api_payload(
            encrypted_payload=encrypted_payload,
            user_id="test_user"
        )
        
        assert decrypted_payload == payload
    
    def test_get_encryption_status(self, encryption_service):
        """Test getting encryption status."""
        status = encryption_service.get_encryption_status()
        
        assert "encryption_enabled" in status
        assert "master_key_exists" in status
        assert "stored_keys" in status
        assert "audit_statistics" in status
    
    def test_validate_encryption(self, encryption_service):
        """Test encryption validation."""
        validation = encryption_service.validate_encryption()
        
        assert "database_encryption" in validation
        assert "file_encryption" in validation
        assert "communication_encryption" in validation
        assert "key_management" in validation
        
        # All should be True for a working system
        assert validation["database_encryption"] is True
        assert validation["file_encryption"] is True
        assert validation["communication_encryption"] is True
        assert validation["key_management"] is True


class TestIntegration:
    """Integration tests for the encryption system."""
    
    def test_end_to_end_database_encryption(self, encryption_service):
        """Test complete database encryption workflow."""
        # Simulate user data
        user_data = {
            "id": 1,
            "username": "johndoe",
            "email": "john@example.com",
            "phone": "+1-555-0123",
            "ssn": "123-45-6789"
        }
        
        # Encrypt sensitive fields
        encrypted_row = encryption_service.encrypt_database_row(
            row_data=user_data,
            encrypted_fields=["email", "phone", "ssn"],
            user_id="admin"
        )
        
        # Verify encryption
        assert encrypted_row["email"] != user_data["email"]
        assert encrypted_row["phone"] != user_data["phone"]
        assert encrypted_row["ssn"] != user_data["ssn"]
        assert encrypted_row["username"] == user_data["username"]
        
        # Decrypt for use
        decrypted_row = encryption_service.decrypt_database_row(
            row_data=encrypted_row,
            encrypted_fields=["email", "phone", "ssn"],
            user_id="admin"
        )
        
        # Verify decryption
        assert decrypted_row == user_data
    
    def test_end_to_end_file_encryption(self, encryption_service, temp_dir):
        """Test complete file encryption workflow."""
        # Create test file
        test_file = os.path.join(temp_dir, "sensitive_document.pdf")
        with open(test_file, 'wb') as f:
            f.write(b"Sensitive document content")
        
        # Encrypt file
        encrypted_file = encryption_service.encrypt_file(
            input_path=test_file,
            user_id="admin"
        )
        
        # Verify encrypted file exists
        assert os.path.exists(encrypted_file)
        
        # Decrypt file
        decrypted_file = encryption_service.decrypt_file(
            input_path=encrypted_file,
            user_id="admin"
        )
        
        # Verify decrypted content
        with open(decrypted_file, 'rb') as f:
            content = f.read()
        assert content == b"Sensitive document content"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
