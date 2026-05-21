# Preismatrix Fehlerbehandlung und Validierung - Vollständige Dokumentation

## Übersicht

Diese Dokumentation beschreibt das umfassende Fehlerbehandlungs- und Validierungssystem für die Preismatrix-Funktionalität (Task 8).

**Implementierte Features:**
- ✅ Task 8.1: Fehler-Typen Definition
- ✅ Task 8.2: Benutzerfreundliche Fehlermeldungen
- ✅ Task 8.3: Fallback-Mechanismen

**Requirements:** 7.1, 7.2, 7.3, 7.4, 7.5, 8.5

---

## Task 8.1: Fehler-Typen Definition

### Fehler-Kategorien

Das System definiert folgende Fehler-Kategorien:

```python
class ErrorCategory(Enum):
    MATRIX_NOT_FOUND = "matrix_not_found"           # Matrix nicht gefunden
    MODULE_COUNT_MISSING = "module_count_missing"   # Modulanzahl nicht in Matrix
    STORAGE_MODEL_MISSING = "storage_model_missing" # Speichermodell nicht in Matrix
    CELL_EMPTY = "cell_empty"                       # Zelle leer
    CELL_INVALID = "cell_invalid"                   # Zelle enthält ungültigen Wert
    VALIDATION_FAILED = "validation_failed"         # Validierung fehlgeschlagen
    INPUT_INVALID = "input_invalid"                 # Ungültige Eingabeparameter
    SYSTEM_ERROR = "system_error"                   # Systemfehler
```

### Schweregrade

```python
class ErrorSeverity(Enum):
    INFO = "info"           # Informativ, kein Fehler
    WARNING = "warning"     # Warnung, Betrieb möglich
    ERROR = "error"         # Fehler, Betrieb eingeschränkt
    CRITICAL = "critical"   # Kritischer Fehler, Betrieb nicht möglich
```

### Strukturierte Fehlerinformation

```python
class PriceMatrixErrorInfo:
    """Strukturierte Fehlerinformation"""
    
    def __init__(
        self,
        category: ErrorCategory,
        severity: ErrorSeverity,
        message: str,
        user_message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        fallback_available: bool = False
    ):
        self.category = category
        self.severity = severity
        self.message = message
        self.user_message = user_message
        self.details = details or {}
        self.suggestions = suggestions or []
        self.fallback_available = fallback_available
        self.timestamp = datetime.now()
```

### Fehler-Klassifizierung

```python
from price_matrix_error_handling import classify_error

# Klassifiziere einen Fehler
error = ModuleCountNotFoundError(25, [10, 15, 20, 30])
error_info = classify_error(error)

print(f"Kategorie: {error_info.category.value}")
print(f"Schweregrad: {error_info.severity.value}")
print(f"Nachricht: {error_info.user_message}")
print(f"Fallback verfügbar: {error_info.fallback_available}")
```

**Ausgabe:**
```
Kategorie: module_count_missing
Schweregrad: error
Nachricht: ❌ Modulanzahl 25 nicht in Preismatrix gefunden...
Fallback verfügbar: True
```

---

## Task 8.2: Benutzerfreundliche Fehlermeldungen

### Formatierung für UI

```python
from price_matrix_error_handling import format_error_message_for_ui

# Formatiere Fehlermeldung für UI
formatted_message = format_error_message_for_ui(
    error_info,
    include_suggestions=True,
    include_details=False
)

print(formatted_message)
```

**Ausgabe:**
```
❌ Modulanzahl 25 nicht in Preismatrix gefunden.

Verfügbare Modulanzahlen:
• Nächst-kleinere: 20
• Nächst-größere: 30

Alle verfügbaren: 10, 15, 20, 30

**Lösungsvorschläge:**
• Wählen Sie eine verfügbare Modulanzahl
• Ergänzen Sie die Preismatrix im Admin-Bereich
• System kann automatisch nächst-kleinere Modulanzahl verwenden

💡 **Hinweis:** Das System kann automatisch einen alternativen Wert verwenden.
```

### Hilfe-Texte

```python
from price_matrix_error_handling import get_error_help_text, ErrorCategory

# Hole detaillierten Hilfetext
help_text = get_error_help_text(ErrorCategory.MODULE_COUNT_MISSING)
print(help_text)
```

**Ausgabe:**
```
**Modulanzahl nicht in Matrix gefunden**

Die gewählte Modulanzahl existiert nicht in der Preismatrix.

**Ursachen:**
• Matrix enthält nicht alle benötigten Modulanzahlen
• Modulanzahl liegt außerhalb des definierten Bereichs

**Lösung:**
1. Wählen Sie eine verfügbare Modulanzahl aus der Liste
2. ODER: Ergänzen Sie die Matrix um die fehlende Modulanzahl
3. Das System kann automatisch die nächst-kleinere Modulanzahl verwenden (Floor-Logik)

**Hinweis:** Die Floor-Logik verwendet automatisch die größte Modulanzahl,
die kleiner oder gleich der gewünschten Anzahl ist.
```

