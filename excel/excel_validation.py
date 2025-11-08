"""
Excel Integration - Validation and Error Handling

Dieses Modul implementiert umfassende Validierung und Fehlerbehandlung
für die Excel-Integration gemäß Task 21.

Features:
- Alle Excel-Fehlertypen (#ERROR!, #REF!, #DIV/0!, etc.)
- Tooltip-Hilfe für Fehler
- Input-Validierung für alle Felder
- Zirkelbezug-Erkennung
"""

from typing import Dict, Any, Optional, List, Tuple, Set
import re
from datetime import datetime

from excel.excel_models import (
    FormulaError,
    SyntaxError,
    ReferenceError,
    DivisionByZeroError,
    CircularReferenceError,
    NameError,
    ValueError as ExcelValueError
)


class ValidationResult:
    """
    Ergebnis einer Validierung
    
    Attributes:
        valid: Ob die Eingabe gültig ist
        error: Fehlermeldung falls ungültig
        error_code: Fehlercode (z.B. "#ERROR!")
        warning: Optionale Warnung
        type: Erkannter Typ ('formula', 'number', 'text', 'date', 'boolean')
        parsed_value: Geparster Wert
        suggestions: Liste von Verbesserungsvorschlägen
    """
    
    def __init__(
        self,
        valid: bool,
        error: Optional[str] = None,
        error_code: Optional[str] = None,
        warning: Optional[str] = None,
        type: str = 'text',
        parsed_value: Any = None,
        suggestions: Optional[List[str]] = None
    ):
        self.valid = valid
        self.error = error
        self.error_code = error_code
        self.warning = warning
        self.type = type
        self.parsed_value = parsed_value
        self.suggestions = suggestions or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            'valid': self.valid,
            'error': self.error,
            'error_code': self.error_code,
            'warning': self.warning,
            'type': self.type,
            'parsed_value': self.parsed_value,
            'suggestions': self.suggestions
        }


