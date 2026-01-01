"""
Test Suite für Formelleiste und Zell-Bearbeitung (Task 9)

Testet:
- Formelleiste über dem Grid
- Aktive Zelle anzeigen
- Formel-Eingabe und -Anzeige
- Zell-Bearbeitung mit Validierung
- Fehleranzeige in Zellen
"""

import pytest
from excel.excel_manager import ExcelManager
from excel.excel_models import ExcelMatrix, Cell, FormulaError, DivisionByZeroError
from excel.excel_utils import cell_to_a1, a1_to_cell


class TestFormulaBarDisplay:
    """Tests für die Formelleisten-Anzeige"""
    
    def test_formula_bar_shows_formula(self):
        """Test: Formelleiste zeigt Formel an"""
        manager = ExcelManager()
        
        # Setze Formel
        manager.set_cell_value(0, 0, None, raw_input="=SUM(B1:B3)")
        
        cell = manager.get_cell(0, 0)
        assert cell.is_formula()
        assert cell.formula == "=SUM(B1:B3)"
    
    def test_formula_bar_shows_value(self):
        """Test: Formelleiste zeigt Wert an"""
        manager = ExcelManager()
        
        # Setze Wert
        manager.set_cell_value(0, 0, 42, raw_input="42")
        
        cell = manager.get_cell(0, 0)
        assert not cell.is_formula()
        assert cell.value == 42
        assert cell.raw_input == "42"
    
    def test_formula_bar_shows_text(self):
        """Test: Formelleiste zeigt Text an"""
        manager = ExcelManager()
        
        # Setze Text
        manager.set_cell_value(0, 0, "Hello", raw_input="Hello")
        
        cell = manager.get_cell(0, 0)
        assert cell.value == "Hello"
        assert cell.data_type == "text"


class TestActiveCellDisplay:
    """Tests für die Anzeige der aktiven Zelle"""
    
    def test_cell_reference_display(self):
        """Test: Zellreferenz wird korrekt angezeigt"""
        # Test verschiedene Zellreferenzen
        assert cell_to_a1(0, 0) == "A1"
        assert cell_to_a1(0, 1) == "B1"
        assert cell_to_a1(1, 0) == "A2"
        assert cell_to_a1(25, 0) == "A26"
        assert cell_to_a1(0, 26) == "AA1"
    
    def test_cell_type_detection(self):
        """Test: Zelltyp wird korrekt erkannt"""
        manager = ExcelManager()
        
        # Formel
        manager.set_cell_value(0, 0, None, raw_input="=SUM(A1:A10)")
        cell = manager.get_cell(0, 0)
        assert cell.is_formula()
        assert cell.data_type == "formula"
        
        # Zahl
        manager.set_cell_value(1, 0, 42, raw_input="42")
        cell = manager.get_cell(1, 0)
        assert cell.data_type == "number"
        
        # Text
        manager.set_cell_value(2, 0, "Test", raw_input="Test")
        cell = manager.get_cell(2, 0)
        assert cell.data_type == "text"
    
    def test_error_cell_detection(self):
        """Test: Fehlerhafte Zellen werden erkannt"""
        manager = ExcelManager()
        
        # Setze Division durch Null
        manager.set_cell_value(0, 0, 10, raw_input="10")
        manager.set_cell_value(1, 0, 0, raw_input="0")
        manager.set_cell_value(2, 0, None, raw_input="=A1/B1")
        
        cell = manager.get_cell(2, 0)
        assert cell.is_error()
        assert cell.error == "#DIV/0!"


