"""
Security Scanner for Solar Calculator Pro
Automated security vulnerability scanning tool
"""
import requests
import json
import time
import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from urllib.parse import quote, urljoin
import hashlib


class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class SecurityFinding:
    """Security finding data structure"""
    title: str
    severity: Severity
    description: str
    endpoint: str
    evidence: str
    recommendation: str
    cwe_id: str = ""
    owasp_category: str = ""


class SecurityScanner:
    """Automated security scanner"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.findings: List[SecurityFinding] = []
        self.session = requests.Session()
        self.session.timeout = 10
        
    def scan_all(self) -> List[SecurityFinding]:
        """Run all security scans"""
        print("Starting comprehensive security scan...")
        
        self.scan_authentication()
        self.scan_injection_vulnerabilities()
        self.scan_xss_vulnerabilities()
        self.scan_security_headers()
        self.scan_information_disclosure()
        self.scan_access_control()
        self.scan_session_management()
        self.scan_api_security()
        
        return self.findings
        
    def scan_authentication(self):
        """Scan authentication mechanisms"""
        print("Scanning authentication...")
        
        # Test for default credentials
        default_creds = [
            ("admin", "admin"),
            ("admin", "password"),
            ("admin", "123456"),
            ("test", "test"),
            ("user", "user"),
            ("root", "root"),
        ]
        
        for username, password in default_creds:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                self.findings.append(SecurityFinding(
                    title="Default Credentials Accepted",
                    severity=Severity.CRITICAL,
                    description=f"Default credentials {username}:{password} were accepted",
                    endpoint="/api/v1/auth/login",
                    evidence=f"Login successful with {username}:{password}",
                    recommendation="Remove default accounts and enforce strong passwords",
                    cwe_id="CWE-798",
                    owasp_category="A07:2021 - Identification and Authentication Failures"
                ))
                
        # Test for username enumeration
        valid_user_response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"username": "admin@example.com", "password": "wrongpassword"}
        )
        invalid_user_response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            json={"username": "nonexistent@example.com", "password": "wrongpassword"}
        )
        
        if valid_user_response.text != invalid_user_response.text:
            # Different responses might indicate username enumeration
            if "user not found" in invalid_user_response.text.lower() or \
               "invalid username" in invalid_user_response.text.lower():
                self.findings.append(SecurityFinding(
                    title="Username Enumeration Possible",
                    severity=Severity.MEDIUM,
                    description="Different error messages for valid/invalid usernames",
                    endpoint="/api/v1/auth/login",
                    evidence="Response differs based on username validity",
                    recommendation="Use generic error messages for authentication failures",
                    cwe_id="CWE-204",
                    owasp_category="A07:2021 - Identification and Authentication Failures"
                ))
                
    def scan_injection_vulnerabilities(self):
        """Scan for injection vulnerabilities"""
        print("Scanning for injection vulnerabilities...")
        
        # SQL Injection payloads
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1 UNION SELECT * FROM users",
            "' AND SLEEP(5)--",
        ]
        
        # Test endpoints
        test_endpoints = [
            ("/api/v1/database/products", "search"),
            ("/api/v1/database/customers", "search"),
            ("/api/v1/crm/leads", "search"),
        ]
        
        for endpoint, param in test_endpoints:
            for payload in sql_payloads:
                start_time = time.time()
                try:
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        params={param: payload}
                    )
                    elapsed = time.time() - start_time
                    
                    # Check for SQL error messages
                    error_indicators = [
                        "sql syntax",
                        "mysql",
                        "sqlite",
                        "postgresql",
                        "ora-",
                        "syntax error",
                    ]
                    
                    response_lower = response.text.lower()
                    for indicator in error_indicators:
                        if indicator in response_lower:
                            self.findings.append(SecurityFinding(
                                title="SQL Injection Vulnerability",
                                severity=Severity.CRITICAL,
                                description=f"SQL error message exposed with payload: {payload[:30]}...",
                                endpoint=endpoint,
                                evidence=f"Response contains: {indicator}",
                                recommendation="Use parameterized queries and input validation",
                                cwe_id="CWE-89",
                                owasp_category="A03:2021 - Injection"
                            ))
                            break
                            
                    # Check for time-based injection
                    if elapsed > 4 and "SLEEP" in payload:
                        self.findings.append(SecurityFinding(
                            title="Time-Based SQL Injection",
                            severity=Severity.CRITICAL,
                            description=f"Response delayed by {elapsed:.2f}s with SLEEP payload",
                            endpoint=endpoint,
                            evidence=f"Payload: {payload}",
                            recommendation="Use parameterized queries",
                            cwe_id="CWE-89",
                            owasp_category="A03:2021 - Injection"
                        ))
                        
                except Exception as e:
                    pass
                    
        # Command Injection payloads
        cmd_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "`whoami`",
            "$(id)",
        ]
        
        for payload in cmd_payloads:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/v1/system/info",
                    params={"cmd": payload}
                )
                
                if "root:" in response.text or "uid=" in response.text:
                    self.findings.append(SecurityFinding(
                        title="Command Injection Vulnerability",
                        severity=Severity.CRITICAL,
                        description="System command execution detected",
                        endpoint="/api/v1/system/info",
                        evidence=f"Payload: {payload}",
                        recommendation="Never pass user input to system commands",
                        cwe_id="CWE-78",
                        owasp_category="A03:2021 - Injection"
                    ))
            except:
                pass
                
    def scan_xss_vulnerabilities(self):
        """Scan for XSS vulnerabilities"""
        print("Scanning for XSS vulnerabilities...")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
        ]
        
        # Test reflection in responses
        test_endpoints = [
            ("/api/v1/database/products", "search"),
            ("/api/v1/database/customers", "name"),
        ]
        
        for endpoint, param in test_endpoints:
            for payload in xss_payloads:
                try:
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        params={param: payload}
                    )
                    
                    # Check if payload is reflected without encoding
                    if payload in response.text:
                        self.findings.append(SecurityFinding(
                            title="Reflected XSS Vulnerability",
                            severity=Severity.HIGH,
                            description=f"XSS payload reflected in response",
                            endpoint=endpoint,
                            evidence=f"Payload: {payload[:30]}...",
                            recommendation="Encode all output and use Content-Security-Policy",
                            cwe_id="CWE-79",
                            owasp_category="A03:2021 - Injection"
                        ))
                except:
                    pass
                    
    def scan_security_headers(self):
        """Scan for missing security headers"""
        print("Scanning security headers...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health")
            headers = response.headers
            
            required_headers = {
                "X-Content-Type-Options": ("nosniff", Severity.MEDIUM),
                "X-Frame-Options": (["DENY", "SAMEORIGIN"], Severity.MEDIUM),
                "X-XSS-Protection": ("1; mode=block", Severity.LOW),
                "Strict-Transport-Security": (None, Severity.MEDIUM),
                "Content-Security-Policy": (None, Severity.MEDIUM),
                "Referrer-Policy": (None, Severity.LOW),
            }
            
            for header, (expected, severity) in required_headers.items():
                value = headers.get(header)
                
                if not value:
                    self.findings.append(SecurityFinding(
                        title=f"Missing Security Header: {header}",
                        severity=severity,
                        description=f"The {header} header is not set",
                        endpoint="/api/v1/health",
                        evidence=f"Header not present in response",
                        recommendation=f"Add {header} header to all responses",
                        cwe_id="CWE-693",
                        owasp_category="A05:2021 - Security Misconfiguration"
                    ))
                elif expected and isinstance(expected, str) and value != expected:
                    self.findings.append(SecurityFinding(
                        title=f"Incorrect Security Header: {header}",
                        severity=Severity.LOW,
                        description=f"Header value '{value}' differs from recommended '{expected}'",
                        endpoint="/api/v1/health",
                        evidence=f"Current value: {value}",
                        recommendation=f"Set {header} to '{expected}'",
                        cwe_id="CWE-693",
                        owasp_category="A05:2021 - Security Misconfiguration"
                    ))
        except:
            pass
            
    def scan_information_disclosure(self):
        """Scan for information disclosure"""
        print("Scanning for information disclosure...")
        
        # Check for verbose error messages
        error_endpoints = [
            "/api/v1/nonexistent",
            "/api/v1/database/products/invalid-id",
            "/api/v1/auth/login",
        ]
        
        for endpoint in error_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_lower = response.text.lower()
                
                # Check for stack traces
                if "traceback" in response_lower or "file \"" in response_lower:
                    self.findings.append(SecurityFinding(
                        title="Stack Trace Disclosure",
                        severity=Severity.MEDIUM,
                        description="Stack trace exposed in error response",
                        endpoint=endpoint,
                        evidence="Response contains traceback information",
                        recommendation="Disable debug mode and use generic error messages",
                        cwe_id="CWE-209",
                        owasp_category="A05:2021 - Security Misconfiguration"
                    ))
                    
                # Check for version disclosure
                version_patterns = [
                    r"python/\d+\.\d+",
                    r"fastapi/\d+\.\d+",
                    r"uvicorn/\d+\.\d+",
                ]
                
                for pattern in version_patterns:
                    if re.search(pattern, response_lower):
                        self.findings.append(SecurityFinding(
                            title="Version Information Disclosure",
                            severity=Severity.LOW,
                            description="Software version exposed in response",
                            endpoint=endpoint,
                            evidence=f"Pattern matched: {pattern}",
                            recommendation="Remove version information from responses",
                            cwe_id="CWE-200",
                            owasp_category="A05:2021 - Security Misconfiguration"
                        ))
            except:
                pass
                
        # Check Server header
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health")
            server = response.headers.get("Server", "")
            
            if server and any(x in server.lower() for x in ["python", "uvicorn", "gunicorn"]):
                self.findings.append(SecurityFinding(
                    title="Server Header Information Disclosure",
                    severity=Severity.LOW,
                    description=f"Server header reveals: {server}",
                    endpoint="/api/v1/health",
                    evidence=f"Server: {server}",
                    recommendation="Remove or obfuscate Server header",
                    cwe_id="CWE-200",
                    owasp_category="A05:2021 - Security Misconfiguration"
                ))
        except:
            pass
            
    def scan_access_control(self):
        """Scan for access control issues"""
        print("Scanning access control...")
        
        # Test for IDOR (Insecure Direct Object Reference)
        idor_endpoints = [
            "/api/v1/users/{id}/profile",
            "/api/v1/database/customers/{id}",
            "/api/v1/projects/{id}",
        ]
        
        for endpoint_template in idor_endpoints:
            # Try accessing different IDs
            for test_id in [1, 2, 999, "admin"]:
                endpoint = endpoint_template.replace("{id}", str(test_id))
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    
                    # If we get data without authentication, it's a problem
                    if response.status_code == 200:
                        self.findings.append(SecurityFinding(
                            title="Potential IDOR Vulnerability",
                            severity=Severity.HIGH,
                            description=f"Resource accessible without proper authorization",
                            endpoint=endpoint,
                            evidence=f"Status code: {response.status_code}",
                            recommendation="Implement proper authorization checks",
                            cwe_id="CWE-639",
                            owasp_category="A01:2021 - Broken Access Control"
                        ))
                        break
                except:
                    pass
                    
        # Test admin endpoints without auth
        admin_endpoints = [
            "/api/v1/admin/users",
            "/api/v1/admin/settings",
            "/api/v1/admin/logs",
            "/admin",
            "/api/v1/database/backup",
        ]
        
        for endpoint in admin_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    self.findings.append(SecurityFinding(
                        title="Admin Endpoint Accessible Without Auth",
                        severity=Severity.CRITICAL,
                        description=f"Admin endpoint accessible without authentication",
                        endpoint=endpoint,
                        evidence=f"Status code: {response.status_code}",
                        recommendation="Require authentication and admin role",
                        cwe_id="CWE-306",
                        owasp_category="A01:2021 - Broken Access Control"
                    ))
            except:
                pass
                
    def scan_session_management(self):
        """Scan session management"""
        print("Scanning session management...")
        
        # Check for session cookies security
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": "test@example.com", "password": "test"}
            )
            
            for cookie in response.cookies:
                # Check Secure flag
                if not cookie.secure:
                    self.findings.append(SecurityFinding(
                        title="Cookie Missing Secure Flag",
                        severity=Severity.MEDIUM,
                        description=f"Cookie '{cookie.name}' missing Secure flag",
                        endpoint="/api/v1/auth/login",
                        evidence=f"Cookie: {cookie.name}",
                        recommendation="Set Secure flag on all cookies",
                        cwe_id="CWE-614",
                        owasp_category="A07:2021 - Identification and Authentication Failures"
                    ))
                    
                # Check HttpOnly flag
                if not cookie.has_nonstandard_attr("HttpOnly"):
                    self.findings.append(SecurityFinding(
                        title="Cookie Missing HttpOnly Flag",
                        severity=Severity.MEDIUM,
                        description=f"Cookie '{cookie.name}' missing HttpOnly flag",
                        endpoint="/api/v1/auth/login",
                        evidence=f"Cookie: {cookie.name}",
                        recommendation="Set HttpOnly flag on session cookies",
                        cwe_id="CWE-1004",
                        owasp_category="A07:2021 - Identification and Authentication Failures"
                    ))
        except:
            pass
            
    def scan_api_security(self):
        """Scan API-specific security issues"""
        print("Scanning API security...")
        
        # Check for rate limiting
        print("  Testing rate limiting...")
        rate_limit_detected = False
        
        for i in range(50):
            try:
                response = self.session.get(f"{self.base_url}/api/v1/health")
                if response.status_code == 429:
                    rate_limit_detected = True
                    break
            except:
                pass
                
        if not rate_limit_detected:
            self.findings.append(SecurityFinding(
                title="No Rate Limiting Detected",
                severity=Severity.MEDIUM,
                description="API does not appear to implement rate limiting",
                endpoint="/api/v1/health",
                evidence="50 requests completed without rate limiting",
                recommendation="Implement rate limiting to prevent abuse",
                cwe_id="CWE-770",
                owasp_category="A05:2021 - Security Misconfiguration"
            ))
            
        # Check for CORS misconfiguration
        try:
            response = self.session.options(
                f"{self.base_url}/api/v1/health",
                headers={"Origin": "http://evil-site.com"}
            )
            
            cors_origin = response.headers.get("Access-Control-Allow-Origin", "")
            
            if cors_origin == "*":
                self.findings.append(SecurityFinding(
                    title="Overly Permissive CORS",
                    severity=Severity.MEDIUM,
                    description="CORS allows all origins (*)",
                    endpoint="/api/v1/health",
                    evidence=f"Access-Control-Allow-Origin: {cors_origin}",
                    recommendation="Restrict CORS to specific trusted origins",
                    cwe_id="CWE-942",
                    owasp_category="A05:2021 - Security Misconfiguration"
                ))
            elif cors_origin == "http://evil-site.com":
                self.findings.append(SecurityFinding(
                    title="CORS Reflects Origin",
                    severity=Severity.HIGH,
                    description="CORS reflects arbitrary Origin header",
                    endpoint="/api/v1/health",
                    evidence=f"Reflected origin: {cors_origin}",
                    recommendation="Validate Origin against whitelist",
                    cwe_id="CWE-942",
                    owasp_category="A05:2021 - Security Misconfiguration"
                ))
        except:
            pass
            
    def generate_report(self) -> str:
        """Generate security scan report"""
        report = f"""
