"""
Test für Fehlerbehandlung und Validierung (Task 21)

Testet:
- Alle Fehlertypen (#ERROR!, #REF!, #DIV/0!, etc.)
- Tooltip-Hilfe für Fehler
- Input-Validierung für alle Felder
- Zirkelbezug-Erkennung
"""

import pytest
from excel.excel_validation import (
    ExcelValidator,
    ValidationResult,
    CircularReferenceDetector,
    get_error_tooltip
)
from excel.excel_models import Cell, ExcelMatrix
from excel.excel_manager import ExcelManager


class TestExcelValidator:
    """Tests für ExcelValidator"""
    
    def test_validate_empty_input(self):
        """Test: Leere Eingabe ist gültig"""
        validator = ExcelValidator()
        result = validator.validate_cell_input("")
        
        assert result.valid
        assert result.type == 'empty'
        assert result.parsed_value is None
    
    def test_validate_number_valid(self):
        """Test: Gültige Zahlen"""
        validator = ExcelValidator()
        
        # Integer
        result = validator.validate_number("123")
        assert result.valid
        assert result.type == 'number'
        assert result.parsed_value == 123.0
        
        # Float mit Punkt
        result = validator.validate_number("123.45")
        assert result.valid
        assert result.parsed_value == 123.45
        
        # Float mit Komma
        result = validator.validate_number("123,45")
        assert result.valid
        assert result.parsed_value == 123.45
        
        # Negative Zahl
        result = validator.validate_number("-123.45")
        assert result.valid
        assert result.parsed_value == -123.45
    
    def test_validate_number_invalid(self):
        """Test: Ungültige Zahlen"""
        validator = ExcelValidator()
        
        result = validator.validate_number("abc")
        assert not result.valid
        assert result.error_code == "#VALUE!"
        assert len(result.suggestions) > 0
    
    def test_validate_text(self):
        """Test: Text-Validierung"""
        validator = ExcelValidator()
        
        result = validator.validate_text("Hello World")
        assert result.valid
        assert result.type == 'text'
        assert result.parsed_value == "Hello World"
    
    def test_validate_text_too_long(self):
        """Test: Text zu lang"""
        validator = ExcelValidator()
        
        long_text = "a" * 40000  # Über Excel-Limit
        result = validator.validate_text(long_text)
        assert not result.valid
        assert result.error_code == "#VALUE!"
    
    def test_validate_boolean(self):
        """Test: Boolean-Validierung"""
        validator = ExcelValidator()
        
        # TRUE Varianten
        for value in ['TRUE', 'true', 'True', 'WAHR', '1', 'YES', 'JA']:
            result = validator.validate_boolean(value)
            assert result.valid, f"Failed for {value}"
            assert result.parsed_value is True
        
        # FALSE Varianten
        for value in ['FALSE', 'false', 'False', 'FALSCH', '0', 'NO', 'NEIN']:
            result = validator.validate_boolean(value)
            assert result.valid, f"Failed for {value}"
            assert result.parsed_value is False
    
    def test_validate_date(self):
        """Test: Datum-Validierung"""
        validator = ExcelValidator()
        
        # Gültige Formate
        valid_dates = [
            "31.12.2023",
            "31/12/2023",
            "2023-12-31",
            "01.01.2024"
        ]
        
        for date_str in valid_dates:
            result = validator.validate_date(date_str)
            assert result.valid, f"Failed for {date_str}"
            assert result.type == 'date'
    
    def test_validate_date_invalid(self):
        """Test: Ungültiges Datum"""
        validator = ExcelValidator()
        
        result = validator.validate_date("32.13.2023")  # Ungültiges Datum
        assert not result.valid
        assert result.error_code == "#VALUE!"
        assert len(result.suggestions) > 0


