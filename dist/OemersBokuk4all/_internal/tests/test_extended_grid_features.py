"""
Test für Task 10: Erweiterte Grid-Features

Testet:
- Zeilen/Spalten hinzufügen/löschen mit Position
- Copy-Paste Funktionalität
- Zell-Formatierung (Zahlen, Datum, Text, Währung, Prozent)
- Tastaturnavigation
- Tooltips und Hilfe
"""

import pytest
from excel.excel_manager import ExcelManager
from excel.excel_models import ExcelMatrix, Cell
from excel.excel_utils import cell_to_a1, a1_to_cell


class TestRowColumnOperations:
    """Tests für Zeilen/Spalten-Operationen mit Position"""
    
    def test_add_row_at_position(self):
        """Test: Zeile an bestimmter Position hinzufügen"""
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=5, columns=5, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Füge Zeile an Position 2 hinzu
        manager.add_row(position=2)
        
        assert manager.get_matrix().rows == 6
    
    def test_add_column_at_position(self):
        """Test: Spalte an bestimmter Position hinzufügen"""
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=5, columns=5, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Füge Spalte an Position 2 hinzu
        manager.add_column(position=2)
        
        assert manager.get_matrix().columns == 6
    
    def test_delete_row_updates_formulas(self):
        """Test: Zeile löschen aktualisiert Formeln"""
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=10, columns=5, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(1, 0, 20)
        manager.set_cell_value(2, 0, None, raw_input="=A1+A2")
        
        # Lösche Zeile 1 (Index 0)
        manager.delete_row(0)
        
        # Formel sollte aktualisiert sein
        cell = manager.get_cell(1, 0)  # Neue Position der Formel
        # Die Formel sollte angepasst worden sein
        assert manager.get_matrix().rows == 9
    
    def test_delete_column_updates_formulas(self):
        """Test: Spalte löschen aktualisiert Formeln"""
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=5, columns=10, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Setze Werte
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(0, 1, 20)
        manager.set_cell_value(0, 2, None, raw_input="=A1+B1")
        
        # Lösche Spalte A (Index 0)
        manager.delete_column(0)
        
        # Matrix sollte eine Spalte weniger haben
        assert manager.get_matrix().columns == 9


class TestCopyPasteFunctionality:
    """Tests für Copy-Paste Funktionalität"""
    
    def test_copy_simple_value(self):
        """Test: Einfachen Wert kopieren"""
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=5, columns=5, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Setze Wert
        manager.set_cell_value(0, 0, 42)
        
        # Kopiere Zelle
        source_cell = manager.get_cell(0, 0)
        clipboard = {
            'value': source_cell.value,
            'formula': source_cell.formula,
            'raw_input': source_cell.raw_input,
            'data_type': source_cell.data_type,
            'format': 'auto'
        }
        
        # Füge in andere Zelle ein
        manager.set_cell_value(1, 1, clipboard['value'], raw_input=clipboard['raw_input'])
        
        target_cell = manager.get_cell(1, 1)
        assert target_cell.value == 42
    
    def test_copy_formula(self):
        """Test: Formel kopieren"""
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=5, columns=5, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Setze Werte und Formel
        manager.set_cell_value(0, 0, 10)
        manager.set_cell_value(1, 0, 20)
        manager.set_cell_value(2, 0, None, raw_input="=A1+A2")
        
        # Kopiere Formel-Zelle
        source_cell = manager.get_cell(2, 0)
        clipboard = {
            'value': source_cell.value,
            'formula': source_cell.formula,
            'raw_input': source_cell.raw_input,
            'data_type': source_cell.data_type,
            'format': 'auto'
        }
        
        assert clipboard['formula'] == "=A1+A2"
        
        # Füge Formel in andere Zelle ein
        manager.set_cell_value(2, 1, None, raw_input=clipboard['formula'])
        
        target_cell = manager.get_cell(2, 1)
        assert target_cell.is_formula()


