"""
Test: Formelberechnung

Testet ob Formeln korrekt berechnet werden
"""

from excel.excel_manager import ExcelManager
from excel.excel_models import ExcelMatrix


def test_simple_reference():
    """Test einfache Zellreferenz =B2"""
    print("=" * 80)
    print("TEST: Einfache Zellreferenz =B2")
    print("=" * 80)
    
    # Erstelle Matrix
    manager = ExcelManager(ExcelMatrix(rows=10, columns=5))
    
    # Setze Wert in B2 (Zeile 1, Spalte 1 - 0-basiert)
    manager.set_cell_value(1, 1, 100, "100")
    print(f"B2 gesetzt auf: 100")
    
    # Hole Wert von B2
    b2_value = manager.get_cell_value(1, 1)
    print(f"B2 Wert: {b2_value}")
    
    # Setze Formel in A1 (Zeile 0, Spalte 0)
    manager.set_cell_value(0, 0, None, raw_input="=B2")
    print(f"A1 Formel gesetzt: =B2")
    
    # Hole Zelle A1
    a1_cell = manager.get_cell(0, 0)
    print(f"\nA1 Details:")
    print(f"  - is_formula: {a1_cell.is_formula()}")
    print(f"  - formula: {a1_cell.formula}")
    print(f"  - value: {a1_cell.value}")
    print(f"  - error: {a1_cell.error}")
    print(f"  - display_value: {a1_cell.get_display_value()}")
    
    # Prüfe Ergebnis
    if a1_cell.value == 100:
        print("\nTEST BESTANDEN: Formel =B2 wurde korrekt berechnet!")
    else:
        print(f"\nTEST FEHLGESCHLAGEN: Erwartet 100, erhalten {a1_cell.value}")
        if a1_cell.error:
            print(f"   Fehler: {a1_cell.error}")


def test_sum_formula():
    """Test SUM Formel"""
    print("\n" + "=" * 80)
    print("TEST: SUM Formel =SUM(A1:A3)")
    print("=" * 80)
    
    # Erstelle Matrix
    manager = ExcelManager(ExcelMatrix(rows=10, columns=5))
    
    # Setze Werte in A1, A2, A3
    manager.set_cell_value(0, 0, 10, "10")
    manager.set_cell_value(1, 0, 20, "20")
    manager.set_cell_value(2, 0, 30, "30")
    print("A1=10, A2=20, A3=30")
    
    # Setze Formel in A4
    manager.set_cell_value(3, 0, None, raw_input="=SUM(A1:A3)")
    print("A4 Formel gesetzt: =SUM(A1:A3)")
    
    # Hole Zelle A4
    a4_cell = manager.get_cell(3, 0)
    print(f"\nA4 Details:")
    print(f"  - is_formula: {a4_cell.is_formula()}")
    print(f"  - formula: {a4_cell.formula}")
    print(f"  - value: {a4_cell.value}")
    print(f"  - error: {a4_cell.error}")
    print(f"  - display_value: {a4_cell.get_display_value()}")
    
    # Prüfe Ergebnis
    if a4_cell.value == 60:
        print("\nTEST BESTANDEN: Formel =SUM(A1:A3) wurde korrekt berechnet!")
    else:
        print(f"\nTEST FEHLGESCHLAGEN: Erwartet 60, erhalten {a4_cell.value}")
        if a4_cell.error:
            print(f"   Fehler: {a4_cell.error}")


def test_arithmetic_formula():
    """Test arithmetische Formel"""
    print("\n" + "=" * 80)
    print("TEST: Arithmetische Formel =A1*2")
    print("=" * 80)
    
    # Erstelle Matrix
    manager = ExcelManager(ExcelMatrix(rows=10, columns=5))
    
    # Setze Wert in A1
    manager.set_cell_value(0, 0, 50, "50")
    print("A1=50")
    
    # Setze Formel in B1
    manager.set_cell_value(0, 1, None, raw_input="=A1*2")
    print("B1 Formel gesetzt: =A1*2")
    
    # Hole Zelle B1
    b1_cell = manager.get_cell(0, 1)
    print(f"\nB1 Details:")
    print(f"  - is_formula: {b1_cell.is_formula()}")
    print(f"  - formula: {b1_cell.formula}")
    print(f"  - value: {b1_cell.value}")
    print(f"  - error: {b1_cell.error}")
    print(f"  - display_value: {b1_cell.get_display_value()}")
    
    # Prüfe Ergebnis
    if b1_cell.value == 100:
        print("\nTEST BESTANDEN: Formel =A1*2 wurde korrekt berechnet!")
    else:
        print(f"\nTEST FEHLGESCHLAGEN: Erwartet 100, erhalten {b1_cell.value}")
        if b1_cell.error:
            print(f"   Fehler: {b1_cell.error}")


def main():
    """Hauptfunktion"""
    print("\n" + "=" * 80)
    print("FORMELBERECHNUNG TESTS")
    print("=" * 80)
    
    try:
        # Test 1: Einfache Referenz
        test_simple_reference()
        
        # Test 2: SUM Formel
        test_sum_formula()
        
        # Test 3: Arithmetische Formel
        test_arithmetic_formula()
        
        print("\n" + "=" * 80)
        print("ALLE TESTS ABGESCHLOSSEN")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nFEHLER: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