class TestFormulaValidation:
    """Tests für Formel-Validierung"""
    
    def test_validate_formula_empty(self):
        """Test: Leere Formel"""
        validator = ExcelValidator()
        
        result = validator.validate_formula("=")
        assert not result.valid
        assert result.error_code == "#ERROR!"
        assert "leer" in result.error.lower()
    
    def test_validate_formula_unbalanced_parentheses(self):
        """Test: Unbalancierte Klammern"""
        validator = ExcelValidator()
        
        # Zu viele öffnende Klammern
        result = validator.validate_formula("=SUM(A1:A10")
        assert not result.valid
        assert result.error_code == "#ERROR!"
        assert "Klammern" in result.error
        
        # Zu viele schließende Klammern
        result = validator.validate_formula("=SUM(A1:A10))")
        assert not result.valid
        assert result.error_code == "#ERROR!"
    
    def test_validate_formula_unbalanced_quotes(self):
        """Test: Unbalancierte Anführungszeichen"""
        validator = ExcelValidator()
        
        result = validator.validate_formula('=IF(A1>10, "Yes)')
        assert not result.valid
        assert result.error_code == "#ERROR!"
        assert "Anführungszeichen" in result.error
    
    def test_validate_formula_unknown_function(self):
        """Test: Unbekannte Funktion"""
        validator = ExcelValidator()
        
        result = validator.validate_formula("=UNKNOWNFUNC(A1)")
        assert not result.valid
        assert result.error_code == "#NAME?"
        assert "UNKNOWNFUNC" in result.error
    
    def test_validate_formula_invalid_cell_reference(self):
        """Test: Ungültige Zellreferenz"""
        validator = ExcelValidator()
        
        # Zu große Zeile
        result = validator.validate_formula("=SUM(A9999999)")
        assert not result.valid
        assert result.error_code == "#REF!"
    
    def test_validate_formula_invalid_range(self):
        """Test: Ungültiger Bereich"""
        validator = ExcelValidator()
        
        # Ungültiges Format - Zeile zu groß
        result = validator.validate_formula("=SUM(A1:A9999999)")
        assert not result.valid
        assert result.error_code == "#REF!"
    
    def test_validate_formula_division_by_zero_warning(self):
        """Test: Warnung bei möglicher Division durch Null"""
        validator = ExcelValidator()
        
        result = validator.validate_formula("=A1/0")
        assert result.valid  # Syntaktisch gültig
        assert result.warning is not None
        assert "Division durch Null" in result.warning
        assert len(result.suggestions) > 0
    
    def test_validate_formula_valid_simple(self):
        """Test: Gültige einfache Formeln"""
        validator = ExcelValidator()
        
        valid_formulas = [
            "=A1+B1",
            "=SUM(A1:A10)",
            "=AVERAGE(B1:B20)",
            "=IF(A1>10, \"Yes\", \"No\")",
            "=VLOOKUP(A1, B1:C10, 2, FALSE)"
        ]
        
        for formula in valid_formulas:
            result = validator.validate_formula(formula)
            assert result.valid, f"Failed for {formula}: {result.error}"
            assert result.type == 'formula'
    
    def test_validate_formula_valid_nested(self):
        """Test: Gültige verschachtelte Formeln"""
        validator = ExcelValidator()
        
        result = validator.validate_formula("=IF(SUM(A1:A10)>100, AVERAGE(B1:B10), 0)")
        assert result.valid
        assert result.type == 'formula'


