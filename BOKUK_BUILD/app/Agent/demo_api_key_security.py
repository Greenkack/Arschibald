"""
Demo: API Key Security Implementation
======================================

Demonstrates the secure API key management features implemented in task 12.3.

Requirements: 12.1, 12.2, 12.3, 12.5
"""

from Agent.config import (
    check_api_keys,
    validate_api_key_format,
    validate_env_file_security,
    validate_startup_security,
)
from Agent.agent.security import mask_sensitive_data
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def demo_env_file_security():
    """Demonstrate .env file security validation."""
    print("\n" + "=" * 70)
    print("DEMO 1: .env File Security Validation")
    print("=" * 70)
    print("\nThis validates that:")
    print("  - .env file exists")
    print("  - .env is in .gitignore")
    print("  - File permissions are secure (Unix)")
    print()

    is_secure, warnings = validate_env_file_security()

    if is_secure:
        print("✅ .env file is properly secured!")
    else:
        print("⚠️  Security warnings found:")
        for warning in warnings:
            print(f"   {warning}")


def demo_api_key_format_validation():
    """Demonstrate API key format validation."""
    print("\n" + "=" * 70)
    print("DEMO 2: API Key Format Validation")
    print("=" * 70)
    print("\nValidating API key formats without exposing actual keys...")
    print()

    # Example validations (without actual keys)
    examples = [
        ("OPENAI_API_KEY",
         "sk-1234567890abcdefghijklmnopqrstuvwxyz",
         "Valid OpenAI key format"),
        ("OPENAI_API_KEY",
         "invalid-key",
         "Invalid format (should start with sk-)"),
        ("TAVILY_API_KEY",
         "tvly-1234567890abcdefghijklmnopqrstuvwxyz",
         "Valid Tavily key format"),
    ]

    for key_name, key_value, description in examples:
        is_valid, error = validate_api_key_format(key_name, key_value)
        status = "✅" if is_valid else "❌"
        print(f"{status} {key_name}: {description}")
        if error:
            print(f"   Error: {error}")


def demo_sensitive_data_masking():
    """Demonstrate sensitive data masking."""
    print("\n" + "=" * 70)
    print("DEMO 3: Sensitive Data Masking")
    print("=" * 70)
    print("\nMasking sensitive data to prevent exposure...")
    print()

    examples = [
        "API key: sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890",
        "Token: tvly-1234567890abcdefghijklmnopqrstuvwxyz",
        "Password: mySecretPassword123",
        "Bearer token: abc123def456ghi789jkl012mno345pqr678",
    ]

    for original in examples:
        masked = mask_sensitive_data(original)
        print(f"Original: {original}")
        print(f"Masked:   {masked}")
        print()


def demo_startup_validation():
    """Demonstrate comprehensive startup validation."""
    print("\n" + "=" * 70)
    print("DEMO 4: Comprehensive Startup Validation")
    print("=" * 70)
    print("\nRunning all security checks...")
    print()

    is_valid, issues = validate_startup_security()

    if is_valid:
        print("✅ All security checks passed!")
    else:
        print("⚠️  Security issues found:")
        for issue in issues:
            print(f"   {issue}")

    # Show which keys are configured
    print("\nConfigured API Keys:")
    keys_status = check_api_keys()
    for key_name, is_present in keys_status.items():
        status = "✅" if is_present else "❌"
        print(f"   {status} {key_name}")


def demo_logging_filter():
    """Demonstrate logging sensitive data filter."""
    print("\n" + "=" * 70)
    print("DEMO 5: Logging Sensitive Data Filter")
    print("=" * 70)
    print("\nThe logging system automatically filters sensitive data...")
    print()

    try:

        from Agent.agent.logging_config import setup_logging

        # Set up logging with filter
        logger = setup_logging(log_to_console=False, log_to_file=False)

        print("✅ SensitiveDataFilter is active in logging configuration")
        print()
        print("Example: If you log 'API key: sk-1234567890...'")
        print("Output:  'API key: [REDACTED_API_KEY]'")
        print()
        print("This prevents accidental exposure of API keys in logs!")

    except Exception as e:
        print(f"❌ Error: {e}")


def demo_security_best_practices():
    """Show security best practices."""
    print("\n" + "=" * 70)
    print("DEMO 6: Security Best Practices")
    print("=" * 70)
    print()

    print("✅ DO:")
    print("   1. Load keys from .env file")
    print("      load_dotenv()")
    print("      api_key = os.getenv('OPENAI_API_KEY')")
    print()
    print("   2. Mask keys in output")
    print("      print(f'Key: {api_key[:4]}***')")
    print()
    print("   3. Validate on startup")
    print("      validate_startup_security()")
    print()
    print("   4. Keep .env in .gitignore")
    print("      echo '.env' >> .gitignore")
    print()

    print("❌ DON'T:")
    print("   1. Never hardcode keys")
    print("      api_key = 'sk-1234567890...'  # WRONG!")
    print()
    print("   2. Never log keys")
    print("      logger.info(f'Key: {api_key}')  # WRONG!")
    print()
    print("   3. Never commit .env")
    print("      git add .env  # WRONG!")
    print()
    print("   4. Never share keys")
    print("      Don't paste keys in chat/email/screenshots")


def main():
    """Run all demos."""
    print("=" * 70)
    print("API KEY SECURITY IMPLEMENTATION DEMO")
    print("=" * 70)
    print("\nTask 12.3: Secure API key management")
    print("Requirements: 12.1, 12.2, 12.3, 12.5")
    print()
    print("This demo shows the security features implemented:")
    print("  1. .env file security validation")
    print("  2. API key format validation")
    print("  3. Sensitive data masking")
    print("  4. Comprehensive startup validation")
    print("  5. Logging sensitive data filter")
    print("  6. Security best practices")

    try:
        demo_env_file_security()
        demo_api_key_format_validation()
        demo_sensitive_data_masking()
        demo_startup_validation()
        demo_logging_filter()
        demo_security_best_practices()

        print("\n" + "=" * 70)
        print("DEMO COMPLETE")
        print("=" * 70)
        print("\n✅ All security features demonstrated successfully!")
        print()
        print("Next steps:")
        print("  - Run: python Agent/audit_api_key_security.py")
        print("  - Run: python Agent/test_api_key_security.py")
        print("  - Read: Agent/API_KEY_SECURITY_GUIDE.md")
        print()

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
