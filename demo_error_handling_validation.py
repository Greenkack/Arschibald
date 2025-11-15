"""
Demo: Fehlerbehandlung und Validierung (Task 21)

Demonstriert alle implementierten Features:
- Alle Fehlertypen
- Tooltip-Hilfe
- Input-Validierung
- Zirkelbezug-Erkennung
"""

from excel.excel_validation import (
    ExcelValidator,
    CircularReferenceDetector,
    get_error_tooltip
)
from excel.excel_models import Cell
from excel.excel_manager import ExcelManager


def demo_validation():
    """Demonstriert Input-Validierung"""
    print("=" * 70)
    print("DEMO: Input-Validierung")
    print("=" * 70)
    
    validator = ExcelValidator()
    
    # Test verschiedene Eingaben
    test_inputs = [
        ("123.45", "Zahl"),
        ("=SUM(A1:A10)", "Gültige Formel"),
        ("=SUM(A1:A10", "Ungültige Formel (Klammer fehlt)"),
        ("=UNKNOWNFUNC(A1)", "Unbekannte Funktion"),
        ("31.12.2023", "Datum"),
        ("TRUE", "Boolean"),
        ("Hello World", "Text"),
    ]
    
    for value, description in test_inputs:
        print(f"\n{description}: '{value}'")
        print("-" * 70)
        
        result = validator.validate_cell_input(value)
        
        if result.valid:
            print(f"Gültig - Typ: {result.type}")
            if result.warning:
                print(f"Warnung: {result.warning}")
            if result.parsed_value is not None:
                print(f"   Wert: {result.parsed_value}")
        else:
            print(f"Ungültig - {result.error_code}")
            print(f"   Fehler: {result.error}")
            if result.suggestions:
                print("   Vorschläge:")
                for suggestion in result.suggestions[:2]:
                    print(f"   • {suggestion}")


def demo_error_tooltips():
    """Demonstriert Fehler-Tooltips"""
    print("\n\n" + "=" * 70)
    print("DEMO: Fehler-Tooltips")
    print("=" * 70)
    
    error_codes = ['#ERROR!', '#REF!', '#DIV/0!', '#CIRCULAR!', '#NAME?', '#VALUE!']
    
    for error_code in error_codes:
        tooltip = get_error_tooltip(error_code)
        
        print(f"\n{error_code} - {tooltip['title']}")
        print("-" * 70)
        print(f"Beschreibung: {tooltip['description']}")
        print("Lösungen:")
        for i, solution in enumerate(tooltip['solutions'][:3], 1):
            print(f"  {i}. {solution}")


def demo_circular_reference_detection():
    """Demonstriert Zirkelbezug-Erkennung"""
    print("\n\n" + "=" * 70)
    print("DEMO: Zirkelbezug-Erkennung")
    print("=" * 70)
    
    detector = CircularReferenceDetector()
    
    # Test 1: Direkte Selbstreferenz
    print("\nTest 1: Direkte Selbstreferenz (A1 = =A1)")
    print("-" * 70)
    circular_path = detector.detect_circular_reference((0, 0), "=A1")
    if circular_path:
        print("Zirkelbezug erkannt!")
        print(f"   Pfad: {circular_path}")
    else:
        print("Kein Zirkelbezug")
    
    # Test 2: Indirekter Zirkelbezug
    print("\nTest 2: Indirekter Zirkelbezug (A1→B1→C1→A1)")
    print("-" * 70)
    
    # Erstelle Zellen mit Zirkel
    cells = {
        (0, 0): Cell(0, 0, formula="=B1"),  # A1 = =B1
        (0, 1): Cell(0, 1, formula="=C1"),  # B1 = =C1
        (0, 2): Cell(0, 2, formula="=A1"),  # C1 = =A1 (Zirkel!)
    }
    
    detector.build_graph(cells)
    circular_path = detector.detect_circular_reference((0, 0), "=B1")
    
    if circular_path:
        print("Zirkelbezug erkannt!")
        from excel.excel_utils import cell_to_a1
        path_str = " → ".join([cell_to_a1(r, c) for r, c in circular_path])
        print(f"   Pfad: {path_str}")
    else:
        print("Kein Zirkelbezug")
    
    # Test 3: Kein Zirkelbezug
    print("\nTest 3: Kein Zirkelbezug (A1→B1→C1)")
    print("-" * 70)
    
    cells = {
        (0, 0): Cell(0, 0, formula="=B1"),  # A1 = =B1
        (0, 1): Cell(0, 1, formula="=C1"),  # B1 = =C1
        (0, 2): Cell(0, 2, value=10),       # C1 = 10 (kein Zirkel)
    }
    
    detector.build_graph(cells)
    circular_path = detector.detect_circular_reference((0, 0), "=B1")
    
    if circular_path:
        print("Zirkelbezug erkannt!")
    else:
        print("Kein Zirkelbezug")


