# Theme Validator Quick Reference

Schnellreferenz für Theme-Validierung.

## Installation

Keine zusätzliche Installation erforderlich. Das Modul ist Teil des Theme-Systems.

## Grundlegende Verwendung

### Theme-Datei validieren

```python
from theming.theme_validator import validate_theme_file

# Einfache Validierung
result = validate_theme_file('theming/themes/my-theme.json')

if result.is_valid:
    print("✅ Theme ist gültig!")
else:
    print("❌ Theme ist ungültig!")
    for error in result.errors:
        print(f"  {error}")
```

### Mit automatischer Fehlerkorrektur

```python
# Fehlende Properties werden automatisch aufgefüllt
result = validate_theme_file(
    'theming/themes/my-theme.json',
    fix_errors=True
)

# Verwende korrigiertes Theme
if result.fixed_theme:
    theme_data = result.fixed_theme
```

### Korrigiertes Theme speichern

```python
# Speichert korrigiertes Theme als *_fixed.json
result = validate_theme_file(
    'theming/themes/my-theme.json',
    fix_errors=True,
    save_fixed=True
)
```

## CLI-Tool

### Einzelne Datei validieren

```bash
python tools/validate_theme.py theming/themes/my-theme.json
```

### Mit Fehlerkorrektur

```bash
python tools/validate_theme.py theming/themes/my-theme.json --fix
```

### Korrigiertes Theme speichern

```bash
python tools/validate_theme.py theming/themes/my-theme.json --fix --save
```

### Alle Themes validieren

```bash
python tools/validate_theme.py --validate-all
```

### Mit Details

```bash
python tools/validate_theme.py --validate-all --verbose
```

### Beispiel-Theme erstellen

```bash
python tools/validate_theme.py --create-example
```

## ValidationResult

```python
result = validate_theme_file('my-theme.json')

# Status prüfen
result.is_valid          # True/False
result.has_errors()      # Hat kritische Fehler?
result.has_warnings()    # Hat Warnungen?

# Fehler und Warnungen
result.errors            # Liste von ValidationError
result.warnings          # Liste von ValidationError
result.info              # Liste von ValidationError

# Korrigiertes Theme
result.fixed_theme       # Dict mit korrigierten Daten

# Reports
print(result.get_summary())          # Kurze Zusammenfassung
print(result.get_detailed_report())  # Detaillierter Report
```

## ThemeValidator Klasse

```python
from theming.theme_validator import ThemeValidator

validator = ThemeValidator()

# Theme-Daten validieren
theme_data = {...}
result = validator.validate_theme(theme_data, fix_errors=True)

# Theme-Datei validieren
result = validator.validate_file('my-theme.json', fix_errors=True)
```

## Validierungs-Regeln

### Farben

✅ **Gültig:**
- `#ffffff`, `#fff`
- `rgb(255, 255, 255)`
- `rgba(255, 255, 255, 0.5)`

❌ **Ungültig:**
- `white`
- `#gggggg`
- `rgb(300, 300, 300)`

### Font-Sizes

✅ **Gültig:**
- `1rem`, `16px`, `1.5em`

❌ **Ungültig:**
- `16` (ohne Einheit)
- `1.5` (ohne Einheit)

### Font-Weights

✅ **Gültig:**
- `400`, `500`, `600`, `700`

⚠️ **Warnung:**
- `450` (kein Vielfaches von 100)

### Line-Heights

✅ **Gültig:**
- `1.5`, `1.25`, `2.0`

⚠️ **Warnung:**
- `0.5` (zu klein)
- `4.0` (zu groß)

## Häufige Fehler

### Fehler: "Pflichtfeld fehlt"

```json
{
  "name": "my-theme",
  "display_name": "My Theme"
  // ❌ Fehlt: colors, typography
}
```

**Lösung:** Verwende `fix_errors=True` oder füge fehlende Felder hinzu.

### Fehler: "Ungültiges Farbformat"

```json
{
  "colors": {
    "primary": "blue"  // ❌ Ungültig
  }
}
```

**Lösung:** Verwende Hex, RGB oder RGBA:
```json
{
  "colors": {
    "primary": "#3b82f6"  // ✅ Gültig
  }
}
```

### Fehler: "Font-Size muss mit 'rem', 'px' oder 'em' enden"

```json
{
  "typography": {
    "font_size_base": "16"  // ❌ Ungültig
  }
}
```

**Lösung:** Füge Einheit hinzu:
```json
{
  "typography": {
    "font_size_base": "1rem"  // ✅ Gültig
  }
}
```

## Integration in App

```python
from theming.theme_manager import ThemeManager
from theming.theme_validator import ThemeValidator

class ThemeManager:
    def __init__(self):
        self.validator = ThemeValidator()
    
    def load_theme(self, theme_name: str):
        filepath = f"theming/themes/{theme_name}.json"
        
        # Validiere und korrigiere Theme
        result = self.validator.validate_file(filepath, fix_errors=True)
        
        if not result.is_valid:
            # Verwende Fallback bei Fehlern
            return self.get_fallback_theme()
        
        return result.fixed_theme
```

## Beispiel: Vollständige Validierung

```python
from theming.theme_validator import validate_theme_file

# Theme validieren
result = validate_theme_file(
    'theming/themes/my-theme.json',
    fix_errors=True,
    save_fixed=True
)

# Ergebnis ausgeben
print(result.get_detailed_report())

# Bei Erfolg: Theme verwenden
if result.is_valid:
    theme_data = result.fixed_theme
    
    # Theme in App laden
    theme_manager.load_theme_data(theme_data)
else:
    # Bei Fehler: Fallback verwenden
    print("⚠️ Theme konnte nicht validiert werden. Verwende Fallback.")
    theme_manager.load_fallback_theme()
```

## Tipps

1. **Immer validieren**: Validiere alle Themes vor der Verwendung
2. **Fehlerkorrektur nutzen**: `fix_errors=True` macht Themes robuster
3. **Warnungen beachten**: Auch gültige Themes können Warnungen haben
4. **CLI für Batch**: Nutze CLI-Tool für mehrere Themes
5. **CI/CD Integration**: Automatisiere Validierung im Build-Prozess

## Siehe auch

- [Theme Validator Reference](../theming/THEME_VALIDATOR_REFERENCE.md) - Vollständige API-Dokumentation
- [Theme System Guide](THEME_SYSTEM_GUIDE.md) - Theme-System-Übersicht
- [Theme Generator](THEME_GENERATOR_QUICK_REFERENCE.md) - Theme-Erstellung
