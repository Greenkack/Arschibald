# Preismatrix Extras - Quick Reference

## Übersicht

Im Preismatrix-Modus enthält der Basispreis bereits Standardkomponenten. Zusätzlich werden nur Sonderprodukte, Extras und zusätzliche Dienstleistungen berechnet.

## Standardprodukte (im Basispreis enthalten)

- PV-Module
- Wechselrichter
- Batteriespeicher
- Standard-Montage
- Standard-Installation

## Sonderprodukte (zusätzlich berechnet)

Produkte mit `is_special_product = 1` in der Datenbank.

### Produkt als Sonderprodukt markieren

```python
from special_products import mark_product_as_special

# Markieren
mark_product_as_special(product_id=123, is_special=True)

# Entfernen
mark_product_as_special(product_id=123, is_special=False)
```

### Prüfen ob Sonderprodukt

```python
from special_products import is_special_product, is_special_product_by_name

# Nach ID
if is_special_product(product_id=123):
    print("Ist Sonderprodukt")

# Nach Name
if is_special_product_by_name("Spezial-Optimierer XYZ"):
    print("Ist Sonderprodukt")
```

### Alle Sonderprodukte abrufen

```python
from special_products import get_special_products

# Alle Sonderprodukte
all_special = get_special_products()

# Nach Kategorie filtern
special_modules = get_special_products(category="PV-Module")
```

## Extras hinzufügen

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

## Extras berechnen

```python
from matrix_extras_calculator import calculate_all_extras

result = calculate_all_extras(details)

# Ergebnis-Struktur:
{
    'total': 1500.0,  # Gesamtsumme
    'special_products': {
        'total': 900.0,
        'items': [...],
        'count': 2
    },
    'services': {
        'total': 350.0,
        'items': [...],
        'count': 1
    },
    'extras': {
        'total': 250.0,
        'items': [...],
        'count': 1
    },
    'breakdown': [...]  # Detaillierte Liste
}
```

## Rabatte und Aufpreise

```python
from matrix_extras_calculator import apply_discounts_and_surcharges

base_amount = 20000.0
details = {
    'discount_percent': 10.0,  # 10% Rabatt
    'surcharge_percent': 5.0   # 5% Aufpreis
}

result = apply_discounts_and_surcharges(base_amount, details)

# Ergebnis:
{
    'base_amount': 20000.0,
    'discount_amount': 2000.0,
    'surcharge_amount': 900.0,  # 5% von 18000
    'final_amount': 18900.0
}
```

## Vollständige Preisberechnung

```python
from solar_calculator import get_total_price_with_matrix_mode

details = {
    'module_quantity': 20,
    'selected_storage_name': '15kWh',
    'additional_extras': [
        {'name': 'Gerüst', 'price': 250.0, 'quantity': 1}
    ]
}

result = get_total_price_with_matrix_mode(details)

if result['success']:
    print(f"Basispreis: {result['base_price']} EUR")
    print(f"Extras: {result['extras_price']} EUR")
    print(f"Netto-Gesamt: {result['net_total']} EUR")
    print(f"MwSt: {result['vat_amount']} EUR")
    print(f"Brutto-Gesamt: {result['gross_total']} EUR")
else:
    print(f"Fehler: {result['error']}")
```

## Datenbank-Schema

```sql
-- Produkte Tabelle
ALTER TABLE products ADD COLUMN is_special_product INTEGER DEFAULT 0;

-- Sonderprodukt markieren
UPDATE products 
SET is_special_product = 1 
WHERE model_name = 'Spezial-Optimierer XYZ';

-- Alle Sonderprodukte anzeigen
SELECT id, model_name, category, price_euro 
FROM products 
WHERE is_special_product = 1;
```

## API-Referenz

### special_products.py

```python
is_special_product(product_id: int) -> bool
is_special_product_by_name(model_name: str) -> bool
get_special_products(category: Optional[str] = None) -> list[dict]
mark_product_as_special(product_id: int, is_special: bool = True) -> bool
get_standard_product_categories() -> list[str]
is_standard_product_category(category: str) -> bool
filter_special_products_from_selection(selected_products: list) -> list
```

### matrix_extras_calculator.py

```python
calculate_special_products_cost(details: dict) -> dict
calculate_services_cost(details: dict) -> dict
calculate_extras_cost(details: dict) -> dict
apply_discounts_and_surcharges(base_amount: float, details: dict) -> dict
calculate_all_extras(details: dict) -> dict
```

## Fehlerbehandlung

```python
try:
    result = calculate_all_extras(details)
    if result['total'] > 0:
        print(f"Extras: {result['total']} EUR")
except Exception as e:
    print(f"Fehler bei Extras-Berechnung: {e}")
```

## Best Practices

1. **Sonderprodukte sparsam verwenden**: Nur Produkte markieren, die wirklich zusätzlich zum Basispreis berechnet werden sollen.

2. **Klare Beschreibungen**: Extras sollten aussagekräftige Namen und Beschreibungen haben.

3. **Mengen prüfen**: Immer `quantity` angeben, auch wenn es 1 ist.

4. **Preise validieren**: Sicherstellen dass Preise numerisch und positiv sind.

5. **Fehlerbehandlung**: Immer `success` Flag prüfen bei Preisberechnungen.

## Beispiel: Komplette Integration

```python
from database import get_pricing_calculation_mode
from price_matrix_lookup import calculate_price_from_matrix
from matrix_extras_calculator import calculate_all_extras

# 1. Prüfe Modus
pricing_mode = get_pricing_calculation_mode()

if pricing_mode == "matrix":
    # 2. Hole Basispreis
    matrix_result = calculate_price_from_matrix(
        module_count=20,
        storage_model="15kWh"
    )
    
    if matrix_result['success']:
        base_price = matrix_result['base_price']
        
        # 3. Berechne Extras
        extras_result = calculate_all_extras(details)
        extras_total = extras_result['total']
        
        # 4. Summiere
        net_total = base_price + extras_total
        vat_amount = net_total * 0.19
        gross_total = net_total + vat_amount
        
        print(f"Basispreis: {base_price} EUR")
        print(f"Extras: {extras_total} EUR")
        print(f"Netto: {net_total} EUR")
        print(f"MwSt: {vat_amount} EUR")
        print(f"Brutto: {gross_total} EUR")
```

## Troubleshooting

### Problem: Produkt wird nicht als Sonderprodukt erkannt

**Lösung:**
```python
# Prüfe Datenbank
from database import get_db_connection
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT is_special_product FROM products WHERE id = ?", (123,))
print(cursor.fetchone())
conn.close()

# Markiere explizit
mark_product_as_special(123, True)
```

### Problem: Extras werden nicht berechnet

**Lösung:**
```python
# Prüfe Format
details['additional_extras'] = [
    {
        'name': 'Test',  # MUSS vorhanden sein
        'price': 100.0,  # MUSS numerisch sein
        'quantity': 1    # MUSS vorhanden sein
    }
]
```

### Problem: Services werden doppelt berechnet

**Lösung:**
- Standard-Services sind im Basispreis enthalten
- Nur optionale Services werden zusätzlich berechnet
- Prüfe `is_standard` Flag in Services

## Support

Bei Fragen oder Problemen:
1. Prüfe `TASK_7_MATRIX_EXTRAS_COMPLETE.md` für Details
2. Führe `test_task7_matrix_extras.py` aus
3. Prüfe Logs für Fehlermeldungen