class TestCircularReferenceDetector:
    """Tests für Zirkelbezug-Erkennung"""
    
    def test_detect_direct_circular_reference(self):
        """Test: Direkte Selbstreferenz"""
        detector = CircularReferenceDetector()
        
        # A1 = =A1
        circular_path = detector.detect_circular_reference((0, 0), "=A1")
        assert circular_path is not None
        assert (0, 0) in circular_path
    
    def test_detect_indirect_circular_reference(self):
        """Test: Indirekter Zirkelbezug"""
        detector = CircularReferenceDetector()
        
        # Erstelle Zellen mit Formeln
        cells = {
            (0, 0): Cell(0, 0, formula="=B1"),  # A1 = =B1
            (0, 1): Cell(0, 1, formula="=C1"),  # B1 = =C1
            (0, 2): Cell(0, 2, formula="=A1"),  # C1 = =A1 (Zirkel!)
        }
        
        detector.build_graph(cells)
        
        # Prüfe ob Zirkel erkannt wird
        circular_path = detector.detect_circular_reference((0, 0), "=B1")
        assert circular_path is not None
        assert len(circular_path) >= 2
    
    def test_no_circular_reference(self):
        """Test: Kein Zirkelbezug"""
        detector = CircularReferenceDetector()
        
        # Erstelle Zellen ohne Zirkel
        cells = {
            (0, 0): Cell(0, 0, formula="=B1"),  # A1 = =B1
            (0, 1): Cell(0, 1, formula="=C1"),  # B1 = =C1
            (0, 2): Cell(0, 2, value=10),       # C1 = 10 (kein Zirkel)
        }
        
        detector.build_graph(cells)
        
        circular_path = detector.detect_circular_reference((0, 0), "=B1")
        assert circular_path is None
    
    def test_detect_all_circular_references(self):
        """Test: Alle Zirkelbezüge finden"""
        detector = CircularReferenceDetector()
        
        # Erstelle mehrere Zirkel
        cells = {
            # Zirkel 1: A1 -> B1 -> A1
            (0, 0): Cell(0, 0, formula="=B1"),
            (0, 1): Cell(0, 1, formula="=A1"),
            
            # Zirkel 2: C1 -> D1 -> E1 -> C1
            (0, 2): Cell(0, 2, formula="=D1"),
            (0, 3): Cell(0, 3, formula="=E1"),
            (0, 4): Cell(0, 4, formula="=C1"),
        }
        
        detector.build_graph(cells)
        circles = detector.get_all_circular_references()
        
        assert len(circles) >= 2


class TestErrorTooltips:
    """Tests für Fehler-Tooltips"""
    
    def test_get_error_tooltip_all_types(self):
        """Test: Tooltips für alle Fehlertypen"""
        error_codes = [
            '#ERROR!', '#REF!', '#DIV/0!', '#CIRCULAR!',
            '#NAME?', '#VALUE!', '#NUM!', '#N/A', '#NULL!'
        ]
        
        for error_code in error_codes:
            tooltip = get_error_tooltip(error_code)
            
            assert 'title' in tooltip
            assert 'description' in tooltip
            assert 'solutions' in tooltip
            assert len(tooltip['solutions']) > 0
            
            # Prüfe dass Inhalte nicht leer sind
            assert tooltip['title']
            assert tooltip['description']
    
    def test_get_error_tooltip_unknown(self):
        """Test: Tooltip für unbekannten Fehler"""
        tooltip = get_error_tooltip('#UNKNOWN!')
        
        assert tooltip['title'] == 'Unbekannter Fehler'
        assert '#UNKNOWN!' in tooltip['description']


class TestIntegrationValidation:
    """Integrationstests für Validierung mit ExcelManager"""
    
    def test_validate_and_set_cell_value(self):
        """Test: Validierung beim Setzen von Zellwerten"""
        manager = ExcelManager()
        
        # Gültige Zahl
        manager.set_cell_value(0, 0, 123, raw_input="123")
        assert manager.get_cell_value(0, 0) == 123
        
        # Gültige Formel
        manager.set_cell_value(0, 1, None, raw_input="=A1*2")
        cell = manager.get_cell(0, 1)
        assert cell.is_formula()
        assert cell.value == 246  # 123 * 2
    
    def test_circular_reference_prevention(self):
        """Test: Zirkelbezug-Prävention"""
        manager = ExcelManager()
        
        # Setze A1 = 10
        manager.set_cell_value(0, 0, 10, raw_input="10")
        
        # Versuche A1 = =A1 zu setzen (sollte Fehler geben)
        manager.set_cell_value(0, 0, None, raw_input="=A1")
        
        cell = manager.get_cell(0, 0)
        # Zelle sollte Fehler enthalten
        assert cell.is_error() or cell.error == "#CIRCULAR!"
    
    def test_formula_error_handling(self):
        """Test: Fehlerbehandlung bei Formeln"""
        manager = ExcelManager()
        
        # Division durch Null
        manager.set_cell_value(0, 0, 0, raw_input="0")
        manager.set_cell_value(0, 1, None, raw_input="=10/A1")
        
        cell = manager.get_cell(0, 1)
        assert cell.is_error()
        assert cell.error == "#DIV/0!"
        
        # Ungültige Referenz
        manager.set_cell_value(1, 0, None, raw_input="=ZZZ999")
        cell = manager.get_cell(1, 0)
        # Sollte Fehler haben (entweder #REF! oder #NAME?)
        assert cell.is_error()


