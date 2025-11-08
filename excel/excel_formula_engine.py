"""
Excel Integration - Formula Engine

Dieses Modul implementiert die Formel-Engine für die Excel-Integration.
Es parst und führt Excel-Formeln aus und verwaltet Abhängigkeiten zwischen Zellen.
"""

import re
from typing import Any, Dict, List, Set, Tuple, Optional
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
from excel.excel_utils import (
    extract_cell_references,
    parse_range,
    a1_to_cell,
    is_valid_cell_reference,
    is_valid_range_reference
)
from excel import python_function_recipes as xl_funcs


class FormulaEngine:
    """
    Formel-Engine für Excel-Formeln

    Diese Klasse parst und führt Excel-Formeln aus. Sie unterstützt:
    - Einfache Arithmetik (+, -, *, /)
    - Excel-Funktionen (SUM, AVERAGE, IF, VLOOKUP, etc.)
    - Zellreferenzen (A1, B2, etc.)
    - Bereiche (A1:A10)
    - Verschachtelte Formeln
    - Caching für Performance-Optimierung

    Attributes:
        functions: Dictionary mit verfügbaren Excel-Funktionen
        dependency_graph: Graph der Zellabhängigkeiten
        formula_cache: Cache für berechnete Formelergebnisse
        dependency_cache: Cache für Zellabhängigkeiten
        cache_enabled: Flag ob Caching aktiviert ist
    """

    def __init__(self, enable_cache: bool = True):
        """
        Initialisiert die Formel-Engine

        Args:
            enable_cache: Ob Caching aktiviert werden soll (Standard: True)
        """
        self.functions = self._load_excel_functions()
        self.dependency_graph: Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}

        # Caching-System
        self.cache_enabled = enable_cache
        self.formula_cache: Dict[str, Any] = {}
        self.dependency_cache: Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}
        self._cache_hits = 0
        self._cache_misses = 0

    def _load_excel_functions(self) -> Dict[str, callable]:
        """
        Lädt alle verfügbaren Excel-Funktionen aus python_function_recipes

        Returns:
            Dictionary mit Funktionsnamen als Keys und Funktionen als Values
        """
        functions = {}

        # Lade alle xl_* Funktionen aus dem Modul
        for name in dir(xl_funcs):
            if name.startswith('xl_'):
                func = getattr(xl_funcs, name)
                if callable(func):
                    # Entferne 'xl_' Präfix für Excel-Kompatibilität
                    excel_name = name[3:].upper()
                    functions[excel_name] = func

        return functions

    def parse_formula(self, formula: str) -> Dict[str, Any]:
        """
        Parst eine Excel-Formel und extrahiert Informationen

        Args:
            formula: Die zu parsende Formel (mit oder ohne '=')

        Returns:
            Dictionary mit:
            - 'type': 'function', 'arithmetic', 'reference', 'value'
            - 'function': Funktionsname (falls type='function')
            - 'args': Liste von Argumenten
            - 'cell_refs': Liste aller Zellreferenzen
            - 'ranges': Liste aller Bereichsreferenzen

        Raises:
            SyntaxError: Wenn die Formel ungültig ist
        """
        # Entferne führendes '=' falls vorhanden
        if formula.startswith('='):
            formula = formula[1:].strip()

        if not formula:
            raise SyntaxError("Leere Formel", display="#ERROR!")

        # Extrahiere alle Zellreferenzen
        cell_refs = extract_cell_references(formula)

        # Prüfe ob es eine Funktion ist
        func_match = re.match(r'^([A-Z_]+)\s*\(', formula, re.IGNORECASE)

        if func_match:
            # Funktionsaufruf
            func_name = func_match.group(1).upper()
            return {
                'type': 'function',
                'function': func_name,
                'formula': formula,
                'cell_refs': cell_refs,
                'ranges': [ref for ref in cell_refs if ':' in ref]
            }
        elif any(op in formula for op in ['+', '-', '*', '/', '>', '<', '=']):
            # Arithmetischer Ausdruck oder Vergleich
            return {
                'type': 'arithmetic',
                'formula': formula,
                'cell_refs': cell_refs,
                'ranges': [ref for ref in cell_refs if ':' in ref]
            }
        elif cell_refs:
            # Einfache Zellreferenz
            return {
                'type': 'reference',
                'formula': formula,
                'cell_refs': cell_refs,
                'ranges': []
            }
        else:
            # Konstanter Wert
            return {
                'type': 'value',
                'formula': formula,
                'cell_refs': [],
                'ranges': []
            }

    def execute_formula(
        self,
        formula: str,
        context: Dict[Tuple[int, int], Any]
    ) -> Any:
        """
        Führt eine Excel-Formel aus (mit Caching)

        Args:
            formula: Die auszuführende Formel (mit oder ohne '=')
            context: Dictionary mit Zellwerten {(row, col): value}

        Returns:
            Berechnetes Ergebnis

        Raises:
            FormulaError: Bei Fehlern in der Formel oder Berechnung
        """
        # Prüfe Cache wenn aktiviert
        if self.cache_enabled:
            cache_key = self._build_cache_key(formula, context)
            if cache_key in self.formula_cache:
                self._cache_hits += 1
                return self.formula_cache[cache_key]
            self._cache_misses += 1

        try:
            # Parse die Formel
            parsed = self.parse_formula(formula)

            # Entferne führendes '=' falls vorhanden
            if formula.startswith('='):
                formula_clean = formula[1:].strip()
            else:
                formula_clean = formula

            # Ersetze Zellreferenzen durch Werte
            formula_with_values = self._replace_cell_references(
                formula_clean,
                context
            )

            # Führe die Formel aus basierend auf dem Typ
            if parsed['type'] == 'function':
                result = self._execute_function(formula_with_values, context)
            elif parsed['type'] == 'arithmetic':
                result = self._execute_arithmetic(formula_with_values)
            elif parsed['type'] == 'reference':
                # Einfache Referenz - gib den Wert zurück
                cell_ref = parsed['cell_refs'][0]
                row, col = a1_to_cell(cell_ref)
                if (row, col) not in context:
                    raise ReferenceError(
                        f"Zelle {cell_ref} nicht gefunden",
                        display="#REF!"
                    )
                result = context[(row, col)]
            elif parsed['type'] == 'value':
                # Konstanter Wert
                result = self._parse_value(formula_clean)
            else:
                result = None

            # Speichere im Cache wenn aktiviert
            if self.cache_enabled:
                cache_key = self._build_cache_key(formula, context)
                self.formula_cache[cache_key] = result

            return result

        except FormulaError:
            raise
        except ZeroDivisionError:
            raise DivisionByZeroError(
                "Division durch Null",
                display="#DIV/0!"
            )
        except Exception as e:
            raise SyntaxError(
                f"Fehler beim Ausführen der Formel: {str(e)}",
                display="#ERROR!"
            )

    def _replace_cell_references(
        self,
        formula: str,
        context: Dict[Tuple[int, int], Any]
    ) -> str:
        """
        Ersetzt Zellreferenzen in einer Formel durch ihre Werte

        Args:
            formula: Die Formel
            context: Dictionary mit Zellwerten

        Returns:
            Formel mit ersetzten Referenzen

        Raises:
            ReferenceError: Wenn eine Zellreferenz nicht gefunden wird
        """
        def replace_ref(match):
            """Callback für regex replacement"""
            ref = match.group(0)

            # Prüfe ob es ein Bereich ist (enthält :)
            # Bereiche werden NICHT ersetzt, sondern von Funktionen verarbeitet
            if ':' in ref:
                return ref

            # Einzelne Zellreferenz
            if not is_valid_cell_reference(ref):
                return ref  # Keine gültige Referenz, behalte Original

            try:
                row, col = a1_to_cell(ref)
                if (row, col) not in context:
                    raise ReferenceError(
                        f"Zelle {ref} nicht gefunden",
                        display="#REF!"
                    )

                value = context[(row, col)]

                # Formatiere den Wert für die Formel
                if isinstance(value, str):
                    # Strings in Anführungszeichen
                    return f'"{value}"'
                elif value is None:
                    return '0'
                else:
                    return str(value)

            except ReferenceError:
                raise
            except Exception:
                return ref

        # Regex für Zellreferenzen und Bereiche
        # Matcht: A1, AA10, A1:B2, aber nicht in "A1" oder 'A1'
        pattern = r'\b([A-Z]+\d+(?::[A-Z]+\d+)?)\b'

        return re.sub(pattern, replace_ref, formula, flags=re.IGNORECASE)

    def _execute_function(
        self,
        formula: str,
        context: Dict[Tuple[int, int], Any]
    ) -> Any:
        """
        Führt einen Funktionsaufruf aus

        Args:
            formula: Die Formel mit Funktionsaufruf
            context: Dictionary mit Zellwerten

        Returns:
            Ergebnis der Funktion

        Raises:
            NameError: Wenn die Funktion nicht existiert
            SyntaxError: Bei ungültiger Syntax
        """
        # Extrahiere Funktionsname und Argumente
        func_match = re.match(
            r'^([A-Z_]+)\s*\((.*)\)$',
            formula,
            re.IGNORECASE | re.DOTALL
        )

        if not func_match:
            raise SyntaxError(
                "Ungültige Funktionssyntax",
                display="#ERROR!"
            )

        func_name = func_match.group(1).upper()
        args_str = func_match.group(2)

        # Prüfe ob Funktion existiert
        if func_name not in self.functions:
            raise NameError(
                f"Unbekannte Funktion: {func_name}",
                display="#NAME?"
            )

        # Parse Argumente
        args = self._parse_function_args(args_str, context)

        # Führe Funktion aus
        try:
            func = self.functions[func_name]
            result = func(*args)
            return result
        except Exception as e:
            raise ExcelValueError(
                f"Fehler in Funktion {func_name}: {str(e)}",
                display="#VALUE!"
            )

    def _parse_function_args(
        self,
        args_str: str,
        context: Dict[Tuple[int, int], Any]
    ) -> List[Any]:
        """
        Parst Funktionsargumente

        Args:
            args_str: String mit Argumenten (z.B. "A1, B2, 10")
            context: Dictionary mit Zellwerten

        Returns:
            Liste von geparsten Argumenten

        Raises:
            SyntaxError: Bei ungültiger Syntax
        """
        if not args_str.strip():
            return []

        args = []
        current_arg = ""
        paren_depth = 0
        in_string = False
        string_char = None

        # Parse Argumente unter Berücksichtigung von Klammern und Strings
        for char in args_str:
            if in_string:
                current_arg += char
                if char == string_char:
                    in_string = False
            elif char in ('"', "'"):
                in_string = True
                string_char = char
                current_arg += char
            elif char == '(':
                paren_depth += 1
                current_arg += char
            elif char == ')':
                paren_depth -= 1
                current_arg += char
            elif char == ',' and paren_depth == 0:
                # Argument-Trenner
                args.append(self._parse_argument(current_arg.strip(), context))
                current_arg = ""
            else:
                current_arg += char

        # Letztes Argument
        if current_arg.strip():
            args.append(self._parse_argument(current_arg.strip(), context))

        return args

    def _parse_argument(
        self,
        arg: str,
        context: Dict[Tuple[int, int], Any]
    ) -> Any:
        """
        Parst ein einzelnes Funktionsargument

        Args:
            arg: Das Argument als String
            context: Dictionary mit Zellwerten

        Returns:
            Geparster Wert (kann Zahl, String, Liste, etc. sein)

        Raises:
            ReferenceError: Bei ungültigen Zellreferenzen
        """
        arg = arg.strip()

        # Prüfe ob es ein Bereich ist (A1:A10)
        if ':' in arg and is_valid_range_reference(arg):
            cells = parse_range(arg)
            values = []
            for row, col in cells:
                if (row, col) in context:
                    val = context[(row, col)]
                    if val is not None:
                        values.append(val)
            return values

        # Prüfe ob es ein String ist (in Anführungszeichen)
        if (arg.startswith('"') and arg.endswith('"')) or \
           (arg.startswith("'") and arg.endswith("'")):
            return arg[1:-1]

        # Prüfe ob es ein Boolean ist
        if arg.upper() == 'TRUE':
            return True
        elif arg.upper() == 'FALSE':
            return False

        # Prüfe ob es ein Vergleichs- oder arithmetischer Ausdruck ist
        # WICHTIG: Dies muss VOR der Zellreferenz-Prüfung kommen
        if any(op in arg for op in ['>=', '<=', '<>', '>', '<', '==', '!=', '+', '-', '*', '/']):
            # Prüfe ob es verschachtelte Funktionen enthält
            if '(' in arg:
                # Finde und ersetze alle Funktionsaufrufe durch ihre Ergebnisse
                # z.B. "SUM(A1:A3)>50" -> "60>50"
                result_str = self._evaluate_nested_functions(arg, context)
                return self._execute_arithmetic(result_str)
            else:
                # Einfacher Ausdruck ohne Funktionen
                formula_with_values = self._replace_cell_references(arg, context)
                return self._execute_arithmetic(formula_with_values)

        # Prüfe ob es eine Zellreferenz ist
        if is_valid_cell_reference(arg):
            row, col = a1_to_cell(arg)
            if (row, col) not in context:
                raise ReferenceError(
                    f"Zelle {arg} nicht gefunden",
                    display="#REF!"
                )
            return context[(row, col)]

        # Prüfe ob es eine Zahl ist
        try:
            if '.' in arg:
                return float(arg)
            else:
                return int(arg)
        except ValueError:
            pass

        # Prüfe ob es eine verschachtelte Funktion ist
        if '(' in arg:
            # Reine Funktion
            return self._execute_function(arg, context)

        # Sonst als String behandeln
        return arg

    def _evaluate_nested_functions(
        self,
        expression: str,
        context: Dict[Tuple[int, int], Any]
    ) -> str:
        """
        Evaluiert verschachtelte Funktionen in einem Ausdruck

        Args:
            expression: Ausdruck mit Funktionen (z.B. "SUM(A1:A3)>50")
            context: Dictionary mit Zellwerten

        Returns:
            Ausdruck mit evaluierten Funktionen (z.B. "60>50")
        """
        # Finde alle Funktionsaufrufe im Ausdruck
        # Regex für Funktionen: FUNKTIONSNAME(...)
        pattern = r'([A-Z_]+)\s*\(([^()]*(?:\([^()]*\))*[^()]*)\)'

        def replace_function(match):
            """Callback für regex replacement"""
            func_name = match.group(1).upper()
            args_str = match.group(2)

            # Führe die Funktion aus
            try:
                result = self._execute_function(
                    f"{func_name}({args_str})",
                    context
                )
                return str(result)
            except Exception:
                # Bei Fehler: Original beibehalten
                return match.group(0)

        # Ersetze alle Funktionen durch ihre Ergebnisse
        # Wiederhole bis keine Funktionen mehr vorhanden sind (für verschachtelte Funktionen)
        max_iterations = 10  # Verhindere Endlosschleifen
        for _ in range(max_iterations):
            new_expression = re.sub(pattern, replace_function, expression, flags=re.IGNORECASE)
            if new_expression == expression:
                # Keine Änderungen mehr
                break
            expression = new_expression

        # Ersetze verbleibende Zellreferenzen
        expression = self._replace_cell_references(expression, context)

        return expression

    def _execute_arithmetic(self, formula: str) -> Any:
        """
        Führt einen arithmetischen Ausdruck aus

        Args:
            formula: Der arithmetische Ausdruck

        Returns:
            Berechnetes Ergebnis

        Raises:
            SyntaxError: Bei ungültiger Syntax
            DivisionByZeroError: Bei Division durch Null
        """
        try:
            # Verwende eval für arithmetische Ausdrücke
            # Sicherheitshinweis: In Produktion sollte ein sicherer Parser
            # verwendet werden (z.B. ast.literal_eval mit Whitelist)
            result = eval(formula, {"__builtins__": {}}, {})
            return result
        except ZeroDivisionError:
            raise DivisionByZeroError(
                "Division durch Null",
                display="#DIV/0!"
            )
        except Exception as e:
            raise SyntaxError(
                f"Fehler im arithmetischen Ausdruck: {str(e)}",
                display="#ERROR!"
            )

    def _parse_value(self, value_str: str) -> Any:
        """
        Parst einen konstanten Wert

        Args:
            value_str: Der Wert als String

        Returns:
            Geparster Wert
        """
        value_str = value_str.strip()

        # String in Anführungszeichen
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]

        # Boolean
        if value_str.upper() == 'TRUE':
            return True
        elif value_str.upper() == 'FALSE':
            return False

        # Zahl
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass

        # Sonst als String
        return value_str

    def build_dependency_graph(
        self,
        cells: Dict[Tuple[int, int], Cell]
    ) -> None:
        """
        Erstellt einen Abhängigkeitsgraphen für alle Zellen mit Formeln

        Der Graph zeigt welche Zellen von welchen anderen Zellen abhängen.
        Dies ermöglicht effiziente Neuberechnung bei Änderungen.

        Args:
            cells: Dictionary mit allen Zellen {(row, col): Cell}
        """
        self.dependency_graph = {}

        for (row, col), cell in cells.items():
            if cell.is_formula():
                # Extrahiere alle Zellreferenzen aus der Formel
                refs = extract_cell_references(cell.formula)

                dependencies = set()
                for ref in refs:
                    if ':' in ref:
                        # Bereich
                        range_cells = parse_range(ref)
                        dependencies.update(range_cells)
                    else:
                        # Einzelne Zelle
                        try:
                            dep_row, dep_col = a1_to_cell(ref)
                            dependencies.add((dep_row, dep_col))
                        except ValueError:
                            # Ungültige Referenz ignorieren
                            pass

                self.dependency_graph[(row, col)] = dependencies

    def get_dependent_cells(
        self,
        cell: Tuple[int, int]
    ) -> Set[Tuple[int, int]]:
        """
        Gibt alle Zellen zurück die von der angegebenen Zelle abhängen

        Args:
            cell: Tupel (row, col) der Zelle

        Returns:
            Set von Zellen die von dieser Zelle abhängen
        """
        dependents = set()

        for dependent_cell, dependencies in self.dependency_graph.items():
            if cell in dependencies:
                dependents.add(dependent_cell)

        return dependents

    def get_calculation_order(
        self,
        cells: Dict[Tuple[int, int], Cell]
    ) -> List[Tuple[int, int]]:
        """
        Berechnet die Reihenfolge in der Zellen berechnet werden müssen

        Verwendet topologische Sortierung um sicherzustellen dass
        Abhängigkeiten vor abhängigen Zellen berechnet werden.

        Args:
            cells: Dictionary mit allen Zellen

        Returns:
            Liste von Zellen in Berechnungsreihenfolge

        Raises:
            CircularReferenceError: Bei Zirkelbezügen
        """
        # Baue Abhängigkeitsgraph
        self.build_dependency_graph(cells)

        if not self.dependency_graph:
            # Keine Formeln vorhanden
            return []

        # Topologische Sortierung (Kahn's Algorithm)
        # in_degree zählt wie viele Abhängigkeiten eine Zelle hat
        in_degree = {}
        for cell in self.dependency_graph.keys():
            in_degree[cell] = len(self.dependency_graph[cell])

        # Finde alle Zellen die als Abhängigkeiten referenziert werden
        # aber selbst keine Formeln haben (z.B. A1 in "=A1*2")
        all_referenced_cells = set()
        for deps in self.dependency_graph.values():
            all_referenced_cells.update(deps)

        # Füge referenzierte Zellen ohne Formeln zum in_degree hinzu
        for cell in all_referenced_cells:
            if cell not in in_degree:
                in_degree[cell] = 0

        # Queue mit Zellen die von keiner anderen Zelle abhängen
        queue = [cell for cell, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            cell = queue.pop(0)
            result.append(cell)

            # Finde alle Zellen die von dieser Zelle abhängen
            for dependent in self.get_dependent_cells(cell):
                if dependent in in_degree:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        # Prüfe auf Zirkelbezüge
        if len(result) < len(self.dependency_graph):
            raise CircularReferenceError(
                "Zirkelbezug in Formeln erkannt",
                display="#CIRCULAR!"
            )

        return result

    def recalculate_affected_cells(
        self,
        changed_cell: Tuple[int, int],
        cells: Dict[Tuple[int, int], Cell],
        context: Dict[Tuple[int, int], Any]
    ) -> Dict[Tuple[int, int], Any]:
        """
        Berechnet alle von einer Änderung betroffenen Zellen neu

        Args:
            changed_cell: Die geänderte Zelle (row, col)
            cells: Dictionary mit allen Zellen
            context: Aktueller Kontext mit Zellwerten

        Returns:
            Aktualisierter Kontext mit neuen Werten

        Raises:
            FormulaError: Bei Fehlern in Formeln
        """
        # Baue Abhängigkeitsgraph (falls noch nicht vorhanden)
        self.build_dependency_graph(cells)

        # Finde alle abhängigen Zellen
        affected = self._get_all_affected_cells(changed_cell, set())

        # Sortiere nach Berechnungsreihenfolge
        try:
            calc_order = self.get_calculation_order(cells)
            # Filtere nur betroffene Zellen
            affected_ordered = [
                cell for cell in calc_order if cell in affected
            ]
        except CircularReferenceError:
            # Bei Zirkelbezug: Berechne in beliebiger Reihenfolge
            affected_ordered = list(affected)

        # Berechne alle betroffenen Zellen neu
        for cell_pos in affected_ordered:
            if cell_pos in cells:
                cell = cells[cell_pos]
                if cell.is_formula():
                    try:
                        result = self.execute_formula(cell.formula, context)
                        context[cell_pos] = result
                        cell.value = result
                        cell.error = None
                    except FormulaError as e:
                        cell.error = e.display
                        cell.value = None
                        context[cell_pos] = None

        return context

    def _get_all_affected_cells(
        self,
        cell: Tuple[int, int],
        visited: Set[Tuple[int, int]]
    ) -> Set[Tuple[int, int]]:
        """
        Rekursiv alle betroffenen Zellen finden

        Args:
            cell: Ausgangszelle
            visited: Bereits besuchte Zellen (verhindert Endlosschleifen)

        Returns:
            Set aller betroffenen Zellen
        """
        if cell in visited:
            return set()

        visited.add(cell)
        affected = set()

        # Direkt abhängige Zellen
        dependents = self.get_dependent_cells(cell)
        affected.update(dependents)

        # Rekursiv für alle abhängigen Zellen
        for dependent in dependents:
            affected.update(
                self._get_all_affected_cells(dependent, visited)
            )

        return affected

    # Cache-Management-Methoden

    def _build_cache_key(
        self,
        formula: str,
        context: Dict[Tuple[int, int], Any]
    ) -> str:
        """
        Erstellt einen Cache-Key aus Formel und relevanten Zellwerten

        Der Cache-Key besteht aus der Formel und den Werten aller
        referenzierten Zellen. So wird sichergestellt dass der Cache
        nur verwendet wird wenn sich keine Abhängigkeiten geändert haben.

        Args:
            formula: Die Formel
            context: Dictionary mit Zellwerten

        Returns:
            Cache-Key als String
        """
        # Extrahiere Zellreferenzen aus der Formel
        cell_refs = extract_cell_references(formula)

        # Sammle Werte aller referenzierten Zellen
        ref_values = []
        for ref in cell_refs:
            if ':' in ref:
                # Bereich
                try:
                    cells = parse_range(ref)
                    for cell in cells:
                        value = context.get(cell, None)
                        ref_values.append(f"{cell}:{value}")
                except ValueError:
                    pass
            else:
                # Einzelne Zelle
                try:
                    row, col = a1_to_cell(ref)
                    value = context.get((row, col), None)
                    ref_values.append(f"{ref}:{value}")
                except ValueError:
                    pass

        # Erstelle Cache-Key
        # Format: "formula|ref1:val1|ref2:val2|..."
        cache_key = formula + "|" + "|".join(sorted(ref_values))
        return cache_key

    def invalidate_cache(
        self,
        changed_cells: Optional[List[Tuple[int, int]]] = None
    ):
        """
        Invalidiert den Cache für betroffene Zellen

        Wenn changed_cells angegeben ist, werden nur Cache-Einträge
        invalidiert die von diesen Zellen abhängen. Sonst wird der
        gesamte Cache geleert.

        Args:
            changed_cells: Liste von geänderten Zellen (optional)
        """
        if changed_cells is None:
            # Leere gesamten Cache
            self.formula_cache.clear()
            return

        # Finde alle betroffenen Zellen
        affected = set()
        for cell in changed_cells:
            affected.update(
                self._get_all_affected_cells(cell, set())
            )
            affected.add(cell)

        # Entferne Cache-Einträge die betroffene Zellen referenzieren
        keys_to_remove = []
        for cache_key in self.formula_cache.keys():
            # Extrahiere Formel aus Cache-Key (vor dem ersten |)
            formula = cache_key.split('|')[0]

            # Prüfe ob Formel betroffene Zellen referenziert
            cell_refs = extract_cell_references(formula)
            for ref in cell_refs:
                if ':' in ref:
                    # Bereich
                    try:
                        cells = parse_range(ref)
                        if any(cell in affected for cell in cells):
                            keys_to_remove.append(cache_key)
                            break
                    except ValueError:
                        pass
                else:
                    # Einzelne Zelle
                    try:
                        row, col = a1_to_cell(ref)
                        if (row, col) in affected:
                            keys_to_remove.append(cache_key)
                            break
                    except ValueError:
                        pass

        # Entferne gefundene Keys
        for key in keys_to_remove:
            del self.formula_cache[key]

    def clear_cache(self):
        """Leert den gesamten Cache"""
        self.formula_cache.clear()
        self.dependency_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Gibt Cache-Statistiken zurück

        Returns:
            Dictionary mit Cache-Statistiken
        """
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (
            self._cache_hits / total_requests * 100
            if total_requests > 0
            else 0
        )

        return {
            'enabled': self.cache_enabled,
            'size': len(self.formula_cache),
            'hits': self._cache_hits,
            'misses': self._cache_misses,
            'hit_rate': hit_rate,
            'dependency_cache_size': len(self.dependency_cache)
        }

    def enable_cache(self):
        """Aktiviert das Caching"""
        self.cache_enabled = True

    def disable_cache(self):
        """Deaktiviert das Caching"""
        self.cache_enabled = False
        self.clear_cache()

    def build_dependency_cache(
        self,
        cells: Dict[Tuple[int, int], Cell]
    ):
        """
        Erstellt einen Dependency-Cache für schnelle Abhängigkeitsabfragen

        Der Dependency-Cache speichert für jede Zelle die Liste aller
        Zellen die von ihr abhängen (umgekehrter Dependency-Graph).

        Args:
            cells: Dictionary mit allen Zellen
        """
        self.dependency_cache.clear()

        # Baue Dependency-Graph falls noch nicht vorhanden
        if not self.dependency_graph:
            self.build_dependency_graph(cells)

        # Erstelle umgekehrten Graph (welche Zellen hängen von mir ab?)
        for cell_pos, dependencies in self.dependency_graph.items():
            for dep_cell in dependencies:
                if dep_cell not in self.dependency_cache:
                    self.dependency_cache[dep_cell] = set()
                self.dependency_cache[dep_cell].add(cell_pos)

    def get_dependents_from_cache(
        self,
        cell: Tuple[int, int]
    ) -> Set[Tuple[int, int]]:
        """
        Gibt abhängige Zellen aus dem Cache zurück

        Dies ist schneller als get_dependent_cells() da keine
        Iteration über den gesamten Dependency-Graph nötig ist.

        Args:
            cell: Zelle für die Abhängigkeiten gesucht werden

        Returns:
            Set von abhängigen Zellen
        """
        return self.dependency_cache.get(cell, set())