# Security Scan Report - Solar Calculator Pro

**Scan Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Target**: {self.base_url}
**Total Findings**: {len(self.findings)}

## Summary by Severity

- CRITICAL: {sum(1 for f in self.findings if f.severity == Severity.CRITICAL)}
- HIGH: {sum(1 for f in self.findings if f.severity == Severity.HIGH)}
- MEDIUM: {sum(1 for f in self.findings if f.severity == Severity.MEDIUM)}
- LOW: {sum(1 for f in self.findings if f.severity == Severity.LOW)}
- INFO: {sum(1 for f in self.findings if f.severity == Severity.INFO)}

## Detailed Findings

"""
        # Sort by severity
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4
        }
        
        sorted_findings = sorted(self.findings, key=lambda f: severity_order[f.severity])
        
        for i, finding in enumerate(sorted_findings, 1):
            report += f"""
### {i}. [{finding.severity.value}] {finding.title}

**Endpoint**: `{finding.endpoint}`
**CWE**: {finding.cwe_id}
**OWASP**: {finding.owasp_category}

**Description**: {finding.description}

**Evidence**: {finding.evidence}

**Recommendation**: {finding.recommendation}

---
"""
        
        report += """
## Remediation Priority

1. Address all CRITICAL findings immediately
2. Fix HIGH severity issues within 1 week
3. Resolve MEDIUM issues within 1 month
4. Address LOW issues in next release cycle

## Next Steps

1. Review and validate each finding
2. Create remediation tickets
3. Implement fixes
4. Re-scan to verify fixes
5. Schedule regular security scans
"""
        
        return report


if __name__ == "__main__":
    scanner = SecurityScanner()
    findings = scanner.scan_all()
    
    report = scanner.generate_report()
    print(report)
    
    # Save report
    with open("security_scan_report.md", "w") as f:
        f.write(report)
    
    print(f"\nScan complete. Found {len(findings)} issues.")
    print("Report saved to security_scan_report.md")
