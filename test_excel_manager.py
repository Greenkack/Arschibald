"""
Tests für ExcelManager Kern-Funktionalität

Testet:
- Matrix laden und initialisieren
- get_cell_value und set_cell_value
- Formel-Parsing und -Ausführung
- Dependency Graph für Zell-Abhängigkeiten
- Automatische Neuberechnung bei Änderungen
"""

import pytest
from excel.excel_manager import ExcelManager
from excel.excel_models import ExcelMatrix, Cell, FormulaError, CircularReferenceError


class TestExcelManagerBasics:
    """Tests für grundlegende ExcelManager-Funktionalität"""
    
    def test_init_empty_matrix(self):
        """Test: Initialisierung mit leerer Matrix"""
        manager = ExcelManager()
        
        assert manager.matrix is not None
        assert manager.matrix.rows == 100
        assert manager.matrix.columns == 26
        assert len(manager.matrix.cells) == 0
        assert manager.formula_engine is not None
    
    def test_init_with_matrix(self):
        """Test: Initialisierung mit vorhandener Matrix"""
        matrix = ExcelMatrix(name="Test Matrix", rows=10, columns=10)
        manager = ExcelManager(matrix)
        
        assert manager.matrix.name == "Test Matrix"
        assert manager.matrix.rows == 10
        assert manager.matrix.columns == 10
    
    def test_get_cell_value_empty(self):
        """Test: Wert aus leerer Zelle holen"""
        manager = ExcelManager()
        value = manager.get_cell_value(0, 0)
        
        assert value is None
    
    def test_set_and_get_cell_value(self):
        """Test: Wert setzen und wieder holen"""
        manager = ExcelManager()
        
        manager.set_cell_value(0, 0, 42)
        value = manager.get_cell_value(0, 0)
        
        assert value == 42
    
    def test_set_cell_value_with_raw_input(self):
        """Test: Wert mit raw_input setzen"""
        manager = ExcelManager()
        
        manager.set_cell_value(0, 0, 100, raw_input="100")
        cell = manager.get_cell(0, 0)
        
        assert cell.value == 100
        assert not cell.is_formula()
    
    def test_clear_cell(self):
        """Test: Zelle löschen"""
        manager = ExcelManager()
        
        manager.set_cell_value(0, 0, 42)
        assert manager.get_cell_value(0, 0) == 42
        
        manager.clear_cell(0, 0)
        assert manager.get_cell_value(0, 0) is None


