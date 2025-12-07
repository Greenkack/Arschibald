"""
Theme Validation System

Dieses Modul implementiert ein umfassendes Validierungssystem für Theme-Dateien.
Es validiert Theme-Struktur, Farb-Werte, Typography und füllt fehlende Properties
mit Defaults auf.
"""

import json
import re
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import copy


# JSON Schema für Theme-Struktur
THEME_SCHEMA = {
    "type": "object",
    "required": ["name", "display_name", "colors", "typography"],
    "properties": {
        "name": {
            "type": "string",
            "pattern": "^[a-z0-9-]+$",
            "description": "Theme-Name (nur Kleinbuchstaben, Zahlen und Bindestriche)"
        },
        "display_name": {
            "type": "string",
            "description": "Anzeigename des Themes"
        },
        "colors": {
            "type": "object",
            "required": ["background", "foreground", "primary"],
            "properties": {
                "background": {"type": "string"},
                "foreground": {"type": "string"},
                "primary": {"type": "string"},
                "primary_foreground": {"type": "string"},
                "secondary": {"type": "string"},
                "secondary_foreground": {"type": "string"},
                "accent": {"type": "string"},
                "accent_foreground": {"type": "string"},
                "success": {"type": "string"},
                "warning": {"type": "string"},
                "error": {"type": "string"},
                "info": {"type": "string"},
                "muted": {"type": "string"},
                "muted_foreground": {"type": "string"},
                "border": {"type": "string"},
                "input": {"type": "string"},
                "ring": {"type": "string"},
                "chart_1": {"type": "string"},
                "chart_2": {"type": "string"},
                "chart_3": {"type": "string"},
                "chart_4": {"type": "string"},
                "chart_5": {"type": "string"}
            }
        },
        "typography": {
            "type": "object",
            "required": ["font_family", "font_size_base"],
            "properties": {
                "font_family": {"type": "string"},
                "font_family_mono": {"type": "string"},
                "font_size_xs": {"type": "string"},
                "font_size_sm": {"type": "string"},
                "font_size_base": {"type": "string"},
                "font_size_lg": {"type": "string"},
                "font_size_xl": {"type": "string"},
                "font_size_2xl": {"type": "string"},
                "font_weight_normal": {"type": "integer"},
                "font_weight_medium": {"type": "integer"},
                "font_weight_semibold": {"type": "integer"},
                "font_weight_bold": {"type": "integer"},
                "line_height_tight": {"type": "number"},
                "line_height_normal": {"type": "number"},
                "line_height_relaxed": {"type": "number"}
            }
        },
        "spacing": {
            "type": "object",
            "properties": {
                "spacing_0": {"type": "string"},
                "spacing_1": {"type": "string"},
                "spacing_2": {"type": "string"},
                "spacing_3": {"type": "string"},
                "spacing_4": {"type": "string"},
                "spacing_6": {"type": "string"},
                "spacing_8": {"type": "string"},
                "spacing_12": {"type": "string"},
                "spacing_16": {"type": "string"}
            }
        },
        "shadows": {
            "type": "object",
            "properties": {
                "shadow_sm": {"type": "string"},
                "shadow_md": {"type": "string"},
                "shadow_lg": {"type": "string"},
                "shadow_xl": {"type": "string"}
            }
        },
        "borders": {
            "type": "object",
            "properties": {
                "border_width": {"type": "string"},
                "border_radius_sm": {"type": "string"},
                "border_radius_md": {"type": "string"},
                "border_radius_lg": {"type": "string"},
                "border_radius_full": {"type": "string"}
            }
        },
        "animations": {
            "type": "object",
            "properties": {
                "transition_fast": {"type": "string"},
                "transition_base": {"type": "string"},
                "transition_slow": {"type": "string"},
                "easing_default": {"type": "string"}
            }
        }
    }
}