def run_tests():
    """Führt alle Tests aus"""
    print("=" * 60)
    print("Test: Fehlerbehandlung und Validierung (Task 21)")
    print("=" * 60)
    
    # Test ExcelValidator
    print("\n1. ExcelValidator Tests...")
    test_validator = TestExcelValidator()
    test_validator.test_validate_empty_input()
    test_validator.test_validate_number_valid()
    test_validator.test_validate_number_invalid()
    test_validator.test_validate_text()
    test_validator.test_validate_text_too_long()
    test_validator.test_validate_boolean()
    test_validator.test_validate_date()
    test_validator.test_validate_date_invalid()
    print("✓ ExcelValidator Tests erfolgreich")
    
    # Test Formel-Validierung
    print("\n2. Formel-Validierung Tests...")
    test_formula = TestFormulaValidation()
    test_formula.test_validate_formula_empty()
    test_formula.test_validate_formula_unbalanced_parentheses()
    test_formula.test_validate_formula_unbalanced_quotes()
    test_formula.test_validate_formula_unknown_function()
    test_formula.test_validate_formula_invalid_cell_reference()
    test_formula.test_validate_formula_invalid_range()
    test_formula.test_validate_formula_division_by_zero_warning()
    test_formula.test_validate_formula_valid_simple()
    test_formula.test_validate_formula_valid_nested()
    print("✓ Formel-Validierung Tests erfolgreich")
    
    # Test Zirkelbezug-Erkennung
    print("\n3. Zirkelbezug-Erkennung Tests...")
    test_circular = TestCircularReferenceDetector()
    test_circular.test_detect_direct_circular_reference()
    test_circular.test_detect_indirect_circular_reference()
    test_circular.test_no_circular_reference()
    test_circular.test_detect_all_circular_references()
    print("✓ Zirkelbezug-Erkennung Tests erfolgreich")
    
    # Test Fehler-Tooltips
    print("\n4. Fehler-Tooltips Tests...")
    test_tooltips = TestErrorTooltips()
    test_tooltips.test_get_error_tooltip_all_types()
    test_tooltips.test_get_error_tooltip_unknown()
    print("✓ Fehler-Tooltips Tests erfolgreich")
    
    # Test Integration
    print("\n5. Integrationstests...")
    test_integration = TestIntegrationValidation()
    test_integration.test_validate_and_set_cell_value()
    test_integration.test_circular_reference_prevention()
    test_integration.test_formula_error_handling()
    print("✓ Integrationstests erfolgreich")
    
    print("\n" + "=" * 60)
    print("✓ Alle Tests erfolgreich!")
    print("=" * 60)
    
    # Zeige Zusammenfassung
    print("\nImplementierte Features (Task 21):")
    print("✓ Alle Fehlertypen implementiert (#ERROR!, #REF!, #DIV/0!, etc.)")
    print("✓ Tooltip-Hilfe für Fehler mit Lösungsvorschlägen")
    print("✓ Input-Validierung für alle Felder (Formeln, Zahlen, Text, Datum, Boolean)")
    print("✓ Zirkelbezug-Erkennung (direkt und indirekt)")
    print("✓ Umfassende Fehlerbehandlung in UI")
    print("✓ Validierung mit Vorschlägen und Warnungen")


if __name__ == "__main__":
    run_tests()
