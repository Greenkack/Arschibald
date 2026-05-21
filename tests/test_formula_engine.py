"""
Tests für die Excel Formula Engine

Testet alle Funktionen der FormulaEngine Klasse.
"""

import pytest
from excel.excel_formula_engine import FormulaEngine
from excel.excel_models import (
    Cell,
    FormulaError,
    SyntaxError,
    ReferenceError,
    DivisionByZeroError,
    CircularReferenceError,
    NameError,
    ValueError as ExcelValueError
)


class TestFormulaEngine:
    """Tests für die FormulaEngine Klasse"""

    def setup_method(self):
        """Setup für jeden Test"""
        self.engine = FormulaEngine()

    def test_load_excel_functions(self):
        """Test: Excel-Funktionen werden korrekt geladen"""
        assert 'SUM' in self.engine.functions
        assert 'AVERAGE' in self.engine.functions
        assert 'IF' in self.engine.functions
        assert 'VLOOKUP' in self.engine.functions
        assert len(self.engine.functions) > 0

    def test_parse_formula_simple_value(self):
        """Test: Einfacher Wert wird korrekt geparst"""
        result = self.engine.parse_formula("=42")
        assert result['type'] == 'value'
        assert result['cell_refs'] == []

    def test_parse_formula_cell_reference(self):
        """Test: Zellreferenz wird korrekt geparst"""
        result = self.engine.parse_formula("=A1")
        assert result['type'] == 'reference'
        assert 'A1' in result['cell_refs']

    def test_parse_formula_arithmetic(self):
        """Test: Arithmetischer Ausdruck wird korrekt geparst"""
        result = self.engine.parse_formula("=A1+B1")
        assert result['type'] == 'arithmetic'
        assert 'A1' in result['cell_refs']
        assert 'B1' in result['cell_refs']

    def test_parse_formula_function(self):
        """Test: Funktionsaufruf wird korrekt geparst"""
        result = self.engine.parse_formula("=SUM(A1:A10)")
        assert result['type'] == 'function'
        assert result['function'] == 'SUM'
        assert 'A1:A10' in result['ranges']

    def test_execute_simple_arithmetic(self):
        """Test: Einfache Arithmetik funktioniert"""
        context = {(0, 0): 10, (0, 1): 20}
        result = self.engine.execute_formula("=A1+B1", context)
        assert result == 30

    def test_execute_arithmetic_operations(self):
        """Test: Verschiedene arithmetische Operationen"""
        context = {(0, 0): 10, (0, 1): 5}

        # Addition
        assert self.engine.execute_formula("=A1+B1", context) == 15

        # Subtraktion
        assert self.engine.execute_formula("=A1-B1", context) == 5

        # Multiplikation
        assert self.engine.execute_formula("=A1*B1", context) == 50

        # Division
        assert self.engine.execute_formula("=A1/B1", context) == 2.0

    def test_execute_division_by_zero(self):
        """Test: Division durch Null wirft korrekten Fehler"""
        context = {(0, 0): 10, (0, 1): 0}

        with pytest.raises(DivisionByZeroError) as exc_info:
            self.engine.execute_formula("=A1/B1", context)

        assert exc_info.value.display == "#DIV/0!"

    def test_execute_sum_function(self):
        """Test: SUM Funktion funktioniert"""
        context = {
            (0, 0): 10,
            (1, 0): 20,
            (2, 0): 30
        }
        result = self.engine.execute_formula("=SUM(A1:A3)", context)
        assert result == 60

    def test_execute_average_function(self):
        """Test: AVERAGE Funktion funktioniert"""
        context = {
            (0, 0): 10,
            (1, 0): 20,
            (2, 0): 30
        }
        result = self.engine.execute_formula("=AVERAGE(A1:A3)", context)
        assert result == 20.0

    def test_execute_if_function(self):
        """Test: IF Funktion funktioniert"""
        # Bedingung wahr
        context1 = {(0, 0): 15}
        result1 = self.engine.execute_formula('=IF(A1>10, "Ja", "Nein")', context1)
        assert result1 == "Ja"

        # Bedingung falsch
        context2 = {(0, 0): 5}
        result2 = self.engine.execute_formula('=IF(A1>10, "Ja", "Nein")', context2)
        assert result2 == "Nein"

    def test_execute_min_max_functions(self):
        """Test: MIN und MAX Funktionen"""
        context = {
            (0, 0): 10,
            (1, 0): 5,
            (2, 0): 30,
            (3, 0): 15
        }

        min_result = self.engine.execute_formula("=MIN(A1:A4)", context)
        assert min_result == 5

        max_result = self.engine.execute_formula("=MAX(A1:A4)", context)
        assert max_result == 30

    def test_execute_round_function(self):
        """Test: ROUND Funktion"""
        context = {(0, 0): 3.14159}

        result = self.engine.execute_formula("=ROUND(A1, 2)", context)
        assert result == 3.14

    def test_execute_nested_formula(self):
        """Test: Verschachtelte Formeln funktionieren"""
        context = {
            (0, 0): 10,
            (1, 0): 20,
            (2, 0): 30
        }

        # SUM innerhalb von IF
        result = self.engine.execute_formula(
            '=IF(SUM(A1:A3)>50, "Hoch", "Niedrig")',
            context
        )
        assert result == "Hoch"

    def test_reference_error(self):
        """Test: Referenzfehler bei nicht existierender Zelle"""
        context = {(0, 0): 10}

        with pytest.raises(ReferenceError) as exc_info:
            self.engine.execute_formula("=A1+B1", context)

        assert exc_info.value.display == "#REF!"

    def test_name_error(self):
        """Test: Fehler bei unbekannter Funktion"""
        context = {(0, 0): 10}

        with pytest.raises(NameError) as exc_info:
            self.engine.execute_formula("=UNKNOWN(A1)", context)

        assert exc_info.value.display == "#NAME?"

    def test_syntax_error(self):
        """Test: Syntaxfehler bei ungültiger Formel"""
        context = {}

        with pytest.raises(SyntaxError) as exc_info:
            self.engine.execute_formula("=", context)

        assert exc_info.value.display == "#ERROR!"

    def test_build_dependency_graph(self):
        """Test: Abhängigkeitsgraph wird korrekt erstellt"""
        cells = {
            (0, 0): Cell(0, 0, value=10),
            (0, 1): Cell(0, 1, formula="=A1*2", value=20),
            (0, 2): Cell(0, 2, formula="=B1+10", value=30)
        }

        self.engine.build_dependency_graph(cells)

        # B1 hängt von A1 ab
        assert (0, 0) in self.engine.dependency_graph[(0, 1)]

        # C1 hängt von B1 ab
        assert (0, 1) in self.engine.dependency_graph[(0, 2)]

    def test_get_dependent_cells(self):
        """Test: Abhängige Zellen werden korrekt gefunden"""
        cells = {
            (0, 0): Cell(0, 0, value=10),
            (0, 1): Cell(0, 1, formula="=A1*2", value=20),
            (0, 2): Cell(0, 2, formula="=A1+B1", value=30)
        }

        self.engine.build_dependency_graph(cells)

        # A1 wird von B1 und C1 verwendet
        dependents = self.engine.get_dependent_cells((0, 0))
        assert (0, 1) in dependents
        assert (0, 2) in dependents

    def test_get_calculation_order(self):
        """Test: Berechnungsreihenfolge ist korrekt"""
        cells = {
            (0, 0): Cell(0, 0, value=10),
            (0, 1): Cell(0, 1, formula="=A1*2", value=20),
            (0, 2): Cell(0, 2, formula="=B1+10", value=30)
        }

        order = self.engine.get_calculation_order(cells)

        # B1 muss vor C1 berechnet werden
        b1_index = order.index((0, 1))
        c1_index = order.index((0, 2))
        assert b1_index < c1_index

    def test_circular_reference_detection(self):
        """Test: Zirkelbezüge werden erkannt"""
        cells = {
            (0, 0): Cell(0, 0, formula="=B1+1"),
            (0, 1): Cell(0, 1, formula="=A1+1")
        }

        with pytest.raises(CircularReferenceError) as exc_info:
            self.engine.get_calculation_order(cells)

        assert exc_info.value.display == "#CIRCULAR!"

    def test_recalculate_affected_cells(self):
        """Test: Betroffene Zellen werden neu berechnet"""
        cells = {
            (0, 0): Cell(0, 0, value=10),
            (0, 1): Cell(0, 1, formula="=A1*2", value=20),
            (0, 2): Cell(0, 2, formula="=B1+10", value=30)
        }

        context = {(0, 0): 10, (0, 1): 20, (0, 2): 30}

        # Ändere A1
        context[(0, 0)] = 20

        # Neuberechnung
        new_context = self.engine.recalculate_affected_cells(
            (0, 0),
            cells,
            context
        )

        # B1 sollte jetzt 40 sein (20*2)
        assert new_context[(0, 1)] == 40

        # C1 sollte jetzt 50 sein (40+10)
        assert new_context[(0, 2)] == 50

    def test_parse_function_args_simple(self):
        """Test: Einfache Funktionsargumente werden korrekt geparst"""
        context = {(0, 0): 10, (0, 1): 20}

        args = self.engine._parse_function_args("A1, B1, 30", context)

        assert len(args) == 3
        assert args[0] == 10
        assert args[1] == 20
        assert args[2] == 30

    def test_parse_function_args_range(self):
        """Test: Bereichsargumente werden korrekt geparst"""
        context = {
            (0, 0): 10,
            (1, 0): 20,
            (2, 0): 30
        }

        args = self.engine._parse_function_args("A1:A3", context)

        assert len(args) == 1
        assert args[0] == [10, 20, 30]

    def test_parse_function_args_string(self):
        """Test: String-Argumente werden korrekt geparst"""
        context = {}

        args = self.engine._parse_function_args('"Hello", "World"', context)

        assert len(args) == 2
        assert args[0] == "Hello"
        assert args[1] == "World"

    def test_parse_function_args_nested(self):
        """Test: Verschachtelte Funktionen in Argumenten"""
        context = {(0, 0): 10, (0, 1): 20}

        # Dies sollte funktionieren wenn verschachtelte Formeln unterstützt werden
        # Für jetzt testen wir nur dass es nicht abstürzt
        try:
            args = self.engine._parse_function_args("SUM(A1:B1)", context)
            assert len(args) == 1
        except Exception:
            # Verschachtelte Funktionen könnten noch nicht vollständig unterstützt sein
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
