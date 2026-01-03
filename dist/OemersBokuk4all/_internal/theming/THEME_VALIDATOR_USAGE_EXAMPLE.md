# Theme Validator Usage Examples

Praktische Beispiele für die Verwendung des Theme-Validators.

## Beispiel 1: Einfache Validierung

```python
from theming.theme_validator import validate_theme_file

# Theme validieren
result = validate_theme_file('theming/themes/shadcn-default.json')

if result.is_valid:
    print("✅ Theme ist gültig!")
else:
    print("❌ Theme hat Fehler:")
    for error in result.errors:
        print(f"  - {error}")
```

## Beispiel 2: Validierung mit Fehlerkorrektur

```python
from theming.theme_validator import validate_theme_file

# Theme validieren und fehlende Properties auffüllen
result = validate_theme_file(
    'theming/themes/my-incomplete-theme.json',
    fix_errors=True
)

if result.is_valid:
    print("✅ Theme wurde korrigiert!")
    
    # Zeige aufgefüllte Properties
    if result.info:
        print("\nAufgefüllte Properties:")
        for info in result.info:
            print(f"  - {info}")
    
    # Verwende korrigiertes Theme
    theme_data = result.fixed_theme
else:
    print("❌ Theme konnte nicht korrigiert werden")
```

## Beispiel 3: Theme speichern nach Korrektur

```python
from theming.theme_validator import validate_theme_file

# Theme validieren, korrigieren und speichern
result = validate_theme_file(
    'theming/themes/my-theme.json',
    fix_errors=True,
    save_fixed=True
)

if result.is_valid:
    print("✅ Theme wurde korrigiert und gespeichert!")
    print("📁 Gespeichert als: my-theme_fixed.json")
```

## Beispiel 4: Detaillierter Report

```python
from theming.theme_validator import validate_theme_file

result = validate_theme_file('theming/themes/my-theme.json')

# Zeige detaillierten Report
print(result.get_detailed_report())

# Output:
# ✅ Theme ist gültig!
# 
# Fehler: 0
# Warnungen: 2
# Hinweise: 5
# 
# WARNUNGEN:
#   ⚠️ colors.background: Rein weiße Farbe kann Kontrast-Probleme verursachen
#   ⚠️ typography.font_size_xs: Sehr kleine Schriftgröße kann Lesbarkeit beeinträchtigen
# 
# HINWEISE:
#   ℹ️ colors.secondary: Fehlende Property wurde mit Default-Wert aufgefüllt
#   ...
```

## Beispiel 5: Programmatische Validierung

```python
from theming.theme_validator import ThemeValidator

validator = ThemeValidator()

# Theme-Daten direkt validieren
theme_data = {
    "name": "my-custom-theme",
    "display_name": "My Custom Theme",
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

if result.is_valid:
    # Verwende korrigiertes Theme
    corrected_theme = result.fixed_theme
    print(f"✅ Theme '{corrected_theme['name']}' ist gültig!")
```

## Beispiel 6: Integration in Theme Manager

```python
from theming.theme_manager import ThemeManager
from theming.theme_validator import ThemeValidator
from theming.theme_errors import ThemeLoadError

class ThemeManager:
    def __init__(self):
        self.validator = ThemeValidator()
        self.themes = {}
    
    def load_theme(self, theme_name: str):
        """Lädt Theme mit Validierung"""
        filepath = f"theming/themes/{theme_name}.json"
        
        # Validiere Theme
        result = self.validator.validate_file(filepath, fix_errors=True)
        
        if not result.is_valid:
            # Logge Fehler
            error_msg = f"Theme '{theme_name}' validation failed:\n"
            for error in result.errors:
                error_msg += f"  - {error}\n"
            
            raise ThemeLoadError(error_msg)
        
        # Logge Warnungen
        if result.has_warnings():
            for warning in result.warnings:
                print(f"⚠️ {warning}")
        
        # Verwende korrigiertes Theme
        self.themes[theme_name] = result.fixed_theme
        return result.fixed_theme
```

## Beispiel 7: Batch-Validierung

```python
from pathlib import Path
from theming.theme_validator import ThemeValidator

validator = ThemeValidator()
themes_dir = Path('theming/themes')

# Validiere alle Themes
results = {}
for theme_file in themes_dir.glob('*.json'):
    result = validator.validate_file(str(theme_file), fix_errors=True)
    results[theme_file.name] = result

# Zusammenfassung
valid_count = sum(1 for r in results.values() if r.is_valid)
total_count = len(results)

print(f"\n{'='*60}")
print(f"Validierung abgeschlossen: {valid_count}/{total_count} Themes gültig")
print(f"{'='*60}\n")

# Details für ungültige Themes
for name, result in results.items():
    if not result.is_valid:
        print(f"❌ {name}:")
        for error in result.errors:
            print(f"    {error}")
        print()
```

## Beispiel 8: Custom Validation Rules

```python
from theming.theme_validator import ThemeValidator, ValidationError

class CustomThemeValidator(ThemeValidator):
    """Erweiterte Validierung mit Custom Rules"""
    
    def validate_theme(self, theme_data, fix_errors=True):
        # Standard-Validierung
        result = super().validate_theme(theme_data, fix_errors)
        
        # Custom Rule: Prüfe Brand-Farben
        if 'colors' in theme_data:
            colors = theme_data['colors']
            
            # Warnung wenn primary und secondary zu ähnlich
            if 'primary' in colors and 'secondary' in colors:
                if colors['primary'] == colors['secondary']:
                    result.warnings.append(ValidationError(
                        field='colors',
                        message='Primary und Secondary sollten unterschiedlich sein',
                        severity='warning'
                    ))
        
        return result

# Verwenden
validator = CustomThemeValidator()
result = validator.validate_theme(theme_data)
```