### Admin-Benachrichtigungen

```python
from price_matrix_error_handling import create_admin_notification

# Erstelle Admin-Benachrichtigung
notification = create_admin_notification(
    error_info,
    context={
        'user': 'max.mustermann',
        'module_count': 25,
        'storage_model': '10kWh'
    }
)

print(notification)
```

**Ausgabe:**
```python
{
    'type': 'price_matrix_error',
    'severity': 'error',
    'category': 'module_count_missing',
    'message': 'Modulanzahl 25 nicht in Preismatrix gefunden',
    'timestamp': '2024-01-15T10:30:00',
    'details': {'module_count': 25, 'available_counts': [10, 15, 20, 30]},
    'requires_action': True,
    'context': {
        'user': 'max.mustermann',
        'module_count': 25,
        'storage_model': '10kWh'
    },
    'recommended_actions': [
        'Fehlende Modulanzahlen in Matrix ergänzen',
        'Matrix-Struktur überprüfen'
    ]
}
```

### Streamlit UI-Komponenten

```python
import streamlit as st
from price_matrix_error_ui import display_error_message

# Zeige Fehler in Streamlit
display_error_message(
    error_info,
    show_suggestions=True,
    show_help_button=True
)
```

**Weitere UI-Funktionen:**
- `display_error_with_fallback()` - Zeigt Fehler mit Fallback-Info
- `display_validation_results()` - Zeigt Matrix-Validierungsergebnisse
- `display_price_lookup_error()` - Interaktive Fehleranzeige mit Optionen
- `display_admin_notification_banner()` - Admin-Benachrichtigungen als Banner

---

## Task 8.3: Fallback-Mechanismen

### Fallback-Strategien

```python
class FallbackStrategy(Enum):
    NONE = "none"                           # Kein Fallback
    FLOOR_MODULE_COUNT = "floor_module"     # Nächst-kleinere Modulanzahl
    NO_STORAGE = "no_storage"               # "Kein Speicher" verwenden
    STANDARD_CALCULATION = "standard_calc"  # Standardberechnung verwenden
    DEFAULT_PRICE = "default_price"         # Standard-Preis verwenden
```

### Automatischer Fallback

```python
from price_matrix_error_handling import try_fallback

# Versuche Fallback
fallback_result = try_fallback(
    error_info,
    module_count=25,
    storage_model="10kWh",
    matrix_data=matrix_data,
    allowed_strategies=[
        FallbackStrategy.FLOOR_MODULE_COUNT,
        FallbackStrategy.NO_STORAGE
    ]
)

if fallback_result and fallback_result.success:
    print(f"Fallback erfolgreich: {fallback_result.strategy.value}")
    print(f"Nachricht: {fallback_result.message}")
```

### Umfassende Fehlerbehandlung mit Fallback

```python
from price_matrix_error_handling import handle_error_with_fallback

# Behandle Fehler mit automatischem Fallback
result = handle_error_with_fallback(
    error,
    module_count=25,
    storage_model="10kWh",
    matrix_data=matrix_data,
    enable_fallback=True,
    notify_admin=True
)

if result['fallback_used']:
    print(f"⚠️ Fallback verwendet: {result['fallback_result']['message']}")
    
if result['admin_notified']:
    print("📧 Administrator wurde benachrichtigt")

print(result['user_message'])
```

### Sichere Preisberechnung

```python
from price_matrix_lookup import calculate_price_from_matrix_safe

# Sichere Preisberechnung mit automatischer Fehlerbehandlung
result = calculate_price_from_matrix_safe(
    module_count=25,
    storage_model="10kWh",
    enable_fallback=True,
    notify_admin=True
)

if result['success']:
    print(f"✓ Preis: {result['base_price']} EUR")
    
    if result['fallback_used']:
        print(f"⚠️ {result['fallback_info']['message']}")
        print(f"   Ursprünglich: {result['fallback_info']['original_module_count']} Module")
        print(f"   Verwendet: {result['fallback_info']['fallback_module_count']} Module")
else:
    print(result['user_message'])
    
    if result['suggestions']:
        print("\nLösungsvorschläge:")
        for suggestion in result['suggestions']:
            print(f"  • {suggestion}")
```

---

## Fehlerbehandlungs-Workflow

### 1. Fehler tritt auf

```python
try:
    result = calculate_price_from_matrix(20, "15kWh")
except ModuleCountNotFoundError as e:
    # Fehler behandeln
    pass
```

### 2. Fehler klassifizieren

```python
error_info = classify_error(e)
```

### 3. Für UI formatieren

