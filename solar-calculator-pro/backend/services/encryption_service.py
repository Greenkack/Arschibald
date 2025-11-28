"""
Encryption Service

High-level service for managing encryption operations across the application.
Provides a unified interface for database, file, and communication encryption.

Requirements: 11.3
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from ..core.encryption import (
    EncryptionManager,
    DatabaseEncryption,
    FileEncryption,
    CommunicationEncryption,
    KeyManager,
    EncryptionAudit,
    get_encryption_manager
)


class EncryptionService:
    """
    High-level encryption service that coordinates all encryption operations.
    """
    
    def __init__(self):
        """Initialize encryption service with all encryption components."""
        self.encryption_manager = get_encryption_manager()
        self.database_encryption = DatabaseEncryption(self.encryption_manager)
        self.file_encryption = FileEncryption(self.encryption_manager)
        self.communication_encryption = CommunicationEncryption(self.encryption_manager)
        self.key_manager = KeyManager()
        self.audit = EncryptionAudit()
        
    # Database Encryption Methods
    
    def encrypt_database_field(
        self,
        value: Any,
        field_name: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Encrypt a database field value.
        
        Args:
            value: Value to encrypt
            field_name: Name of the field
            user_id: Optional user ID for audit logging
            
        Returns:
            Encrypted value
        """
        try:
            encrypted_value = self.database_encryption.encrypt_field(value, field_name)
            self.audit.log_operation(
                operation='encrypt_field',
                data_type='database',
                user_id=user_id,
                success=True,
                metadata={'field_name': field_name}
            )
            return encrypted_value
        except Exception as e:
            self.audit.log_operation(
                operation='encrypt_field',
                data_type='database',
                user_id=user_id,
                success=False,
                error=str(e),
                metadata={'field_name': field_name}
            )
            raise
    
    def decrypt_database_field(
        self,
        encrypted_value: str,
        field_name: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Decrypt a database field value.
        
        Args:
            encrypted_value: Encrypted value
            field_name: Name of the field
            user_id: Optional user ID for audit logging
            
        Returns:
            Decrypted value
        """
        try:
            decrypted_value = self.database_encryption.decrypt_field(encrypted_value, field_name)
            self.audit.log_operation(
                operation='decrypt_field',
                data_type='database',
                user_id=user_id,
                success=True,
                metadata={'field_name': field_name}
            )
            return decrypted_value
        except Exception as e:
            self.audit.log_operation(
                operation='decrypt_field',
                data_type='database',
                user_id=user_id,
                success=False,
                error=str(e),
                metadata={'field_name': field_name}
            )
            raise
    
    def encrypt_database_row(
        self,
        row_data: Dict[str, Any],
        encrypted_fields: List[str],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Encrypt specified fields in a database row.
        
        Args:
            row_data: Dictionary of row data
            encrypted_fields: List of field names to encrypt
            user_id: Optional user ID for audit logging
            
        Returns:
            Dictionary with encrypted fields
        """
        try:
            encrypted_row = self.database_encryption.encrypt_row(row_data, encrypted_fields)
            self.audit.log_operation(
                operation='encrypt_row',
                data_type='database',
                user_id=user_id,
                success=True,
                metadata={'fields': encrypted_fields}
            )
            return encrypted_row
        except Exception as e:
            self.audit.log_operation(
                operation='encrypt_row',
                data_type='database',
                user_id=user_id,
                success=False,
                error=str(e),
                metadata={'fields': encrypted_fields}
            )
            raise
    
    def decrypt_database_row(
        self,
        row_data: Dict[str, Any],
        encrypted_fields: List[str],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Decrypt specified fields in a database row.
        
        Args:
            row_data: Dictionary of row data with encrypted fields
            encrypted_fields: List of field names to decrypt
            user_id: Optional user ID for audit logging
            
        Returns:
            Dictionary with decrypted fields
        """
        try:
            decrypted_row = self.database_encryption.decrypt_row(row_data, encrypted_fields)
            self.audit.log_operation(
                operation='decrypt_row',
                data_type='database',
                user_id=user_id,
                success=True,
                metadata={'fields': encrypted_fields}
            )
            return decrypted_row
        except Exception as e:
            self.audit.log_operation(
                operation='decrypt_row',
                data_type='database',
                user_id=user_id,
                success=False,
                error=str(e),
                metadata={'fields': encrypted_fields}
            )
            raise
    
    # File Encryption Methods
    
    def encrypt_file(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Encrypt a file.
        
        Args:
            input_path: Path to file to encrypt
            output_path: Optional output path
            user_id: Optional user ID for audit logging
            
        Returns:
            Path to encrypted file
        """
        try:
            encrypted_path = self.file_encryption.encrypt_file(input_path, output_path)
            self.audit.log_operation(
                operation='encrypt_file',
                data_type='file',
                user_id=user_id,
                success=True,
                metadata={'input_path': input_path, 'output_path': encrypted_path}
            )
            return encrypted_path
        except Exception as e:
            self.audit.log_operation(
                operation='encrypt_file',
                data_type='file',
                user_id=user_id,
                success=False,
                error=str(e),
                metadata={'input_path': input_path}
            )
            raise
    
    def decrypt_file(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Decrypt a file.
        
        Args:
            input_path: Path to encrypted file
            output_path: Optional output path
            user_id: Optional user ID for audit logging
            
        Returns:
            Path to decrypted file
        """
        try:
            decrypted_path = self.file_encryption.decrypt_file(input_path, output_path)
            self.audit.log_operation(
                operation='decrypt_file',
                data_type='file',
                user_id=user_id,
                success=True,
                metadata={'input_path': input_path, 'output_path': decrypted_path}
            )
            return decrypted_path
        except Exception as e:
            self.audit.log_operation(
                operation='decrypt_file',
                data_type='file',
                user_id=user_id,
                success=False,
                error=str(e),
                metadata={'input_path': input_path}
            )
            raise
    
    def encrypt_file_data(
        self,
        file_data: bytes,
        user_id: Optional[str] = None
    ) -> bytes:
        """
        Encrypt file data in memory.
        
        Args:
            file_data: File data as bytes
            user_id: Optional user ID for audit logging
            
        Returns:
            Encrypted file data
        """
        try:
            encrypted_data = self.file_encryption.encrypt_file_in_memory(file_data)
            self.audit.log_operation(
                operation='encrypt_file_memory',
                data_type='file',
                user_id=user_id,
                success=True,
                metadata={'size': len(file_data)}
            )
            return encrypted_data
        except Exception as e:
            self.audit.log_operation(
                operation='encrypt_file_memory',
                data_type='file',
                user_id=user_id,
                success=False,
                error=str(e)
            )
            raise
    
    def decrypt_file_data(
        self,
        encrypted_data: bytes,
        user_id: Optional[str] = None
    ) -> bytes:
        """
        Decrypt file data in memory.
        
        Args:
            encrypted_data: Encrypted file data
            user_id: Optional user ID for audit logging
            
        Returns:
            Decrypted file data
        """
        try:
            decrypted_data = self.file_encryption.decrypt_file_in_memory(encrypted_data)
            self.audit.log_operation(
                operation='decrypt_file_memory',
                data_type='file',
                user_id=user_id,
                success=True,
                metadata={'size': len(encrypted_data)}
            )
            return decrypted_data
        except Exception as e:
            self.audit.log_operation(
                operation='decrypt_file_memory',
                data_type='file',
                user_id=user_id,
                success=False,
                error=str(e)
            )
            raise
    
    # Communication Encryption Methods
    
    def encrypt_api_payload(
        self,
        payload: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Encrypt an API payload.
        
        Args:
            payload: Dictionary payload to encrypt
            user_id: Optional user ID for audit logging
            
        Returns:
            Dictionary with encrypted payload
        """
        try:
            encrypted_payload = self.communication_encryption.encrypt_payload(payload)
            self.audit.log_operation(
                operation='encrypt_payload',
                data_type='communication',
                user_id=user_id,
                success=True
            )
            return encrypted_payload
        except Exception as e:
            self.audit.log_operation(
                operation='encrypt_payload',
                data_type='communication',
                user_id=user_id,
                success=False,
                error=str(e)
            )
            raise
    
    def decrypt_api_payload(
        self,
        encrypted_payload: Dict[str, str],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Decrypt an API payload.
        
        Args:
            encrypted_payload: Dictionary with encrypted payload
            user_id: Optional user ID for audit logging
            
        Returns:
            Decrypted payload dictionary
        """
        try:
            decrypted_payload = self.communication_encryption.decrypt_payload(encrypted_payload)
            self.audit.log_operation(
                operation='decrypt_payload',
                data_type='communication',
                user_id=user_id,
                success=True
            )
            return decrypted_payload
        except Exception as e:
            self.audit.log_operation(
                operation='decrypt_payload',
                data_type='communication',
                user_id=user_id,
                success=False,
                error=str(e)
            )
            raise
    
    def encrypt_websocket_message(
        self,
        message: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Encrypt a WebSocket message.
        
        Args:
            message: Message to encrypt
            user_id: Optional user ID for audit logging
            
        Returns:
            Encrypted message
        """
        try:
            encrypted_message = self.communication_encryption.encrypt_websocket_message(message)
            self.audit.log_operation(
                operation='encrypt_websocket',
                data_type='communication',
                user_id=user_id,
                success=True
            )
            return encrypted_message
        except Exception as e:
            self.audit.log_operation(
                operation='encrypt_websocket',
                data_type='communication',
                user_id=user_id,
                success=False,
                error=str(e)
            )
            raise
    
    def decrypt_websocket_message(
        self,
        encrypted_message: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Decrypt a WebSocket message.
        
        Args:
            encrypted_message: Encrypted message
            user_id: Optional user ID for audit logging
            
        Returns:
            Decrypted message
        """
        try:
            decrypted_message = self.communication_encryption.decrypt_websocket_message(encrypted_message)
            self.audit.log_operation(
                operation='decrypt_websocket',
                data_type='communication',
                user_id=user_id,
                success=True
            )
            return decrypted_message
        except Exception as e:
            self.audit.log_operation(
                operation='decrypt_websocket',
                data_type='communication',
                user_id=user_id,
                success=False,
                error=str(e)
            )
            raise
    
    # Key Management Methods
    
    def generate_key(
        self,
        key_name: str,
        user_id: Optional[str] = None
    ) -> bytes:
        """
        Generate a new encryption key.
        
        Args:
            key_name: Name for the key
            user_id: Optional user ID for audit logging
            
        Returns:
            Generated key
        """
        try:
            key = self.key_manager.generate_key(key_name)
            self.key_manager.store_key(key_name, key)
            self.audit.log_operation(
                operation='generate_key',
                data_type='key_management',
                user_id=user_id,
                success=True,
                metadata={'key_name': key_name}
            )
            return key
        except Exception as e:
            self.audit.log_operation(
                operation='generate_key',
                data_type='key_management',
                user_id=user_id,
                success=False,
                error=str(e),
                metadata={'key_name': key_name}
            )
            raise
    
    def rotate_key(
        self,
        key_name: str,
        user_id: Optional[str] = None
    ) -> bytes:
        """
        Rotate an encryption key.
        
        Args:
            key_name: Name of the key to rotate
            user_id: Optional user ID for audit logging
            
        Returns:
            New key
        """
        try:
            new_key = self.key_manager.rotate_key(key_name)
            self.audit.log_operation(
                operation='rotate_key',
                data_type='key_management',
                user_id=user_id,
                success=True,
                metadata={'key_name': key_name}
            )
            return new_key
        except Exception as e:
            self.audit.log_operation(
                operation='rotate_key',
                data_type='key_management',
                user_id=user_id,
                success=False,
                error=str(e),
                metadata={'key_name': key_name}
            )
            raise
    
    def list_keys(self) -> List[str]:
        """
        List all stored keys.
        
        Returns:
            List of key names
        """
        return self.key_manager.list_keys()
    
    def delete_key(
        self,
        key_name: str,
        user_id: Optional[str] = None
    ):
        """
        Delete an encryption key.
        
        Args:
            key_name: Name of the key to delete
            user_id: Optional user ID for audit logging
        """
        try:
            self.key_manager.delete_key(key_name)
            self.audit.log_operation(
                operation='delete_key',
                data_type='key_management',
                user_id=user_id,
                success=True,
                metadata={'key_name': key_name}
            )
        except Exception as e:
            self.audit.log_operation(
                operation='delete_key',
                data_type='key_management',
                user_id=user_id,
                success=False,
                error=str(e),
                metadata={'key_name': key_name}
            )
            raise
    
    # Audit Methods
    
    def get_audit_log(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        operation: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve audit log entries.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            operation: Optional operation type filter
            user_id: Optional user ID filter
            
        Returns:
            List of audit log entries
        """
        return self.audit.get_audit_log(start_date, end_date, operation, user_id)
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """
        Get encryption operation statistics.
        
        Returns:
            Dictionary with statistics
        """
        return self.audit.get_statistics()
    
    # Configuration Methods
    
    def get_encryption_status(self) -> Dict[str, Any]:
        """
        Get current encryption system status.
        
        Returns:
            Dictionary with encryption status information
        """
        return {
            'encryption_enabled': True,
            'master_key_exists': self.encryption_manager.master_key is not None,
            'stored_keys': self.list_keys(),
            'audit_statistics': self.get_audit_statistics()
        }
    
    def validate_encryption(self) -> Dict[str, bool]:
        """
        Validate encryption system functionality.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'database_encryption': False,
            'file_encryption': False,
            'communication_encryption': False,
            'key_management': False
        }
        
        try:
            # Test database encryption
            test_value = "test_data"
            encrypted = self.database_encryption.encrypt_field(test_value, "test_field")
            decrypted = self.database_encryption.decrypt_field(encrypted, "test_field")
            results['database_encryption'] = (decrypted == test_value)
        except:
            pass
        
        try:
            # Test file encryption
            test_data = b"test file data"
            encrypted = self.file_encryption.encrypt_file_in_memory(test_data)
            decrypted = self.file_encryption.decrypt_file_in_memory(encrypted)
            results['file_encryption'] = (decrypted == test_data)
        except:
            pass
        
        try:
            # Test communication encryption
            test_payload = {"test": "data"}
            encrypted = self.communication_encryption.encrypt_payload(test_payload)
            decrypted = self.communication_encryption.decrypt_payload(encrypted)
            results['communication_encryption'] = (decrypted == test_payload)
        except:
            pass
        
        try:
            # Test key management
            test_key_name = "test_key_validation"
            key = self.key_manager.generate_key(test_key_name)
            self.key_manager.store_key(test_key_name, key)
            loaded_key = self.key_manager.load_key(test_key_name)
            self.key_manager.delete_key(test_key_name)
            results['key_management'] = (key == loaded_key)
        except:
            pass
        
        return results


# Global encryption service instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get or create the global encryption service instance."""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
