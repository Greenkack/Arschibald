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
    
    def test_undo_formula_change(self):
        """Test: Undo bei Formel-Änderung"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, 20)
        
        # Setze Formel
        manager.set_cell_value(0, 2, None, raw_input="=A1+B1")
        assert manager.get_cell_value(0, 2) == 30
        
        # Undo Formel
        manager.undo()
        assert manager.get_cell_value(0, 2) is None
        
        # Redo Formel
        manager.redo()
        assert manager.get_cell_value(0, 2) == 30
    
    def test_undo_clear_cell(self):
        """Test: Undo bei Zelle löschen"""
        manager = ExcelManager()
        
        # Setze Wert
        manager.set_cell_value(0, 0, 42)
        assert manager.get_cell_value(0, 0) == 42
        
        # Lösche Zelle
        manager.clear_cell(0, 0)
        assert manager.get_cell_value(0, 0) is None
        
        # Undo
        manager.undo()
        assert manager.get_cell_value(0, 0) == 42
    
    def test_undo_add_row(self):
        """Test: Undo bei Zeile hinzufügen"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(1, 0, 20)
        
        initial_rows = manager.matrix.rows
        
        # Füge Zeile hinzu
        manager.add_row(position=1)
        assert manager.matrix.rows == initial_rows + 1
        assert manager.get_cell_value(2, 0) == 20  # Verschoben
        
        # Undo
        manager.undo()
        assert manager.matrix.rows == initial_rows
        assert manager.get_cell_value(1, 0) == 20  # Zurück
    
    def test_undo_add_column(self):
        """Test: Undo bei Spalte hinzufügen"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, 20)
        
        initial_cols = manager.matrix.columns
        
        # Füge Spalte hinzu
        manager.add_column(position=1)
        assert manager.matrix.columns == initial_cols + 1
        assert manager.get_cell_value(0, 2) == 20  # Verschoben
        
        # Undo
        manager.undo()
        assert manager.matrix.columns == initial_cols
        assert manager.get_cell_value(0, 1) == 20  # Zurück
    
    def test_undo_delete_row(self):
        """Test: Undo bei Zeile löschen"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(1, 0, 20)
        manager.set_cell_value(2, 0, 30)
        
        initial_rows = manager.matrix.rows
        
        # Lösche Zeile
        manager.delete_row(1)
        assert manager.matrix.rows == initial_rows - 1
        assert manager.get_cell_value(1, 0) == 30  # Verschoben
        
        # Undo
        manager.undo()
        assert manager.matrix.rows == initial_rows
        assert manager.get_cell_value(1, 0) == 20  # Wiederhergestellt
        assert manager.get_cell_value(2, 0) == 30
    
    def test_undo_delete_column(self):
        """Test: Undo bei Spalte löschen"""
        manager = ExcelManager()
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, 20)
        manager.set_cell_value(0, 2, 30)
        
        initial_cols = manager.matrix.columns
        
        # Lösche Spalte
        manager.delete_column(1)
        assert manager.matrix.columns == initial_cols - 1
        assert manager.get_cell_value(0, 1) == 30  # Verschoben
        
        # Undo
        manager.undo()
        assert manager.matrix.columns == initial_cols
        assert manager.get_cell_value(0, 1) == 20  # Wiederhergestellt
        assert manager.get_cell_value(0, 2) == 30
    
    def test_redo_clears_on_new_change(self):
        """Test: Redo-Stack wird bei neuer Änderung gelöscht"""
        manager = ExcelManager()
        
        # Änderung 1
        manager.set_cell_value(0, 0, 10)
        
        # Undo
        manager.undo()
        assert manager.can_redo() is True
        
        # Neue Änderung
        manager.set_cell_value(0, 1, 20)
        
        # Redo sollte nicht mehr verfügbar sein
        assert manager.can_redo() is False
    
    def test_undo_stack_limit(self):
        """Test: Undo-Stack hat maximale Größe"""
        manager = ExcelManager()
        max_steps = manager.max_undo_steps
        
        # Mache mehr Änderungen als das Limit
        for i in range(max_steps + 10):
            manager.set_cell_value(0, 0, i)
        
        # Prüfe dass Stack nicht größer als Limit ist
        assert len(manager.undo_stack) <= max_steps
    
    def test_undo_redo_preserves_formulas(self):
        """Test: Undo/Redo erhält Formeln"""
        manager = ExcelManager()
        
        # Setze Werte und Formel
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, 20)
        manager.set_cell_value(0, 2, None, raw_input="=A1+B1")
        
        # Prüfe Formel
        cell = manager.get_cell(0, 2)
        assert cell.formula == "=A1+B1"
        assert cell.value == 30
        
        # Ändere Wert
        manager.set_cell_value(0, 0, 100)
        assert manager.get_cell_value(0, 2) == 120
        
        # Undo
        manager.undo()
        
        # Prüfe dass Formel noch existiert und neu berechnet wurde
        cell = manager.get_cell(0, 2)
        assert cell.formula == "=A1+B1"
        assert cell.value == 30
    
    def test_undo_redo_preserves_dependency_graph(self):
        """Test: Undo/Redo erhält Dependency Graph"""
        manager = ExcelManager()
        
        # Setze Abhängigkeiten
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, None, raw_input="=A1*2")
        manager.set_cell_value(0, 2, None, raw_input="=B1+5")
        
        # Prüfe Dependencies
        assert (0, 1) in manager.dependency_graph
        assert (0, 2) in manager.dependency_graph
        
        # Ändere Wert
        manager.set_cell_value(0, 0, 20)
        
        # Undo
        manager.undo()
        
        # Prüfe dass Dependencies noch existieren
        assert (0, 1) in manager.dependency_graph
        assert (0, 2) in manager.dependency_graph
        
        # Prüfe dass Werte korrekt sind
        assert manager.get_cell_value(0, 0) == 10
        assert manager.get_cell_value(0, 1) == 20
        assert manager.get_cell_value(0, 2) == 25
    
    def test_multiple_undo_redo_sequence(self):
        """Test: Mehrfache Undo/Redo-Sequenz"""
        manager = ExcelManager()
        
        # Änderungen
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, 20)
        manager.set_cell_value(0, 2, 30)
        
        # Undo 2x
        manager.undo()
        manager.undo()
        assert manager.get_cell_value(0, 2) is None
        assert manager.get_cell_value(0, 1) is None
        
        # Redo 1x
        manager.redo()
        assert manager.get_cell_value(0, 1) == 20
        assert manager.get_cell_value(0, 2) is None
        
        # Undo 1x
        manager.undo()
        assert manager.get_cell_value(0, 1) is None
        
        # Redo 2x
        manager.redo()
        manager.redo()
        assert manager.get_cell_value(0, 1) == 20
        assert manager.get_cell_value(0, 2) == 30
    
    def test_undo_when_empty_stack(self):
        """Test: Undo bei leerem Stack"""
        manager = ExcelManager()
        
        # Versuche Undo ohne Änderungen
        success = manager.undo()
        assert success is False
    
    def test_redo_when_empty_stack(self):
        """Test: Redo bei leerem Stack"""
        manager = ExcelManager()
        
        # Versuche Redo ohne Undo
        success = manager.redo()
        assert success is False
    
    def test_undo_with_save_undo_false(self):
        """Test: Änderung ohne Undo-Speicherung"""
        manager = ExcelManager()
        
        # Setze Wert mit save_undo=False
        manager.set_cell_value(0, 0, 10, save_undo=False)
        
        # Undo sollte nicht verfügbar sein
        assert manager.can_undo() is False
    
    def test_undo_redo_with_complex_operations(self):
        """Test: Undo/Redo mit komplexen Operationen"""
        manager = ExcelManager()
        
        # Komplexe Sequenz
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, 20)
        manager.set_cell_value(0, 2, None, raw_input="=SUM(A1:B1)")
        manager.add_row(position=1)
        manager.set_cell_value(1, 0, 30)
        manager.delete_column(1)
        
        # Undo alle Operationen
        for _ in range(6):
            if manager.can_undo():
                manager.undo()
        
        # Prüfe dass alles zurückgesetzt wurde
        assert len(manager.matrix.cells) == 0
        assert manager.matrix.rows == 100
        assert manager.matrix.columns == 26


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