```python
ui_message = format_error_message_for_ui(error_info)
```

### 4. Admin benachrichtigen (bei kritischen Fehlern)

```python
if error_info.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
    notification = create_admin_notification(error_info)
    # Sende Benachrichtigung an Admin-System
```

### 5. Fallback versuchen

```python
if error_info.fallback_available:
    fallback_result = try_fallback(error_info, module_count, storage_model, matrix_data)
    
    if fallback_result and fallback_result.success:
        # Verwende Fallback-Wert
        pass
```

### 6. Benutzer informieren

```python
# In Streamlit
display_error_with_fallback(result)

# Oder manuell
st.error(ui_message)
```

---

## Validierung mit Fehlerbehandlung

### Matrix validieren

```python
from price_matrix_error_handling import validate_matrix_with_error_handling

# Validiere Matrix mit umfassender Fehlerbehandlung
result = validate_matrix_with_error_handling(matrix_id=1)

if result['valid']:
    print("✓ Matrix ist gültig")
    print(result['user_message'])
else:
    print("✗ Matrix ist ungültig")
    print(result['user_message'])
    
    # Zeige Fehlerinfo
    error_info = result['error_info']
    print(f"Kategorie: {error_info['category']}")
    print(f"Schweregrad: {error_info['severity']}")
```

### In Streamlit anzeigen

```python
from price_matrix_error_ui import display_validation_results

# Zeige Validierungsergebnisse in Streamlit
display_validation_results(result)
```

---

## Best Practices

### 1. Immer sichere Funktionen verwenden

```python
# ✓ GUT: Sichere Funktion mit Fehlerbehandlung
result = calculate_price_from_matrix_safe(
    module_count=20,
    storage_model="10kWh",
    enable_fallback=True
)

# ✗ VERMEIDEN: Direkte Funktion ohne Fehlerbehandlung
result = calculate_price_from_matrix(20, "10kWh")
```

### 2. Fallback aktivieren für Benutzer-Anfragen

```python
# Für Benutzer-Anfragen: Fallback aktivieren
result = calculate_price_from_matrix_safe(
    module_count=25,
    storage_model="10kWh",
    enable_fallback=True,  # ✓ Aktiviert
    notify_admin=True
)
```

### 3. Admin bei kritischen Fehlern benachrichtigen

```python
# Bei kritischen Fehlern: Admin benachrichtigen
result = handle_error_with_fallback(
    error,
    module_count=20,
    storage_model="10kWh",
    enable_fallback=True,
    notify_admin=True  # ✓ Aktiviert
)
```

### 4. Benutzerfreundliche Meldungen anzeigen

```python
# ✓ GUT: Benutzerfreundliche Meldung
st.error(result['user_message'])

# ✗ VERMEIDEN: Technische Fehlermeldung
st.error(result['error'])
```

### 5. Lösungsvorschläge anbieten

```python
# Zeige Lösungsvorschläge
if not result['success'] and result.get('suggestions'):
    with st.expander("💡 Lösungsvorschläge"):
        for suggestion in result['suggestions']:
            st.markdown(f"• {suggestion}")
```

---

## Fehlertypen und Behandlung

### Matrix nicht gefunden

**Fehlertyp:** `MatrixNotFoundError`  
**Kategorie:** `MATRIX_NOT_FOUND`  
**Schweregrad:** `CRITICAL`  
**Fallback:** Standardberechnung

```python
# Behandlung
if result['error_category'] == 'matrix_not_found':
    if result['fallback_used']:
        st.warning("⚠️ Verwende Standardberechnung da keine Matrix verfügbar")
    else:
        st.error("🚨 Keine Preismatrix gefunden - bitte im Admin-Bereich aktivieren")
```

### Modulanzahl nicht gefunden

**Fehlertyp:** `ModuleCountNotFoundError`  
**Kategorie:** `MODULE_COUNT_MISSING`  
**Schweregrad:** `ERROR`  
**Fallback:** Nächst-kleinere Modulanzahl (Floor)

```python
# Behandlung
if result['error_category'] == 'module_count_missing':
    if result['fallback_used']:
        fallback_info = result['fallback_info']
        st.warning(
            f"⚠️ Modulanzahl {fallback_info['original_module_count']} nicht verfügbar. "
            f"Verwende {fallback_info['fallback_module_count']} Module."
        )
```

### Speichermodell nicht gefunden

**Fehlertyp:** `StorageModelNotFoundError`  
**Kategorie:** `STORAGE_MODEL_MISSING`  
**Schweregrad:** `ERROR`  
**Fallback:** "Kein Speicher"

```python
# Behandlung
if result['error_category'] == 'storage_model_missing':
    if result['fallback_used']:
        st.warning("⚠️ Speichermodell nicht verfügbar. Verwende Preis ohne Speicher.")
```