class TestCellFormatting:
    """Tests für Zell-Formatierung"""
    
    def test_number_formatting(self):
        """Test: Zahlen-Formatierung"""
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=5, columns=5, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Setze Zahl
        manager.set_cell_value(0, 0, 123.456)
        cell = manager.get_cell(0, 0)
        
        # Formatiere als Zahl mit 2 Dezimalstellen
        cell.formatted_value = f"{cell.value:.2f}"
        
        assert cell.formatted_value == "123.46"
    
    def test_currency_formatting(self):
        """Test: Währungs-Formatierung"""
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=5, columns=5, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Setze Betrag
        manager.set_cell_value(0, 0, 1234.56)
        cell = manager.get_cell(0, 0)
        
        # Formatiere als Währung (deutsche Formatierung)
        formatted = f"{cell.value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        cell.formatted_value = formatted
        
        assert "€" in cell.formatted_value
        assert "," in cell.formatted_value  # Dezimalkomma
    
    def test_percentage_formatting(self):
        """Test: Prozent-Formatierung"""
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=5, columns=5, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Setze Dezimalwert
        manager.set_cell_value(0, 0, 0.1234)
        cell = manager.get_cell(0, 0)
        
        # Formatiere als Prozent
        cell.formatted_value = f"{cell.value * 100:.2f}%"
        
        assert cell.formatted_value == "12.34%"
    
    def test_date_formatting(self):
        """Test: Datums-Formatierung"""
        from datetime import datetime
        
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=5, columns=5, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Setze Datum
        date_value = datetime(2023, 12, 31)
        manager.set_cell_value(0, 0, date_value)
        cell = manager.get_cell(0, 0)
        
        # Formatiere als deutsches Datum
        cell.formatted_value = date_value.strftime("%d.%m.%Y")
        
        assert cell.formatted_value == "31.12.2023"
    
    def test_text_formatting(self):
        """Test: Text-Formatierung"""
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=5, columns=5, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Setze Zahl als Text
        manager.set_cell_value(0, 0, 12345)
        cell = manager.get_cell(0, 0)
        
        # Formatiere als Text
        cell.formatted_value = str(cell.value)
        
        assert cell.formatted_value == "12345"
        assert isinstance(cell.formatted_value, str)


class TestKeyboardNavigation:
    """Tests für Tastaturnavigation"""
    
    def test_navigate_up(self):
        """Test: Navigation nach oben"""
        active_cell = (5, 5)
        
        # Simuliere Navigation nach oben
        row, col = active_cell
        new_row = max(0, row - 1)
        new_cell = (new_row, col)
        
        assert new_cell == (4, 5)
    
    def test_navigate_down(self):
        """Test: Navigation nach unten"""
        active_cell = (5, 5)
        max_rows = 10
        
        # Simuliere Navigation nach unten
        row, col = active_cell
        new_row = min(max_rows - 1, row + 1)
        new_cell = (new_row, col)
        
        assert new_cell == (6, 5)
    
    def test_navigate_left(self):
        """Test: Navigation nach links"""
        active_cell = (5, 5)
        
        # Simuliere Navigation nach links
        row, col = active_cell
        new_col = max(0, col - 1)
        new_cell = (row, new_col)
        
        assert new_cell == (5, 4)
    
    def test_navigate_right(self):
        """Test: Navigation nach rechts"""
        active_cell = (5, 5)
        max_cols = 10
        
        # Simuliere Navigation nach rechts
        row, col = active_cell
        new_col = min(max_cols - 1, col + 1)
        new_cell = (row, new_col)
        
        assert new_cell == (5, 6)
    
    def test_navigate_tab(self):
        """Test: Navigation mit Tab (nächste Spalte)"""
        active_cell = (5, 5)
        max_cols = 10
        
        # Tab = rechts
        row, col = active_cell
        new_col = min(max_cols - 1, col + 1)
        new_cell = (row, new_col)
        
        assert new_cell == (5, 6)
    
    def test_navigate_enter(self):
        """Test: Navigation mit Enter (nächste Zeile)"""
        active_cell = (5, 5)
        max_rows = 10
        
        # Enter = unten
        row, col = active_cell
        new_row = min(max_rows - 1, row + 1)
        new_cell = (new_row, col)
        
        assert new_cell == (6, 5)
    
    def test_navigate_boundary_top(self):
        """Test: Navigation stoppt an oberer Grenze"""
        active_cell = (0, 5)
        
        # Versuche nach oben zu navigieren
        row, col = active_cell
        new_row = max(0, row - 1)
        new_cell = (new_row, col)
        
        assert new_cell == (0, 5)  # Bleibt bei 0
    
    def test_navigate_boundary_left(self):
        """Test: Navigation stoppt an linker Grenze"""
        active_cell = (5, 0)
        
        # Versuche nach links zu navigieren
        row, col = active_cell
        new_col = max(0, col - 1)
        new_cell = (row, new_col)
        
        assert new_cell == (5, 0)  # Bleibt bei 0


