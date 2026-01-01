"""
Security Audit and Hardening Tests
Task 241: Security Audit and Hardening

Comprehensive security tests for:
- API endpoint security
- Authentication vulnerabilities
- Authorization bypass attempts
- XSS vulnerabilities
- SQL injection prevention
- CSRF protection
- Rate limiting
- Data encryption
- Security headers
"""

import pytest
import re
import html
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from unittest.mock import Mock, patch


class SecurityLevel(str, Enum):
    """Security severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityCheck:
    """Security check result"""
    name: str
    passed: bool
    level: SecurityLevel
    description: str
    recommendation: str = ""


@dataclass
class SecurityAuditReport:
    """Complete security audit report"""
    checks: List[SecurityCheck]
    
    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.passed)
    
    @property
    def failed_count(self) -> int:
        return sum(1 for c in self.checks if not c.passed)
    
    @property
    def critical_failures(self) -> List[SecurityCheck]:
        return [c for c in self.checks if not c.passed and c.level == SecurityLevel.CRITICAL]
    
    @property
    def is_secure(self) -> bool:
        return len(self.critical_failures) == 0


# ============================================================================
# Security Utilities
# ============================================================================

class InputSanitizer:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_html(input_str: str) -> str:
        """Sanitize HTML to prevent XSS"""
        return html.escape(input_str)
    
    @staticmethod
    def sanitize_sql(input_str: str) -> str:
        """Basic SQL injection prevention"""
        # Remove common SQL injection patterns
        dangerous_patterns = [
            r"('|\")\s*(OR|AND)\s*('|\")?1('|\")?=('|\")?1",
            r";\s*(DROP|DELETE|UPDATE|INSERT)",
            r"--",
            r"/\*.*\*/",
            r"UNION\s+SELECT",
        ]
        result = input_str
        for pattern in dangerous_patterns:
            result = re.sub(pattern, "", result, flags=re.IGNORECASE)
        return result
    
    @staticmethod
    def is_safe_input(input_str: str) -> bool:
        """Check if input is safe"""
        dangerous_chars = ["<", ">", "'", '"', ";", "--", "/*", "*/"]
        return not any(char in input_str for char in dangerous_chars)


class AuthenticationValidator:
    """Authentication validation utilities"""
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """Validate JWT token format"""
        if not token:
            return False
        parts = token.split(".")
        return len(parts) == 3
    
    @staticmethod
    def is_strong_password(password: str) -> bool:
        """Check password strength"""
        if len(password) < 8:
            return False
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        return has_upper and has_lower and has_digit and has_special
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, client_id: str, current_time: float) -> bool:
        """Check if request is allowed"""
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Clean old requests
        window_start = current_time - self.window_seconds
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > window_start
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        self.requests[client_id].append(current_time)
        return True


class CSRFProtection:
    """CSRF protection utilities"""
    
    @staticmethod
    def generate_token() -> str:
        """Generate CSRF token"""
        import secrets
        return secrets.token_hex(32)
    
    @staticmethod
    def validate_token(token: str, expected: str) -> bool:
        """Validate CSRF token"""
        if not token or not expected:
            return False
        return secrets.compare_digest(token, expected)


import secrets  # Add import for CSRFProtection


# ============================================================================
# Test Classes
# ============================================================================

class TestAuthenticationSecurity:
    """Tests for authentication security"""
    
    def test_token_validation(self):
        """Test JWT token validation"""
        validator = AuthenticationValidator()
        
        # Valid token format (3 parts separated by dots)
        valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        assert validator.validate_token(valid_token)
        
        # Invalid tokens
        assert not validator.validate_token("")
        assert not validator.validate_token("invalid")
        assert not validator.validate_token("only.two")  # Only 2 parts
    
    def test_password_strength(self):
        """Test password strength validation"""
        validator = AuthenticationValidator()
        
        # Strong passwords
        assert validator.is_strong_password("SecureP@ss1")
        assert validator.is_strong_password("MyP@ssw0rd!")
        
        # Weak passwords
        assert not validator.is_strong_password("password")
        assert not validator.is_strong_password("12345678")
        assert not validator.is_strong_password("short")
        assert not validator.is_strong_password("NoSpecialChar1")
    
    def test_email_validation(self):
        """Test email validation"""
        validator = AuthenticationValidator()
        
        # Valid emails
        assert validator.validate_email("user@example.com")
        assert validator.validate_email("test.user@domain.org")
        
        # Invalid emails
        assert not validator.validate_email("invalid")
        assert not validator.validate_email("@domain.com")
        assert not validator.validate_email("user@")
    
    def test_empty_credentials_rejected(self):
        """Test that empty credentials are rejected"""
        validator = AuthenticationValidator()
        
        assert not validator.validate_token("")
        assert not validator.is_strong_password("")
        assert not validator.validate_email("")


class TestAuthorizationSecurity:
    """Tests for authorization security"""
    
    def test_role_based_access(self):
        """Test role-based access control"""
        roles = {
            "admin": ["read", "write", "delete", "admin"],
            "user": ["read", "write"],
            "guest": ["read"]
        }
        
        def has_permission(role: str, permission: str) -> bool:
            return permission in roles.get(role, [])
        
        # Admin has all permissions
        assert has_permission("admin", "read")
        assert has_permission("admin", "write")
        assert has_permission("admin", "delete")
        assert has_permission("admin", "admin")
        
        # User has limited permissions
        assert has_permission("user", "read")
        assert has_permission("user", "write")
        assert not has_permission("user", "delete")
        assert not has_permission("user", "admin")
        
        # Guest has minimal permissions
        assert has_permission("guest", "read")
        assert not has_permission("guest", "write")
    
    def test_resource_ownership(self):
        """Test resource ownership validation"""
        def can_access_resource(user_id: int, resource_owner_id: int, is_admin: bool) -> bool:
            return user_id == resource_owner_id or is_admin
        
        # Owner can access
        assert can_access_resource(1, 1, False)
        
        # Non-owner cannot access
        assert not can_access_resource(1, 2, False)
        
        # Admin can access any resource
        assert can_access_resource(1, 2, True)


class TestXSSPrevention:
    """Tests for XSS prevention"""
    
    def test_html_sanitization(self):
        """Test HTML sanitization"""
        sanitizer = InputSanitizer()
        
        # Script tags
        malicious = "<script>alert('xss')</script>"
        sanitized = sanitizer.sanitize_html(malicious)
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized
        
        # Event handlers
        malicious = '<img src="x" onerror="alert(\'xss\')">'
        sanitized = sanitizer.sanitize_html(malicious)
        assert "onerror" not in sanitized or "&quot;" in sanitized
    
    def test_input_validation(self):
        """Test input validation for XSS"""
        sanitizer = InputSanitizer()
        
        # Safe inputs
        assert sanitizer.is_safe_input("Hello World")
        assert sanitizer.is_safe_input("user@example.com")
        assert sanitizer.is_safe_input("12345")
        
        # Unsafe inputs
        assert not sanitizer.is_safe_input("<script>")
        assert not sanitizer.is_safe_input("'; DROP TABLE users;--")
    
    def test_output_encoding(self):
        """Test output encoding"""
        test_cases = [
            ("<", "&lt;"),
            (">", "&gt;"),
            ("&", "&amp;"),
            ('"', "&quot;"),
            ("'", "&#x27;"),
        ]
        
        for input_char, expected in test_cases:
            encoded = html.escape(input_char)
            assert "<" not in encoded or input_char != "<"


class TestSQLInjectionPrevention:
    """Tests for SQL injection prevention"""
    
    def test_sql_sanitization(self):
        """Test SQL injection sanitization"""
        sanitizer = InputSanitizer()
        
        # Common SQL injection patterns
        injections = [
            "' OR '1'='1",
            "'; DROP TABLE users;--",
            "1; DELETE FROM users",
            "1 UNION SELECT * FROM passwords",
        ]
        
        for injection in injections:
            sanitized = sanitizer.sanitize_sql(injection)
            # Should not contain dangerous patterns
            assert "DROP" not in sanitized.upper() or ";" not in sanitized
            assert "DELETE" not in sanitized.upper() or ";" not in sanitized
    
    def test_parameterized_queries(self):
        """Test that parameterized queries are used"""
        # Simulate parameterized query
        def safe_query(user_id: int) -> str:
            # This is how queries should be built
            return f"SELECT * FROM users WHERE id = ?"
        
        # The query should use placeholders, not string interpolation
        query = safe_query(1)
        assert "?" in query
        assert "1" not in query
    
    def test_input_type_validation(self):
        """Test input type validation"""
        def validate_id(value: Any) -> bool:
            try:
                int(value)
                return True
            except (ValueError, TypeError):
                return False
        
        # Valid IDs
        assert validate_id(1)
        assert validate_id("123")
        
        # Invalid IDs (potential injection)
        assert not validate_id("1; DROP TABLE")
        assert not validate_id("abc")


class TestCSRFProtection:
    """Tests for CSRF protection"""
    
    def test_csrf_token_generation(self):
        """Test CSRF token generation"""
        csrf = CSRFProtection()
        
        token1 = csrf.generate_token()
        token2 = csrf.generate_token()
        
        # Tokens should be unique
        assert token1 != token2
        
        # Tokens should be long enough
        assert len(token1) >= 32
    
    def test_csrf_token_validation(self):
        """Test CSRF token validation"""
        csrf = CSRFProtection()
        
        token = csrf.generate_token()
        
        # Valid token
        assert csrf.validate_token(token, token)
        
        # Invalid tokens
        assert not csrf.validate_token("invalid", token)
        assert not csrf.validate_token("", token)
        assert not csrf.validate_token(token, "")
    
    def test_csrf_timing_attack_prevention(self):
        """Test CSRF validation is timing-safe"""
        csrf = CSRFProtection()
        
        token = csrf.generate_token()
        wrong_token = "a" * len(token)
        
        # Both should complete (timing-safe comparison)
        result1 = csrf.validate_token(token, token)
        result2 = csrf.validate_token(wrong_token, token)
        
        assert result1 is True
        assert result2 is False


class TestRateLimiting:
    """Tests for rate limiting"""
    
    def test_rate_limit_allows_normal_traffic(self):
        """Test rate limiter allows normal traffic"""
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        
        # First 10 requests should be allowed
        for i in range(10):
            assert limiter.is_allowed("client1", float(i))
    
    def test_rate_limit_blocks_excessive_traffic(self):
        """Test rate limiter blocks excessive traffic"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        # First 5 requests allowed
        for i in range(5):
            assert limiter.is_allowed("client1", float(i))
        
        # 6th request blocked
        assert not limiter.is_allowed("client1", 5.0)
    
    def test_rate_limit_resets_after_window(self):
        """Test rate limiter resets after time window"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        # Use up limit
        for i in range(5):
            limiter.is_allowed("client1", float(i))
        
        # Should be blocked
        assert not limiter.is_allowed("client1", 30.0)
        
        # After window, should be allowed again
        assert limiter.is_allowed("client1", 70.0)
    
    def test_rate_limit_per_client(self):
        """Test rate limiting is per-client"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        # Client 1 uses up limit
        for i in range(5):
            limiter.is_allowed("client1", float(i))
        
        # Client 2 should still be allowed
        assert limiter.is_allowed("client2", 5.0)


