"""
Tests für Excel Integration - Datenmodelle und Basis-Klassen

Testet die Grundfunktionalität der Excel-Datenmodelle.
"""

import pytest
from excel.excel_models import Cell, ExcelMatrix
from excel.excel_utils import (
    col_to_letter, 
    letter_to_col, 
    cell_to_a1, 
    a1_to_cell,
    parse_range,
    extract_cell_references,
    update_formula_references
)
from excel.excel_manager import ExcelManager


class TestCellReferenceUtils:
    """Tests für Zellreferenz-Hilfsfunktionen"""
    
    def test_col_to_letter(self):
        """Test Spalten-zu-Buchstaben Konvertierung"""
        assert col_to_letter(0) == 'A'
        assert col_to_letter(25) == 'Z'
        assert col_to_letter(26) == 'AA'
        assert col_to_letter(51) == 'AZ'
        assert col_to_letter(701) == 'ZZ'
    
    def test_letter_to_col(self):
        """Test Buchstaben-zu-Spalten Konvertierung"""
        assert letter_to_col('A') == 0
        assert letter_to_col('Z') == 25
        assert letter_to_col('AA') == 26
        assert letter_to_col('AZ') == 51
        assert letter_to_col('ZZ') == 701
    
    def test_cell_to_a1(self):
        """Test Zell-zu-A1 Konvertierung"""
        assert cell_to_a1(0, 0) == 'A1'
        assert cell_to_a1(9, 1) == 'B10'
        assert cell_to_a1(0, 26) == 'AA1'
        assert cell_to_a1(99, 25) == 'Z100'
    
    def test_a1_to_cell(self):
        """Test A1-zu-Zell Konvertierung"""
        assert a1_to_cell('A1') == (0, 0)
        assert a1_to_cell('B10') == (9, 1)
        assert a1_to_cell('AA1') == (0, 26)
        assert a1_to_cell('Z100') == (99, 25)
    
    def test_parse_range(self):
        """Test Bereichs-Parsing"""
        # Einzelne Zelle
        assert parse_range('A1') == [(0, 0)]
        
        # Bereich
        cells = parse_range('A1:B2')
        assert len(cells) == 4
        assert (0, 0) in cells
        assert (0, 1) in cells
        assert (1, 0) in cells
        assert (1, 1) in cells
        
        # Spaltenbereich
        cells = parse_range('A1:A3')
        assert len(cells) == 3
        assert cells == [(0, 0), (1, 0), (2, 0)]
    
    def test_extract_cell_references(self):
        """Test Extraktion von Zellreferenzen aus Formeln"""
        assert extract_cell_references('=A1+B2') == ['A1', 'B2']
        assert extract_cell_references('=SUM(A1:A10)') == ['A1:A10']
        assert extract_cell_references('=IF(A1>10, B1, C1)') == ['A1', 'B1', 'C1']
        assert extract_cell_references('=A1*B2+C3') == ['A1', 'B2', 'C3']
    
    def test_update_formula_references(self):
        """Test Aktualisierung von Formelreferenzen"""
        # Zeilen-Offset
        assert update_formula_references('=A1+B1', 1, 0) == '=A2+B2'
        
        # Spalten-Offset
        assert update_formula_references('=A1+B1', 0, 1) == '=B1+C1'
        
        # Bereich
        assert update_formula_references('=SUM(A1:A10)', 0, 1) == '=SUM(B1:B10)'


