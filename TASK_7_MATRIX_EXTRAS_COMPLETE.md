# Task 7: Zusatzkosten-Logik für Sonderprodukte - ABGESCHLOSSEN

## Übersicht

Task 7 implementiert die vollständige Logik zur Berechnung von Zusatzkosten im Preismatrix-Modus. Im Preismatrix-Modus enthält der Basispreis bereits die Standardkomponenten (Module, Wechselrichter, Speicher, Standard-Montage). Zusätzlich werden nur Sonderprodukte, Extras und zusätzliche Dienstleistungen berechnet.

## Implementierte Subtasks

### 7.1 Sonderprodukte identifizieren ✅

**Implementierung:**

1. **Datenbank-Erweiterung** (`product_db.py`):
   - Neues Feld `is_special_product` (INTEGER, 0/1 boolean) zur `products` Tabelle hinzugefügt
   - Automatische Migration für bestehende Datenbanken

2. **Sonderprodukt-Modul** (`special_products.py`):
   ```python
   # Hauptfunktionen:
   - is_special_product(product_id: int) -> bool
   - is_special_product_by_name(model_name: str) -> bool
   - get_special_products(category: Optional[str]) -> list[dict]
   - mark_product_as_special(product_id: int, is_special: bool) -> bool
   - filter_special_products_from_selection(selected_products: list) -> list
   ```

3. **Standardprodukt-Kategorien**:
   - PV-Module
   - Wechselrichter
   - Batteriespeicher/Speicher/Storage
   
   Diese Kategorien sind im Preismatrix-Basispreis enthalten und werden NICHT zusätzlich berechnet.

**Verwendung:**

```python
from special_products import mark_product_as_special, is_special_product

# Produkt als Sonderprodukt markieren
mark_product_as_special(product_id=123, is_special=True)

# Prüfen ob Produkt ein Sonderprodukt ist
if is_special_product(product_id=123):
    # Zusätzlich zum Basispreis berechnen
    pass
```

### 7.2 Extras und Dienstleistungen ✅

**Implementierung:**

**Matrix Extras Calculator** (`matrix_extras_calculator.py`):

Umfassende Berechnung aller Zusatzkosten mit folgenden Funktionen:

1. **`calculate_special_products_cost(details)`**:
   - Identifiziert Sonderprodukte in der Auswahl
   - Berechnet Kosten basierend auf Menge und Einzelpreis
   - Unterstützt: Module, Wechselrichter, Speicher, Zusatzkomponenten

2. **`calculate_services_cost(details)`**:
   - Integration mit `services_integration.py`
   - Berechnet nur optionale/zusätzliche Dienstleistungen
   - Standard-Dienstleistungen sind im Basispreis enthalten

3. **`calculate_extras_cost(details)`**:
   - Benutzerdefinierte Extras aus `details['additional_extras']`
   - Custom Items aus Session State
   - Flexible Mengen und Preise

4. **`apply_discounts_and_surcharges(base_amount, details)`**:
   - Prozentuale Rabatte
   - Festbetrags-Rabatte
   - Prozentuale Aufpreise
   - Festbetrags-Aufpreise
   - Detaillierte Aufschlüsselung

5. **`calculate_all_extras(details)`**:
   - Kombiniert alle Kategorien
   - Erstellt vollständige Aufschlüsselung
   - Strukturiertes Ergebnis für UI-Anzeige

**Rückgabe-Struktur:**

```python
{
    'total': float,  # Gesamtsumme aller Extras
    'special_products': {
        'total': float,
        'items': [
            {
                'name': str,
                'category': str,
                'unit_price': float,
                'quantity': int,
                'price': float
            }
        ],
        'count': int
    },
    'services': {
        'total': float,
        'items': [...],
        'count': int
    },
    'extras': {
        'total': float,
        'items': [...],
        'count': int
    },
    'breakdown': [
        {
            'category': str,  # 'Sonderprodukt', 'Dienstleistung', 'Extra'
            'name': str,
            'quantity': int,
            'unit_price': float,
            'total_price': float,
            'description': str  # optional
        }
    ]
}
```

