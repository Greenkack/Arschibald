"""
Tests für Theme Validator

Testet alle Funktionen des Theme-Validierungssystems.
"""

import pytest
import json
import tempfile
from pathlib import Path
from theming.theme_validator import (
    ThemeValidator,
    validate_theme_file,
    ValidationResult,
    ValidationError,
    THEME_SCHEMA,
    DEFAULT_THEME_VALUES
)


class TestThemeValidator:
    """Tests für ThemeValidator-Klasse"""
    
    def test_validator_initialization(self):
        """Test: Validator kann initialisiert werden"""
        validator = ThemeValidator()
        assert validator.schema == THEME_SCHEMA
        assert validator.defaults == DEFAULT_THEME_VALUES
    
    def test_validate_valid_theme(self):
        """Test: Gültiges Theme wird akzeptiert"""
        validator = ThemeValidator()
        
        theme_data = {
            "name": "test-theme",
            "display_name": "Test Theme",
            "colors": {
                "background": "#ffffff",
                "foreground": "#000000",
                "primary": "#3b82f6"
            },
            "typography": {
                "font_family": "Inter, sans-serif",
                "font_size_base": "1rem"
            }
        }
        
        result = validator.validate_theme(theme_data, fix_errors=True)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.fixed_theme is not None
    
    def test_validate_missing_required_fields(self):
        """Test: Fehlende Pflichtfelder werden erkannt"""
        validator = ThemeValidator()
        
        theme_data = {
            "name": "test-theme"
            # Fehlt: display_name, colors, typography
        }
        
        result = validator.validate_theme(theme_data, fix_errors=False)
        
        assert not result.is_valid
        assert len(result.errors) > 0
        
        # Prüfe dass Pflichtfelder fehlen
        error_fields = [e.field for e in result.errors]
        assert "display_name" in error_fields
        assert "colors" in error_fields
        assert "typography" in error_fields
    
    def test_validate_invalid_name_pattern(self):
        """Test: Ungültiger Name wird erkannt"""
        validator = ThemeValidator()
        
        theme_data = {
            "name": "Test Theme",  # Ungültig: Leerzeichen und Großbuchstaben
            "display_name": "Test Theme",
            "colors": {"background": "#fff", "foreground": "#000", "primary": "#00f"},
            "typography": {"font_family": "Arial", "font_size_base": "1rem"}
        }
        
        result = validator.validate_theme(theme_data, fix_errors=False)
        
        assert not result.is_valid
        assert any(e.field == "name" for e in result.errors)
    
    def test_fill_missing_properties(self):
        """Test: Fehlende Properties werden aufgefüllt"""
        validator = ThemeValidator()
        
        theme_data = {
            "name": "test-theme",
            "display_name": "Test Theme",
            "colors": {
                "background": "#ffffff",
                "foreground": "#000000",
                "primary": "#3b82f6"
            },
            "typography": {
                "font_family": "Inter, sans-serif",
                "font_size_base": "1rem"
            }
        }
        
        result = validator.validate_theme(theme_data, fix_errors=True)
        
        assert result.is_valid
        assert result.fixed_theme is not None
        
        # Prüfe dass fehlende Farben aufgefüllt wurden
        assert "secondary" in result.fixed_theme["colors"]
        assert "success" in result.fixed_theme["colors"]
        assert "error" in result.fixed_theme["colors"]
        
        # Prüfe dass Info-Messages vorhanden sind
        assert len(result.info) > 0