class TestCRUDOperationsComprehensive:
    """Umfassende Tests für CRUD-Operationen"""
    
    def test_create_multiple_cells(self):
        """Test: Mehrere Zellen erstellen"""
        manager = ExcelManager()
        
        # Erstelle 10x10 Grid
        for row in range(10):
            for col in range(10):
                manager.set_cell_value(row, col, row * 10 + col)
        
        # Prüfe alle Werte
        for row in range(10):
            for col in range(10):
                assert manager.get_cell_value(row, col) == row * 10 + col
    
    def test_read_nonexistent_cell(self):
        """Test: Lesen einer nicht existierenden Zelle"""
        manager = ExcelManager()
        
        # Lese Zelle die nicht existiert
        value = manager.get_cell_value(99, 99)
        assert value is None
    
    def test_update_existing_cell(self):
        """Test: Bestehende Zelle aktualisieren"""
        manager = ExcelManager()
        
        # Erstelle Zelle
        manager.set_cell_value(0, 0, 10)
        assert manager.get_cell_value(0, 0) == 10
        
        # Aktualisiere Zelle
        manager.set_cell_value(0, 0, 20)
        assert manager.get_cell_value(0, 0) == 20
    
    def test_delete_cell_with_clear(self):
        """Test: Zelle mit clear_cell löschen"""
        manager = ExcelManager()
        
        # Erstelle Zelle
        manager.set_cell_value(0, 0, 42)
        assert (0, 0) in manager.matrix.cells
        
        # Lösche Zelle
        manager.clear_cell(0, 0)
        assert (0, 0) not in manager.matrix.cells
    
    def test_bulk_operations(self):
        """Test: Bulk-Operationen"""
        manager = ExcelManager()
        
        # Erstelle viele Zellen
        for i in range(100):
            manager.set_cell_value(i, 0, i, save_undo=False)
        
        # Prüfe Anzahl
        assert len(manager.matrix.cells) == 100
        
        # Lösche alle
        for i in range(100):
            manager.clear_cell(i, 0, save_undo=False)
        
        # Prüfe dass alle gelöscht wurden
        assert len(manager.matrix.cells) == 0
    
    def test_crud_with_formulas(self):
        """Test: CRUD mit Formeln"""
        manager = ExcelManager()
        
        # Create: Erstelle Zellen mit Formeln
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, 20)
        manager.set_cell_value(0, 2, None, raw_input="=A1+B1")
        
        # Read: Lese Formel-Ergebnis
        assert manager.get_cell_value(0, 2) == 30
        
        # Update: Aktualisiere Formel
        manager.set_cell_value(0, 2, None, raw_input="=A1*B1")
        assert manager.get_cell_value(0, 2) == 200
        
        # Delete: Lösche Formel
        manager.clear_cell(0, 2)
        assert manager.get_cell_value(0, 2) is None