### 7.3 Preisaufschlüsselung ✅

**Implementierung:**

**Solar Calculator Integration** (`solar_calculator.py`):

1. **`_calculate_matrix_extras_detailed(details)`** - Aktualisiert:
   - Verwendet `matrix_extras_calculator.calculate_all_extras()`
   - Konvertiert Ergebnis in erwartetes Format
   - Fallback für fehlende Module

2. **`_display_matrix_pricing(details, texts)`** - Verbessert:
   - Detaillierte Aufschlüsselung in Expander
   - Zeigt Menge × Einzelpreis = Gesamtpreis
   - Beschreibungen für Dienstleistungen und Extras
   - Übersichtliche Kategorisierung

**UI-Anzeige:**

```
💰 Preisübersicht (Preismatrix-Modus)

📊 Matrix-Lookup-Details
  Verwendete Matrix: Preisliste 2024
  Modulanzahl: 20 → Zeile: 20
  Speichermodell: 15kWh → Spalte: 15kWh
  Gefundener Basispreis: 18.500,00 €

Preisaufschlüsselung
  Basispreis (aus Preismatrix):        18.500,00 €
  + Extras & Sonderprodukte:           + 2.350,00 €
  
  🔍 Extras-Details
    Sonderprodukte:
    - Sondermodul XYZ: 2x 450,00 € = 900,00 €
    
    Dienstleistungen:
    - Zusätzliche Elektroinstallation: 1.200,00 €
      Verlegung zusätzlicher Leitungen
    
    Zusätzliche Extras:
    - Gerüstmiete: 250,00 €
  
  ─────────────────────────────────────────────
  Netto-Gesamtpreis:                   20.850,00 €
  + MwSt. (19%):                       + 3.961,50 €
  ─────────────────────────────────────────────
  🎯 Brutto-Gesamtpreis:               24.811,50 €

ℹ️ Hinweis: Im Preismatrix-Modus sind Standard-Aufschläge 
(Montage, Installation, etc.) deaktiviert. Der Basispreis 
aus der Matrix ist ein schlüsselfertiger Preis. Nur explizit 
ausgewählte Extras und Sonderprodukte werden hinzugefügt.
```

## Datenfluss

```
1. Benutzer wählt Komponenten im Solar Calculator
   ↓
2. System prüft Preisberechnungsmodus (database.get_pricing_calculation_mode())
   ↓
3. Bei "matrix" Modus:
   a) Hole Basispreis aus Matrix (price_matrix_lookup.calculate_price_from_matrix())
   b) Berechne Extras (matrix_extras_calculator.calculate_all_extras())
      - Identifiziere Sonderprodukte (special_products.is_special_product())
      - Berechne Services (services_integration)
      - Berechne Extras
   c) Summiere: Basispreis + Extras = Netto-Gesamt
   d) Berechne MwSt und Brutto-Gesamt
   ↓
4. Zeige detaillierte Aufschlüsselung in UI
   ↓
5. Speichere in Session State für PDF-Generierung
```

## Verwendete Module

### Neue Module:
- `special_products.py` - Sonderprodukt-Identifikation
- `matrix_extras_calculator.py` - Extras-Berechnung

### Erweiterte Module:
- `product_db.py` - Neues Feld `is_special_product`
- `solar_calculator.py` - Verbesserte Matrix-Preisanzeige

### Integrierte Module:
- `price_matrix_lookup.py` - Basispreis-Lookup
- `services_integration.py` - Dienstleistungen
- `database.py` - Preisberechnungsmodus

## Konfiguration

### Produkt als Sonderprodukt markieren:

**Option 1: Direkt in Datenbank**
```sql
UPDATE products 
SET is_special_product = 1 
WHERE model_name = 'Spezial-Optimierer XYZ';
```

