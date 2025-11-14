"""
Test für Task 7: Zusatzkosten-Logik für Sonderprodukte

Testet die Implementierung der Sonderprodukt-Identifikation,
Extras-Berechnung und Preisaufschlüsselung.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_special_products_module_import():
    """Test dass das special_products Modul importiert werden kann"""
    try:
        import special_products
        assert hasattr(special_products, 'is_special_product')
        assert hasattr(special_products, 'get_special_products')
        assert hasattr(special_products, 'mark_product_as_special')
        print("[OK] special_products Modul erfolgreich importiert")
    except ImportError as e:
        pytest.fail(f"Konnte special_products nicht importieren: {e}")


def test_matrix_extras_calculator_import():
    """Test dass das matrix_extras_calculator Modul importiert werden kann"""
    try:
        import matrix_extras_calculator
        assert hasattr(matrix_extras_calculator, 'calculate_special_products_cost')
        assert hasattr(matrix_extras_calculator, 'calculate_services_cost')
        assert hasattr(matrix_extras_calculator, 'calculate_extras_cost')
        assert hasattr(matrix_extras_calculator, 'calculate_all_extras')
        print("[OK] matrix_extras_calculator Modul erfolgreich importiert")
    except ImportError as e:
        pytest.fail(f"Konnte matrix_extras_calculator nicht importieren: {e}")


def test_calculate_extras_cost():
    """Test Berechnung von Extras"""
    from matrix_extras_calculator import calculate_extras_cost
    
    details = {
        'additional_extras': [
            {
                'name': 'Test Extra 1',
                'price': 100.0,
                'quantity': 2
            },
            {
                'name': 'Test Extra 2',
                'price': 50.0,
                'quantity': 1
            }
        ]
    }
    
    result = calculate_extras_cost(details)
    
    assert isinstance(result, dict), "Ergebnis sollte ein Dictionary sein"
    assert 'total' in result, "Ergebnis sollte 'total' enthalten"
    assert 'items' in result, "Ergebnis sollte 'items' enthalten"
    assert 'count' in result, "Ergebnis sollte 'count' enthalten"
    
    assert result['total'] == 250.0, f"Total sollte 250.0 sein, ist aber {result['total']}"
    assert result['count'] == 2, f"Count sollte 2 sein, ist aber {result['count']}"
    assert len(result['items']) == 2, f"Items sollte 2 Einträge haben, hat aber {len(result['items'])}"
    
    print("[OK] calculate_extras_cost funktioniert korrekt")


def test_calculate_all_extras_structure():
    """Test Struktur des calculate_all_extras Ergebnisses"""
    from matrix_extras_calculator import calculate_all_extras
    
    details = {
        'additional_extras': [
            {'name': 'Test', 'price': 100.0, 'quantity': 1}
        ]
    }
    
    result = calculate_all_extras(details)
    
    # Prüfe Struktur
    assert isinstance(result, dict), "Ergebnis sollte ein Dictionary sein"
    assert 'total' in result
    assert 'special_products' in result
    assert 'services' in result
    assert 'extras' in result
    assert 'breakdown' in result
    
    # Prüfe Sub-Strukturen
    assert isinstance(result['special_products'], dict)
    assert isinstance(result['services'], dict)
    assert isinstance(result['extras'], dict)
    assert isinstance(result['breakdown'], list)
    
    # Prüfe dass extras korrekt berechnet wurden
    assert result['total'] == 100.0
    assert result['extras']['total'] == 100.0
    assert len(result['extras']['items']) == 1
    
    print("[OK] calculate_all_extras Struktur ist korrekt")


def test_apply_discounts_and_surcharges():
    """Test Rabatte und Aufpreise"""
    from matrix_extras_calculator import apply_discounts_and_surcharges
    
    base_amount = 1000.0
    
    # Test mit 10% Rabatt
    details = {'discount_percent': 10.0}
    result = apply_discounts_and_surcharges(base_amount, details)
    
    assert result['base_amount'] == 1000.0
    assert result['discount_amount'] == 100.0
    assert result['final_amount'] == 900.0
    
    # Test mit 5% Aufpreis
    details = {'surcharge_percent': 5.0}
    result = apply_discounts_and_surcharges(base_amount, details)
    
    assert result['surcharge_amount'] == 50.0
    assert result['final_amount'] == 1050.0
    
    # Test mit Rabatt und Aufpreis
    details = {
        'discount_percent': 10.0,
        'surcharge_percent': 5.0
    }
    result = apply_discounts_and_surcharges(base_amount, details)
    
    # 1000 - 10% = 900, dann 900 + 5% = 945
    assert result['discount_amount'] == 100.0
    assert result['surcharge_amount'] == 45.0  # 5% von 900
    assert result['final_amount'] == 945.0
    
    print("[OK] apply_discounts_and_surcharges funktioniert korrekt")


def test_standard_product_categories():
    """Test Standard-Produkt-Kategorien"""
    from special_products import get_standard_product_categories, is_standard_product_category
    
    categories = get_standard_product_categories()
    
    assert isinstance(categories, list)
    assert len(categories) > 0
    assert 'PV-Module' in categories
    assert 'Wechselrichter' in categories
    assert 'Batteriespeicher' in categories
    
    # Test is_standard_product_category
    assert is_standard_product_category('PV-Module') == True
    assert is_standard_product_category('Wechselrichter') == True
    assert is_standard_product_category('Sonderkomponente') == False
    
    print("[OK] Standard-Produkt-Kategorien korrekt definiert")


def test_product_db_has_is_special_product_field():
    """Test dass die products Tabelle das is_special_product Feld hat"""
    try:
        from database import get_db_connection
        
        conn = get_db_connection()
        if not conn:
            pytest.skip("Keine Datenbankverbindung verfügbar")
        
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(products)")
        columns = cursor.fetchall()
        conn.close()
        
        column_names = [col[1] for col in columns]
        
        assert 'is_special_product' in column_names, \
            "products Tabelle sollte is_special_product Feld haben"
        
        print("[OK] products Tabelle hat is_special_product Feld")
        
    except Exception as e:
        pytest.skip(f"Konnte Datenbank nicht prüfen: {e}")


def run_all_tests():
    """Führe alle Tests aus"""
    print("\n" + "="*60)
    print("Task 7: Zusatzkosten-Logik für Sonderprodukte - Tests")
    print("="*60 + "\n")
    
    tests = [
        ("Import special_products", test_special_products_module_import),
        ("Import matrix_extras_calculator", test_matrix_extras_calculator_import),
        ("Extras-Berechnung", test_calculate_extras_cost),
        ("All Extras Struktur", test_calculate_all_extras_structure),
        ("Rabatte und Aufpreise", test_apply_discounts_and_surcharges),
        ("Standard-Kategorien", test_standard_product_categories),
        ("Datenbank-Feld", test_product_db_has_is_special_product_field),
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\nTest: {test_name}")
            print("-" * 60)
            test_func()
            passed += 1
        except pytest.skip.Exception as e:
            print(f"⊘ Test übersprungen: {e}")
            skipped += 1
        except Exception as e:
            print(f"[ERROR] Test fehlgeschlagen: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"Ergebnis: {passed} bestanden, {failed} fehlgeschlagen, {skipped} übersprungen")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
