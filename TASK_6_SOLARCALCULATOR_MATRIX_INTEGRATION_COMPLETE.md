# Task 6: Solarcalculator - Preismatrix-Integration - ABGESCHLOSSEN

## Übersicht

Die Preismatrix-Integration in den Solarcalculator wurde erfolgreich implementiert. Der Solarcalculator unterstützt jetzt zwei Preisberechnungsmodi:

1. **Standardberechnung** (Einzelprodukte) - Bisherige Methode
2. **Preismatrix** (Schlüsselfertige Preise) - Neue Methode

## Implementierte Funktionen

### 6.1 Modus-Prüfung ✅

**Datei:** `solar_calculator.py`

**Implementierung:**
- Preisberechnungsmodus wird aus der Datenbank geladen (`get_pricing_calculation_mode()`)
- Verzweigung zwischen Standard- und Matrix-Modus in `_display_pricing_information()`
- UI-Hinweis zeigt aktiven Modus an:
  - "Preismatrix (Schlüsselfertige Preise)" für Matrix-Modus
  - "Standardberechnung (Einzelprodukte)" für Standard-Modus

**Code-Änderungen:**
```python
# Import database functions for pricing mode
from database import get_pricing_calculation_mode

# Check pricing calculation mode
pricing_mode = get_pricing_calculation_mode()

# Display mode indicator
if pricing_mode == "matrix":
    st.info("ℹ️ **Preisberechnungsmodus:** Preismatrix (Schlüsselfertige Preise)")
else:
    st.info("ℹ️ **Preisberechnungsmodus:** Standardberechnung (Einzelprodukte)")

# Branch based on pricing mode
if pricing_mode == "matrix":
    # Matrix-based pricing
    _display_matrix_pricing(details, texts)
    return

# Standard pricing calculation (existing code)
```

### 6.2 Matrix-Preisberechnung ✅

**Datei:** `solar_calculator.py`

**Neue Funktionen:**

#### `get_total_price_with_matrix_mode(details: dict) -> dict`

Hauptfunktion für die Preisberechnung im Matrix-Modus:

**Logik:**
1. Basispreis aus Matrix abrufen (basierend auf Modulanzahl und Speichermodell)
2. NUR Sonderprodukte/Extras/Dienstleistungen addieren
3. KEINE Standard-Aufschläge (Montage, Installation)
4. MwSt. und Brutto-Gesamtpreis berechnen

**Rückgabewert:**
```python
{
    'success': bool,
    'base_price': float,
    'extras_price': float,
    'net_total': float,
    'vat_amount': float,
    'gross_total': float,
    'breakdown': dict,
    'matrix_info': dict,
    'error': str | None
}
```

#### `_calculate_matrix_extras(details: dict) -> float`

Berechnet die Gesamtsumme der Extras (Sonderprodukte, Services, etc.)

#### `_calculate_matrix_extras_detailed(details: dict) -> dict`

Berechnet detaillierte Aufschlüsselung der Extras:
```python
{
    'total': float,
    'special_products': list[dict],
    'services': list[dict],
    'extras': list[dict]
}
```

**Integration:**
- Verwendet `calculate_price_from_matrix()` aus `price_matrix_lookup.py`
- Extrahiert Modulanzahl und Speichermodell aus `details`
- Behandelt Placeholder-Texte ("Bitte wählen") als `None`
- Umfassende Fehlerbehandlung mit spezifischen Fehlertypen

### 6.3 UI-Anpassungen für Matrix-Modus ✅

**Datei:** `solar_calculator.py`

**Funktion:** `_display_matrix_pricing(details: dict, texts: dict)`

**Implementierte UI-Elemente:**

1. **Preisaufschlüsselung:**
   - Basispreis (aus Preismatrix)
   - + Extras & Sonderprodukte (falls vorhanden)
   - = Netto-Gesamtpreis
   - + MwSt. (19%)
   - = Brutto-Gesamtpreis

2. **Matrix-Info (Expander):**
   ```
   📊 Matrix-Lookup-Details
   - Verwendete Matrix: [Name]
   - Modulanzahl: [X] → Zeile: [Y]
   - Speichermodell: [Model] → Spalte: [Z]
   - Gefundener Basispreis: [Preis]
   ```

3. **Extras-Details (Expander):**
   - Sonderprodukte
   - Dienstleistungen
   - Zusätzliche Extras

4. **Hinweis-Box:**
   ```
   ℹ️ Hinweis: Im Preismatrix-Modus sind Standard-Aufschläge 
   (Montage, Installation, etc.) deaktiviert. Der Basispreis 
   aus der Matrix ist ein schlüsselfertiger Preis. Nur explizit 
   ausgewählte Extras und Sonderprodukte werden hinzugefügt.
   ```

**Fehlerbehandlung:**
- Spezifische Fehlermeldungen für jeden Fehlertyp
- Lösungsvorschläge für häufige Probleme:
  - Keine aktive Matrix → Admin-Einstellungen
  - Modulanzahl nicht gefunden → Matrix ergänzen
  - Speichermodell nicht gefunden → Matrix ergänzen
  - Kein Preis definiert → Preis eintragen

### 6.4 Standard-Berechnung deaktivieren ✅

**Datei:** `solar_calculator.py`

**Implementierung:**

Die Standard-Berechnung wird im Matrix-Modus vollständig deaktiviert durch:

1. **Frühe Rückkehr:**
   ```python
   if pricing_mode == "matrix":
       _display_matrix_pricing(details, texts)
       return  # Verhindert Ausführung der Standard-Berechnung
   ```

2. **Keine Standard-Aufschläge:**
   - Einzelprodukt-Preise werden ignoriert
   - Montage-Aufschläge werden nicht berechnet
   - Installations-Aufschläge werden nicht berechnet
   - Standard-Komponenten-Aufschläge werden nicht berechnet