class TestDependencyGraphComprehensive:
    """Umfassende Tests für Dependency Graph"""
    
    def test_simple_dependency(self):
        """Test: Einfache Abhängigkeit"""
        manager = ExcelManager()
        
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, None, raw_input="=A1")
        
        # Prüfe Dependency
        assert (0, 1) in manager.dependency_graph
        assert (0, 0) in manager.dependency_graph[(0, 1)]
    
    def test_multiple_dependencies(self):
        """Test: Mehrere Abhängigkeiten"""
        manager = ExcelManager()
        
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, 20)
        manager.set_cell_value(0, 2, 30)
        manager.set_cell_value(0, 3, None, raw_input="=A1+B1+C1")
        
        # Prüfe Dependencies
        deps = manager.dependency_graph[(0, 3)]
        assert (0, 0) in deps
        assert (0, 1) in deps
        assert (0, 2) in deps
    
    def test_range_dependency(self):
        """Test: Bereichs-Abhängigkeit"""
        manager = ExcelManager()
        
        for i in range(5):
            manager.set_cell_value(i, 0, i * 10)
        
        manager.set_cell_value(5, 0, None, raw_input="=SUM(A1:A5)")
        
        # Prüfe dass alle Zellen im Bereich als Dependencies erfasst sind
        deps = manager.dependency_graph[(5, 0)]
        for i in range(5):
            assert (i, 0) in deps
    
    def test_nested_dependencies(self):
        """Test: Verschachtelte Abhängigkeiten"""
        manager = ExcelManager()
        
        # A1 = 10
        manager.set_cell_value(0, 0, 10)
        
        # B1 = A1 * 2
        manager.set_cell_value(0, 1, None, raw_input="=A1*2")
        
        # C1 = B1 + 5
        manager.set_cell_value(0, 2, None, raw_input="=B1+5")
        
        # D1 = C1 * 2
        manager.set_cell_value(0, 3, None, raw_input="=C1*2")
        
        # Prüfe Dependency Chain
        assert (0, 0) in manager.dependency_graph[(0, 1)]
        assert (0, 1) in manager.dependency_graph[(0, 2)]
        assert (0, 2) in manager.dependency_graph[(0, 3)]
    
    def test_dependency_update_on_formula_change(self):
        """Test: Dependency-Update bei Formel-Änderung"""
        manager = ExcelManager()
        
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, 20)
        manager.set_cell_value(0, 2, None, raw_input="=A1")
        
        # Prüfe initiale Dependency
        assert (0, 0) in manager.dependency_graph[(0, 2)]
        assert (0, 1) not in manager.dependency_graph[(0, 2)]
        
        # Ändere Formel
        manager.set_cell_value(0, 2, None, raw_input="=B1")
        
        # Prüfe aktualisierte Dependency
        assert (0, 0) not in manager.dependency_graph[(0, 2)]
        assert (0, 1) in manager.dependency_graph[(0, 2)]
    
    def test_dependency_removal_on_clear(self):
        """Test: Dependency-Entfernung bei clear_cell"""
        manager = ExcelManager()
        
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, None, raw_input="=A1")
        
        # Prüfe Dependency existiert
        assert (0, 1) in manager.dependency_graph
        
        # Lösche Zelle
        manager.clear_cell(0, 1)
        
        # Prüfe Dependency wurde entfernt
        assert (0, 1) not in manager.dependency_graph
    
    def test_affected_cells_calculation(self):
        """Test: Berechnung betroffener Zellen"""
        manager = ExcelManager()
        
        # Erstelle Dependency Chain
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, None, raw_input="=A1*2")
        manager.set_cell_value(0, 2, None, raw_input="=B1+5")
        
        # Hole betroffene Zellen
        affected = manager._get_all_affected_cells_recursive((0, 0), set())
        
        # Prüfe dass beide abhängigen Zellen gefunden wurden
        assert (0, 1) in affected
        assert (0, 2) in affected
    
    def test_dependency_graph_rebuild(self):
        """Test: Dependency Graph Rebuild"""
        manager = ExcelManager()
        
        # Erstelle Formeln
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, None, raw_input="=A1")
        
        # Lösche Graph
        manager.dependency_graph.clear()
        assert len(manager.dependency_graph) == 0
        
        # Rebuild
        manager._rebuild_dependency_graph()
        
        # Prüfe dass Graph wiederhergestellt wurde
        assert (0, 1) in manager.dependency_graph
        assert (0, 0) in manager.dependency_graph[(0, 1)]
    
    def test_circular_reference_detection(self):
        """Test: Zirkelbezug-Erkennung"""
        manager = ExcelManager()
        
        # A1 = B1
        manager.set_cell_value(0, 0, None, raw_input="=B1")
        
        # Prüfe ob B1 = A1 einen Zirkelbezug erstellen würde
        would_create = manager._would_create_circular_reference(0, 1, "=A1")
        assert would_create is True
    
    def test_complex_dependency_network(self):
        """Test: Komplexes Dependency-Netzwerk"""
        manager = ExcelManager()
        
        # Erstelle komplexes Netzwerk
        # A1 = 10
        manager.set_cell_value(0, 0, 10)
        
        # B1 = A1, C1 = A1
        manager.set_cell_value(0, 1, None, raw_input="=A1")
        manager.set_cell_value(0, 2, None, raw_input="=A1")
        
        # D1 = B1 + C1
        manager.set_cell_value(0, 3, None, raw_input="=B1+C1")
        
        # Prüfe Dependencies
        assert (0, 0) in manager.dependency_graph[(0, 1)]
        assert (0, 0) in manager.dependency_graph[(0, 2)]
        assert (0, 1) in manager.dependency_graph[(0, 3)]
        assert (0, 2) in manager.dependency_graph[(0, 3)]
        
        # Ändere A1 und prüfe dass alle neu berechnet werden
        manager.set_cell_value(0, 0, 20)
        assert manager.get_cell_value(0, 1) == 20
        assert manager.get_cell_value(0, 2) == 20
        assert manager.get_cell_value(0, 3) == 40