class TestFormulaInput:
    """Tests für Formel-Eingabe"""
    
    def test_simple_formula_input(self):
        """Test: Einfache Formel eingeben"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10, raw_input="10")
        manager.set_cell_value(1, 0, 20, raw_input="20")
        
        # Setze Formel
        manager.set_cell_value(2, 0, None, raw_input="=A1+B1")
        
        cell = manager.get_cell(2, 0)
        assert cell.is_formula()
        assert cell.value == 30
    
    def test_function_formula_input(self):
        """Test: Funktions-Formel eingeben"""
        manager = ExcelManager()
        
        # Setze Werte
        for i in range(5):
            manager.set_cell_value(i, 0, i + 1, raw_input=str(i + 1))
        
        # Setze SUM-Formel
        manager.set_cell_value(5, 0, None, raw_input="=SUM(A1:A5)")
        
        cell = manager.get_cell(5, 0)
        assert cell.is_formula()
        assert cell.value == 15  # 1+2+3+4+5
    
    def test_nested_formula_input(self):
        """Test: Verschachtelte Formel eingeben"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10, raw_input="10")
        manager.set_cell_value(1, 0, 20, raw_input="20")
        manager.set_cell_value(2, 0, 30, raw_input="30")
        
        # Setze verschachtelte Formel
        manager.set_cell_value(3, 0, None, raw_input="=IF(SUM(A1:A3)>50, 'Ja', 'Nein')")
        
        cell = manager.get_cell(3, 0)
        assert cell.is_formula()
        assert cell.value == "Ja"  # 10+20+30=60 > 50


class TestCellValidation:
    """Tests für Zell-Validierung"""
    
    def test_validate_empty_input(self):
        """Test: Leere Eingabe validieren"""
        from excel_grid_ui import _validate_cell_input
        
        result = _validate_cell_input("")
        assert result['valid'] == True
        assert result['type'] == 'empty'
    
    def test_validate_number_input(self):
        """Test: Zahlen-Eingabe validieren"""
        from excel_grid_ui import _validate_cell_input
        
        result = _validate_cell_input("42")
        assert result['valid'] == True
        assert result['type'] == 'number'
        
        result = _validate_cell_input("3.14")
        assert result['valid'] == True
        assert result['type'] == 'number'
        
        result = _validate_cell_input("3,14")  # German format
        assert result['valid'] == True
        assert result['type'] == 'number'
    
    def test_validate_text_input(self):
        """Test: Text-Eingabe validieren"""
        from excel_grid_ui import _validate_cell_input
        
        result = _validate_cell_input("Hello World")
        assert result['valid'] == True
        assert result['type'] == 'text'
    
    def test_validate_formula_input(self):
        """Test: Formel-Eingabe validieren"""
        from excel_grid_ui import _validate_cell_input
        
        # Gültige Formel
        result = _validate_cell_input("=SUM(A1:A10)")
        assert result['valid'] == True
        assert result['type'] == 'formula'
        
        # Leere Formel
        result = _validate_cell_input("=")
        assert result['valid'] == False
        assert 'leer' in result['error'].lower()
    
    def test_validate_unbalanced_parentheses(self):
        """Test: Unbalancierte Klammern erkennen"""
        from excel_grid_ui import _validate_cell_input
        
        result = _validate_cell_input("=SUM(A1:A10")
        assert result['valid'] == False
        assert 'klammern' in result['error'].lower()
        
        result = _validate_cell_input("=SUM(A1:A10))")
        assert result['valid'] == False
        assert 'klammern' in result['error'].lower()
    
    def test_validate_unbalanced_quotes(self):
        """Test: Unbalancierte Anführungszeichen erkennen"""
        from excel_grid_ui import _validate_cell_input
        
        result = _validate_cell_input('=IF(A1>10, "Yes)')
        assert result['valid'] == False
        assert 'anführungszeichen' in result['error'].lower()


