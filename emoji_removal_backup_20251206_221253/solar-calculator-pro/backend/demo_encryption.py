"""
Encryption System Demo

Demonstrates all features of the data encryption system.

Requirements: 11.3
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.encryption_service import get_encryption_service


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_database_encryption():
    """Demonstrate database encryption."""
    print_section("DATABASE ENCRYPTION")
    
    encryption_service = get_encryption_service()
    
    # Encrypt a single field
    print("1. Encrypting a single field...")
    original_email = "john.doe@example.com"
    encrypted_email = encryption_service.encrypt_database_field(
        value=original_email,
        field_name="email",
        user_id="demo_user"
    )
    print(f"   Original: {original_email}")
    print(f"   Encrypted: {encrypted_email[:50]}...")
    
    # Decrypt the field
    print("\n2. Decrypting the field...")
    decrypted_email = encryption_service.decrypt_database_field(
        encrypted_value=encrypted_email,
        field_name="email",
        user_id="demo_user"
    )
    print(f"   Decrypted: {decrypted_email}")
    print(f"   ✅ Match: {decrypted_email == original_email}")
    
    # Encrypt a database row
    print("\n3. Encrypting a database row...")
    user_data = {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1-555-0123",
        "address": "123 Main St, City, State 12345"
    }
    print(f"   Original row: {user_data}")
    
    encrypted_row = encryption_service.encrypt_database_row(
        row_data=user_data,
        encrypted_fields=["email", "phone", "address"],
        user_id="demo_user"
    )
    print(f"   Encrypted row: {encrypted_row}")
    
    # Decrypt the row
    print("\n4. Decrypting the database row...")
    decrypted_row = encryption_service.decrypt_database_row(
        row_data=encrypted_row,
        encrypted_fields=["email", "phone", "address"],
        user_id="demo_user"
    )
    print(f"   Decrypted row: {decrypted_row}")
    print(f"   ✅ Match: {decrypted_row == user_data}")


def demo_file_encryption():
    """Demonstrate file encryption."""
    print_section("FILE ENCRYPTION")
    
    encryption_service = get_encryption_service()
    
    # Encrypt file data in memory
    print("1. Encrypting file data in memory...")
    original_data = b"This is sensitive file content that needs to be encrypted."
    print(f"   Original size: {len(original_data)} bytes")
    
    encrypted_data = encryption_service.encrypt_file_data(
        file_data=original_data,
        user_id="demo_user"
    )
    print(f"   Encrypted size: {len(encrypted_data)} bytes")
    print(f"   Encrypted data: {encrypted_data[:50]}...")
    
    # Decrypt file data
    print("\n2. Decrypting file data...")
    decrypted_data = encryption_service.decrypt_file_data(
        encrypted_data=encrypted_data,
        user_id="demo_user"
    )
    print(f"   Decrypted size: {len(decrypted_data)} bytes")
    print(f"   Decrypted data: {decrypted_data.decode('utf-8')}")
    print(f"   ✅ Match: {decrypted_data == original_data}")


def demo_communication_encryption():
    """Demonstrate communication encryption."""
    print_section("COMMUNICATION ENCRYPTION")
    
    encryption_service = get_encryption_service()
    
    # Encrypt API payload
    print("1. Encrypting API payload...")
    payload = {
        "user_id": 123,
        "action": "update_profile",
        "data": {
            "email": "new@example.com",
            "phone": "+1-555-9999"
        }
    }
    print(f"   Original payload: {payload}")
    
    encrypted_payload = encryption_service.encrypt_api_payload(
        payload=payload,
        user_id="demo_user"
    )
    print(f"   Encrypted payload: {encrypted_payload}")
    
    # Decrypt API payload
    print("\n2. Decrypting API payload...")
    decrypted_payload = encryption_service.decrypt_api_payload(
        encrypted_payload=encrypted_payload,
        user_id="demo_user"
    )
    print(f"   Decrypted payload: {decrypted_payload}")
    print(f"   ✅ Match: {decrypted_payload == payload}")
    
    # Encrypt WebSocket message
    print("\n3. Encrypting WebSocket message...")
    message = "This is a sensitive WebSocket message"
    print(f"   Original message: {message}")
    
    encrypted_message = encryption_service.encrypt_websocket_message(
        message=message,
        user_id="demo_user"
    )
    print(f"   Encrypted message: {encrypted_message[:50]}...")
    
    # Decrypt WebSocket message
    print("\n4. Decrypting WebSocket message...")
    decrypted_message = encryption_service.decrypt_websocket_message(
        encrypted_message=encrypted_message,
        user_id="demo_user"
    )
    print(f"   Decrypted message: {decrypted_message}")
    print(f"   ✅ Match: {decrypted_message == message}")


def demo_key_management():
    """Demonstrate key management."""
    print_section("KEY MANAGEMENT")
    
    encryption_service = get_encryption_service()
    
    # Generate a new key
    print("1. Generating a new encryption key...")
    key_name = "demo_key"
    try:
        key = encryption_service.generate_key(
            key_name=key_name,
            user_id="admin_user"
        )
        print(f"   ✅ Key '{key_name}' generated successfully")
    except Exception as e:
        print(f"   ℹ️  Key may already exist: {e}")
    
    # List all keys
    print("\n2. Listing all encryption keys...")
    keys = encryption_service.list_keys()
    print(f"   Available keys: {keys}")
    
    # Rotate a key
    print("\n3. Rotating encryption key...")
    try:
        new_key = encryption_service.rotate_key(
            key_name=key_name,
            user_id="admin_user"
        )
        print(f"   ✅ Key '{key_name}' rotated successfully")
    except Exception as e:
        print(f"   ⚠️  Key rotation failed: {e}")
    
    # Delete the demo key
    print("\n4. Deleting demo key...")
    try:
        encryption_service.delete_key(
            key_name=key_name,
            user_id="admin_user"
        )
        print(f"   ✅ Key '{key_name}' deleted successfully")
    except Exception as e:
        print(f"   ⚠️  Key deletion failed: {e}")


def demo_audit_logging():
    """Demonstrate audit logging."""
    print_section("AUDIT LOGGING")
    
    encryption_service = get_encryption_service()
    
    # Get audit statistics
    print("1. Getting encryption operation statistics...")
    stats = encryption_service.get_audit_statistics()
    print(f"   Total operations: {stats['total_operations']}")
    print(f"   Successful operations: {stats['successful_operations']}")
    print(f"   Failed operations: {stats['failed_operations']}")
    print(f"   Operations by type: {stats['operations_by_type']}")
    print(f"   Operations by data type: {stats['operations_by_data_type']}")
    
    # Get recent audit logs
    print("\n2. Getting recent audit logs...")
    start_date = datetime.utcnow() - timedelta(hours=1)
    audit_logs = encryption_service.get_audit_log(
        start_date=start_date,
        user_id="demo_user"
    )
    print(f"   Found {len(audit_logs)} log entries in the last hour")
    
    if audit_logs:
        print("\n   Recent operations:")
        for log in audit_logs[-5:]:  # Show last 5
            print(f"   - {log['timestamp']}: {log['operation']} ({log['data_type']}) - {'✅' if log['success'] else '❌'}")


def demo_encryption_status():
    """Demonstrate encryption status and validation."""
    print_section("ENCRYPTION STATUS & VALIDATION")
    
    encryption_service = get_encryption_service()
    
    # Get encryption status
    print("1. Getting encryption system status...")
    status = encryption_service.get_encryption_status()
    print(f"   Encryption enabled: {status['encryption_enabled']}")
    print(f"   Master key exists: {status['master_key_exists']}")
    print(f"   Stored keys: {status['stored_keys']}")
    
    # Validate encryption system
    print("\n2. Validating encryption system...")
    validation = encryption_service.validate_encryption()
    print(f"   Database encryption: {'✅' if validation['database_encryption'] else '❌'}")
    print(f"   File encryption: {'✅' if validation['file_encryption'] else '❌'}")
    print(f"   Communication encryption: {'✅' if validation['communication_encryption'] else '❌'}")
    print(f"   Key management: {'✅' if validation['key_management'] else '❌'}")
    
    all_valid = all(validation.values())
    print(f"\n   Overall status: {'✅ All systems operational' if all_valid else '❌ Some systems need attention'}")


def main():
    """Run all encryption demos."""
    print("\n" + "="*60)
    print("  SOLAR CALCULATOR PRO - ENCRYPTION SYSTEM DEMO")
    print("="*60)
    
    try:
        # Run all demos
        demo_database_encryption()
        demo_file_encryption()
        demo_communication_encryption()
        demo_key_management()
        demo_audit_logging()
        demo_encryption_status()
        
        # Final summary
        print_section("DEMO COMPLETE")
        print("✅ All encryption features demonstrated successfully!")
        print("\nFor more information, see:")
        print("  - docs/ENCRYPTION_SYSTEM_GUIDE.md")
        print("  - docs/ENCRYPTION_QUICK_REFERENCE.md")
        print("  - API documentation at /docs")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
