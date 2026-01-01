"""
Tests for Security Implementation

Tests for rate limiting, CSRF protection, input sanitization, and security headers.
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from backend.middleware.rate_limiter import get_limiter, setup_rate_limiting
from backend.middleware.csrf_protection import CSRFProtection
from backend.middleware.input_sanitizer import InputSanitizer
from backend.middleware.security_headers import SecurityHeaders
from backend.core.security_manager import setup_security, SecurityPresets


# Test Rate Limiting
class TestRateLimiting:
    """Tests for rate limiting"""
    
    def test_rate_limiter_creation(self):
        """Test rate limiter can be created"""
        limiter = get_limiter()
        assert limiter is not None
        assert limiter.enabled is True
    
    def test_rate_limiter_setup(self):
        """Test rate limiter can be setup on app"""
        app = FastAPI()
        setup_rate_limiting(app)
        
        assert hasattr(app.state, 'limiter')
        assert app.state.limiter is not None


# Test CSRF Protection
class TestCSRFProtection:
    """Tests for CSRF protection"""
    
    def test_csrf_token_generation(self):
        """Test CSRF token can be generated"""
        csrf = CSRFProtection(secret_key="test-secret-key")
        token = csrf.generate_token()
        
        assert token is not None
        assert len(token) > 0
        assert ":" in token  # Token should have parts separated by colons
    
    def test_csrf_token_validation(self):
        """Test CSRF token validation"""
        csrf = CSRFProtection(secret_key="test-secret-key")
        token = csrf.generate_token()
        
        # Valid token should pass
        assert csrf.validate_token(token) is True
        
        # Invalid token should fail
        assert csrf.validate_token("invalid:token:signature") is False
    
    def test_csrf_token_expiration(self):
        """Test CSRF token expiration"""
        csrf = CSRFProtection(secret_key="test-secret-key", token_lifetime=1)
        token = csrf.generate_token()
        
        # Token should be valid immediately
        assert csrf.validate_token(token) is True
        
        # Wait for token to expire
        import time
        time.sleep(2)
        
        # Token should be expired
        assert csrf.validate_token(token) is False
    
    def test_csrf_safe_methods(self):
        """Test CSRF protection allows safe methods"""
        app = FastAPI()
        csrf = CSRFProtection(secret_key="test-secret-key")
        app.middleware("http")(csrf)
        
        @app.get("/test")
        async def test_get():
            return {"message": "success"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        # GET request should succeed without CSRF token
        assert response.status_code == 200
        
        # Response should include CSRF token
        assert "X-CSRF-Token" in response.headers


# Test Input Sanitization
class TestInputSanitization:
    """Tests for input sanitization"""
    
    def test_sql_injection_detection(self):
        """Test SQL injection pattern detection"""
        sanitizer = InputSanitizer()
        
        # Should detect SQL injection
        assert sanitizer.check_sql_injection("SELECT * FROM users") is True
        assert sanitizer.check_sql_injection("DROP TABLE users") is True
        assert sanitizer.check_sql_injection("' OR '1'='1") is True
        
        # Should not detect in normal text
        assert sanitizer.check_sql_injection("Hello world") is False
    
    def test_xss_detection(self):
        """Test XSS pattern detection"""
        sanitizer = InputSanitizer()
        
        # Should detect XSS
        assert sanitizer.check_xss("<script>alert('xss')</script>") is True
        assert sanitizer.check_xss("javascript:alert('xss')") is True
        assert sanitizer.check_xss("<img onerror='alert(1)'>") is True
        
        # Should not detect in normal text
        assert sanitizer.check_xss("Hello world") is False
    
    def test_path_traversal_detection(self):
        """Test path traversal pattern detection"""
        sanitizer = InputSanitizer()
        
        # Should detect path traversal
        assert sanitizer.check_path_traversal("../../../etc/passwd") is True
        assert sanitizer.check_path_traversal("..\\..\\windows\\system32") is True
        
        # Should not detect in normal paths
        assert sanitizer.check_path_traversal("/home/user/file.txt") is False
    
    def test_command_injection_detection(self):
        """Test command injection pattern detection"""
        sanitizer = InputSanitizer()
        
        # Should detect command injection
        assert sanitizer.check_command_injection("ls; rm -rf /") is True
        assert sanitizer.check_command_injection("cat file | grep password") is True
        assert sanitizer.check_command_injection("$(whoami)") is True
        
        # Should not detect in normal text
        assert sanitizer.check_command_injection("Hello world") is False
    
    def test_string_sanitization(self):
        """Test string sanitization"""
        sanitizer = InputSanitizer()
        
        # Normal string should pass
        result = sanitizer.sanitize_string("Hello world")
        assert result == "Hello world"
        
        # HTML should be escaped
        result = sanitizer.sanitize_string("<b>Bold</b>")
        assert "&lt;b&gt;" in result
    
    def test_value_sanitization(self):
        """Test recursive value sanitization"""
        sanitizer = InputSanitizer()
        
        # Test dict sanitization
        data = {
            "name": "John",
            "message": "<script>alert('xss')</script>"
        }
        
        with pytest.raises(Exception):
            sanitizer.sanitize_value(data)
    
    def test_max_string_length(self):
        """Test maximum string length enforcement"""
        sanitizer = InputSanitizer(max_string_length=100)
        
        # Short string should pass
        short_string = "a" * 50
        result = sanitizer.sanitize_string(short_string)
        assert len(result) == 50
        
        # Long string should fail
        long_string = "a" * 200
        with pytest.raises(Exception):
            sanitizer.sanitize_string(long_string)
    
    def test_max_array_length(self):
        """Test maximum array length enforcement"""
        sanitizer = InputSanitizer(max_array_length=10)
        
        # Short array should pass
        short_array = [1, 2, 3]
        result = sanitizer.sanitize_value(short_array)
        assert len(result) == 3
        
        # Long array should fail
        long_array = list(range(100))
        with pytest.raises(Exception):
            sanitizer.sanitize_value(long_array)


# Test Security Headers
class TestSecurityHeaders:
    """Tests for security headers"""
    
    def test_security_headers_creation(self):
        """Test security headers can be created"""
        headers = SecurityHeaders()
        assert headers is not None
    
    def test_hsts_header(self):
        """Test HSTS header generation"""
        headers = SecurityHeaders(
            hsts_max_age=31536000,
            hsts_include_subdomains=True,
            hsts_preload=True
        )
        
        hsts = headers.get_hsts_header()
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts
        assert "preload" in hsts
    
    def test_csp_header(self):
        """Test CSP header generation"""
        headers = SecurityHeaders()
        csp = headers.get_csp_header()
        
        assert "default-src" in csp
        assert "script-src" in csp
        assert "style-src" in csp
    
    def test_permissions_policy_header(self):
        """Test Permissions-Policy header generation"""
        headers = SecurityHeaders()
        policy = headers.get_permissions_policy_header()
        
        assert "geolocation=()" in policy
        assert "camera=()" in policy
        assert "microphone=()" in policy
    
    def test_security_headers_in_response(self):
        """Test security headers are added to response"""
        app = FastAPI()
        headers = SecurityHeaders()
        app.middleware("http")(headers)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        # Check security headers are present
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Permissions-Policy" in response.headers


# Test Security Manager
class TestSecurityManager:
    """Tests for security manager"""
    
    def test_security_manager_setup(self):
        """Test security manager can be setup"""
        app = FastAPI()
        security_manager = setup_security(app, **SecurityPresets.testing())
        
        assert security_manager is not None
        assert hasattr(app.state, 'security_manager')
    
    def test_security_status(self):
        """Test security status endpoint"""
        app = FastAPI()
        security_manager = setup_security(app, **SecurityPresets.production())
        
        @app.get("/security/status")
        async def security_status():
            return app.state.security_manager.get_security_status()
        
        client = TestClient(app)
        response = client.get("/security/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "rate_limiting" in data
        assert "csrf_protection" in data
        assert "input_sanitization" in data
        assert "security_headers" in data
        assert "sql_injection_prevention" in data
    
    def test_development_preset(self):
        """Test development security preset"""
        preset = SecurityPresets.development()
        
        assert preset["enable_rate_limiting"] is False
        assert preset["enable_csrf_protection"] is False
        assert preset["enable_input_sanitization"] is True
    
    def test_production_preset(self):
        """Test production security preset"""
        preset = SecurityPresets.production()
        
        assert preset["enable_rate_limiting"] is True
        assert preset["enable_csrf_protection"] is True
        assert preset["enable_input_sanitization"] is True
        assert preset["enable_security_headers"] is True
    
    def test_testing_preset(self):
        """Test testing security preset"""
        preset = SecurityPresets.testing()
        
        assert preset["enable_rate_limiting"] is False
        assert preset["enable_csrf_protection"] is False
        assert preset["enable_input_sanitization"] is False


# Integration Tests
class TestSecurityIntegration:
    """Integration tests for security features"""
    
    def test_full_security_stack(self):
        """Test all security features working together"""
        app = FastAPI()
        setup_security(app, **SecurityPresets.production())
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        # Should succeed with all security features enabled
        assert response.status_code == 200
        
        # Should have security headers
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers
        
        # Should have rate limit headers
        # Note: Rate limit headers may not be present in test client
    
    def test_sql_injection_prevention(self):
        """Test SQL injection is prevented"""
        app = FastAPI()
        setup_security(app, **SecurityPresets.production())
        
        @app.get("/search")
        async def search(q: str):
            return {"query": q}
        
        client = TestClient(app)
        
        # SQL injection attempt should be blocked
        response = client.get("/search?q=SELECT * FROM users")
        assert response.status_code == 400  # Bad Request


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