class TestErrorDisplay:
    """Tests für Fehleranzeige"""
    
    def test_syntax_error_display(self):
        """Test: Syntaxfehler anzeigen"""
        manager = ExcelManager()
        
        # Ungültige Formel
        manager.set_cell_value(0, 0, None, raw_input="=INVALID()")
        
        cell = manager.get_cell(0, 0)
        assert cell.is_error()
        assert cell.error in ["#NAME?", "#ERROR!"]
    
    def test_reference_error_display(self):
        """Test: Referenzfehler anzeigen"""
        manager = ExcelManager()
        
        # Referenz auf nicht existierende Zelle (außerhalb der Matrix)
        manager.set_cell_value(0, 0, None, raw_input="=ZZZ999")
        
        cell = manager.get_cell(0, 0)
        # Kann #REF! oder #ERROR! sein, je nach Implementierung
        assert cell.is_error()
    
    def test_division_by_zero_error_display(self):
        """Test: Division durch Null anzeigen"""
        manager = ExcelManager()
        
        manager.set_cell_value(0, 0, 10, raw_input="10")
        manager.set_cell_value(1, 0, 0, raw_input="0")
        manager.set_cell_value(2, 0, None, raw_input="=A1/B1")
        
        cell = manager.get_cell(2, 0)
        assert cell.is_error()
        assert cell.error == "#DIV/0!"
    
    def test_error_help_text(self):
        """Test: Hilfetext für Fehler"""
        from excel_grid_ui import _get_error_help
        
        # Teste alle Fehler-Codes
        assert _get_error_help("#ERROR!") is not None
        assert _get_error_help("#REF!") is not None
        assert _get_error_help("#DIV/0!") is not None
        assert _get_error_help("#CIRCULAR!") is not None
        assert _get_error_help("#NAME?") is not None
        assert _get_error_help("#VALUE!") is not None
        
        # Unbekannter Fehler
        assert _get_error_help("#UNKNOWN!") is None


