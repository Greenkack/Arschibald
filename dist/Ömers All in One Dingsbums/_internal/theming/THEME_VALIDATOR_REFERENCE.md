# Theme Validator Reference

Vollständige API-Referenz für das Theme-Validierungssystem.

## Übersicht

Das Theme-Validierungssystem bietet umfassende Validierung von Theme-Dateien mit:
- JSON-Schema-Validierung
- Farb-Validierung (Hex, RGB, RGBA)
- Typography-Validierung
- Automatisches Auffüllen fehlender Properties
- Detaillierte Fehlerberichte

## Klassen

### ThemeValidator

Hauptklasse für Theme-Validierung.

```python
from theming.theme_validator import ThemeValidator

validator = ThemeValidator()
```

#### Methoden

##### `validate_theme(theme_data: Dict, fix_errors: bool = True) -> ValidationResult`

Validiert Theme-Daten.

**Parameter:**
- `theme_data`: Theme-Daten als Dictionary
- `fix_errors`: Wenn True, werden fehlende Properties mit Defaults aufgefüllt

**Returns:** `ValidationResult` mit allen Fehlern und Warnungen

**Beispiel:**
```python
theme_data = {
    "name": "my-theme",
    "display_name": "My Theme",
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
    print("✅ Theme ist gültig!")
    # Verwende result.fixed_theme für korrigiertes Theme
else:
    print("❌ Theme ist ungültig!")
    for error in result.errors:
        print(f"  {error}")
```

##### `validate_file(filepath: str, fix_errors: bool = True) -> ValidationResult`

Validiert Theme-Datei.

**Parameter:**
- `filepath`: Pfad zur Theme-JSON-Datei
- `fix_errors`: Wenn True, werden fehlende Properties mit Defaults aufgefüllt

**Returns:** `ValidationResult`

**Beispiel:**
```python
result = validator.validate_file('theming/themes/my-theme.json', fix_errors=True)

print(result.get_summary())
print(result.get_detailed_report())
```

### ValidationResult

Ergebnis einer Theme-Validierung.

**Attribute:**
- `is_valid: bool` - Ob Theme gültig ist
- `errors: List[ValidationError]` - Liste kritischer Fehler
- `warnings: List[ValidationError]` - Liste von Warnungen
- `info: List[ValidationError]` - Liste von Hinweisen
- `fixed_theme: Optional[Dict]` - Korrigiertes Theme (wenn fix_errors=True)

**Methoden:**

##### `has_errors() -> bool`

Prüft ob kritische Fehler vorhanden sind.

##### `has_warnings() -> bool`

Prüft ob Warnungen vorhanden sind.

##### `get_summary() -> str`

Gibt eine Zusammenfassung zurück.

```python
print(result.get_summary())
# Output:
# ✅ Theme ist gültig!
# 
# Fehler: 0
# Warnungen: 2
# Hinweise: 5
```

##### `get_detailed_report() -> str`

Gibt einen detaillierten Report zurück.

```python
print(result.get_detailed_report())
# Output:
# ✅ Theme ist gültig!
# 
# Fehler: 0
# Warnungen: 2
# Hinweise: 5
# 
# WARNUNGEN:
#   ⚠️ colors.background: Rein weiße Farbe kann Kontrast-Probleme verursachen (Wert: #ffffff)
#   ⚠️ typography.font_size_xs: Sehr kleine Schriftgröße kann Lesbarkeit beeinträchtigen (Wert: 0.5rem)
# 
# HINWEISE:
#   ℹ️ colors.secondary: Fehlende Property wurde mit Default-Wert aufgefüllt
#   ...
```

### ValidationError

Repräsentiert einen Validierungs-Fehler.

**Attribute:**
- `field: str` - Feld-Name (z.B. "colors.primary")
- `message: str` - Fehlermeldung
- `severity: str` - Schweregrad ('error', 'warning', 'info')
- `value: Optional[Any]` - Fehlerhafter Wert

**String-Repräsentation:**
```python
error = ValidationError(
    field='colors.primary',
    message='Ungültiges Farbformat',
    severity='error',
    value='invalid'
)

print(error)
# Output: ❌ colors.primary: Ungültiges Farbformat (Wert: invalid)
```

## Convenience-Funktionen

### `validate_theme_file(filepath: str, fix_errors: bool = True, save_fixed: bool = False) -> ValidationResult`

Convenience-Funktion zum Validieren einer Theme-Datei.

**Parameter:**
- `filepath`: Pfad zur Theme-JSON-Datei
- `fix_errors`: Wenn True, werden fehlende Properties mit Defaults aufgefüllt
- `save_fixed`: Wenn True, wird das korrigierte Theme als *_fixed.json gespeichert

**Beispiel:**
```python
from theming.theme_validator import validate_theme_file

result = validate_theme_file(
    'theming/themes/my-theme.json',
    fix_errors=True,
    save_fixed=True
)

if result.is_valid:
    print("✅ Theme validiert und korrigiert!")
    # Korrigiertes Theme wurde als my-theme_fixed.json gespeichert
```

## JSON Schema

Das Theme-Schema definiert die Struktur eines gültigen Themes:

```python
THEME_SCHEMA = {
    "type": "object",
    "required": ["name", "display_name", "colors", "typography"],
    "properties": {
        "name": {
            "type": "string",
            "pattern": "^[a-z0-9-]+$"
        },
        "display_name": {
            "type": "string"
        },
        "colors": {
            "type": "object",
            "required": ["background", "foreground", "primary"],
            "properties": {
                "background": {"type": "string"},
                "foreground": {"type": "string"},
                "primary": {"type": "string"},
                # ... weitere Farben
            }
        },
        "typography": {
            "type": "object",
            "required": ["font_family", "font_size_base"],
            "properties": {
                "font_family": {"type": "string"},
                "font_size_base": {"type": "string"},
                # ... weitere Typography-Properties
            }
        },
        # ... weitere Sections
    }
}
```

## Default-Werte

Fehlende Properties werden mit diesen Default-Werten aufgefüllt:

```python
DEFAULT_THEME_VALUES = {
    "colors": {
        "background": "#ffffff",
        "foreground": "#0a0a0a",
        "primary": "#18181b",
        # ... weitere Farben
    },
    "typography": {
        "font_family": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        "font_size_base": "1rem",
        # ... weitere Typography-Properties
    },
    # ... weitere Sections
}
```

## Validierungs-Regeln

### Farben

**Gültige Formate:**
- Hex: `#ffffff`, `#fff`, `#3b82f6`
- RGB: `rgb(255, 255, 255)`
- RGBA: `rgba(255, 255, 255, 0.5)`

**Warnungen:**
- Rein weiße Farbe (#ffffff) kann Kontrast-Probleme verursachen
- Rein schwarze Farbe (#000000) kann Kontrast-Probleme verursachen

### Typography

**Font-Sizes:**
- Muss mit 'rem', 'px' oder 'em' enden
- Warnung bei < 0.5rem (zu klein)
- Warnung bei > 3rem (zu groß)

**Font-Weights:**
- Muss eine Zahl sein
- Sollte ein Vielfaches von 100 sein (100-900)

**Line-Heights:**
- Muss eine Zahl sein
- Sollte zwischen 1.0 und 3.0 liegen

### Spacing

- Sollte mit 'rem' oder 'px' enden
- Oder '0' für keinen Abstand

### Shadows

- Sollte rgba() oder rgb() verwenden

### Borders

- Border-Radius sollte mit 'rem' oder 'px' enden

### Animations

- Transitions sollten eine Zeitangabe enthalten (ms oder s)

## CLI-Tool

Das CLI-Tool `tools/validate_theme.py` bietet Kommandozeilen-Zugriff:

```bash
# Einzelne Datei validieren
python tools/validate_theme.py theming/themes/my-theme.json

# Mit automatischer Fehlerkorrektur
python tools/validate_theme.py theming/themes/my-theme.json --fix

# Korrigiertes Theme speichern
python tools/validate_theme.py theming/themes/my-theme.json --fix --save

# Alle Themes validieren
python tools/validate_theme.py --validate-all

# Mit Details
python tools/validate_theme.py --validate-all --verbose

# Beispiel-Theme erstellen
python tools/validate_theme.py --create-example
```

## Integration in Theme Manager

```python
from theming.theme_manager import ThemeManager
from theming.theme_validator import ThemeValidator

class ThemeManager:
    def __init__(self):
        self.validator = ThemeValidator()
        # ...
    
    def load_theme(self, theme_name: str):
        """Lädt Theme mit Validierung"""
        filepath = f"theming/themes/{theme_name}.json"
        
        # Validiere Theme
        result = self.validator.validate_file(filepath, fix_errors=True)
        
        if not result.is_valid:
            # Logge Fehler
            for error in result.errors:
                logger.error(f"Theme validation error: {error}")
            
            # Verwende Fallback-Theme
            return self.get_fallback_theme()
        
        # Verwende korrigiertes Theme
        return result.fixed_theme
```

## Best Practices

1. **Immer validieren**: Validiere alle Theme-Dateien vor der Verwendung
2. **Fehlerkorrektur aktivieren**: Verwende `fix_errors=True` für robuste Themes
3. **Warnungen beachten**: Auch wenn Theme gültig ist, können Warnungen auf Probleme hinweisen
4. **CI/CD Integration**: Integriere Validierung in Build-Pipeline
5. **Versionierung**: Speichere korrigierte Themes für Nachvollziehbarkeit

## Fehlerbehandlung

```python
from theming.theme_validator import validate_theme_file

try:
    result = validate_theme_file('my-theme.json')
    
    if result.is_valid:
        # Theme verwenden
        theme_data = result.fixed_theme
    else:
        # Fehler behandeln
        print("Theme-Validierung fehlgeschlagen:")
        for error in result.errors:
            print(f"  - {error}")
        
        # Fallback verwenden
        theme_data = get_fallback_theme()

except FileNotFoundError:
    print("Theme-Datei nicht gefunden")
    theme_data = get_fallback_theme()

except Exception as e:
    print(f"Unerwarteter Fehler: {e}")
    theme_data = get_fallback_theme()
```

## Performance

- Validierung dauert typischerweise < 10ms pro Theme
- Caching empfohlen für häufig validierte Themes
- Batch-Validierung für mehrere Themes optimiert

## Siehe auch

- [Theme Validator Quick Reference](../docs/THEME_VALIDATOR_QUICK_REFERENCE.md)
- [Theme System Reference](THEME_SYSTEM_REFERENCE.md)
- [Theme Generator Reference](../tools/THEME_GENERATOR_REFERENCE.md)