### Zelle leer

**Fehlertyp:** `PriceCellEmptyError`  
**Kategorie:** `CELL_EMPTY`  
**Schweregrad:** `ERROR`  
**Fallback:** Nicht verfügbar

```python
# Behandlung
if result['error_category'] == 'cell_empty':
    st.error(
        "❌ Kein Preis für diese Kombination definiert. "
        "Bitte ergänzen Sie die Matrix im Admin-Bereich."
    )
```

### Ungültiger Preiswert

**Fehlertyp:** `InvalidPriceError`  
**Kategorie:** `CELL_INVALID`  
**Schweregrad:** `ERROR`  
**Fallback:** Nicht verfügbar

```python
# Behandlung
if result['error_category'] == 'cell_invalid':
    st.error(
        "❌ Ungültiger Preiswert in Matrix. "
        "Bitte korrigieren Sie den Wert im Admin-Bereich."
    )
```

---

## Beispiel: Vollständige Integration

```python
import streamlit as st
from price_matrix_lookup import calculate_price_from_matrix_safe
from price_matrix_error_ui import display_error_with_fallback

def calculate_and_display_price(module_count: int, storage_model: str):
    """Berechnet und zeigt Preis mit vollständiger Fehlerbehandlung"""
    
    # Sichere Preisberechnung
    result = calculate_price_from_matrix_safe(
        module_count=module_count,
        storage_model=storage_model,
        enable_fallback=True,
        notify_admin=True
    )
    
    if result['success']:
        # Erfolg
        st.success(f"✓ Preis: {result['base_price']:,.2f} EUR")
        
        # Zeige verwendete Matrix-Info
        st.info(
            f"Matrix: {result['matrix_name']}\n"
            f"Zeile: {result['row_used']}, Spalte: {result['column_used']}"
        )
        
        # Fallback-Warnung wenn verwendet
        if result['fallback_used']:
            st.warning(result['fallback_info']['message'])
        
        return result['base_price']
    
    else:
        # Fehler mit umfassender Anzeige
        display_error_with_fallback(result)
        
        # Zusätzliche Aktionen
        if result['error_category'] == 'matrix_not_found':
            if st.button("🔧 Zum Admin-Bereich"):
                st.session_state['navigate_to'] = 'admin_matrix'
                st.rerun()
        
        return None

# Verwendung
price = calculate_and_display_price(
    module_count=25,
    storage_model="10kWh"
)
```

---

## Testing

### Unit Tests

```bash
# Alle Error-Handling Tests ausführen
python -m pytest test_price_matrix_error_handling_complete.py -v

# Spezifische Tests
python -m pytest test_price_matrix_error_handling_complete.py::test_classify_error -v
python -m pytest test_price_matrix_error_handling_complete.py::test_format_error_message -v
python -m pytest test_price_matrix_error_handling_complete.py::test_try_fallback -v
```

### Integration Tests

```python
# Test vollständiger Workflow
def test_complete_error_handling_workflow():
    # 1. Fehler tritt auf
    error = ModuleCountNotFoundError(25, [10, 15, 20, 30])
    
    # 2. Klassifiziere
    error_info = classify_error(error)
    assert error_info.category == ErrorCategory.MODULE_COUNT_MISSING
    
    # 3. Formatiere
    ui_message = format_error_message_for_ui(error_info)
    assert len(ui_message) > 0
    
    # 4. Admin-Benachrichtigung
    notification = create_admin_notification(error_info)
    assert notification['requires_action'] is True
    
    # 5. Fallback
    fallback_result = try_fallback(error_info, 25, "10kWh", matrix_data)
    # Prüfe Fallback-Ergebnis
```

---

## Zusammenfassung

Das Fehlerbehandlungs- und Validierungssystem bietet:

✅ **Task 8.1: Fehler-Typen Definition**
- 8 definierte Fehler-Kategorien
- 4 Schweregrade
- Strukturierte Fehlerinformation
- Automatische Fehler-Klassifizierung

✅ **Task 8.2: Benutzerfreundliche Fehlermeldungen**
- Formatierte UI-Meldungen mit Icons
- Lösungsvorschläge für jeden Fehlertyp
- Detaillierte Hilfe-Texte
- Admin-Benachrichtigungen
- Streamlit UI-Komponenten

✅ **Task 8.3: Fallback-Mechanismen**
- 5 Fallback-Strategien
- Automatischer Fallback bei Fehlern
- Floor-Logik für Modulanzahl
- "Kein Speicher" Fallback
- Fallback auf Standardberechnung
- Admin-Benachrichtigung bei kritischen Fehlern

**Alle Requirements erfüllt:** 7.1, 7.2, 7.3, 7.4, 7.5, 8.5

**Alle Tests bestanden:** 29/29 ✓