# Default-Werte für fehlende Properties
DEFAULT_THEME_VALUES = {
    "colors": {
        "background": "#ffffff",
        "foreground": "#0a0a0a",
        "primary": "#18181b",
        "primary_foreground": "#fafafa",
        "secondary": "#f4f4f5",
        "secondary_foreground": "#18181b",
        "accent": "#f4f4f5",
        "accent_foreground": "#18181b",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#3b82f6",
        "muted": "#f4f4f5",
        "muted_foreground": "#71717a",
        "border": "#e4e4e7",
        "input": "#e4e4e7",
        "ring": "#18181b",
        "chart_1": "#38bdf8",
        "chart_2": "#34d399",
        "chart_3": "#f87171",
        "chart_4": "#fbbf24",
        "chart_5": "#a78bfa"
    },
    "typography": {
        "font_family": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "font_family_mono": "'Fira Code', 'Courier New', monospace",
        "font_size_xs": "0.75rem",
        "font_size_sm": "0.875rem",
        "font_size_base": "1rem",
        "font_size_lg": "1.125rem",
        "font_size_xl": "1.25rem",
        "font_size_2xl": "1.5rem",
        "font_weight_normal": 400,
        "font_weight_medium": 500,
        "font_weight_semibold": 600,
        "font_weight_bold": 700,
        "line_height_tight": 1.25,
        "line_height_normal": 1.5,
        "line_height_relaxed": 1.75
    },
    "spacing": {
        "spacing_0": "0",
        "spacing_1": "0.25rem",
        "spacing_2": "0.5rem",
        "spacing_3": "0.75rem",
        "spacing_4": "1rem",
        "spacing_6": "1.5rem",
        "spacing_8": "2rem",
        "spacing_12": "3rem",
        "spacing_16": "4rem"
    },
    "shadows": {
        "shadow_sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        "shadow_md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
        "shadow_lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
        "shadow_xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1)"
    },
    "borders": {
        "border_width": "1px",
        "border_radius_sm": "0.25rem",
        "border_radius_md": "0.375rem",
        "border_radius_lg": "0.5rem",
        "border_radius_full": "9999px"
    },
    "animations": {
        "transition_fast": "150ms cubic-bezier(0.4, 0, 0.2, 1)",
        "transition_base": "200ms cubic-bezier(0.4, 0, 0.2, 1)",
        "transition_slow": "300ms cubic-bezier(0.4, 0, 0.2, 1)",
        "easing_default": "cubic-bezier(0.4, 0, 0.2, 1)"
    }
}


@dataclass
class ValidationError:
    """Repräsentiert einen Validierungs-Fehler"""
    field: str
    message: str
    severity: str  # 'error', 'warning', 'info'
    value: Optional[Any] = None
    
    def __str__(self) -> str:
        severity_emoji = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        emoji = severity_emoji.get(self.severity, '•')
        
        if self.value is not None:
            return f"{emoji} {self.field}: {self.message} (Wert: {self.value})"
        return f"{emoji} {self.field}: {self.message}"


@dataclass
class ValidationResult:
    """Ergebnis einer Theme-Validierung"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]
    fixed_theme: Optional[Dict] = None
    
    def has_errors(self) -> bool:
        """Prüft ob kritische Fehler vorhanden sind"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Prüft ob Warnungen vorhanden sind"""
        return len(self.warnings) > 0
    
    def get_summary(self) -> str:
        """Gibt eine Zusammenfassung zurück"""
        lines = []
        
        if self.is_valid:
            lines.append("✅ Theme ist gültig!")
        else:
            lines.append("❌ Theme ist ungültig!")
        
        lines.append(f"\nFehler: {len(self.errors)}")
        lines.append(f"Warnungen: {len(self.warnings)}")
        lines.append(f"Hinweise: {len(self.info)}")
        
        return "\n".join(lines)
    
    def get_detailed_report(self) -> str:
        """Gibt einen detaillierten Report zurück"""
        lines = [self.get_summary(), ""]
        
        if self.errors:
            lines.append("FEHLER:")
            for error in self.errors:
                lines.append(f"  {error}")
            lines.append("")
        
        if self.warnings:
            lines.append("WARNUNGEN:")
            for warning in self.warnings:
                lines.append(f"  {warning}")
            lines.append("")
        
        if self.info:
            lines.append("HINWEISE:")
            for info_item in self.info:
                lines.append(f"  {info_item}")
        
        return "\n".join(lines)