class TestCellModel:
    """Tests für Cell-Datenmodell"""
    
    def test_cell_creation(self):
        """Test Zell-Erstellung"""
        cell = Cell(row=0, col=0)
        assert cell.row == 0
        assert cell.col == 0
        assert cell.value is None
        assert cell.formula is None
    
    def test_cell_with_value(self):
        """Test Zelle mit Wert"""
        cell = Cell(row=0, col=0, value=42)
        assert cell.value == 42
        assert not cell.is_formula()
    
    def test_cell_with_formula(self):
        """Test Zelle mit Formel"""
        cell = Cell(row=0, col=0, formula='=A1+B1')
        assert cell.is_formula()
        assert cell.formula == '=A1+B1'
    
    def test_cell_display_value(self):
        """Test Anzeige-Wert"""
        cell = Cell(row=0, col=0, value=42)
        assert cell.get_display_value() == '42'
        
        cell.formatted_value = '42.00'
        assert cell.get_display_value() == '42.00'
        
        cell.error = '#DIV/0!'
        assert cell.get_display_value() == '#DIV/0!'
    
    def test_cell_reference(self):
        """Test Zellreferenz"""
        cell = Cell(row=0, col=0)
        assert cell.get_cell_reference() == 'A1'
        
        cell = Cell(row=9, col=1)
        assert cell.get_cell_reference() == 'B10'


class TestExcelMatrix:
    """Tests für ExcelMatrix-Datenmodell"""
    
    def test_matrix_creation(self):
        """Test Matrix-Erstellung"""
        matrix = ExcelMatrix()
        assert matrix.name == "Neue Matrix"
        assert matrix.rows == 100
        assert matrix.columns == 26
        assert len(matrix.cells) == 0
    
    def test_get_set_cell(self):
        """Test Zell-Zugriff"""
        matrix = ExcelMatrix()
        
        # Get erstellt leere Zelle
        cell = matrix.get_cell(0, 0)
        assert cell.row == 0
        assert cell.col == 0
        
        # Set Zelle
        new_cell = Cell(row=1, col=1, value=42)
        matrix.set_cell(1, 1, new_cell)
        assert matrix.get_cell(1, 1).value == 42
    
    def test_get_set_cell_value(self):
        """Test Zellwert-Zugriff"""
        matrix = ExcelMatrix()
        
        matrix.set_cell_value(0, 0, 42)
        assert matrix.get_cell_value(0, 0) == 42
        
        matrix.set_cell_value(1, 1, "Test", raw_input="Test")
        assert matrix.get_cell_value(1, 1) == "Test"
    
    def test_formula_detection(self):
        """Test Formel-Erkennung"""
        matrix = ExcelMatrix()
        
        matrix.set_cell_value(0, 0, None, raw_input='=A1+B1')
        cell = matrix.get_cell(0, 0)
        
        assert cell.is_formula()
        assert cell.formula == '=A1+B1'
        assert cell.data_type == 'formula'
    
    def test_clear_cell(self):
        """Test Zelle löschen"""
        matrix = ExcelMatrix()
        
        matrix.set_cell_value(0, 0, 42)
        assert (0, 0) in matrix.cells
        
        matrix.clear_cell(0, 0)
        assert (0, 0) not in matrix.cells
    
    def test_get_cells_with_formulas(self):
        """Test Formeln finden"""
        matrix = ExcelMatrix()
        
        matrix.set_cell_value(0, 0, 10)
        matrix.set_cell_value(1, 0, 20)
        matrix.set_cell_value(2, 0, None, raw_input='=A1+A2')
        
        formula_cells = matrix.get_cells_with_formulas()
        assert len(formula_cells) == 1
        assert formula_cells[0].row == 2
    
    def test_get_used_range(self):
        """Test benutzten Bereich ermitteln"""
        matrix = ExcelMatrix()
        
        matrix.set_cell_value(0, 0, 1)
        matrix.set_cell_value(5, 10, 2)
        
        min_row, min_col, max_row, max_col = matrix.get_used_range()
        assert min_row == 0
        assert min_col == 0
        assert max_row == 5
        assert max_col == 10