class TestCellEditing:
    """Tests für Zell-Bearbeitung"""
    
    def test_edit_cell_value(self):
        """Test: Zellwert bearbeiten"""
        manager = ExcelManager()
        
        # Setze initialen Wert
        manager.set_cell_value(0, 0, 10, raw_input="10")
        assert manager.get_cell_value(0, 0) == 10
        
        # Ändere Wert
        manager.set_cell_value(0, 0, 20, raw_input="20")
        assert manager.get_cell_value(0, 0) == 20
    
    def test_edit_cell_formula(self):
        """Test: Zellformel bearbeiten"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10, raw_input="10")
        manager.set_cell_value(1, 0, 20, raw_input="20")
        
        # Setze Formel
        manager.set_cell_value(2, 0, None, raw_input="=A1+B1")
        assert manager.get_cell_value(2, 0) == 30
        
        # Ändere Formel
        manager.set_cell_value(2, 0, None, raw_input="=A1*B1")
        assert manager.get_cell_value(2, 0) == 200
    
    def test_convert_value_to_formula(self):
        """Test: Wert zu Formel konvertieren"""
        manager = ExcelManager()
        
        # Setze Wert
        manager.set_cell_value(0, 0, 42, raw_input="42")
        cell = manager.get_cell(0, 0)
        assert not cell.is_formula()
        
        # Konvertiere zu Formel
        manager.set_cell_value(0, 0, None, raw_input="=21*2")
        cell = manager.get_cell(0, 0)
        assert cell.is_formula()
        assert cell.value == 42
    
    def test_convert_formula_to_value(self):
        """Test: Formel zu Wert konvertieren"""
        manager = ExcelManager()
        
        # Setze Formel
        manager.set_cell_value(0, 0, None, raw_input="=21*2")
        cell = manager.get_cell(0, 0)
        assert cell.is_formula()
        
        # Konvertiere zu Wert
        manager.set_cell_value(0, 0, 42, raw_input="42")
        cell = manager.get_cell(0, 0)
        assert not cell.is_formula()
        assert cell.value == 42


class TestFormulaDetails:
    """Tests für Formel-Details-Anzeige"""
    
    def test_extract_cell_references(self):
        """Test: Zellreferenzen aus Formel extrahieren"""
        from excel.excel_utils import extract_cell_references
        
        refs = extract_cell_references("=A1+B2")
        assert "A1" in refs
        assert "B2" in refs
        
        refs = extract_cell_references("=SUM(A1:A10)")
        assert "A1:A10" in refs
        
        refs = extract_cell_references("=IF(A1>10, B1, C1)")
        assert "A1" in refs
        assert "B1" in refs
        assert "C1" in refs
    
    def test_show_dependent_cells(self):
        """Test: Abhängige Zellen anzeigen"""
        manager = ExcelManager()
        
        # Setze Werte und Formeln
        manager.set_cell_value(0, 0, 10, raw_input="10")
        manager.set_cell_value(1, 0, None, raw_input="=A1*2")
        manager.set_cell_value(2, 0, None, raw_input="=B1+5")
        
        # Baue Dependency Graph
        manager._build_dependency_graph()
        
        # Prüfe Abhängigkeiten
        dependents = manager.formula_engine.get_dependent_cells((0, 0))
        assert (1, 0) in dependents  # B1 hängt von A1 ab


class TestErrorSummary:
    """Tests für Fehler-Zusammenfassung"""
    
    def test_get_error_cells(self):
        """Test: Alle Fehlerzellen finden"""
        from excel_grid_ui import _get_error_cells
        
        manager = ExcelManager()
        
        # Erstelle verschiedene Fehler
        manager.set_cell_value(0, 0, 10, raw_input="10")
        manager.set_cell_value(1, 0, 0, raw_input="0")
        manager.set_cell_value(2, 0, None, raw_input="=A1/B1")  # #DIV/0!
        manager.set_cell_value(3, 0, None, raw_input="=INVALID()")  # #NAME?
        
        error_cells = _get_error_cells(manager)
        assert len(error_cells) >= 1  # Mindestens ein Fehler
        
        # Prüfe dass Fehler-Informationen vorhanden sind
        for row, col, error in error_cells:
            assert isinstance(row, int)
            assert isinstance(col, int)
            assert isinstance(error, str)
            assert error.startswith("#")
    
    def test_no_errors(self):
        """Test: Keine Fehler vorhanden"""
        from excel_grid_ui import _get_error_cells
        
        manager = ExcelManager()
        
        # Nur gültige Werte
        manager.set_cell_value(0, 0, 10, raw_input="10")
        manager.set_cell_value(1, 0, 20, raw_input="20")
        manager.set_cell_value(2, 0, None, raw_input="=A1+B1")
        
        error_cells = _get_error_cells(manager)
        assert len(error_cells) == 0


class TestIntegration:
    """Integrationstests für Formelleiste und Zell-Bearbeitung"""
    
    def test_complete_workflow(self):
        """Test: Kompletter Workflow von Eingabe bis Anzeige"""
        manager = ExcelManager()
        
        # 1. Werte eingeben
        manager.set_cell_value(0, 0, 100, raw_input="100")
        manager.set_cell_value(1, 0, 200, raw_input="200")
        
        # 2. Formel eingeben
        manager.set_cell_value(2, 0, None, raw_input="=A1+B1")
        
        # 3. Prüfe Ergebnis
        cell = manager.get_cell(2, 0)
        assert cell.is_formula()
        assert cell.formula == "=A1+B1"
        assert cell.value == 300
        
        # 4. Ändere Eingabewert
        manager.set_cell_value(0, 0, 150, raw_input="150")
        
        # 5. Prüfe dass Formel neu berechnet wurde
        cell = manager.get_cell(2, 0)
        assert cell.value == 350
    
    def test_error_recovery(self):
        """Test: Fehler-Wiederherstellung"""
        manager = ExcelManager()
        
        # 1. Erstelle Fehler
        manager.set_cell_value(0, 0, 10, raw_input="10")
        manager.set_cell_value(1, 0, 0, raw_input="0")
        manager.set_cell_value(2, 0, None, raw_input="=A1/B1")
        
        cell = manager.get_cell(2, 0)
        assert cell.is_error()
        assert cell.error == "#DIV/0!"
        
        # 2. Behebe Fehler
        manager.set_cell_value(1, 0, 2, raw_input="2")
        
        # 3. Prüfe dass Fehler behoben ist
        cell = manager.get_cell(2, 0)
        assert not cell.is_error()
        assert cell.value == 5


def run_tests():
    """Führt alle Tests aus"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