class TestColorValidation:
    """Tests für Farb-Validierung"""
    
    def test_valid_hex_colors(self):
        """Test: Gültige Hex-Farben werden akzeptiert"""
        validator = ThemeValidator()
        
        valid_colors = ["#ffffff", "#fff", "#3b82f6", "#000"]
        
        for color in valid_colors:
            assert validator._is_hex_color(color), f"{color} sollte gültig sein"
    
    def test_invalid_hex_colors(self):
        """Test: Ungültige Hex-Farben werden erkannt"""
        validator = ThemeValidator()
        
        invalid_colors = ["#gggggg", "#12345", "ffffff", "#12"]
        
        for color in invalid_colors:
            assert not validator._is_hex_color(color), f"{color} sollte ungültig sein"
    
    def test_valid_rgb_colors(self):
        """Test: Gültige RGB-Farben werden akzeptiert"""
        validator = ThemeValidator()
        
        valid_colors = [
            "rgb(255, 255, 255)",
            "rgb(0, 0, 0)",
            "rgb(59, 130, 246)"
        ]
        
        for color in valid_colors:
            assert validator._is_rgb_color(color), f"{color} sollte gültig sein"
    
    def test_valid_rgba_colors(self):
        """Test: Gültige RGBA-Farben werden akzeptiert"""
        validator = ThemeValidator()
        
        valid_colors = [
            "rgba(255, 255, 255, 1)",
            "rgba(0, 0, 0, 0.5)",
            "rgba(59, 130, 246, 0.8)"
        ]
        
        for color in valid_colors:
            assert validator._is_rgba_color(color), f"{color} sollte gültig sein"
    
    def test_invalid_color_format(self):
        """Test: Ungültige Farbformate werden erkannt"""
        validator = ThemeValidator()
        
        theme_data = {
            "name": "test-theme",
            "display_name": "Test Theme",
            "colors": {
                "background": "white",  # Ungültig
                "foreground": "#000",
                "primary": "#00f"
            },
            "typography": {
                "font_family": "Arial",
                "font_size_base": "1rem"
            }
        }
        
        result = validator.validate_theme(theme_data, fix_errors=False)
        
        assert not result.is_valid
        assert any(
            e.field == "colors.background" and "Ungültiges Farbformat" in e.message
            for e in result.errors
        )
    
    def test_pure_white_warning(self):
        """Test: Warnung bei rein weißer Farbe"""
        validator = ThemeValidator()
        
        theme_data = {
            "name": "test-theme",
            "display_name": "Test Theme",
            "colors": {
                "background": "#ffffff",  # Rein weiß
                "foreground": "#000",
                "primary": "#00f"
            },
            "typography": {
                "font_family": "Arial",
                "font_size_base": "1rem"
            }
        }
        
        result = validator.validate_theme(theme_data, fix_errors=True)
        
        assert result.is_valid
        assert any(
            e.field == "colors.background" and "weiße Farbe" in e.message
            for e in result.warnings
        )


class TestTypographyValidation:
    """Tests für Typography-Validierung"""
    
    def test_valid_font_sizes(self):
        """Test: Gültige Font-Sizes werden akzeptiert"""
        validator = ThemeValidator()
        
        theme_data = {
            "name": "test-theme",
            "display_name": "Test Theme",
            "colors": {"background": "#fff", "foreground": "#000", "primary": "#00f"},
            "typography": {
                "font_family": "Arial",
                "font_size_base": "1rem",
                "font_size_sm": "0.875rem",
                "font_size_lg": "16px"
            }
        }
        
        result = validator.validate_theme(theme_data, fix_errors=True)
        
        assert result.is_valid
    
    def test_invalid_font_size_unit(self):
        """Test: Ungültige Font-Size-Einheit wird erkannt"""
        validator = ThemeValidator()
        
        theme_data = {
            "name": "test-theme",
            "display_name": "Test Theme",
            "colors": {"background": "#fff", "foreground": "#000", "primary": "#00f"},
            "typography": {
                "font_family": "Arial",
                "font_size_base": "16"  # Fehlt Einheit
            }
        }
        
        result = validator.validate_theme(theme_data, fix_errors=False)
        
        assert not result.is_valid
        assert any(
            "font_size" in e.field and "rem" in e.message
            for e in result.errors
        )
    
    def test_font_weight_validation(self):
        """Test: Font-Weight-Validierung"""
        validator = ThemeValidator()
        
        theme_data = {
            "name": "test-theme",
            "display_name": "Test Theme",
            "colors": {"background": "#fff", "foreground": "#000", "primary": "#00f"},
            "typography": {
                "font_family": "Arial",
                "font_size_base": "1rem",
                "font_weight_normal": 400,
                "font_weight_bold": 450  # Warnung: kein Vielfaches von 100
            }
        }
        
        result = validator.validate_theme(theme_data, fix_errors=True)
        
        assert result.is_valid
        assert any(
            "font_weight_bold" in e.field and "Vielfaches von 100" in e.message
            for e in result.warnings
        )
    
    def test_line_height_validation(self):
        """Test: Line-Height-Validierung"""
        validator = ThemeValidator()
        
        theme_data = {
            "name": "test-theme",
            "display_name": "Test Theme",
            "colors": {"background": "#fff", "foreground": "#000", "primary": "#00f"},
            "typography": {
                "font_family": "Arial",
                "font_size_base": "1rem",
                "line_height_normal": 1.5,
                "line_height_tight": 0.5  # Warnung: zu klein
            }
        }
        
        result = validator.validate_theme(theme_data, fix_errors=True)
        
        assert result.is_valid
        assert any(
            "line_height_tight" in e.field
            for e in result.warnings
        )


