# Theme Validator Quick Start

Schnellstart-Anleitung für Theme-Validierung.

## 5-Minuten-Start

### 1. Theme validieren (Python)

```python
from theming.theme_validator import validate_theme_file

result = validate_theme_file('my-theme.json', fix_errors=True)

if result.is_valid:
    print("✅ Gültig!")
else:
    print("❌ Ungültig!")
    for error in result.errors:
        print(f"  {error}")
```

### 2. Theme validieren (CLI)

```bash
python tools/validate_theme.py my-theme.json --fix
```

### 3. Alle Themes validieren

```bash
python tools/validate_theme.py --validate-all
```

## Häufigste Verwendungsfälle

### Theme-Datei hochladen und validieren

```python
import streamlit as st
from theming.theme_validator import validate_theme_file
import tempfile

uploaded_file = st.file_uploader("Theme hochladen", type=['json'])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    
    result = validate_theme_file(tmp_path, fix_errors=True)
    
    if result.is_valid:
        st.success("✅ Theme ist gültig!")
        st.json(result.fixed_theme)
    else:
        st.error("❌ Theme ist ungültig!")
        for error in result.errors:
            st.error(str(error))
```

### Theme in App laden mit Validierung

```python
from theming.theme_validator import ThemeValidator

class ThemeManager:
    def __init__(self):
        self.validator = ThemeValidator()
    
    def load_theme(self, theme_name: str):
        filepath = f"theming/themes/{theme_name}.json"
        result = self.validator.validate_file(filepath, fix_errors=True)
        
        if not result.is_valid:
            return self.get_fallback_theme()
        
        return result.fixed_theme
```

### Batch-Validierung

```python
from pathlib import Path
from theming.theme_validator import ThemeValidator

validator = ThemeValidator()
themes_dir = Path('theming/themes')

for theme_file in themes_dir.glob('*.json'):
    result = validator.validate_file(str(theme_file))
    
    if result.is_valid:
        print(f"✅ {theme_file.name}")
    else:
        print(f"❌ {theme_file.name}")
        for error in result.errors:
            print(f"    {error}")
```

## Validierungs-Regeln (Cheat Sheet)

### Farben ✅ / ❌

```python
# ✅ Gültig
"#ffffff"              # Hex 6-stellig
"#fff"                 # Hex 3-stellig
"rgb(255, 255, 255)"   # RGB
"rgba(255, 255, 255, 0.5)"  # RGBA

# ❌ Ungültig
"white"                # Farb-Name
"#gggggg"              # Ungültiges Hex
"rgb(300, 300, 300)"   # Werte > 255
```

### Font-Sizes ✅ / ❌

```python
# ✅ Gültig
"1rem"
"16px"
"1.5em"

# ❌ Ungültig
"16"        # Fehlt Einheit
"1.5"       # Fehlt Einheit
```

### Font-Weights ✅ / ⚠️

```python
# ✅ Gültig
400, 500, 600, 700

# ⚠️ Warnung (funktioniert, aber nicht empfohlen)
450, 550
```

### Line-Heights ✅ / ⚠️

```python
# ✅ Gültig
1.5, 1.25, 2.0

# ⚠️ Warnung
0.5   # Zu klein
4.0   # Zu groß
```

## CLI-Befehle (Cheat Sheet)

```bash
# Einzelne Datei
python tools/validate_theme.py my-theme.json

# Mit Fehlerkorrektur
python tools/validate_theme.py my-theme.json --fix

# Korrigiertes Theme speichern
python tools/validate_theme.py my-theme.json --fix --save

# Alle Themes
python tools/validate_theme.py --validate-all

# Mit Details
python tools/validate_theme.py --validate-all --verbose

# Beispiel erstellen
python tools/validate_theme.py --create-example
```

## Fehler beheben

### "Pflichtfeld fehlt"

```json
{
  "name": "my-theme",
  "display_name": "My Theme"
  // ❌ Fehlt: colors, typography
}
```

**Lösung:** Verwende `fix_errors=True`

```python
result = validate_theme_file('my-theme.json', fix_errors=True)
# Fehlende Felder werden automatisch aufgefüllt
```

### "Ungültiges Farbformat"

```json
{
  "colors": {
    "primary": "blue"  // ❌
  }
}
```

**Lösung:** Verwende Hex, RGB oder RGBA

```json
{
  "colors": {
    "primary": "#3b82f6"  // ✅
  }
}
```

### "Font-Size muss mit 'rem', 'px' oder 'em' enden"

```json
{
  "typography": {
    "font_size_base": "16"  // ❌
  }
}
```

**Lösung:** Füge Einheit hinzu

```json
{
  "typography": {
    "font_size_base": "1rem"  // ✅
  }
}
```

## Demo starten

```bash
streamlit run demo_theme_validator.py
```

## Tests ausführen

```bash
pytest tests/test_theme_validator.py -v
```

## Weitere Ressourcen

- [Vollständige Referenz](THEME_VALIDATOR_REFERENCE.md)
- [Quick Reference](../docs/THEME_VALIDATOR_QUICK_REFERENCE.md)
- [Verwendungsbeispiele](THEME_VALIDATOR_USAGE_EXAMPLE.md)
- [CLI-Tool](../tools/validate_theme.py)
- [Demo-App](../demo_theme_validator.py)

---

**Tipp:** Verwende immer `fix_errors=True` für robuste Theme-Validierung!