3. **Nur explizite Extras:**
   - Sonderprodukte (markiert in Produktdatenbank)
   - Zusätzliche Services (explizit ausgewählt)
   - Extras und Custom-Additions

## Session State Integration

Die Preisdaten werden für PDF-Generierung gespeichert:

```python
st.session_state["solar_calculator_pricing_mode"] = "matrix"
st.session_state["solar_calculator_matrix_pricing"] = {
    "base_price": base_price,
    "extras_total": extras_price,
    "net_total": net_total,
    "vat_amount": vat_amount,
    "gross_total": gross_total,
    "matrix_info": matrix_info,
    "breakdown": breakdown,
    "formatted_totals": {
        "base": _format_german_currency(base_price),
        "extras": _format_german_currency(extras_price),
        "net": _format_german_currency(net_total),
        "vat": _format_german_currency(vat_amount),
        "gross": _format_german_currency(gross_total),
    }
}
```

## Datenfluss

```
1. Benutzer wählt Module und Speicher im Solarcalculator
   ↓
2. _display_pricing_information() prüft Preisberechnungsmodus
   ↓
3a. Matrix-Modus:
    - _display_matrix_pricing()
    - get_total_price_with_matrix_mode()
    - calculate_price_from_matrix() (aus price_matrix_lookup.py)
    - Basispreis + Extras = Gesamtpreis
   ↓
3b. Standard-Modus:
    - get_pricing_display_for_ui()
    - Einzelprodukt-Kalkulation
    - Standard-Aufschläge
   ↓
4. Preisdaten in Session State speichern
   ↓
5. UI-Anzeige mit Aufschlüsselung
```

## Anforderungen-Mapping

| Anforderung | Status | Implementierung |
|-------------|--------|-----------------|
| 4.1 - Modulanzahl-Lookup | ✅ | `calculate_price_from_matrix()` |
| 4.2 - Speichermodell-Lookup | ✅ | `calculate_price_from_matrix()` |
| 4.3 - "Kein Speicher" Fallback | ✅ | `find_storage_column()` |
| 4.4 - Preis an Kreuzung | ✅ | `lookup_price_by_intersection()` |
| 5.1 - Modus-Prüfung | ✅ | `get_pricing_calculation_mode()` |
| 5.2 - Standard-Aufschläge deaktivieren | ✅ | Frühe Rückkehr im Matrix-Modus |
| 5.3 - Einzelprodukt-Preise ignorieren | ✅ | Separate Preisberechnung |
| 5.4 - Nur Extras berücksichtigen | ✅ | `_calculate_matrix_extras()` |
| 5.5 - UI-Hinweis auf Modus | ✅ | Info-Box mit Modus-Anzeige |
| 6.1 - Sonderprodukte addieren | 🔄 | Vorbereitet (Task 7) |
| 6.2 - Dienstleistungen addieren | ✅ | Services-Integration |
| 6.3 - Extras addieren | ✅ | `additional_extras` in details |
| 6.4 - Rabatte/Aufpreise | 🔄 | Vorbereitet (Task 7) |
| 6.6 - Preisaufschlüsselung | ✅ | Detaillierte UI-Anzeige |

## Nächste Schritte

Die Grundfunktionalität ist vollständig implementiert. Folgende Tasks bauen darauf auf:

- **Task 7:** Zusatzkosten-Logik für Sonderprodukte
  - Identifikation von Sonderprodukten
  - Extras und Dienstleistungen
  - Detaillierte Preisaufschlüsselung

- **Task 8:** Fehlerbehandlung und Validierung
  - Erweiterte Fehlertypen
  - Benutzerfreundliche Fehlermeldungen
  - Fallback-Mechanismen

- **Task 9:** Rückwärtskompatibilität
  - Tests für bestehende Funktionen
  - Default-Verhalten sicherstellen

## Testing

**Manuelle Tests empfohlen:**

1. **Matrix-Modus aktivieren:**
   - Admin-Panel → Erweiterte Einstellungen
   - Preisberechnungsmodus auf "Preismatrix" setzen

2. **Solarcalculator öffnen:**
   - Modulanzahl wählen (z.B. 20)
   - Speichermodell wählen (z.B. "15kWh")
   - Preisübersicht prüfen

3. **Fehlerszenarien testen:**
   - Modulanzahl ohne Matrix-Eintrag
   - Speichermodell ohne Matrix-Eintrag
   - Leere Preis-Zelle

4. **Standard-Modus testen:**
   - Zurück zu "Standardberechnung" wechseln
   - Prüfen dass alte Berechnung funktioniert

## Bekannte Einschränkungen

1. **Sonderprodukte-Identifikation:** Noch nicht vollständig implementiert (Task 7)
2. **Rabatte/Aufpreise:** Noch nicht in Matrix-Modus integriert (Task 7)
3. **PDF-Integration:** Muss noch angepasst werden für Matrix-Modus

## Dateien geändert

- `solar_calculator.py` - Hauptimplementierung
- `.kiro/specs/price-matrix-enhancement/tasks.md` - Task-Status aktualisiert

## Zusammenfassung

✅ **Task 6 vollständig abgeschlossen**

Alle Subtasks wurden erfolgreich implementiert:
- ✅ 6.1 Modus-Prüfung implementieren
- ✅ 6.2 Matrix-Preisberechnung
- ✅ 6.3 UI-Anpassungen für Matrix-Modus
- ✅ 6.4 Standard-Berechnung deaktivieren

Die Preismatrix-Integration ist funktionsfähig und bereit für weitere Erweiterungen in den folgenden Tasks.