class TestFileValidation:
    """Tests für Datei-Validierung"""
    
    def test_validate_existing_file(self):
        """Test: Existierende Datei wird validiert"""
        # Erstelle temporäre Theme-Datei
        theme_data = {
            "name": "test-theme",
            "display_name": "Test Theme",
            "colors": {"background": "#fff", "foreground": "#000", "primary": "#00f"},
            "typography": {"font_family": "Arial", "font_size_base": "1rem"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_path = f.name
        
        try:
            result = validate_theme_file(temp_path, fix_errors=True)
            assert result.is_valid
        finally:
            Path(temp_path).unlink()
    
    def test_validate_nonexistent_file(self):
        """Test: Nicht-existierende Datei wird erkannt"""
        result = validate_theme_file('nonexistent.json')
        
        assert not result.is_valid
        assert any(e.field == "file" for e in result.errors)
    
    def test_validate_invalid_json(self):
        """Test: Ungültiges JSON wird erkannt"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            result = validate_theme_file(temp_path)
            assert not result.is_valid
            assert any(e.field == "json" for e in result.errors)
        finally:
            Path(temp_path).unlink()
    
    def test_save_fixed_theme(self):
        """Test: Korrigiertes Theme wird gespeichert"""
        theme_data = {
            "name": "test-theme",
            "display_name": "Test Theme",
            "colors": {"background": "#fff", "foreground": "#000", "primary": "#00f"},
            "typography": {"font_family": "Arial", "font_size_base": "1rem"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(theme_data, f)
            temp_path = f.name
        
        try:
            result = validate_theme_file(temp_path, fix_errors=True, save_fixed=True)
            
            assert result.is_valid
            
            # Prüfe dass _fixed.json erstellt wurde
            fixed_path = temp_path.replace('.json', '_fixed.json')
            assert Path(fixed_path).exists()
            
            # Cleanup
            Path(fixed_path).unlink()
        finally:
            Path(temp_path).unlink()


class TestValidationResult:
    """Tests für ValidationResult-Klasse"""
    
    def test_validation_result_creation(self):
        """Test: ValidationResult kann erstellt werden"""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            info=[]
        )
        
        assert result.is_valid
        assert not result.has_errors()
        assert not result.has_warnings()
    
    def test_has_errors(self):
        """Test: has_errors() funktioniert"""
        error = ValidationError(
            field="test",
            message="Test error",
            severity="error"
        )
        
        result = ValidationResult(
            is_valid=False,
            errors=[error],
            warnings=[],
            info=[]
        )
        
        assert result.has_errors()
    
    def test_has_warnings(self):
        """Test: has_warnings() funktioniert"""
        warning = ValidationError(
            field="test",
            message="Test warning",
            severity="warning"
        )
        
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[warning],
            info=[]
        )
        
        assert result.has_warnings()
    
    def test_get_summary(self):
        """Test: get_summary() gibt Zusammenfassung zurück"""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            info=[]
        )
        
        summary = result.get_summary()
        
        assert "✅" in summary or "gültig" in summary.lower()
        assert "Fehler: 0" in summary
    
    def test_get_detailed_report(self):
        """Test: get_detailed_report() gibt detaillierten Report zurück"""
        error = ValidationError(
            field="test.field",
            message="Test error",
            severity="error"
        )
        
        result = ValidationResult(
            is_valid=False,
            errors=[error],
            warnings=[],
            info=[]
        )
        
        report = result.get_detailed_report()
        
        assert "FEHLER" in report
        assert "test.field" in report


class TestValidationError:
    """Tests für ValidationError-Klasse"""
    
    def test_validation_error_creation(self):
        """Test: ValidationError kann erstellt werden"""
        error = ValidationError(
            field="test.field",
            message="Test message",
            severity="error",
            value="test_value"
        )
        
        assert error.field == "test.field"
        assert error.message == "Test message"
        assert error.severity == "error"
        assert error.value == "test_value"
    
    def test_validation_error_string(self):
        """Test: ValidationError String-Repräsentation"""
        error = ValidationError(
            field="test.field",
            message="Test message",
            severity="error",
            value="test_value"
        )
        
        error_str = str(error)
        
        assert "test.field" in error_str
        assert "Test message" in error_str
        assert "test_value" in error_str
        assert "❌" in error_str


def test_default_values_completeness():
    """Test: Default-Werte sind vollständig"""
    # Prüfe dass alle Sections vorhanden sind
    assert "colors" in DEFAULT_THEME_VALUES
    assert "typography" in DEFAULT_THEME_VALUES
    assert "spacing" in DEFAULT_THEME_VALUES
    assert "shadows" in DEFAULT_THEME_VALUES
    assert "borders" in DEFAULT_THEME_VALUES
    assert "animations" in DEFAULT_THEME_VALUES
    
    # Prüfe dass wichtige Farben vorhanden sind
    colors = DEFAULT_THEME_VALUES["colors"]
    assert "background" in colors
    assert "foreground" in colors
    assert "primary" in colors
    
    # Prüfe dass wichtige Typography-Werte vorhanden sind
    typography = DEFAULT_THEME_VALUES["typography"]
    assert "font_family" in typography
    assert "font_size_base" in typography


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
