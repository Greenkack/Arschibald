"""
Core Encryption Module

Provides comprehensive encryption functionality for:
- Database encryption (at-rest)
- File encryption
- Communication encryption
- Key management
- Encryption audit logging

Requirements: 11.3
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64
import json
from typing import Optional, Dict, Any, Union
from datetime import datetime
import secrets


class EncryptionManager:
    """
    Central encryption manager for all encryption operations.
    Handles key generation, storage, and encryption/decryption.
    """
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize encryption manager.
        
        Args:
            master_key: Optional master key. If not provided, will be generated.
        """
        self.master_key = master_key or self._generate_master_key()
        self.fernet = Fernet(self.master_key)
        self._key_cache: Dict[str, bytes] = {}
        
    def _generate_master_key(self) -> bytes:
        """Generate a new master encryption key."""
        return Fernet.generate_key()
    
    def derive_key(self, password: str, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """
        Derive an encryption key from a password using PBKDF2.
        
        Args:
            password: Password to derive key from
            salt: Optional salt. If not provided, will be generated.
            
        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        Encrypt data using Fernet symmetric encryption.
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Encrypted data as bytes
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.fernet.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data using Fernet symmetric encryption.
        
        Args:
            encrypted_data: Encrypted data as bytes
            
        Returns:
            Decrypted data as bytes
        """
        return self.fernet.decrypt(encrypted_data)
    
    def encrypt_string(self, text: str) -> str:
        """
        Encrypt a string and return base64-encoded result.
        
        Args:
            text: Text to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        encrypted = self.encrypt(text)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """
        Decrypt a base64-encoded encrypted string.
        
        Args:
            encrypted_text: Base64-encoded encrypted string
            
        Returns:
            Decrypted text
        """
        encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))
        decrypted = self.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """
        Encrypt a dictionary by converting to JSON first.
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            Base64-encoded encrypted JSON string
        """
        json_str = json.dumps(data)
        return self.encrypt_string(json_str)
    
    def decrypt_dict(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt an encrypted dictionary.
        
        Args:
            encrypted_data: Base64-encoded encrypted JSON string
            
        Returns:
            Decrypted dictionary
        """
        json_str = self.decrypt_string(encrypted_data)
        return json.loads(json_str)
    
    def rotate_key(self, new_master_key: Optional[bytes] = None) -> bytes:
        """
        Rotate the master encryption key.
        
        Args:
            new_master_key: Optional new master key. If not provided, will be generated.
            
        Returns:
            New master key
        """
        old_key = self.master_key
        self.master_key = new_master_key or self._generate_master_key()
        self.fernet = Fernet(self.master_key)
        self._key_cache.clear()
        return self.master_key
    
    def get_master_key(self) -> bytes:
        """Get the current master key."""
        return self.master_key


class DatabaseEncryption:
    """
    Database-specific encryption for sensitive fields.
    Provides field-level encryption for database columns.
    """
    
    def __init__(self, encryption_manager: EncryptionManager):
        """
        Initialize database encryption.
        
        Args:
            encryption_manager: EncryptionManager instance
        """
        self.encryption_manager = encryption_manager
        
    def encrypt_field(self, value: Any, field_name: str) -> str:
        """
        Encrypt a database field value.
        
        Args:
            value: Value to encrypt
            field_name: Name of the field (for audit logging)
            
        Returns:
            Encrypted value as string
        """
        if value is None:
            return None
            
        # Convert value to string if needed
        if not isinstance(value, str):
            value = str(value)
            
        return self.encryption_manager.encrypt_string(value)
    
    def decrypt_field(self, encrypted_value: str, field_name: str) -> str:
        """
        Decrypt a database field value.
        
        Args:
            encrypted_value: Encrypted value
            field_name: Name of the field (for audit logging)
            
        Returns:
            Decrypted value
        """
        if encrypted_value is None:
            return None
            
        return self.encryption_manager.decrypt_string(encrypted_value)
    
    def encrypt_row(self, row_data: Dict[str, Any], encrypted_fields: list[str]) -> Dict[str, Any]:
        """
        Encrypt specified fields in a database row.
        
        Args:
            row_data: Dictionary of row data
            encrypted_fields: List of field names to encrypt
            
        Returns:
            Dictionary with encrypted fields
        """
        encrypted_row = row_data.copy()
        for field in encrypted_fields:
            if field in encrypted_row and encrypted_row[field] is not None:
                encrypted_row[field] = self.encrypt_field(encrypted_row[field], field)
        return encrypted_row
    
    def decrypt_row(self, row_data: Dict[str, Any], encrypted_fields: list[str]) -> Dict[str, Any]:
        """
        Decrypt specified fields in a database row.
        
        Args:
            row_data: Dictionary of row data with encrypted fields
            encrypted_fields: List of field names to decrypt
            
        Returns:
            Dictionary with decrypted fields
        """
        decrypted_row = row_data.copy()
        for field in encrypted_fields:
            if field in decrypted_row and decrypted_row[field] is not None:
                decrypted_row[field] = self.decrypt_field(decrypted_row[field], field)
        return decrypted_row


class FileEncryption:
    """
    File encryption for sensitive documents and data files.
    """
    
    def __init__(self, encryption_manager: EncryptionManager):
        """
        Initialize file encryption.
        
        Args:
            encryption_manager: EncryptionManager instance
        """
        self.encryption_manager = encryption_manager
        
    def encrypt_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Encrypt a file.
        
        Args:
            input_path: Path to file to encrypt
            output_path: Optional output path. If not provided, will append .encrypted
            
        Returns:
            Path to encrypted file
        """
        if output_path is None:
            output_path = f"{input_path}.encrypted"
            
        with open(input_path, 'rb') as f:
            data = f.read()
            
        encrypted_data = self.encryption_manager.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)
            
        return output_path
    
    def decrypt_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file.
        
        Args:
            input_path: Path to encrypted file
            output_path: Optional output path. If not provided, will remove .encrypted extension
            
        Returns:
            Path to decrypted file
        """
        if output_path is None:
            if input_path.endswith('.encrypted'):
                output_path = input_path[:-10]  # Remove .encrypted
            else:
                output_path = f"{input_path}.decrypted"
                
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()
            
        decrypted_data = self.encryption_manager.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
            
        return output_path
    
    def encrypt_file_in_memory(self, file_data: bytes) -> bytes:
        """
        Encrypt file data in memory without writing to disk.
        
        Args:
            file_data: File data as bytes
            
        Returns:
            Encrypted file data
        """
        return self.encryption_manager.encrypt(file_data)
    
    def decrypt_file_in_memory(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt file data in memory without writing to disk.
        
        Args:
            encrypted_data: Encrypted file data
            
        Returns:
            Decrypted file data
        """
        return self.encryption_manager.decrypt(encrypted_data)


class CommunicationEncryption:
    """
    Encryption for API communications and data in transit.
    Provides additional encryption layer on top of HTTPS.
    """
    
    def __init__(self, encryption_manager: EncryptionManager):
        """
        Initialize communication encryption.
        
        Args:
            encryption_manager: EncryptionManager instance
        """
        self.encryption_manager = encryption_manager
        
    def encrypt_payload(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """
        Encrypt an API payload.
        
        Args:
            payload: Dictionary payload to encrypt
            
        Returns:
            Dictionary with encrypted payload and metadata
        """
        encrypted_data = self.encryption_manager.encrypt_dict(payload)
        return {
            'encrypted': True,
            'data': encrypted_data,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def decrypt_payload(self, encrypted_payload: Dict[str, str]) -> Dict[str, Any]:
        """
        Decrypt an API payload.
        
        Args:
            encrypted_payload: Dictionary with encrypted payload
            
        Returns:
            Decrypted payload dictionary
        """
        if not encrypted_payload.get('encrypted'):
            raise ValueError("Payload is not encrypted")
            
        return self.encryption_manager.decrypt_dict(encrypted_payload['data'])
    
    def encrypt_websocket_message(self, message: str) -> str:
        """
        Encrypt a WebSocket message.
        
        Args:
            message: Message to encrypt
            
        Returns:
            Encrypted message
        """
        return self.encryption_manager.encrypt_string(message)
    
    def decrypt_websocket_message(self, encrypted_message: str) -> str:
        """
        Decrypt a WebSocket message.
        
        Args:
            encrypted_message: Encrypted message
            
        Returns:
            Decrypted message
        """
        return self.encryption_manager.decrypt_string(encrypted_message)


class KeyManager:
    """
    Manages encryption keys, including generation, storage, and rotation.
    """
    
    def __init__(self, key_storage_path: str = "keys"):
        """
        Initialize key manager.
        
        Args:
            key_storage_path: Path to store encryption keys
        """
        self.key_storage_path = key_storage_path
        os.makedirs(key_storage_path, exist_ok=True)
        self._keys: Dict[str, bytes] = {}
        
    def generate_key(self, key_name: str) -> bytes:
        """
        Generate a new encryption key.
        
        Args:
            key_name: Name for the key
            
        Returns:
            Generated key
        """
        key = Fernet.generate_key()
        self._keys[key_name] = key
        return key
    
    def store_key(self, key_name: str, key: bytes, encrypted: bool = True):
        """
        Store an encryption key.
        
        Args:
            key_name: Name for the key
            key: Key to store
            encrypted: Whether to encrypt the key before storing
        """
        key_path = os.path.join(self.key_storage_path, f"{key_name}.key")
        
        if encrypted:
            # Encrypt the key with a master key derived from environment
            master_password = os.getenv('ENCRYPTION_MASTER_PASSWORD', 'default_master_password')
            encryption_manager = EncryptionManager()
            derived_key, salt = encryption_manager.derive_key(master_password)
            temp_manager = EncryptionManager(derived_key)
            encrypted_key = temp_manager.encrypt(key)
            
            # Store both encrypted key and salt
            with open(key_path, 'wb') as f:
                f.write(salt + encrypted_key)
        else:
            with open(key_path, 'wb') as f:
                f.write(key)
                
        self._keys[key_name] = key
    
    def load_key(self, key_name: str, encrypted: bool = True) -> bytes:
        """
        Load an encryption key.
        
        Args:
            key_name: Name of the key
            encrypted: Whether the key is encrypted
            
        Returns:
            Loaded key
        """
        if key_name in self._keys:
            return self._keys[key_name]
            
        key_path = os.path.join(self.key_storage_path, f"{key_name}.key")
        
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Key '{key_name}' not found")
            
        with open(key_path, 'rb') as f:
            data = f.read()
            
        if encrypted:
            # Extract salt and encrypted key
            salt = data[:16]
            encrypted_key = data[16:]
            
            # Decrypt the key
            master_password = os.getenv('ENCRYPTION_MASTER_PASSWORD', 'default_master_password')
            encryption_manager = EncryptionManager()
            derived_key, _ = encryption_manager.derive_key(master_password, salt)
            temp_manager = EncryptionManager(derived_key)
            key = temp_manager.decrypt(encrypted_key)
        else:
            key = data
            
        self._keys[key_name] = key
        return key
    
    def rotate_key(self, key_name: str) -> bytes:
        """
        Rotate an encryption key.
        
        Args:
            key_name: Name of the key to rotate
            
        Returns:
            New key
        """
        new_key = self.generate_key(key_name)
        self.store_key(key_name, new_key)
        return new_key
    
    def list_keys(self) -> list[str]:
        """
        List all stored keys.
        
        Returns:
            List of key names
        """
        keys = []
        for filename in os.listdir(self.key_storage_path):
            if filename.endswith('.key'):
                keys.append(filename[:-4])
        return keys
    
    def delete_key(self, key_name: str):
        """
        Delete an encryption key.
        
        Args:
            key_name: Name of the key to delete
        """
        key_path = os.path.join(self.key_storage_path, f"{key_name}.key")
        if os.path.exists(key_path):
            os.remove(key_path)
        if key_name in self._keys:
            del self._keys[key_name]


class EncryptionAudit:
    """
    Audit logging for encryption operations.
    Tracks all encryption/decryption operations for security compliance.
    """
    
    def __init__(self, audit_log_path: str = "encryption_audit.log"):
        """
        Initialize encryption audit.
        
        Args:
            audit_log_path: Path to audit log file
        """
        self.audit_log_path = audit_log_path
        
    def log_operation(
        self,
        operation: str,
        data_type: str,
        user_id: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an encryption operation.
        
        Args:
            operation: Type of operation (encrypt, decrypt, key_rotation, etc.)
            data_type: Type of data (database, file, communication)
            user_id: Optional user ID
            success: Whether operation was successful
            error: Optional error message
            metadata: Optional additional metadata
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'data_type': data_type,
            'user_id': user_id,
            'success': success,
            'error': error,
            'metadata': metadata or {}
        }
        
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_audit_log(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        operation: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> list[Dict[str, Any]]:
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
        if not os.path.exists(self.audit_log_path):
            return []
            
        entries = []
        with open(self.audit_log_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Apply filters
                    if start_date and datetime.fromisoformat(entry['timestamp']) < start_date:
                        continue
                    if end_date and datetime.fromisoformat(entry['timestamp']) > end_date:
                        continue
                    if operation and entry['operation'] != operation:
                        continue
                    if user_id and entry.get('user_id') != user_id:
                        continue
                        
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
                    
        return entries
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get encryption operation statistics.
        
        Returns:
            Dictionary with statistics
        """
        entries = self.get_audit_log()
        
        stats = {
            'total_operations': len(entries),
            'successful_operations': sum(1 for e in entries if e['success']),
            'failed_operations': sum(1 for e in entries if not e['success']),
            'operations_by_type': {},
            'operations_by_data_type': {}
        }
        
        for entry in entries:
            op_type = entry['operation']
            data_type = entry['data_type']
            
            stats['operations_by_type'][op_type] = stats['operations_by_type'].get(op_type, 0) + 1
            stats['operations_by_data_type'][data_type] = stats['operations_by_data_type'].get(data_type, 0) + 1
            
        return stats


# Global encryption manager instance
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """Get or create the global encryption manager instance."""
    global _encryption_manager
    if _encryption_manager is None:
        # Try to load master key from environment or key manager
        key_manager = KeyManager()
        try:
            master_key = key_manager.load_key('master')
        except FileNotFoundError:
            # Generate and store new master key
            master_key = Fernet.generate_key()
            key_manager.store_key('master', master_key)
            
        _encryption_manager = EncryptionManager(master_key)
    return _encryption_manager