class ExcelValidator:
    """
    Validator für Excel-Eingaben
    
    Validiert:
    - Formeln (Syntax, Funktionen, Referenzen)
    - Zahlen (Format, Bereich)
    - Text (Länge, Zeichen)
    - Datum (Format, Gültigkeit)
    - Boolesche Werte
    """
    
    # Unterstützte Excel-Funktionen (aus python_function_recipes)
    SUPPORTED_FUNCTIONS = {
        # Mathematische Funktionen
        'SUM', 'AVERAGE', 'MIN', 'MAX', 'COUNT', 'COUNTA',
        'ROUND', 'ROUNDUP', 'ROUNDDOWN', 'FLOOR', 'CEILING',
        'ABS', 'SQRT', 'POWER', 'MOD', 'PRODUCT',
        
        # Logische Funktionen
        'IF', 'AND', 'OR', 'NOT', 'IFERROR', 'IFNA',
        
        # Lookup-Funktionen
        'VLOOKUP', 'HLOOKUP', 'INDEX', 'MATCH', 'LOOKUP',
        
        # Textfunktionen
        'TEXT', 'CONCATENATE', 'LEFT', 'RIGHT', 'MID',
        'LEN', 'TRIM', 'UPPER', 'LOWER', 'SUBSTITUTE',
        
        # Datumsfunktionen
        'DATE', 'TODAY', 'NOW', 'YEAR', 'MONTH', 'DAY',
        'HOUR', 'MINUTE', 'SECOND', 'WEEKDAY',
        
        # Statistische Funktionen
        'MEDIAN', 'MODE', 'STDEV', 'VAR', 'PERCENTILE',
        
        # Bedingte Funktionen
        'SUMIF', 'SUMIFS', 'COUNTIF', 'COUNTIFS',
        'AVERAGEIF', 'AVERAGEIFS'
    }
    
    def __init__(self):
        """Initialisiert den Validator"""
        self.max_text_length = 32767  # Excel-Limit
        self.max_number = 9.99999999999999E+307  # Excel-Limit
        self.min_number = -9.99999999999999E+307
    
    def validate_cell_input(
        self,
        value: str,
        expected_type: Optional[str] = None
    ) -> ValidationResult:
        """
        Validiert Benutzereingabe für eine Zelle
        
        Args:
            value: Zu validierender Wert
            expected_type: Erwarteter Typ (optional)
            
        Returns:
            ValidationResult-Objekt
        """
        if not value or value.strip() == "":
            return ValidationResult(
                valid=True,
                type='empty',
                parsed_value=None
            )
        
        value = value.strip()
        
        # Prüfe ob Formel
        if value.startswith('='):
            return self.validate_formula(value)
        
        # Prüfe erwarteten Typ
        if expected_type:
            if expected_type == 'number':
                return self.validate_number(value)
            elif expected_type == 'date':
                return self.validate_date(value)
            elif expected_type == 'boolean':
                return self.validate_boolean(value)
            elif expected_type == 'text':
                return self.validate_text(value)
        
        # Auto-Erkennung
        # Versuche Zahl
        number_result = self.validate_number(value)
        if number_result.valid:
            return number_result
        
        # Versuche Boolean
        boolean_result = self.validate_boolean(value)
        if boolean_result.valid:
            return boolean_result
        
        # Versuche Datum
        date_result = self.validate_date(value)
        if date_result.valid:
            return date_result
        
        # Fallback: Text
        return self.validate_text(value)
    
    def validate_formula(self, formula: str) -> ValidationResult:
        """
        Validiert eine Excel-Formel
        
        Args:
            formula: Formel (mit '=')
            
        Returns:
            ValidationResult-Objekt
        """
        if not formula.startswith('='):
            return ValidationResult(
                valid=False,
                error="Formel muss mit '=' beginnen",
                error_code="#ERROR!",
                type='formula'
            )
        
        if len(formula) == 1:
            return ValidationResult(
                valid=False,
                error="Formel ist leer",
                error_code="#ERROR!",
                type='formula',
                suggestions=["Geben Sie eine gültige Formel ein, z.B. =SUM(A1:A10)"]
            )
        
        formula_body = formula[1:].strip()
        
        # Prüfe auf unbalancierte Klammern
        open_parens = formula_body.count('(')
        close_parens = formula_body.count(')')
        if open_parens != close_parens:
            return ValidationResult(
                valid=False,
                error=f"Unbalancierte Klammern: {open_parens} öffnende, {close_parens} schließende",
                error_code="#ERROR!",
                type='formula',
                suggestions=[
                    "Prüfen Sie, ob alle Klammern geschlossen sind",
                    "Jede öffnende Klammer '(' benötigt eine schließende ')'"
                ]
            )
        
        # Prüfe auf unbalancierte Anführungszeichen
        double_quotes = formula_body.count('"')
        if double_quotes % 2 != 0:
            return ValidationResult(
                valid=False,
                error="Unbalancierte Anführungszeichen",
                error_code="#ERROR!",
                type='formula',
                suggestions=[
                    "Prüfen Sie, ob alle Anführungszeichen geschlossen sind",
                    "Text-Strings müssen in doppelten Anführungszeichen stehen: \"Text\""
                ]
            )
        
        # Extrahiere Funktionsnamen
        func_pattern = r'([A-Z_]+)\s*\('
        functions = re.findall(func_pattern, formula_body, re.IGNORECASE)
        
        # Prüfe ob Funktionen unterstützt werden
        unknown_functions = []
        for func in functions:
            func_upper = func.upper()
            if func_upper not in self.SUPPORTED_FUNCTIONS:
                unknown_functions.append(func)
        
        if unknown_functions:
            return ValidationResult(
                valid=False,
                error=f"Unbekannte Funktion(en): {', '.join(unknown_functions)}",
                error_code="#NAME?",
                type='formula',
                suggestions=[
                    f"Unterstützte Funktionen: {', '.join(sorted(list(self.SUPPORTED_FUNCTIONS)[:10]))}...",
                    "Prüfen Sie die Schreibweise der Funktion"
                ]
            )
        
        # Prüfe Zellreferenzen
        cell_ref_pattern = r'\b([A-Z]+\d+)\b'
        cell_refs = re.findall(cell_ref_pattern, formula_body, re.IGNORECASE)
        
        invalid_refs = []
        for ref in cell_refs:
            if not self._is_valid_cell_reference(ref):
                invalid_refs.append(ref)
        
        if invalid_refs:
            return ValidationResult(
                valid=False,
                error=f"Ungültige Zellreferenz(en): {', '.join(invalid_refs)}",
                error_code="#REF!",
                type='formula',
                suggestions=[
                    "Zellreferenzen müssen im Format A1, B2, AA10 etc. sein",
                    "Spalte: Buchstaben (A-ZZ), Zeile: Zahlen (1-1048576)"
                ]
            )
        
        # Prüfe Bereichsreferenzen
        range_pattern = r'\b([A-Z]+\d+:[A-Z]+\d+)\b'
        ranges = re.findall(range_pattern, formula_body, re.IGNORECASE)
        
        invalid_ranges = []
        for range_ref in ranges:
            if not self._is_valid_range_reference(range_ref):
                invalid_ranges.append(range_ref)
        
        if invalid_ranges:
            return ValidationResult(
                valid=False,
                error=f"Ungültiger Bereich: {', '.join(invalid_ranges)}",
                error_code="#REF!",
                type='formula',
                suggestions=[
                    "Bereiche müssen im Format A1:B10 sein",
                    "Start-Zelle muss vor End-Zelle liegen"
                ]
            )
        
        # Prüfe auf potenzielle Division durch Null
        if '/0' in formula_body or '/ 0' in formula_body:
            return ValidationResult(
                valid=True,  # Syntaktisch gültig, aber Warnung
                warning="Mögliche Division durch Null",
                type='formula',
                suggestions=[
                    "Verwenden Sie IFERROR() um Division durch Null abzufangen",
                    "Beispiel: =IFERROR(A1/B1, 0)"
                ]
            )
        
        # Formel ist gültig
        return ValidationResult(
            valid=True,
            type='formula',
            parsed_value=formula
        )
    
    def validate_number(self, value: str) -> ValidationResult:
        """
        Validiert eine Zahl
        
        Args:
            value: Zu validierender Wert
            
        Returns:
            ValidationResult-Objekt
        """
        # Erlaube Komma als Dezimaltrennzeichen
        value_normalized = value.replace(',', '.')
        
        # Entferne Tausendertrennzeichen
        value_normalized = value_normalized.replace(' ', '')
        
        try:
            parsed = float(value_normalized)
            
            # Prüfe Bereich
            if parsed > self.max_number:
                return ValidationResult(
                    valid=False,
                    error=f"Zahl zu groß (Maximum: {self.max_number})",
                    error_code="#NUM!",
                    type='number'
                )
            
            if parsed < self.min_number:
                return ValidationResult(
                    valid=False,
                    error=f"Zahl zu klein (Minimum: {self.min_number})",
                    error_code="#NUM!",
                    type='number'
                )
            
            return ValidationResult(
                valid=True,
                type='number',
                parsed_value=parsed
            )
            
        except ValueError:
            return ValidationResult(
                valid=False,
                error=f"'{value}' ist keine gültige Zahl",
                error_code="#VALUE!",
                type='number',
                suggestions=[
                    "Verwenden Sie Punkt oder Komma als Dezimaltrennzeichen",
                    "Beispiele: 123, 123.45, 123,45"
                ]
            )
    
    def validate_text(self, value: str) -> ValidationResult:
        """
        Validiert Text
        
        Args:
            value: Zu validierender Text
            
        Returns:
            ValidationResult-Objekt
        """
        if len(value) > self.max_text_length:
            return ValidationResult(
                valid=False,
                error=f"Text zu lang (Maximum: {self.max_text_length} Zeichen)",
                error_code="#VALUE!",
                type='text'
            )
        
        return ValidationResult(
            valid=True,
            type='text',
            parsed_value=value
        )
    
    def validate_date(self, value: str) -> ValidationResult:
        """
        Validiert ein Datum
        
        Args:
            value: Zu validierender Wert
            
        Returns:
            ValidationResult-Objekt
        """
        # Unterstützte Datumsformate
        date_formats = [
            '%d.%m.%Y',  # 31.12.2023
            '%d/%m/%Y',  # 31/12/2023
            '%Y-%m-%d',  # 2023-12-31
            '%d.%m.%y',  # 31.12.23
            '%d/%m/%y',  # 31/12/23
        ]
        
        for fmt in date_formats:
            try:
                parsed = datetime.strptime(value, fmt)
                return ValidationResult(
                    valid=True,
                    type='date',
                    parsed_value=parsed
                )
            except ValueError:
                continue
        
        return ValidationResult(
            valid=False,
            error=f"'{value}' ist kein gültiges Datum",
            error_code="#VALUE!",
            type='date',
            suggestions=[
                "Unterstützte Formate: DD.MM.YYYY, DD/MM/YYYY, YYYY-MM-DD",
                "Beispiele: 31.12.2023, 31/12/2023, 2023-12-31"
            ]
        )
    
    def validate_boolean(self, value: str) -> ValidationResult:
        """
        Validiert einen Boolean-Wert
        
        Args:
            value: Zu validierender Wert
            
        Returns:
            ValidationResult-Objekt
        """
        value_upper = value.upper()
        
        if value_upper in ('TRUE', 'WAHR', '1', 'YES', 'JA'):
            return ValidationResult(
                valid=True,
                type='boolean',
                parsed_value=True
            )
        
        if value_upper in ('FALSE', 'FALSCH', '0', 'NO', 'NEIN'):
            return ValidationResult(
                valid=True,
                type='boolean',
                parsed_value=False
            )
        
        return ValidationResult(
            valid=False,
            error=f"'{value}' ist kein gültiger Boolean-Wert",
            error_code="#VALUE!",
            type='boolean',
            suggestions=[
                "Gültige Werte: TRUE, FALSE, WAHR, FALSCH, 1, 0"
            ]
        )
    
    def _is_valid_cell_reference(self, ref: str) -> bool:
        """
        Prüft ob eine Zellreferenz gültig ist
        
        Args:
            ref: Zellreferenz (z.B. "A1")
            
        Returns:
            True wenn gültig
        """
        pattern = r'^[A-Z]{1,3}\d{1,7}$'
        if not re.match(pattern, ref, re.IGNORECASE):
            return False
        
        # Extrahiere Spalte und Zeile
        match = re.match(r'([A-Z]+)(\d+)', ref, re.IGNORECASE)
        if not match:
            return False
        
        col_str, row_str = match.groups()
        
        # Prüfe Spalte (max ZZZ = 18278)
        col_num = 0
        for char in col_str.upper():
            col_num = col_num * 26 + (ord(char) - ord('A') + 1)
        
        if col_num > 16384:  # Excel-Limit
            return False
        
        # Prüfe Zeile (max 1048576)
        row_num = int(row_str)
        if row_num < 1 or row_num > 1048576:
            return False
        
        return True
    
    def _is_valid_range_reference(self, range_ref: str) -> bool:
        """
        Prüft ob eine Bereichsreferenz gültig ist
        
        Args:
            range_ref: Bereichsreferenz (z.B. "A1:B10")
            
        Returns:
            True wenn gültig
        """
        if ':' not in range_ref:
            return False
        
        parts = range_ref.split(':')
        if len(parts) != 2:
            return False
        
        start_ref, end_ref = parts
        
        # Prüfe dass beide Teile nicht leer sind
        if not start_ref.strip() or not end_ref.strip():
            return False
        
        # Prüfe beide Referenzen
        if not self._is_valid_cell_reference(start_ref):
            return False
        if not self._is_valid_cell_reference(end_ref):
            return False
        
        return True