class TestFormulaExecution:
    """Tests für Formel-Ausführung"""
    
    def test_simple_formula(self):
        """Test: Einfache Formel =A1+B1"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(0, 1, 20)  # B1
        
        # Setze Formel in C1
        manager.set_cell_value(0, 2, None, raw_input="=A1+B1")
        
        # Prüfe Ergebnis
        cell = manager.get_cell(0, 2)
        assert cell.value == 30
        assert cell.is_formula()
        assert cell.error is None
    
    def test_sum_formula(self):
        """Test: SUM-Formel"""
        manager = ExcelManager()
        
        # Setze Werte A1:A3
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(1, 0, 20)  # A2
        manager.set_cell_value(2, 0, 30)  # A3
        
        # Setze SUM-Formel in A4
        manager.set_cell_value(3, 0, None, raw_input="=SUM(A1:A3)")
        
        # Prüfe Ergebnis
        cell = manager.get_cell(3, 0)
        assert cell.value == 60
        assert cell.error is None
    
    def test_nested_formula(self):
        """Test: Verschachtelte Formel"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(0, 1, 20)  # B1
        manager.set_cell_value(0, 2, 5)   # C1
        
        # Setze verschachtelte Formel in D1: =IF(A1>5, SUM(A1:C1), 0)
        manager.set_cell_value(0, 3, None, raw_input="=IF(A1>5, SUM(A1:C1), 0)")
        
        # Prüfe Ergebnis
        cell = manager.get_cell(0, 3)
        assert cell.value == 35  # 10+20+5
        assert cell.error is None
    
    def test_parse_and_execute_formula(self):
        """Test: parse_and_execute_formula Methode"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(0, 1, 20)  # B1
        
        # Führe Formel aus ohne sie zu setzen
        result = manager.parse_and_execute_formula("=A1*B1")
        
        assert result == 200
    
    def test_formula_error_handling(self):
        """Test: Fehlerbehandlung bei ungültigen Formeln"""
        manager = ExcelManager()
        
        # Setze ungültige Formel
        manager.set_cell_value(0, 0, None, raw_input="=INVALID_FUNC()")
        
        # Prüfe dass Fehler gesetzt wurde
        cell = manager.get_cell(0, 0)
        assert cell.error is not None
        assert "#NAME?" in cell.error


class TestDependencyGraph:
    """Tests für Dependency Graph"""
    
    def test_dependency_graph_simple(self):
        """Test: Einfacher Dependency Graph"""
        manager = ExcelManager()
        
        # A1 = 10
        manager.set_cell_value(0, 0, 10)
        
        # B1 = A1 * 2
        manager.set_cell_value(0, 1, None, raw_input="=A1*2")
        
        # Prüfe Dependency Graph
        assert (0, 1) in manager.dependency_graph
        assert (0, 0) in manager.dependency_graph[(0, 1)]
    
    def test_dependency_graph_chain(self):
        """Test: Dependency Chain A1 -> B1 -> C1"""
        manager = ExcelManager()
        
        # A1 = 10
        manager.set_cell_value(0, 0, 10)
        
        # B1 = A1 * 2
        manager.set_cell_value(0, 1, None, raw_input="=A1*2")
        
        # C1 = B1 + 5
        manager.set_cell_value(0, 2, None, raw_input="=B1+5")
        
        # Prüfe Dependencies
        assert (0, 1) in manager.dependency_graph
        assert (0, 2) in manager.dependency_graph
        assert (0, 0) in manager.dependency_graph[(0, 1)]
        assert (0, 1) in manager.dependency_graph[(0, 2)]


class TestAutomaticRecalculation:
    """Tests für automatische Neuberechnung"""
    
    def test_recalculate_on_change(self):
        """Test: Automatische Neuberechnung bei Änderung"""
        manager = ExcelManager()
        
        # A1 = 10
        manager.set_cell_value(0, 0, 10)
        
        # B1 = A1 * 2
        manager.set_cell_value(0, 1, None, raw_input="=A1*2")
        
        # Prüfe initialen Wert
        assert manager.get_cell_value(0, 1) == 20
        
        # Ändere A1
        manager.set_cell_value(0, 0, 15)
        
        # Prüfe dass B1 neu berechnet wurde
        assert manager.get_cell_value(0, 1) == 30
    
    def test_recalculate_chain(self):
        """Test: Neuberechnung einer Kette von Abhängigkeiten"""
        manager = ExcelManager()
        
        # A1 = 10
        manager.set_cell_value(0, 0, 10)
        
        # B1 = A1 * 2
        manager.set_cell_value(0, 1, None, raw_input="=A1*2")
        
        # C1 = B1 + 5
        manager.set_cell_value(0, 2, None, raw_input="=B1+5")
        
        # Prüfe initiale Werte
        assert manager.get_cell_value(0, 1) == 20
        assert manager.get_cell_value(0, 2) == 25
        
        # Ändere A1
        manager.set_cell_value(0, 0, 20)
        
        # Prüfe dass beide neu berechnet wurden
        assert manager.get_cell_value(0, 1) == 40
        assert manager.get_cell_value(0, 2) == 45
    
    def test_recalculate_all_formulas(self):
        """Test: Alle Formeln neu berechnen"""
        manager = ExcelManager()
        
        # Setze mehrere Werte und Formeln
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(0, 1, 20)  # B1
        manager.set_cell_value(0, 2, None, raw_input="=A1+B1")  # C1
        manager.set_cell_value(1, 0, None, raw_input="=C1*2")   # A2
        
        # Ändere Werte direkt in der Matrix (ohne Neuberechnung)
        manager.matrix.cells[(0, 0)].value = 100
        manager.matrix.cells[(0, 1)].value = 200
        
        # Berechne alle Formeln neu
        manager.recalculate_all_formulas()
        
        # Prüfe Ergebnisse
        assert manager.get_cell_value(0, 2) == 300  # C1 = 100+200
        assert manager.get_cell_value(1, 0) == 600  # A2 = 300*2


class TestCircularReferences:
    """Tests für Zirkelbezug-Erkennung"""
    
    def test_detect_direct_circular_reference(self):
        """Test: Direkter Zirkelbezug A1 = A1"""
        manager = ExcelManager()
        
        # Versuche Zirkelbezug zu erstellen
        with pytest.raises(CircularReferenceError):
            manager.parse_and_execute_formula("=A1", row=0, col=0)
    
    def test_detect_indirect_circular_reference(self):
        """Test: Indirekter Zirkelbezug A1 -> B1 -> A1"""
        manager = ExcelManager()
        
        # A1 = B1
        manager.set_cell_value(0, 0, None, raw_input="=B1")
        
        # Versuche B1 = A1 zu setzen (würde Zirkelbezug erstellen)
        result = manager._would_create_circular_reference(0, 1, "=A1")
        
        assert result is True


class TestUndoRedo:
    """Tests für Undo/Redo-Funktionalität"""
    
    def test_undo_single_change(self):
        """Test: Einzelne Änderung rückgängig machen"""
        manager = ExcelManager()
        
        # Setze Wert
        manager.set_cell_value(0, 0, 10)
        assert manager.get_cell_value(0, 0) == 10
        
        # Undo
        success = manager.undo()
        assert success is True
        assert manager.get_cell_value(0, 0) is None
    
    def test_redo_after_undo(self):
        """Test: Redo nach Undo"""
        manager = ExcelManager()
        
        # Setze Wert
        manager.set_cell_value(0, 0, 10)
        
        # Undo
        manager.undo()
        assert manager.get_cell_value(0, 0) is None
        
        # Redo
        success = manager.redo()
        assert success is True
        assert manager.get_cell_value(0, 0) == 10
    
    def test_undo_multiple_changes(self):
        """Test: Mehrere Änderungen rückgängig machen"""
        manager = ExcelManager()
        
        # Mehrere Änderungen
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, 20)
        manager.set_cell_value(0, 2, 30)
        
        # Undo 3x
        manager.undo()
        assert manager.get_cell_value(0, 2) is None
        
        manager.undo()
        assert manager.get_cell_value(0, 1) is None
        
        manager.undo()
        assert manager.get_cell_value(0, 0) is None
    
    def test_can_undo_can_redo(self):
        """Test: can_undo und can_redo Methoden"""
        manager = ExcelManager()
        
        # Initial: kein Undo/Redo verfügbar
        assert manager.can_undo() is False
        assert manager.can_redo() is False
        
        # Nach Änderung: Undo verfügbar
        manager.set_cell_value(0, 0, 10)
        assert manager.can_undo() is True
        assert manager.can_redo() is False
        
        # Nach Undo: Redo verfügbar
        manager.undo()
        assert manager.can_undo() is False
        assert manager.can_redo() is True


class TestMatrixInfo:
    """Tests für Matrix-Informationen"""
    
    def test_get_matrix_info(self):
        """Test: Matrix-Informationen abrufen"""
        manager = ExcelManager()
        
        # Setze einige Werte und Formeln
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, 20)
        manager.set_cell_value(0, 2, None, raw_input="=A1+B1")
        
        info = manager.get_matrix_info()
        
        assert info['rows'] == 100
        assert info['columns'] == 26
        assert info['cell_count'] == 3
        assert info['formula_count'] == 1
        assert 'created_at' in info
        assert 'updated_at' in info


class TestRowColumnOperations:
    """Tests für Zeilen/Spalten-Operationen"""

    def test_add_row(self):
        """Test: Zeile hinzufügen"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(1, 0, 20)  # A2

        initial_rows = manager.matrix.rows

        # Füge Zeile bei Position 1 ein
        manager.add_row(position=1)

        # Prüfe dass Zeile hinzugefügt wurde
        assert manager.matrix.rows == initial_rows + 1

        # Prüfe dass Zellen verschoben wurden
        assert manager.get_cell_value(0, 0) == 10  # A1 bleibt
        assert manager.get_cell_value(2, 0) == 20  # A2 -> A3

    def test_add_row_at_end(self):
        """Test: Zeile am Ende hinzufügen"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(1, 0, 20)  # A2

        initial_rows = manager.matrix.rows

        # Füge Zeile am Ende ein (position=None)
        manager.add_row(position=None)

        # Prüfe dass Zeile hinzugefügt wurde
        assert manager.matrix.rows == initial_rows + 1

        # Prüfe dass Zellen nicht verschoben wurden
        assert manager.get_cell_value(0, 0) == 10  # A1 bleibt
        assert manager.get_cell_value(1, 0) == 20  # A2 bleibt

    def test_add_row_with_formula_update(self):
        """Test: Zeile hinzufügen mit Formel-Aktualisierung"""
        manager = ExcelManager()

        # Setze Werte und Formel
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(1, 0, 20)  # A2
        manager.set_cell_value(2, 0, None, raw_input="=A1+A2")  # A3

        # Prüfe initiale Formel
        cell = manager.get_cell(2, 0)
        assert cell.formula == "=A1+A2"
        assert cell.value == 30

        # Füge Zeile bei Position 1 ein
        manager.add_row(position=1)

        # Prüfe dass Formel aktualisiert wurde
        # A3 ist jetzt A4 und Formel sollte =A1+A3 sein
        cell = manager.get_cell(3, 0)
        assert cell.formula == "=A1+A3"
        assert cell.value == 30

    def test_add_row_with_range_formula_update(self):
        """Test: Zeile hinzufügen mit Bereichs-Formel-Aktualisierung"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(1, 0, 20)  # A2
        manager.set_cell_value(2, 0, 30)  # A3
        manager.set_cell_value(3, 0, None, raw_input="=SUM(A1:A3)")  # A4

        # Prüfe initiale Formel
        cell = manager.get_cell(3, 0)
        assert cell.formula == "=SUM(A1:A3)"
        assert cell.value == 60

        # Füge Zeile bei Position 1 ein
        manager.add_row(position=1)

        # Prüfe dass Formel aktualisiert wurde
        # A4 ist jetzt A5 und Formel sollte =SUM(A1:A4) sein
        cell = manager.get_cell(4, 0)
        assert cell.formula == "=SUM(A1:A4)"

    def test_add_column(self):
        """Test: Spalte hinzufügen"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(0, 1, 20)  # B1

        initial_cols = manager.matrix.columns

        # Füge Spalte bei Position 1 ein
        manager.add_column(position=1)

        # Prüfe dass Spalte hinzugefügt wurde
        assert manager.matrix.columns == initial_cols + 1

        # Prüfe dass Zellen verschoben wurden
        assert manager.get_cell_value(0, 0) == 10  # A1 bleibt
        assert manager.get_cell_value(0, 2) == 20  # B1 -> C1

    def test_add_column_at_end(self):
        """Test: Spalte am Ende hinzufügen"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(0, 1, 20)  # B1

        initial_cols = manager.matrix.columns

        # Füge Spalte am Ende ein (position=None)
        manager.add_column(position=None)

        # Prüfe dass Spalte hinzugefügt wurde
        assert manager.matrix.columns == initial_cols + 1

        # Prüfe dass Zellen nicht verschoben wurden
        assert manager.get_cell_value(0, 0) == 10  # A1 bleibt
        assert manager.get_cell_value(0, 1) == 20  # B1 bleibt

    def test_add_column_with_formula_update(self):
        """Test: Spalte hinzufügen mit Formel-Aktualisierung"""
        manager = ExcelManager()

        # Setze Werte und Formel
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(0, 1, 20)  # B1
        manager.set_cell_value(0, 2, None, raw_input="=A1+B1")  # C1

        # Prüfe initiale Formel
        cell = manager.get_cell(0, 2)
        assert cell.formula == "=A1+B1"
        assert cell.value == 30

        # Füge Spalte bei Position 1 ein
        manager.add_column(position=1)

        # Prüfe dass Formel aktualisiert wurde
        # C1 ist jetzt D1 und Formel sollte =A1+C1 sein
        cell = manager.get_cell(0, 3)
        assert cell.formula == "=A1+C1"
        assert cell.value == 30

    def test_add_column_with_range_formula_update(self):
        """Test: Spalte hinzufügen mit Bereichs-Formel-Aktualisierung"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(0, 1, 20)  # B1
        manager.set_cell_value(0, 2, 30)  # C1
        manager.set_cell_value(0, 3, None, raw_input="=SUM(A1:C1)")  # D1

        # Prüfe initiale Formel
        cell = manager.get_cell(0, 3)
        assert cell.formula == "=SUM(A1:C1)"
        assert cell.value == 60

        # Füge Spalte bei Position 1 ein
        manager.add_column(position=1)

        # Prüfe dass Formel aktualisiert wurde
        # D1 ist jetzt E1 und Formel sollte =SUM(A1:D1) sein
        cell = manager.get_cell(0, 4)
        assert cell.formula == "=SUM(A1:D1)"

    def test_delete_row(self):
        """Test: Zeile löschen"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(1, 0, 20)  # A2
        manager.set_cell_value(2, 0, 30)  # A3

        initial_rows = manager.matrix.rows

        # Lösche Zeile 1 (A2)
        manager.delete_row(1)

        # Prüfe dass Zeile gelöscht wurde
        assert manager.matrix.rows == initial_rows - 1

        # Prüfe dass Zellen verschoben wurden
        assert manager.get_cell_value(0, 0) == 10  # A1 bleibt
        assert manager.get_cell_value(1, 0) == 30  # A3 -> A2

    def test_delete_row_with_formula_update(self):
        """Test: Zeile löschen mit Formel-Aktualisierung"""
        manager = ExcelManager()

        # Setze Werte und Formel
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(1, 0, 20)  # A2
        manager.set_cell_value(2, 0, 30)  # A3
        manager.set_cell_value(3, 0, None, raw_input="=A1+A3")  # A4

        # Prüfe initiale Formel
        cell = manager.get_cell(3, 0)
        assert cell.formula == "=A1+A3"
        assert cell.value == 40

        # Lösche Zeile 1 (A2)
        manager.delete_row(1)

        # Prüfe dass Formel aktualisiert wurde
        # A4 ist jetzt A3 und Formel sollte =A1+A2 sein
        cell = manager.get_cell(2, 0)
        assert cell.formula == "=A1+A2"
        assert cell.value == 40

    def test_delete_row_with_range_formula_update(self):
        """Test: Zeile löschen mit Bereichs-Formel-Aktualisierung"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(1, 0, 20)  # A2
        manager.set_cell_value(2, 0, 30)  # A3
        manager.set_cell_value(3, 0, 40)  # A4
        manager.set_cell_value(4, 0, None, raw_input="=SUM(A1:A4)")  # A5

        # Prüfe initiale Formel
        cell = manager.get_cell(4, 0)
        assert cell.formula == "=SUM(A1:A4)"
        assert cell.value == 100

        # Lösche Zeile 1 (A2)
        manager.delete_row(1)

        # Prüfe dass Formel aktualisiert wurde
        # A5 ist jetzt A4 und Formel sollte =SUM(A1:A3) sein
        cell = manager.get_cell(3, 0)
        assert cell.formula == "=SUM(A1:A3)"

    def test_delete_column(self):
        """Test: Spalte löschen"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(0, 1, 20)  # B1
        manager.set_cell_value(0, 2, 30)  # C1

        initial_cols = manager.matrix.columns

        # Lösche Spalte 1 (B)
        manager.delete_column(1)

        # Prüfe dass Spalte gelöscht wurde
        assert manager.matrix.columns == initial_cols - 1

        # Prüfe dass Zellen verschoben wurden
        assert manager.get_cell_value(0, 0) == 10  # A1 bleibt
        assert manager.get_cell_value(0, 1) == 30  # C1 -> B1

    def test_delete_column_with_formula_update(self):
        """Test: Spalte löschen mit Formel-Aktualisierung"""
        manager = ExcelManager()

        # Setze Werte und Formel
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(0, 1, 20)  # B1
        manager.set_cell_value(0, 2, 30)  # C1
        manager.set_cell_value(0, 3, None, raw_input="=A1+C1")  # D1

        # Prüfe initiale Formel
        cell = manager.get_cell(0, 3)
        assert cell.formula == "=A1+C1"
        assert cell.value == 40

        # Lösche Spalte 1 (B)
        manager.delete_column(1)

        # Prüfe dass Formel aktualisiert wurde
        # D1 ist jetzt C1 und Formel sollte =A1+B1 sein
        cell = manager.get_cell(0, 2)
        assert cell.formula == "=A1+B1"
        assert cell.value == 40

    def test_delete_column_with_range_formula_update(self):
        """Test: Spalte löschen mit Bereichs-Formel-Aktualisierung"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(0, 1, 20)  # B1
        manager.set_cell_value(0, 2, 30)  # C1
        manager.set_cell_value(0, 3, 40)  # D1
        manager.set_cell_value(0, 4, None, raw_input="=SUM(A1:D1)")  # E1

        # Prüfe initiale Formel
        cell = manager.get_cell(0, 4)
        assert cell.formula == "=SUM(A1:D1)"
        assert cell.value == 100

        # Lösche Spalte 1 (B)
        manager.delete_column(1)

        # Prüfe dass Formel aktualisiert wurde
        # E1 ist jetzt D1 und Formel sollte =SUM(A1:C1) sein
        cell = manager.get_cell(0, 3)
        assert cell.formula == "=SUM(A1:C1)"

    def test_row_operations_with_undo(self):
        """Test: Zeilen-Operationen mit Undo"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(1, 0, 20)  # A2

        # Füge Zeile hinzu
        manager.add_row(position=1)
        assert manager.matrix.rows == 101

        # Undo
        manager.undo()
        assert manager.matrix.rows == 100
        assert manager.get_cell_value(0, 0) == 10
        assert manager.get_cell_value(1, 0) == 20

    def test_column_operations_with_undo(self):
        """Test: Spalten-Operationen mit Undo"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(0, 1, 20)  # B1

        # Füge Spalte hinzu
        manager.add_column(position=1)
        assert manager.matrix.columns == 27

        # Undo
        manager.undo()
        assert manager.matrix.columns == 26
        assert manager.get_cell_value(0, 0) == 10
        assert manager.get_cell_value(0, 1) == 20

    def test_complex_formula_update_on_row_insert(self):
        """Test: Komplexe Formel-Aktualisierung bei Zeilen-Einfügung"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(1, 0, 20)  # A2
        manager.set_cell_value(2, 0, 30)  # A3

        # Komplexe Formel mit mehreren Referenzen
        manager.set_cell_value(
            3, 0, None,
            raw_input="=IF(A1>5, SUM(A1:A3), A2)"
        )  # A4

        # Prüfe initiale Formel
        cell = manager.get_cell(3, 0)
        assert cell.formula == "=IF(A1>5, SUM(A1:A3), A2)"
        assert cell.value == 60

        # Füge Zeile bei Position 1 ein
        manager.add_row(position=1)

        # Prüfe dass Formel aktualisiert wurde
        cell = manager.get_cell(4, 0)
        assert cell.formula == "=IF(A1>5, SUM(A1:A4), A3)"

    def test_complex_formula_update_on_column_insert(self):
        """Test: Komplexe Formel-Aktualisierung bei Spalten-Einfügung"""
        manager = ExcelManager()

        # Setze Werte
        manager.set_cell_value(0, 0, 10)  # A1
        manager.set_cell_value(0, 1, 20)  # B1
        manager.set_cell_value(0, 2, 30)  # C1

        # Komplexe Formel mit mehreren Referenzen
        manager.set_cell_value(
            0, 3, None,
            raw_input="=IF(A1>5, SUM(A1:C1), B1)"
        )  # D1

        # Prüfe initiale Formel
        cell = manager.get_cell(0, 3)
        assert cell.formula == "=IF(A1>5, SUM(A1:C1), B1)"
        assert cell.value == 60

        # Füge Spalte bei Position 1 ein
        manager.add_column(position=1)

        # Prüfe dass Formel aktualisiert wurde
        cell = manager.get_cell(0, 4)
        assert cell.formula == "=IF(A1>5, SUM(A1:D1), C1)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