**Option 2: Über Python-API**
```python
from special_products import mark_product_as_special

# Produkt als Sonderprodukt markieren
mark_product_as_special(product_id=123, is_special=True)

# Markierung entfernen
mark_product_as_special(product_id=123, is_special=False)
```

**Option 3: Admin-Panel** (zukünftige Erweiterung)
- Checkbox "Als Sonderprodukt markieren" in Produktverwaltung

### Extras hinzufügen:

```python
# In project_details
details['additional_extras'] = [
    {
        'name': 'Gerüstmiete',
        'price': 250.0,
        'quantity': 1,
        'description': 'Gerüst für 2 Wochen'
    },
    {
        'name': 'Zusätzliche Kabel',
        'price': 15.0,
        'quantity': 50,
        'description': '50m Solarkabel'
    }
]
```

## Testing

### Unit Tests:

```python
# Test Sonderprodukt-Identifikation
def test_is_special_product():
    # Produkt als Sonderprodukt markieren
    mark_product_as_special(product_id=1, is_special=True)
    assert is_special_product(product_id=1) == True
    
    # Markierung entfernen
    mark_product_as_special(product_id=1, is_special=False)
    assert is_special_product(product_id=1) == False

# Test Extras-Berechnung
def test_calculate_all_extras():
    details = {
        'additional_extras': [
            {'name': 'Test Extra', 'price': 100.0, 'quantity': 2}
        ]
    }
    result = calculate_all_extras(details)
    assert result['total'] == 200.0
    assert len(result['extras']['items']) == 1
```

### Integrationstests:

```python
# Test vollständige Preisberechnung im Matrix-Modus
def test_matrix_pricing_with_extras():
    details = {
        'module_quantity': 20,
        'selected_storage_name': '15kWh',
        'additional_extras': [
            {'name': 'Gerüst', 'price': 250.0, 'quantity': 1}
        ]
    }
    
    result = get_total_price_with_matrix_mode(details)
    
    assert result['success'] == True
    assert result['base_price'] > 0
    assert result['extras_price'] == 250.0
    assert result['net_total'] == result['base_price'] + 250.0
```

## Anforderungen erfüllt

✅ **Requirement 6.1**: Sonderprodukte werden identifiziert und zum Preismatrix-Preis addiert
✅ **Requirement 6.2**: Zusätzliche Dienstleistungen werden zum Preismatrix-Preis addiert
✅ **Requirement 6.3**: Extras und Sonderwünsche werden zum Preismatrix-Preis addiert
✅ **Requirement 6.4**: Rabatte werden vom Gesamtpreis abgezogen
✅ **Requirement 6.5**: Aufpreise werden zum Gesamtpreis addiert
✅ **Requirement 6.6**: Detaillierte Preisaufschlüsselung wird angezeigt

## Nächste Schritte

### Task 8: Fehlerbehandlung und Validierung
- Fehlertypen definieren
- Benutzerfreundliche Fehlermeldungen
- Fallback-Mechanismen

### Task 9: Rückwärtskompatibilität
- Bestehende Funktionen testen
- Default-Verhalten sicherstellen

### Task 10: Testing (Optional)
- Unit Tests für alle neuen Funktionen
- Integrationstests für End-to-End Szenarien

### Task 11: Dokumentation (Optional)
- Benutzer-Dokumentation
- Entwickler-Dokumentation

## Zusammenfassung

Task 7 implementiert die vollständige Zusatzkosten-Logik für den Preismatrix-Modus:

1. **Sonderprodukte** können in der Datenbank markiert werden (`is_special_product = 1`)
2. **Extras und Dienstleistungen** werden automatisch erkannt und berechnet
3. **Detaillierte Aufschlüsselung** zeigt alle Positionen übersichtlich an
4. **Rabatte und Aufpreise** können flexibel angewendet werden

Die Implementierung ist modular, erweiterbar und vollständig in den bestehenden Solar Calculator integriert.