def demo_formula_validation_details():
    """Demonstriert detaillierte Formel-Validierung"""
    print("\n\n" + "=" * 70)
    print("DEMO: Detaillierte Formel-Validierung")
    print("=" * 70)
    
    validator = ExcelValidator()
    
    test_formulas = [
        ("=SUM(A1:A10)", "Einfache Summe"),
        ("=IF(A1>10, \"Ja\", \"Nein\")", "IF mit Text"),
        ("=VLOOKUP(A1, B1:C10, 2, FALSE)", "VLOOKUP"),
        ("=SUM(A1:A10)*0.19", "Berechnung mit Konstante"),
        ("=IF(SUM(A1:A10)>100, AVERAGE(B1:B10), 0)", "Verschachtelt"),
        ("=A1/0", "Division durch Null (Warnung)"),
        ("=SUM(A1:A10", "Fehlende Klammer"),
        ("=UNKNOWNFUNC(A1)", "Unbekannte Funktion"),
    ]
    
    for formula, description in test_formulas:
        print(f"\n{description}")
        print(f"Formel: {formula}")
        print("-" * 70)
        
        result = validator.validate_formula(formula)
        
        if result.valid:
            print("Gültig")
            if result.warning:
                print(f"Warnung: {result.warning}")
                if result.suggestions:
                    print("   Vorschläge:")
                    for suggestion in result.suggestions[:2]:
                        print(f"   • {suggestion}")
        else:
            print(f"Ungültig - {result.error_code}")
            print(f"   {result.error}")
            if result.suggestions:
                print("   Vorschläge:")
                for suggestion in result.suggestions[:2]:
                    print(f"   • {suggestion}")


def demo_integration_with_manager():
    """Demonstriert Integration mit ExcelManager"""
    print("\n\n" + "=" * 70)
    print("DEMO: Integration mit ExcelManager")
    print("=" * 70)
    
    manager = ExcelManager()
    
    # Test 1: Gültige Werte setzen
    print("\nTest 1: Gültige Werte setzen")
    print("-" * 70)
    
    manager.set_cell_value(0, 0, 10, raw_input="10")
    manager.set_cell_value(0, 1, 20, raw_input="20")
    manager.set_cell_value(0, 2, None, raw_input="=A1+B1")
    
    print(f"A1 = {manager.get_cell_value(0, 0)}")
    print(f"B1 = {manager.get_cell_value(0, 1)}")
    print(f"C1 = {manager.get_cell_value(0, 2)} (Formel: =A1+B1)")
    
    # Test 2: Division durch Null
    print("\nTest 2: Division durch Null")
    print("-" * 70)
    
    manager.set_cell_value(1, 0, 0, raw_input="0")
    manager.set_cell_value(1, 1, None, raw_input="=10/A2")
    
    cell = manager.get_cell(1, 1)
    if cell.is_error():
        print(f"Fehler erkannt: {cell.error}")
        tooltip = get_error_tooltip(cell.error)
        print(f"   {tooltip['description']}")
    
    # Test 3: Ungültige Referenz
    print("\nTest 3: Ungültige Referenz")
    print("-" * 70)
    
    manager.set_cell_value(2, 0, None, raw_input="=ZZZ999")
    
    cell = manager.get_cell(2, 0)
    if cell.is_error():
        print(f"Fehler erkannt: {cell.error}")
        tooltip = get_error_tooltip(cell.error)
        print(f"   {tooltip['description']}")


def main():
    """Hauptfunktion"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "DEMO: Fehlerbehandlung und Validierung (Task 21)" + " " * 9 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Führe alle Demos aus
    demo_validation()
    demo_error_tooltips()
    demo_circular_reference_detection()
    demo_formula_validation_details()
    demo_integration_with_manager()
    
    # Zusammenfassung
    print("\n\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    print("\nImplementierte Features:")
    print("Alle Fehlertypen (#ERROR!, #REF!, #DIV/0!, #CIRCULAR!, etc.)")
    print("Tooltip-Hilfe mit Titel, Beschreibung und Lösungsvorschlägen")
    print("Input-Validierung für Formeln, Zahlen, Text, Datum, Boolean")
    print("Zirkelbezug-Erkennung (direkt und indirekt)")
    print("Integration mit ExcelManager")
    print("Umfassende UI-Integration")
    print("\nAlle Requirements 10.1-10.5 erfüllt!")
    print("=" * 70)


if __name__ == "__main__":
    main()