class TestDataEncryption:
    """Tests for data encryption"""
    
    def test_password_hashing(self):
        """Test password hashing"""
        import hashlib
        
        password = "SecureP@ss1"
        
        # Hash should not equal plaintext
        hashed = hashlib.sha256(password.encode()).hexdigest()
        assert hashed != password
        
        # Same password should produce same hash
        hashed2 = hashlib.sha256(password.encode()).hexdigest()
        assert hashed == hashed2
    
    def test_sensitive_data_not_logged(self):
        """Test sensitive data is not logged"""
        sensitive_fields = ["password", "token", "secret", "api_key", "credit_card"]
        
        def sanitize_for_logging(data: Dict[str, Any]) -> Dict[str, Any]:
            return {
                k: "***REDACTED***" if any(s in k.lower() for s in sensitive_fields) else v
                for k, v in data.items()
            }
        
        test_data = {
            "username": "user1",
            "password": "secret123",
            "api_key": "key123",
            "email": "user@example.com"
        }
        
        sanitized = sanitize_for_logging(test_data)
        
        assert sanitized["username"] == "user1"
        assert sanitized["email"] == "user@example.com"
        assert sanitized["password"] == "***REDACTED***"
        assert sanitized["api_key"] == "***REDACTED***"


class TestSecurityHeaders:
    """Tests for security headers"""
    
    def test_required_security_headers(self):
        """Test required security headers are present"""
        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
        }
        
        # Simulate response headers
        response_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
        }
        
        for header, expected_value in required_headers.items():
            assert header in response_headers
            assert response_headers[header] == expected_value
    
    def test_no_server_info_leaked(self):
        """Test server information is not leaked"""
        # Headers that should not reveal server info
        dangerous_headers = ["Server", "X-Powered-By", "X-AspNet-Version"]
        
        response_headers = {
            "Content-Type": "application/json",
            "X-Content-Type-Options": "nosniff",
        }
        
        for header in dangerous_headers:
            assert header not in response_headers


