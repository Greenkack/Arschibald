"""
Task 35: Export und Sharing
===========================
Theme-Export als JSON/CSS und Sharing-Funktionen.
"""

import json
import base64
from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class ThemeVersion:
    """Theme version information."""
    version: str
    created_at: str
    author: str
    description: str


class ThemeExporter:
    """Export themes in various formats."""
    
    @staticmethod
    def export_as_json(theme: Dict, pretty: bool = True) -> str:
        """Export theme as JSON string."""
        if pretty:
            return json.dumps(theme, indent=2, ensure_ascii=False)
        return json.dumps(theme, ensure_ascii=False)
    
    @staticmethod
    def export_as_css(theme: Dict) -> str:
        """Export theme as CSS variables."""
        css_lines = [":root {"]
        
        # Colors
        if "colors" in theme:
            for name, value in theme["colors"].items():
                css_lines.append(f"  --{name}: {value};")
        
        # Typography
        if "typography" in theme:
            typo = theme["typography"]
            if "fontFamily" in typo:
                css_lines.append(f"  --font-family: {typo['fontFamily']};")
            if "fontSize" in typo:
                for size_name, size_value in typo["fontSize"].items():
                    css_lines.append(f"  --font-size-{size_name}: {size_value};")
        
        # Spacing
        if "spacing" in theme:
            for name, value in theme["spacing"].items():
                css_lines.append(f"  --spacing-{name}: {value};")
        
        # Border Radius
        if "borderRadius" in theme:
            for name, value in theme["borderRadius"].items():
                css_lines.append(f"  --radius-{name}: {value};")
        
        css_lines.append("}")
        return "\n".join(css_lines)
    
    @staticmethod
    def export_as_scss(theme: Dict) -> str:
        """Export theme as SCSS variables."""
        scss_lines = ["// Theme Variables"]
        
        if "colors" in theme:
            scss_lines.append("\n// Colors")
            for name, value in theme["colors"].items():
                scss_lines.append(f"${name}: {value};")
        
        if "typography" in theme:
            scss_lines.append("\n// Typography")
            typo = theme["typography"]
            if "fontFamily" in typo:
                scss_lines.append(f"$font-family: {typo['fontFamily']};")
        
        return "\n".join(scss_lines)


class ThemeImporter:
    """Import themes from various formats."""
    
    @staticmethod
    def import_from_json(json_str: str) -> Dict:
        """Import theme from JSON string."""
        return json.loads(json_str)
    
    @staticmethod
    def import_from_file(file_path: str) -> Dict:
        """Import theme from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def validate_theme(theme: Dict) -> bool:
        """Validate imported theme structure."""
        required_keys = ["name", "colors"]
        return all(key in theme for key in required_keys)


class ThemeSharing:
    """Share themes via URL."""
    
    @staticmethod
    def encode_theme_url(theme: Dict) -> str:
        """Encode theme as URL-safe string."""
        json_str = json.dumps(theme, separators=(',', ':'))
        encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
        return f"?theme={encoded}"
    
    @staticmethod
    def decode_theme_url(url_param: str) -> Dict:
        """Decode theme from URL parameter."""
        decoded = base64.urlsafe_b64decode(url_param.encode()).decode()
        return json.loads(decoded)
    
    @staticmethod
    def create_share_link(base_url: str, theme: Dict) -> str:
        """Create shareable link for theme."""
        encoded = ThemeSharing.encode_theme_url(theme)
        return f"{base_url}{encoded}"


class ThemeVersioning:
    """Theme version management."""
    
    def __init__(self):
        self.versions: Dict[str, list] = {}
    
    def add_version(self, theme_name: str, theme: Dict, 
                    version: str, author: str = "Unknown",
                    description: str = "") -> ThemeVersion:
        """Add a new version of a theme."""
        version_info = ThemeVersion(
            version=version,
            created_at=datetime.now().isoformat(),
            author=author,
            description=description
        )
        
        if theme_name not in self.versions:
            self.versions[theme_name] = []
        
        self.versions[theme_name].append({
            "version_info": asdict(version_info),
            "theme": theme
        })
        
        return version_info
    
    def get_version(self, theme_name: str, version: str) -> Optional[Dict]:
        """Get a specific version of a theme."""
        if theme_name not in self.versions:
            return None
        
        for v in self.versions[theme_name]:
            if v["version_info"]["version"] == version:
                return v["theme"]
        return None
    
    def get_latest_version(self, theme_name: str) -> Optional[Dict]:
        """Get the latest version of a theme."""
        if theme_name not in self.versions or not self.versions[theme_name]:
            return None
        return self.versions[theme_name][-1]["theme"]
    
    def list_versions(self, theme_name: str) -> list:
        """List all versions of a theme."""
        if theme_name not in self.versions:
            return []
        return [v["version_info"] for v in self.versions[theme_name]]


# Convenience functions
exporter = ThemeExporter()
importer = ThemeImporter()
sharing = ThemeSharing()
versioning = ThemeVersioning()


def export_theme_json(theme: Dict) -> str:
    """Export theme as JSON."""
    return exporter.export_as_json(theme)


def export_theme_css(theme: Dict) -> str:
    """Export theme as CSS."""
    return exporter.export_as_css(theme)


def import_theme_json(json_str: str) -> Dict:
    """Import theme from JSON."""
    return importer.import_from_json(json_str)


def create_share_link(theme: Dict, base_url: str = "https://app.example.com") -> str:
    """Create shareable link."""
    return sharing.create_share_link(base_url, theme)
