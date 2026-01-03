"""
Task 37: Security Layer
=======================
Theme Security Manager für XSS-Schutz und Validierung.
"""

import re
import html
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SecurityReport:
    """Security validation report."""
    is_safe: bool
    issues: List[str]
    sanitized_data: Optional[Dict]


class ThemeSecurityManager:
    """Security manager for theme data."""
    
    # Allowed CSS properties
    ALLOWED_CSS_PROPERTIES = {
        'color', 'background-color', 'background', 'border-color',
        'border-radius', 'font-family', 'font-size', 'font-weight',
        'padding', 'margin', 'width', 'height', 'display', 'flex',
        'grid', 'gap', 'opacity', 'transition', 'transform',
        'box-shadow', 'text-align', 'line-height', 'letter-spacing'
    }
    
    # Dangerous patterns
    DANGEROUS_PATTERNS = [
        r'javascript:',
        r'data:text/html',
        r'expression\s*\(',
        r'url\s*\(\s*["\']?\s*javascript:',
        r'<script',
        r'</script>',
        r'on\w+\s*=',
        r'@import',
        r'behavior:',
        r'-moz-binding:',
    ]
    
    # Valid color patterns
    COLOR_PATTERNS = [
        r'^#[0-9a-fA-F]{3}$',
        r'^#[0-9a-fA-F]{6}$',
        r'^#[0-9a-fA-F]{8}$',
        r'^rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)$',
        r'^rgba\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*[\d.]+\s*\)$',
        r'^hsl\(\s*\d{1,3}\s*,\s*\d{1,3}%\s*,\s*\d{1,3}%\s*\)$',
    ]
    
    def __init__(self, themes_dir: str = "themes"):
        self.themes_dir = themes_dir
        self.allowed_users: List[str] = []
    
    def sanitize_string(self, value: str) -> str:
        """Sanitize a string value against XSS."""
        # HTML escape
        sanitized = html.escape(value)
        
        # Remove dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def validate_color(self, color: str) -> bool:
        """Validate a color value."""
        for pattern in self.COLOR_PATTERNS:
            if re.match(pattern, color):
                return True
        return False
    
    def sanitize_theme(self, theme: Dict) -> Tuple[Dict, List[str]]:
        """Sanitize theme data and return issues found."""
        issues = []
        sanitized = {}
        
        # Sanitize name
        if "name" in theme:
            sanitized["name"] = self.sanitize_string(str(theme["name"]))
        
        # Sanitize display name
        if "displayName" in theme:
            sanitized["displayName"] = self.sanitize_string(str(theme["displayName"]))
        
        # Validate and sanitize colors
        if "colors" in theme:
            sanitized["colors"] = {}
            for key, value in theme["colors"].items():
                safe_key = self.sanitize_string(str(key))
                if self.validate_color(str(value)):
                    sanitized["colors"][safe_key] = value
                else:
                    issues.append(f"Invalid color value for {key}: {value}")
                    sanitized["colors"][safe_key] = "#000000"  # Default fallback
        
        # Sanitize typography
        if "typography" in theme:
            sanitized["typography"] = {}
            typo = theme["typography"]
            
            if "fontFamily" in typo:
                # Only allow safe font families
                font = str(typo["fontFamily"])
                if not any(p in font.lower() for p in ['javascript', 'expression', '<']):
                    sanitized["typography"]["fontFamily"] = font
                else:
                    issues.append(f"Unsafe font family: {font}")
                    sanitized["typography"]["fontFamily"] = "sans-serif"
            
            if "fontSize" in typo:
                sanitized["typography"]["fontSize"] = {}
                for key, value in typo["fontSize"].items():
                    safe_key = self.sanitize_string(str(key))
                    # Validate font size format
                    if re.match(r'^[\d.]+(?:px|rem|em|%)$', str(value)):
                        sanitized["typography"]["fontSize"][safe_key] = value
                    else:
                        issues.append(f"Invalid font size: {value}")
        
        # Copy other safe properties
        for key in ["spacing", "borderRadius"]:
            if key in theme:
                sanitized[key] = {}
                for k, v in theme[key].items():
                    safe_key = self.sanitize_string(str(k))
                    if re.match(r'^[\d.]+(?:px|rem|em|%)$', str(v)):
                        sanitized[key][safe_key] = v
        
        return sanitized, issues
    
    def validate_theme_upload(self, theme: Dict, user_id: str) -> SecurityReport:
        """Validate a theme upload."""
        issues = []
        
        # Check user authorization
        if self.allowed_users and user_id not in self.allowed_users:
            issues.append(f"User {user_id} not authorized for theme uploads")
            return SecurityReport(is_safe=False, issues=issues, sanitized_data=None)
        
        # Check for dangerous content
        theme_str = str(theme)
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, theme_str, re.IGNORECASE):
                issues.append(f"Dangerous pattern detected: {pattern}")
        
        # Sanitize theme
        sanitized, sanitize_issues = self.sanitize_theme(theme)
        issues.extend(sanitize_issues)
        
        is_safe = len([i for i in issues if "Dangerous" in i]) == 0
        
        return SecurityReport(
            is_safe=is_safe,
            issues=issues,
            sanitized_data=sanitized if is_safe else None
        )
    
    def get_safe_theme_path(self, theme_name: str) -> str:
        """Get safe file path for theme storage."""
        # Sanitize theme name for file system
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '', theme_name)
        if not safe_name:
            safe_name = "unnamed_theme"
        
        # Ensure path is within themes directory
        full_path = os.path.join(self.themes_dir, f"{safe_name}.json")
        abs_path = os.path.abspath(full_path)
        abs_themes_dir = os.path.abspath(self.themes_dir)
        
        if not abs_path.startswith(abs_themes_dir):
            raise ValueError("Path traversal attempt detected")
        
        return full_path
    
    def add_authorized_user(self, user_id: str):
        """Add user to authorized uploaders."""
        if user_id not in self.allowed_users:
            self.allowed_users.append(user_id)
    
    def remove_authorized_user(self, user_id: str):
        """Remove user from authorized uploaders."""
        if user_id in self.allowed_users:
            self.allowed_users.remove(user_id)
    
    def generate_csp_header(self) -> str:
        """Generate Content-Security-Policy header."""
        return (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )


# Global instance
security_manager = ThemeSecurityManager()


def sanitize_theme(theme: Dict) -> Dict:
    """Sanitize theme data."""
    sanitized, _ = security_manager.sanitize_theme(theme)
    return sanitized


def validate_upload(theme: Dict, user_id: str) -> SecurityReport:
    """Validate theme upload."""
    return security_manager.validate_theme_upload(theme, user_id)