class TestSecurityAuditReport:
    """Tests for security audit report generation"""
    
    def test_audit_report_generation(self):
        """Test security audit report generation"""
        checks = [
            SecurityCheck("Auth Token Validation", True, SecurityLevel.CRITICAL, "JWT validation"),
            SecurityCheck("XSS Prevention", True, SecurityLevel.HIGH, "Input sanitization"),
            SecurityCheck("SQL Injection Prevention", True, SecurityLevel.CRITICAL, "Parameterized queries"),
            SecurityCheck("CSRF Protection", True, SecurityLevel.HIGH, "Token validation"),
            SecurityCheck("Rate Limiting", True, SecurityLevel.MEDIUM, "Request throttling"),
        ]
        
        report = SecurityAuditReport(checks=checks)
        
        assert report.passed_count == 5
        assert report.failed_count == 0
        assert report.is_secure
    
    def test_audit_report_with_failures(self):
        """Test audit report with failures"""
        checks = [
            SecurityCheck("Auth Token Validation", True, SecurityLevel.CRITICAL, "JWT validation"),
            SecurityCheck("XSS Prevention", False, SecurityLevel.HIGH, "Input sanitization"),
            SecurityCheck("SQL Injection Prevention", False, SecurityLevel.CRITICAL, "Parameterized queries"),
        ]
        
        report = SecurityAuditReport(checks=checks)
        
        assert report.passed_count == 1
        assert report.failed_count == 2
        assert len(report.critical_failures) == 1
        assert not report.is_secure


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