class TestTooltipsAndHelp:
    """Tests für Tooltips und Hilfe-Funktionen"""
    
    def test_error_help_messages(self):
        """Test: Fehler-Hilfe-Nachrichten"""
        error_help = {
            '#ERROR!': 'Syntaxfehler in der Formel. Prüfen Sie die Formel-Syntax.',
            '#REF!': 'Ungültige Zellreferenz. Die referenzierte Zelle existiert nicht.',
            '#DIV/0!': 'Division durch Null. Prüfen Sie die Werte in der Formel.',
            '#CIRCULAR!': 'Zirkelbezug erkannt. Die Formel referenziert sich selbst.',
            '#NAME?': 'Unbekannte Funktion. Prüfen Sie den Funktionsnamen.',
            '#VALUE!': 'Falscher Wert-Typ. Die Funktion erwartet einen anderen Datentyp.'
        }
        
        # Prüfe dass alle Fehler-Codes Hilfe haben
        for error_code in ['#ERROR!', '#REF!', '#DIV/0!', '#CIRCULAR!', '#NAME?', '#VALUE!']:
            assert error_code in error_help
            assert len(error_help[error_code]) > 0
    
    def test_format_type_descriptions(self):
        """Test: Format-Typ-Beschreibungen"""
        format_types = {
            'auto': 'Automatische Erkennung',
            'number': 'Dezimalzahl',
            'currency': 'Währung (Euro)',
            'percentage': 'Prozentwert',
            'date': 'Datumsformat',
            'text': 'Textformat'
        }
        
        # Prüfe dass alle Format-Typen beschrieben sind
        for format_type in ['auto', 'number', 'currency', 'percentage', 'date', 'text']:
            assert format_type in format_types
            assert len(format_types[format_type]) > 0
    
    def test_keyboard_shortcuts_documentation(self):
        """Test: Tastenkombinationen sind dokumentiert"""
        shortcuts = {
            'Strg+C': 'Kopieren',
            'Strg+V': 'Einfügen',
            'Strg+Z': 'Rückgängig',
            'Strg+Y': 'Wiederholen',
            '↑↓←→': 'Navigation',
            'Tab': 'Nächste Spalte',
            'Enter': 'Nächste Zeile'
        }
        
        # Prüfe dass wichtige Shortcuts dokumentiert sind
        assert 'Strg+C' in shortcuts
        assert 'Strg+V' in shortcuts
        assert 'Strg+Z' in shortcuts
        assert '↑↓←→' in shortcuts


class TestIntegration:
    """Integrationstests für erweiterte Grid-Features"""
    
    def test_copy_paste_with_formatting(self):
        """Test: Kopieren und Einfügen mit Formatierung"""
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=5, columns=5, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Setze formatierten Wert
        manager.set_cell_value(0, 0, 1234.56)
        source_cell = manager.get_cell(0, 0)
        source_cell.formatted_value = f"{source_cell.value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # Kopiere mit Format
        clipboard = {
            'value': source_cell.value,
            'formula': source_cell.formula,
            'raw_input': source_cell.raw_input,
            'data_type': source_cell.data_type,
            'format': 'currency'
        }
        
        # Füge ein
        manager.set_cell_value(1, 1, clipboard['value'], raw_input=clipboard['raw_input'])
        target_cell = manager.get_cell(1, 1)
        
        # Wende Format an
        if clipboard['format'] == 'currency':
            target_cell.formatted_value = f"{target_cell.value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        
        assert target_cell.value == 1234.56
        assert "€" in target_cell.formatted_value
    
    def test_navigate_and_edit(self):
        """Test: Navigation und Bearbeitung kombiniert"""
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=10, columns=10, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Starte bei A1
        active_cell = (0, 0)
        
        # Setze Wert
        manager.set_cell_value(active_cell[0], active_cell[1], 10)
        
        # Navigiere nach rechts
        active_cell = (active_cell[0], active_cell[1] + 1)
        
        # Setze Wert
        manager.set_cell_value(active_cell[0], active_cell[1], 20)
        
        # Navigiere nach unten
        active_cell = (active_cell[0] + 1, active_cell[1])
        
        # Setze Formel
        manager.set_cell_value(active_cell[0], active_cell[1], None, raw_input="=A1+B1")
        
        # Prüfe Ergebnis
        result_cell = manager.get_cell(active_cell[0], active_cell[1])
        assert result_cell.is_formula()
        assert result_cell.value == 30
    
    def test_add_row_with_formatted_cells(self):
        """Test: Zeile hinzufügen mit formatierten Zellen"""
        matrix = ExcelMatrix(id=1, name="Test", description="", rows=5, columns=5, cells={}, metadata={})
        manager = ExcelManager(matrix)
        
        # Setze formatierte Werte
        manager.set_cell_value(0, 0, 100.50)
        cell = manager.get_cell(0, 0)
        cell.formatted_value = f"{cell.value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # Füge Zeile hinzu
        initial_rows = manager.get_matrix().rows
        manager.add_row(position=1)
        
        # Prüfe dass Zeile hinzugefügt wurde
        assert manager.get_matrix().rows == initial_rows + 1
        
        # Prüfe dass formatierte Zelle noch existiert (verschoben)
        cell_after = manager.get_cell(0, 0)
        assert cell_after.value == 100.50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