class ThemeValidator:
    """
    Validiert Theme-Dateien gegen Schema und Regeln.
    
    Features:
    - JSON-Schema-Validierung
    - Farb-Validierung (Hex, RGB, RGBA)
    - Typography-Validierung
    - Automatisches Auffüllen fehlender Properties
    - Detaillierte Fehlerberichte
    """
    
    def __init__(self, schema: Dict = THEME_SCHEMA, defaults: Dict = DEFAULT_THEME_VALUES):
        self.schema = schema
        self.defaults = defaults
    
    def validate_theme(self, theme_data: Dict, fix_errors: bool = True) -> ValidationResult:
        """
        Validiert Theme-Daten.
        
        Args:
            theme_data: Theme-Daten als Dictionary
            fix_errors: Wenn True, werden fehlende Properties mit Defaults aufgefüllt
        
        Returns:
            ValidationResult mit allen Fehlern und Warnungen
        """
        errors = []
        warnings = []
        info = []
        
        # Kopie für Fixes erstellen
        fixed_theme = copy.deepcopy(theme_data) if fix_errors else None
        
        # 1. Schema-Validierung
        schema_errors = self._validate_schema(theme_data)
        errors.extend(schema_errors)
        
        # 2. Farb-Validierung
        color_errors, color_warnings = self._validate_colors(theme_data.get('colors', {}))
        errors.extend(color_errors)
        warnings.extend(color_warnings)
        
        # 3. Typography-Validierung
        typo_errors, typo_warnings = self._validate_typography(theme_data.get('typography', {}))
        errors.extend(typo_errors)
        warnings.extend(typo_warnings)
        
        # 4. Spacing-Validierung
        spacing_warnings = self._validate_spacing(theme_data.get('spacing', {}))
        warnings.extend(spacing_warnings)
        
        # 5. Shadows-Validierung
        shadow_warnings = self._validate_shadows(theme_data.get('shadows', {}))
        warnings.extend(shadow_warnings)
        
        # 6. Borders-Validierung
        border_warnings = self._validate_borders(theme_data.get('borders', {}))
        warnings.extend(border_warnings)
        
        # 7. Animations-Validierung
        animation_warnings = self._validate_animations(theme_data.get('animations', {}))
        warnings.extend(animation_warnings)
        
        # 8. Fehlende Properties auffüllen
        if fix_errors and fixed_theme:
            missing_props = self._fill_missing_properties(fixed_theme)
            for prop in missing_props:
                info.append(ValidationError(
                    field=prop,
                    message="Fehlende Property wurde mit Default-Wert aufgefüllt",
                    severity='info'
                ))
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            info=info,
            fixed_theme=fixed_theme
        )
    
    def validate_file(self, filepath: str, fix_errors: bool = True) -> ValidationResult:
        """
        Validiert Theme-Datei.
        
        Args:
            filepath: Pfad zur Theme-JSON-Datei
            fix_errors: Wenn True, werden fehlende Properties mit Defaults aufgefüllt
        
        Returns:
            ValidationResult
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            return self.validate_theme(theme_data, fix_errors)
        
        except FileNotFoundError:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(
                    field='file',
                    message=f"Datei nicht gefunden: {filepath}",
                    severity='error'
                )],
                warnings=[],
                info=[]
            )
        
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError(
                    field='json',
                    message=f"Ungültiges JSON-Format: {e}",
                    severity='error'
                )],
                warnings=[],
                info=[]
            )
    
    def _validate_schema(self, theme_data: Dict) -> List[ValidationError]:
        """Validiert Theme gegen JSON-Schema"""
        errors = []
        
        # Prüfe required fields
        required = self.schema.get('required', [])
        for field in required:
            if field not in theme_data:
                errors.append(ValidationError(
                    field=field,
                    message="Pflichtfeld fehlt",
                    severity='error'
                ))
        
        # Prüfe name pattern
        if 'name' in theme_data:
            name = theme_data['name']
            pattern = self.schema['properties']['name']['pattern']
            if not re.match(pattern, name):
                errors.append(ValidationError(
                    field='name',
                    message="Name muss nur Kleinbuchstaben, Zahlen und Bindestriche enthalten",
                    severity='error',
                    value=name
                ))
        
        # Prüfe colors required fields
        if 'colors' in theme_data:
            colors_required = self.schema['properties']['colors'].get('required', [])
            for field in colors_required:
                if field not in theme_data['colors']:
                    errors.append(ValidationError(
                        field=f'colors.{field}',
                        message="Pflichtfeld fehlt",
                        severity='error'
                    ))
        
        # Prüfe typography required fields
        if 'typography' in theme_data:
            typo_required = self.schema['properties']['typography'].get('required', [])
            for field in typo_required:
                if field not in theme_data['typography']:
                    errors.append(ValidationError(
                        field=f'typography.{field}',
                        message="Pflichtfeld fehlt",
                        severity='error'
                    ))
        
        return errors
    
    def _validate_colors(self, colors: Dict) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validiert Farb-Werte"""
        errors = []
        warnings = []
        
        for key, value in colors.items():
            if not isinstance(value, str):
                errors.append(ValidationError(
                    field=f'colors.{key}',
                    message="Farbe muss ein String sein",
                    severity='error',
                    value=value
                ))
                continue
            
            if not self._is_valid_color(value):
                errors.append(ValidationError(
                    field=f'colors.{key}',
                    message="Ungültiges Farbformat (erwartet: Hex, RGB oder RGBA)",
                    severity='error',
                    value=value
                ))
            
            # Warnung bei sehr hellen/dunklen Farben
            if self._is_hex_color(value):
                if value.lower() in ['#ffffff', '#fff']:
                    warnings.append(ValidationError(
                        field=f'colors.{key}',
                        message="Rein weiße Farbe kann Kontrast-Probleme verursachen",
                        severity='warning',
                        value=value
                    ))
                elif value.lower() in ['#000000', '#000']:
                    warnings.append(ValidationError(
                        field=f'colors.{key}',
                        message="Rein schwarze Farbe kann Kontrast-Probleme verursachen",
                        severity='warning',
                        value=value
                    ))
        
        return errors, warnings
    
    def _validate_typography(self, typography: Dict) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validiert Typography-Werte"""
        errors = []
        warnings = []
        
        # Prüfe Font-Sizes
        for key, value in typography.items():
            if 'font_size' in key:
                if not isinstance(value, str):
                    errors.append(ValidationError(
                        field=f'typography.{key}',
                        message="Font-Size muss ein String sein",
                        severity='error',
                        value=value
                    ))
                    continue
                
                if not (value.endswith('rem') or value.endswith('px') or value.endswith('em')):
                    errors.append(ValidationError(
                        field=f'typography.{key}',
                        message="Font-Size muss mit 'rem', 'px' oder 'em' enden",
                        severity='error',
                        value=value
                    ))
                
                # Warnung bei sehr kleinen/großen Schriftgrößen
                if value.endswith('rem'):
                    try:
                        size = float(value.replace('rem', ''))
                        if size < 0.5:
                            warnings.append(ValidationError(
                                field=f'typography.{key}',
                                message="Sehr kleine Schriftgröße kann Lesbarkeit beeinträchtigen",
                                severity='warning',
                                value=value
                            ))
                        elif size > 3:
                            warnings.append(ValidationError(
                                field=f'typography.{key}',
                                message="Sehr große Schriftgröße kann Layout-Probleme verursachen",
                                severity='warning',
                                value=value
                            ))
                    except ValueError:
                        pass
            
            # Prüfe Font-Weights
            if 'font_weight' in key:
                if not isinstance(value, int):
                    errors.append(ValidationError(
                        field=f'typography.{key}',
                        message="Font-Weight muss eine Zahl sein",
                        severity='error',
                        value=value
                    ))
                elif value not in [100, 200, 300, 400, 500, 600, 700, 800, 900]:
                    warnings.append(ValidationError(
                        field=f'typography.{key}',
                        message="Font-Weight sollte ein Vielfaches von 100 sein (100-900)",
                        severity='warning',
                        value=value
                    ))
            
            # Prüfe Line-Heights
            if 'line_height' in key:
                if not isinstance(value, (int, float)):
                    errors.append(ValidationError(
                        field=f'typography.{key}',
                        message="Line-Height muss eine Zahl sein",
                        severity='error',
                        value=value
                    ))
                elif value < 1.0 or value > 3.0:
                    warnings.append(ValidationError(
                        field=f'typography.{key}',
                        message="Line-Height sollte zwischen 1.0 und 3.0 liegen",
                        severity='warning',
                        value=value
                    ))
        
        return errors, warnings
    
    def _validate_spacing(self, spacing: Dict) -> List[ValidationError]:
        """Validiert Spacing-Werte"""
        warnings = []
        
        for key, value in spacing.items():
            if not isinstance(value, str):
                warnings.append(ValidationError(
                    field=f'spacing.{key}',
                    message="Spacing-Wert sollte ein String sein",
                    severity='warning',
                    value=value
                ))
            elif not (value.endswith('rem') or value.endswith('px') or value == '0'):
                warnings.append(ValidationError(
                    field=f'spacing.{key}',
                    message="Spacing sollte mit 'rem' oder 'px' enden",
                    severity='warning',
                    value=value
                ))
        
        return warnings
    
    def _validate_shadows(self, shadows: Dict) -> List[ValidationError]:
        """Validiert Shadow-Werte"""
        warnings = []
        
        for key, value in shadows.items():
            if not isinstance(value, str):
                warnings.append(ValidationError(
                    field=f'shadows.{key}',
                    message="Shadow-Wert sollte ein String sein",
                    severity='warning',
                    value=value
                ))
            elif 'rgba' not in value and 'rgb' not in value:
                warnings.append(ValidationError(
                    field=f'shadows.{key}',
                    message="Shadow sollte rgba() oder rgb() verwenden",
                    severity='warning',
                    value=value
                ))
        
        return warnings
    
    def _validate_borders(self, borders: Dict) -> List[ValidationError]:
        """Validiert Border-Werte"""
        warnings = []
        
        for key, value in borders.items():
            if not isinstance(value, str):
                warnings.append(ValidationError(
                    field=f'borders.{key}',
                    message="Border-Wert sollte ein String sein",
                    severity='warning',
                    value=value
                ))
            elif 'border_radius' in key and not (value.endswith('rem') or value.endswith('px') or value.isdigit()):
                warnings.append(ValidationError(
                    field=f'borders.{key}',
                    message="Border-Radius sollte mit 'rem' oder 'px' enden",
                    severity='warning',
                    value=value
                ))
        
        return warnings
    
    def _validate_animations(self, animations: Dict) -> List[ValidationError]:
        """Validiert Animation-Werte"""
        warnings = []
        
        for key, value in animations.items():
            if not isinstance(value, str):
                warnings.append(ValidationError(
                    field=f'animations.{key}',
                    message="Animation-Wert sollte ein String sein",
                    severity='warning',
                    value=value
                ))
            elif 'transition' in key and 'ms' not in value and 's' not in value:
                warnings.append(ValidationError(
                    field=f'animations.{key}',
                    message="Transition sollte eine Zeitangabe enthalten (ms oder s)",
                    severity='warning',
                    value=value
                ))
        
        return warnings
    
    def _is_valid_color(self, color: str) -> bool:
        """Prüft ob Farbe gültig ist (Hex, RGB, RGBA)"""
        return (
            self._is_hex_color(color) or
            self._is_rgb_color(color) or
            self._is_rgba_color(color)
        )
    
    def _is_hex_color(self, color: str) -> bool:
        """Prüft ob Farbe ein gültiger Hex-Wert ist"""
        hex_pattern = r'^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$'
        return bool(re.match(hex_pattern, color))
    
    def _is_rgb_color(self, color: str) -> bool:
        """Prüft ob Farbe ein gültiger RGB-Wert ist"""
        rgb_pattern = r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$'
        return bool(re.match(rgb_pattern, color))
    
    def _is_rgba_color(self, color: str) -> bool:
        """Prüft ob Farbe ein gültiger RGBA-Wert ist"""
        rgba_pattern = r'^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)$'
        return bool(re.match(rgba_pattern, color))
    
    def _fill_missing_properties(self, theme_data: Dict) -> List[str]:
        """
        Füllt fehlende Properties mit Default-Werten auf.
        
        Returns:
            Liste der aufgefüllten Property-Namen
        """
        filled_props = []
        
        for section, defaults in self.defaults.items():
            if section not in theme_data:
                theme_data[section] = {}
            
            for key, default_value in defaults.items():
                if key not in theme_data[section]:
                    theme_data[section][key] = default_value
                    filled_props.append(f'{section}.{key}')
        
        return filled_props


def validate_theme_file(filepath: str, fix_errors: bool = True, save_fixed: bool = False) -> ValidationResult:
    """
    Convenience-Funktion zum Validieren einer Theme-Datei.
    
    Args:
        filepath: Pfad zur Theme-JSON-Datei
        fix_errors: Wenn True, werden fehlende Properties mit Defaults aufgefüllt
        save_fixed: Wenn True, wird das korrigierte Theme gespeichert
    
    Returns:
        ValidationResult
    """
    validator = ThemeValidator()
    result = validator.validate_file(filepath, fix_errors)
    
    if save_fixed and result.fixed_theme and not result.has_errors():
        # Speichere korrigiertes Theme
        fixed_path = filepath.replace('.json', '_fixed.json')
        with open(fixed_path, 'w', encoding='utf-8') as f:
            json.dump(result.fixed_theme, f, indent=2, ensure_ascii=False)
        
        result.info.append(ValidationError(
            field='file',
            message=f"Korrigiertes Theme gespeichert: {fixed_path}",
            severity='info'
        ))
    
    return result
