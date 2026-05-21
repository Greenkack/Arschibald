# Preismatrix Fehlerbehandlung - Quick Reference

## Schnellstart

### Sichere Preisberechnung

```python
from price_matrix_lookup import calculate_price_from_matrix_safe

result = calculate_price_from_matrix_safe(
    module_count=20,
    storage_model="10kWh",
    enable_fallback=True,
    notify_admin=True
)

if result['success']:
    price = result['base_price']
else:
    error_message = result['user_message']
```

### Fehler in Streamlit anzeigen

```python
from price_matrix_error_ui import display_error_with_fallback

display_error_with_fallback(result)
```

---

## Fehlertypen

| Fehlertyp | Kategorie | Schweregrad | Fallback |
|-----------|-----------|-------------|----------|
| Matrix nicht gefunden | `MATRIX_NOT_FOUND` | CRITICAL | Standardberechnung |
| Modulanzahl fehlt | `MODULE_COUNT_MISSING` | ERROR | Nächst-kleinere Zahl |
| Speichermodell fehlt | `STORAGE_MODEL_MISSING` | ERROR | "Kein Speicher" |
| Zelle leer | `CELL_EMPTY` | ERROR | Nein |
| Zelle ungültig | `CELL_INVALID` | ERROR | Nein |

---

## Wichtige Funktionen

### Fehlerbehandlung

```python
from price_matrix_error_handling import (
    classify_error,                    # Fehler klassifizieren
    format_error_message_for_ui,       # Für UI formatieren
    get_error_help_text,               # Hilfetext holen
    create_admin_notification,         # Admin benachrichtigen
    try_fallback,                      # Fallback versuchen
    handle_error_with_fallback,        # Umfassende Behandlung
    validate_matrix_with_error_handling # Matrix validieren
)
```

### UI-Komponenten

```python
from price_matrix_error_ui import (
    display_error_message,             # Basis-Fehleranzeige
    display_error_with_fallback,       # Mit Fallback-Info
    display_validation_results,        # Validierungsergebnisse
    display_price_lookup_error,        # Interaktive Anzeige
    display_admin_notification_banner, # Admin-Banner
    show_error_help_dialog            # Hilfe-Dialog
)
```

---

## Fallback-Strategien

```python
from price_matrix_error_handling import FallbackStrategy

# Verfügbare Strategien
FallbackStrategy.FLOOR_MODULE_COUNT    # Nächst-kleinere Modulanzahl
FallbackStrategy.NO_STORAGE            # "Kein Speicher"
FallbackStrategy.STANDARD_CALCULATION  # Standardberechnung
FallbackStrategy.DEFAULT_PRICE         # Standard-Preis
FallbackStrategy.NONE                  # Kein Fallback
```

---

## Beispiele

### Beispiel 1: Einfache Verwendung

```python
result = calculate_price_from_matrix_safe(20, "10kWh")

if result['success']:
    st.success(f"Preis: {result['base_price']} EUR")
else:
    st.error(result['user_message'])
```

### Beispiel 2: Mit Fallback-Info

```python
result = calculate_price_from_matrix_safe(
    module_count=25,
    storage_model="10kWh",
    enable_fallback=True
)

if result['success']:
    if result['fallback_used']:
        st.warning(result['fallback_info']['message'])
    st.success(f"Preis: {result['base_price']} EUR")
```

### Beispiel 3: Mit UI-Komponenten

```python
from price_matrix_error_ui import display_error_with_fallback

result = calculate_price_from_matrix_safe(20, "10kWh")
display_error_with_fallback(result)
```

### Beispiel 4: Matrix validieren

```python
from price_matrix_error_handling import validate_matrix_with_error_handling
from price_matrix_error_ui import display_validation_results

result = validate_matrix_with_error_handling(matrix_id=1)
display_validation_results(result)
```

---

## Ergebnis-Struktur

```python
{
    'success': bool,                    # True wenn erfolgreich
    'base_price': float | None,         # Gefundener Preis
    'row_used': str | None,             # Verwendete Zeile
    'column_used': str | None,          # Verwendete Spalte
    'matrix_id': int | None,            # Matrix-ID
    'matrix_name': str | None,          # Matrix-Name
    'error': str | None,                # Technische Fehlermeldung
    'error_type': str | None,           # Fehlertyp
    'error_category': str | None,       # Fehler-Kategorie
    'error_severity': str | None,       # Schweregrad
    'user_message': str | None,         # Benutzerfreundliche Meldung
    'suggestions': list | None,         # Lösungsvorschläge
    'fallback_used': bool,              # Fallback verwendet?
    'fallback_info': dict | None,       # Fallback-Details
    'admin_notified': bool,             # Admin benachrichtigt?
    'error_info': dict | None           # Strukturierte Fehlerinfo
}
```

---

## Best Practices

✅ **DO:**
- Verwende `calculate_price_from_matrix_safe()` statt `calculate_price_from_matrix()`
- Aktiviere Fallback für Benutzer-Anfragen
- Zeige `user_message` statt `error`
- Biete Lösungsvorschläge an
- Benachrichtige Admin bei kritischen Fehlern

❌ **DON'T:**
- Verwende nicht die unsichere Funktion in Produktion
- Zeige keine technischen Fehlermeldungen an Benutzer
- Ignoriere keine Fallback-Warnungen
- Vergiss nicht Admin-Benachrichtigungen

---

## Cheat Sheet

### Fehler klassifizieren
```python
error_info = classify_error(error)
```

### Für UI formatieren
```python
message = format_error_message_for_ui(error_info)
```

### Fallback versuchen
```python
fallback = try_fallback(error_info, module_count, storage_model, matrix_data)
```

### Umfassende Behandlung
```python
result = handle_error_with_fallback(error, module_count, storage_model)
```

### In Streamlit anzeigen
```python
display_error_with_fallback(result)
```

---

## Weitere Informationen

📖 **Vollständige Dokumentation:**  
`docs/PRICE_MATRIX_ERROR_HANDLING_COMPLETE.md`

📝 **Implementierungs-Details:**  
`TASK_8_ERROR_HANDLING_COMPLETE.md`

🧪 **Tests:**  
`test_price_matrix_error_handling_complete.py`

💻 **Code:**
- `price_matrix_error_handling.py` - Hauptmodul
- `price_matrix_error_ui.py` - UI-Komponenten
- `price_matrix_lookup.py` - Sichere Preisberechnung