## Beispiel 9: CLI-Tool verwenden

```bash
# Einzelnes Theme validieren
python tools/validate_theme.py theming/themes/my-theme.json

# Mit Fehlerkorrektur
python tools/validate_theme.py theming/themes/my-theme.json --fix

# Korrigiertes Theme speichern
python tools/validate_theme.py theming/themes/my-theme.json --fix --save

# Alle Themes validieren
python tools/validate_theme.py --validate-all

# Mit detaillierter Ausgabe
python tools/validate_theme.py --validate-all --verbose

# Beispiel-Theme erstellen
python tools/validate_theme.py --create-example --output my-new-theme.json
```

## Beispiel 10: Streamlit Integration

```python
import streamlit as st
from theming.theme_validator import validate_theme_file

st.title("Theme Validator")

# File Upload
uploaded_file = st.file_uploader("Theme-Datei hochladen", type=['json'])

if uploaded_file:
    # Speichere temporär
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    
    # Validiere
    with st.spinner("Validiere Theme..."):
        result = validate_theme_file(tmp_path, fix_errors=True)
    
    # Zeige Ergebnis
    if result.is_valid:
        st.success("✅ Theme ist gültig!")
    else:
        st.error("❌ Theme ist ungültig!")
    
    # Details
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Fehler", len(result.errors))
    with col2:
        st.metric("Warnungen", len(result.warnings))
    with col3:
        st.metric("Hinweise", len(result.info))
    
    # Fehler anzeigen
    if result.errors:
        st.subheader("Fehler")
        for error in result.errors:
            st.error(str(error))
    
    # Warnungen anzeigen
    if result.warnings:
        st.subheader("Warnungen")
        for warning in result.warnings:
            st.warning(str(warning))
    
    # Korrigiertes Theme anzeigen
    if result.fixed_theme:
        st.subheader("Korrigiertes Theme")
        st.json(result.fixed_theme)
        
        # Download-Button
        import json
        theme_json = json.dumps(result.fixed_theme, indent=2)
        st.download_button(
            "📥 Korrigiertes Theme herunterladen",
            theme_json,
            file_name="theme_fixed.json",
            mime="application/json"
        )
```

## Beispiel 11: Fehlerbehandlung

```python
from theming.theme_validator import validate_theme_file
import logging

logger = logging.getLogger(__name__)

def load_validated_theme(theme_name: str):
    """Lädt Theme mit umfassender Fehlerbehandlung"""
    filepath = f"theming/themes/{theme_name}.json"
    
    try:
        # Validiere Theme
        result = validate_theme_file(filepath, fix_errors=True)
        
        if not result.is_valid:
            # Logge alle Fehler
            logger.error(f"Theme '{theme_name}' validation failed:")
            for error in result.errors:
                logger.error(f"  {error}")
            
            # Verwende Fallback
            logger.info("Using fallback theme")
            return get_fallback_theme()
        
        # Logge Warnungen
        if result.has_warnings():
            logger.warning(f"Theme '{theme_name}' has warnings:")
            for warning in result.warnings:
                logger.warning(f"  {warning}")
        
        # Logge Hinweise
        if result.info:
            logger.info(f"Theme '{theme_name}' was auto-corrected:")
            for info in result.info:
                logger.info(f"  {info}")
        
        return result.fixed_theme
    
    except FileNotFoundError:
        logger.error(f"Theme file not found: {filepath}")
        return get_fallback_theme()
    
    except Exception as e:
        logger.error(f"Unexpected error loading theme: {e}")
        return get_fallback_theme()

def get_fallback_theme():
    """Gibt Fallback-Theme zurück"""
    return {
        "name": "fallback",
        "display_name": "Fallback Theme",
        # ... Default-Werte
    }
```

## Beispiel 12: CI/CD Integration

```python
# validate_themes.py - Für CI/CD Pipeline

import sys
from pathlib import Path
from theming.theme_validator import ThemeValidator

def main():
    """Validiert alle Themes und gibt Exit-Code zurück"""
    validator = ThemeValidator()
    themes_dir = Path('theming/themes')
    
    all_valid = True
    
    for theme_file in themes_dir.glob('*.json'):
        result = validator.validate_file(str(theme_file), fix_errors=False)
        
        if not result.is_valid:
            print(f"❌ {theme_file.name} ist ungültig:")
            for error in result.errors:
                print(f"    {error}")
            all_valid = False
        else:
            print(f"✅ {theme_file.name} ist gültig")
    
    # Exit mit Fehlercode wenn Themes ungültig
    sys.exit(0 if all_valid else 1)

if __name__ == '__main__':
    main()
```

```yaml
# .github/workflows/validate-themes.yml
name: Validate Themes

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Validate themes
        run: python validate_themes.py
```

## Siehe auch

- [Theme Validator Reference](THEME_VALIDATOR_REFERENCE.md)
- [Theme Validator Quick Reference](../docs/THEME_VALIDATOR_QUICK_REFERENCE.md)
- [Theme System Guide](../docs/THEME_SYSTEM_GUIDE.md)