class TestExcelManager:
    """Tests für ExcelManager"""
    
    def test_manager_creation(self):
        """Test Manager-Erstellung"""
        manager = ExcelManager()
        assert manager.matrix is not None
        assert manager.matrix.rows == 100
        assert manager.matrix.columns == 26
    
    def test_get_set_cell_value(self):
        """Test Zellwert-Operationen"""
        manager = ExcelManager()
        
        manager.set_cell_value(0, 0, 42, save_undo=False)
        assert manager.get_cell_value(0, 0) == 42
    
    def test_undo_redo(self):
        """Test Undo/Redo"""
        manager = ExcelManager()
        
        # Initiale Änderung
        manager.set_cell_value(0, 0, 10)
        assert manager.can_undo()
        assert not manager.can_redo()
        
        # Weitere Änderung
        manager.set_cell_value(0, 0, 20)
        assert manager.get_cell_value(0, 0) == 20
        
        # Undo
        manager.undo()
        assert manager.get_cell_value(0, 0) == 10
        assert manager.can_redo()
        
        # Redo
        manager.redo()
        assert manager.get_cell_value(0, 0) == 20
    
    def test_add_row(self):
        """Test Zeile hinzufügen"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 'A', save_undo=False)
        manager.set_cell_value(1, 0, 'B', save_undo=False)
        
        initial_rows = manager.matrix.rows
        
        # Füge Zeile bei Position 1 ein
        manager.add_row(position=1, save_undo=False)
        
        assert manager.matrix.rows == initial_rows + 1
        assert manager.get_cell_value(0, 0) == 'A'  # Unverändert
        assert manager.get_cell_value(2, 0) == 'B'  # Verschoben
    
    def test_add_column(self):
        """Test Spalte hinzufügen"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 'A', save_undo=False)
        manager.set_cell_value(0, 1, 'B', save_undo=False)
        
        initial_cols = manager.matrix.columns
        
        # Füge Spalte bei Position 1 ein
        manager.add_column(position=1, save_undo=False)
        
        assert manager.matrix.columns == initial_cols + 1
        assert manager.get_cell_value(0, 0) == 'A'  # Unverändert
        assert manager.get_cell_value(0, 2) == 'B'  # Verschoben
    
    def test_delete_row(self):
        """Test Zeile löschen"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 'A', save_undo=False)
        manager.set_cell_value(1, 0, 'B', save_undo=False)
        manager.set_cell_value(2, 0, 'C', save_undo=False)
        
        initial_rows = manager.matrix.rows
        
        # Lösche Zeile 1
        manager.delete_row(1, save_undo=False)
        
        assert manager.matrix.rows == initial_rows - 1
        assert manager.get_cell_value(0, 0) == 'A'
        assert manager.get_cell_value(1, 0) == 'C'  # Verschoben
    
    def test_delete_column(self):
        """Test Spalte löschen"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 'A', save_undo=False)
        manager.set_cell_value(0, 1, 'B', save_undo=False)
        manager.set_cell_value(0, 2, 'C', save_undo=False)
        
        initial_cols = manager.matrix.columns
        
        # Lösche Spalte 1
        manager.delete_column(1, save_undo=False)
        
        assert manager.matrix.columns == initial_cols - 1
        assert manager.get_cell_value(0, 0) == 'A'
        assert manager.get_cell_value(0, 1) == 'C'  # Verschoben
    
    def test_dependency_graph(self):
        """Test Abhängigkeitsgraph"""
        manager = ExcelManager()
        
        # Setze Werte und Formel
        manager.set_cell_value(0, 0, 10, save_undo=False)
        manager.set_cell_value(1, 0, 20, save_undo=False)
        manager.set_cell_value(2, 0, None, raw_input='=A1+A2', save_undo=False)
        
        # Prüfe Abhängigkeiten
        assert (2, 0) in manager.dependency_graph
        dependencies = manager.dependency_graph[(2, 0)]
        assert (0, 0) in dependencies
        assert (1, 0) in dependencies
    
    def test_get_matrix_info(self):
        """Test Matrix-Informationen"""
        manager = ExcelManager()
        
        manager.set_cell_value(0, 0, 10, save_undo=False)
        manager.set_cell_value(1, 0, None, raw_input='=A1*2', save_undo=False)
        
        info = manager.get_matrix_info()
        
        assert info['rows'] == 100
        assert info['columns'] == 26
        assert info['cell_count'] == 2
        assert info['formula_count'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