class CircularReferenceDetector:
    """
    Erkennt Zirkelbezüge in Formeln
    
    Ein Zirkelbezug entsteht wenn eine Formel direkt oder indirekt
    auf sich selbst verweist.
    """
    
    def __init__(self):
        """Initialisiert den Detector"""
        self.dependency_graph: Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}
    
    def build_graph(
        self,
        cells: Dict[Tuple[int, int], Any]
    ):
        """
        Baut den Abhängigkeitsgraphen auf
        
        Args:
            cells: Dictionary mit Zellen {(row, col): Cell}
        """
        from excel.excel_utils import extract_cell_references, parse_range, a1_to_cell
        
        self.dependency_graph.clear()
        
        for (row, col), cell in cells.items():
            if hasattr(cell, 'is_formula') and cell.is_formula():
                # Extrahiere Referenzen
                refs = extract_cell_references(cell.formula)
                
                dependencies = set()
                for ref in refs:
                    try:
                        if ':' in ref:
                            # Bereich
                            range_cells = parse_range(ref)
                            dependencies.update(range_cells)
                        else:
                            # Einzelne Zelle
                            dep_row, dep_col = a1_to_cell(ref)
                            dependencies.add((dep_row, dep_col))
                    except (ValueError, AttributeError):
                        # Ungültige Referenz ignorieren
                        pass
                
                self.dependency_graph[(row, col)] = dependencies
    
    def detect_circular_reference(
        self,
        cell: Tuple[int, int],
        formula: str
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Erkennt ob eine Formel einen Zirkelbezug erstellen würde
        
        Args:
            cell: Zelle (row, col)
            formula: Zu prüfende Formel
            
        Returns:
            Liste von Zellen im Zirkel oder None wenn kein Zirkel
        """
        from excel.excel_utils import extract_cell_references, parse_range, a1_to_cell
        
        # Extrahiere Referenzen aus der Formel
        refs = extract_cell_references(formula)
        
        temp_dependencies = set()
        for ref in refs:
            try:
                if ':' in ref:
                    # Bereich
                    range_cells = parse_range(ref)
                    temp_dependencies.update(range_cells)
                else:
                    # Einzelne Zelle
                    dep_row, dep_col = a1_to_cell(ref)
                    temp_dependencies.add((dep_row, dep_col))
            except (ValueError, AttributeError):
                pass
        
        # Prüfe ob Zelle sich selbst referenziert
        if cell in temp_dependencies:
            return [cell]
        
        # Prüfe ob eine Abhängigkeit zurück zur Zelle führt
        for dep in temp_dependencies:
            path = self._find_path_to_cell(dep, cell, set())
            if path:
                return [cell] + path
        
        return None
    
    def _find_path_to_cell(
        self,
        from_cell: Tuple[int, int],
        to_cell: Tuple[int, int],
        visited: Set[Tuple[int, int]]
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Findet einen Pfad von einer Zelle zu einer anderen
        
        Args:
            from_cell: Start-Zelle
            to_cell: Ziel-Zelle
            visited: Bereits besuchte Zellen
            
        Returns:
            Liste von Zellen im Pfad oder None
        """
        if from_cell == to_cell:
            return [to_cell]
        
        if from_cell in visited:
            return None
        
        visited.add(from_cell)
        
        # Prüfe alle Abhängigkeiten
        if from_cell in self.dependency_graph:
            for dep in self.dependency_graph[from_cell]:
                path = self._find_path_to_cell(dep, to_cell, visited.copy())
                if path:
                    return [from_cell] + path
        
        return None
    
    def get_all_circular_references(self) -> List[List[Tuple[int, int]]]:
        """
        Findet alle Zirkelbezüge im Graph
        
        Returns:
            Liste von Zirkel-Pfaden
        """
        circles = []
        visited = set()
        
        for cell in self.dependency_graph.keys():
            if cell not in visited:
                circle = self._detect_circle_from_cell(cell, set(), [])
                if circle:
                    circles.append(circle)
                    visited.update(circle)
        
        return circles
    
    def _detect_circle_from_cell(
        self,
        cell: Tuple[int, int],
        visited: Set[Tuple[int, int]],
        path: List[Tuple[int, int]]
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Erkennt Zirkel ausgehend von einer Zelle
        
        Args:
            cell: Aktuelle Zelle
            visited: Bereits besuchte Zellen
            path: Aktueller Pfad
            
        Returns:
            Zirkel-Pfad oder None
        """
        if cell in path:
            # Zirkel gefunden
            circle_start = path.index(cell)
            return path[circle_start:]
        
        if cell in visited:
            return None
        
        visited.add(cell)
        path.append(cell)
        
        # Prüfe alle Abhängigkeiten
        if cell in self.dependency_graph:
            for dep in self.dependency_graph[cell]:
                circle = self._detect_circle_from_cell(
                    dep,
                    visited.copy(),
                    path.copy()
                )
                if circle:
                    return circle
        
        return None


def get_error_tooltip(error_code: str) -> Dict[str, str]:
    """
    Gibt detaillierte Tooltip-Informationen für einen Fehlercode zurück
    
    Args:
        error_code: Fehlercode (z.B. "#DIV/0!")
        
    Returns:
        Dictionary mit 'title', 'description', 'solutions'
    """
    error_tooltips = {
        '#ERROR!': {
            'title': 'Syntaxfehler',
            'description': 'Die Formel enthält einen Syntaxfehler und kann nicht ausgeführt werden.',
            'solutions': [
                'Prüfen Sie die Formel-Syntax',
                'Stellen Sie sicher, dass alle Klammern geschlossen sind',
                'Prüfen Sie die Schreibweise von Funktionsnamen',
                'Verwenden Sie korrekte Trennzeichen (Komma für Argumente)'
            ]
        },
        '#REF!': {
            'title': 'Ungültige Referenz',
            'description': 'Die Formel verweist auf eine Zelle oder einen Bereich, der nicht existiert.',
            'solutions': [
                'Prüfen Sie ob die referenzierte Zelle existiert',
                'Stellen Sie sicher, dass Zellreferenzen im Format A1, B2 etc. sind',
                'Prüfen Sie ob Zeilen oder Spalten gelöscht wurden',
                'Verwenden Sie gültige Bereichsreferenzen (z.B. A1:B10)'
            ]
        },
        '#DIV/0!': {
            'title': 'Division durch Null',
            'description': 'Die Formel versucht durch Null zu teilen.',
            'solutions': [
                'Prüfen Sie die Werte in der Formel',
                'Verwenden Sie IFERROR() um den Fehler abzufangen',
                'Beispiel: =IFERROR(A1/B1, 0)',
                'Stellen Sie sicher, dass der Divisor nicht Null ist'
            ]
        },
        '#CIRCULAR!': {
            'title': 'Zirkelbezug',
            'description': 'Die Formel verweist direkt oder indirekt auf sich selbst.',
            'solutions': [
                'Prüfen Sie die Formel auf Selbstreferenzen',
                'Überprüfen Sie die Abhängigkeitskette',
                'Entfernen Sie die zirkuläre Referenz',
                'Verwenden Sie eine andere Zelle für Zwischenergebnisse'
            ]
        },
        '#NAME?': {
            'title': 'Unbekannte Funktion',
            'description': 'Die Formel verwendet eine Funktion, die nicht erkannt wird.',
            'solutions': [
                'Prüfen Sie die Schreibweise der Funktion',
                'Verwenden Sie nur unterstützte Excel-Funktionen',
                'Beispiele: SUM, AVERAGE, IF, VLOOKUP',
                'Achten Sie auf Groß-/Kleinschreibung'
            ]
        },
        '#VALUE!': {
            'title': 'Falscher Wert-Typ',
            'description': 'Die Funktion erwartet einen anderen Datentyp als übergeben wurde.',
            'solutions': [
                'Prüfen Sie die Datentypen der Argumente',
                'Stellen Sie sicher, dass Zahlen als Zahlen übergeben werden',
                'Verwenden Sie TEXT() um Zahlen in Text zu konvertieren',
                'Verwenden Sie VALUE() um Text in Zahlen zu konvertieren'
            ]
        },
        '#NUM!': {
            'title': 'Numerischer Fehler',
            'description': 'Die Zahl ist zu groß, zu klein oder ungültig.',
            'solutions': [
                'Prüfen Sie den Wertebereich',
                'Excel unterstützt Zahlen von -9.99E+307 bis 9.99E+307',
                'Vermeiden Sie sehr große oder sehr kleine Zahlen',
                'Prüfen Sie auf ungültige mathematische Operationen'
            ]
        },
        '#N/A': {
            'title': 'Wert nicht verfügbar',
            'description': 'Ein Wert ist nicht verfügbar oder wurde nicht gefunden.',
            'solutions': [
                'Prüfen Sie VLOOKUP/HLOOKUP Suchkriterien',
                'Stellen Sie sicher, dass der Suchwert existiert',
                'Verwenden Sie IFNA() um den Fehler abzufangen',
                'Beispiel: =IFNA(VLOOKUP(...), "Nicht gefunden")'
            ]
        },
        '#NULL!': {
            'title': 'Null-Schnittmenge',
            'description': 'Die angegebenen Bereiche haben keine gemeinsamen Zellen.',
            'solutions': [
                'Prüfen Sie die Bereichsreferenzen',
                'Verwenden Sie Komma statt Leerzeichen für mehrere Bereiche',
                'Beispiel: SUM(A1:A10, B1:B10) statt SUM(A1:A10 B1:B10)'
            ]
        }
    }
    
    return error_tooltips.get(
        error_code,
        {
            'title': 'Unbekannter Fehler',
            'description': f'Ein unbekannter Fehler ist aufgetreten: {error_code}',
            'solutions': [
                'Prüfen Sie die Formel auf Fehler',
                'Kontaktieren Sie den Support'
            ]
        }
    )