class TestPerformance:
    """Performance-Tests für ExcelManager"""
    
    def test_large_matrix_creation(self):
        """Test: Große Matrix erstellen"""
        import time
        
        manager = ExcelManager()
        
        start = time.time()
        
        # Erstelle 1000 Zellen
        for i in range(1000):
            manager.set_cell_value(i, 0, i, save_undo=False)
        
        elapsed = time.time() - start
        
        # Sollte unter 1 Sekunde sein
        assert elapsed < 1.0
        assert len(manager.matrix.cells) == 1000
    
    def test_formula_recalculation_performance(self):
        """Test: Performance der Formel-Neuberechnung"""
        import time
        
        manager = ExcelManager()
        
        # Erstelle 100 Formeln die voneinander abhängen
        manager.set_cell_value(0, 0, 1)
        
        for i in range(1, 100):
            ref = f"A{i}"
            manager.set_cell_value(i, 0, None, raw_input=f"={ref}+1", save_undo=False)
        
        start = time.time()
        
        # Ändere erste Zelle (triggert Neuberechnung aller)
        manager.set_cell_value(0, 0, 10, save_undo=False)
        
        elapsed = time.time() - start
        
        # Sollte unter 2 Sekunden sein (Requirement 11.2)
        assert elapsed < 2.0
        
        # Prüfe dass letzte Zelle korrekt berechnet wurde
        assert manager.get_cell_value(99, 0) == 109  # 10 + 99
    
    def test_undo_stack_memory_efficiency(self):
        """Test: Speicher-Effizienz des Undo-Stacks"""
        manager = ExcelManager()
        
        # Mache viele Änderungen
        for i in range(100):
            manager.set_cell_value(0, 0, i)
        
        # Prüfe dass Stack begrenzt ist
        assert len(manager.undo_stack) <= manager.max_undo_steps
    
    def test_dependency_graph_performance(self):
        """Test: Performance des Dependency Graphs"""
        import time
        
        manager = ExcelManager()
        
        # Erstelle 50 Zellen mit Formeln
        for i in range(50):
            manager.set_cell_value(i, 0, i)
            manager.set_cell_value(i, 1, None, raw_input=f"=A{i+1}*2", save_undo=False)
        
        start = time.time()
        
        # Rebuild Dependency Graph
        manager._rebuild_dependency_graph()
        
        elapsed = time.time() - start
        
        # Sollte sehr schnell sein
        assert elapsed < 0.5
        assert len(manager.dependency_graph) == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
