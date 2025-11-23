"""
Price Matrix Formula Engine

Implements Excel-like formula parsing and evaluation with focus on INDEX/MATCH
for price matrix lookups. Supports German number formatting and provides
comprehensive error handling.

**Feature: streamlit-to-electron-migration, Task 140**
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import re
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class FormulaError(Exception):
    """Base exception for formula errors"""
    pass


class ParseError(FormulaError):
    """Error during formula parsing"""
    pass


class EvaluationError(FormulaError):
    """Error during formula evaluation"""
    pass


class CircularReferenceError(FormulaError):
    """Circular reference detected in formulas"""
    pass


class MatchType(Enum):
    """Match types for MATCH function"""
    EXACT = 0  # Exact match
    LESS_THAN_OR_EQUAL = 1  # Less than or equal (requires sorted ascending)
    GREATER_THAN_OR_EQUAL = -1  # Greater than or equal (requires sorted descending)


class FormulaEngine:
    """
    Excel-like formula engine with INDEX/MATCH support for price matrix lookups.
    
    Supports:
    - INDEX(array, row_num, col_num): Returns value at specified position
    - MATCH(lookup_value, lookup_array, match_type): Finds position of value
    - Nested INDEX/MATCH: =INDEX(A2:A200, MATCH(value1, A2:XX200, 0), MATCH(value2, B2:XX2, 0))
    - German number formatting (16.999,00 €)
    - Circular reference detection
    - Formula dependency resolution
    """
    
    def __init__(self):
        self.formulas: Dict[str, str] = {}
        self.values: Dict[str, Any] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.evaluation_stack: List[str] = []
        
    def set_value(self, cell_ref: str, value: Any) -> None:
        """Set a cell value"""
        self.values[cell_ref] = value
        
    def set_formula(self, cell_ref: str, formula: str) -> None:
        """Set a cell formula"""
        self.formulas[cell_ref] = formula
        self._analyze_dependencies(cell_ref, formula)
        
    def get_value(self, cell_ref: str) -> Any:
        """Get cell value, evaluating formula if necessary"""
        if cell_ref in self.evaluation_stack:
            raise CircularReferenceError(
                f"Zirkuläre Referenz erkannt: {' -> '.join(self.evaluation_stack + [cell_ref])}"
            )
            
        if cell_ref in self.formulas:
            self.evaluation_stack.append(cell_ref)
            try:
                result = self.evaluate(self.formulas[cell_ref])
                self.values[cell_ref] = result
                return result
            finally:
                self.evaluation_stack.pop()
        
        return self.values.get(cell_ref)
    
    def _analyze_dependencies(self, cell_ref: str, formula: str) -> None:
        """Analyze formula dependencies"""
        # Extract cell references from formula
        cell_pattern = r'[A-Z]+\d+'
        refs = re.findall(cell_pattern, formula)
        self.dependencies[cell_ref] = list(set(refs))
        
    def evaluate(self, formula: str) -> Any:
        """
        Evaluate a formula string.
        
        Args:
            formula: Formula string (e.g., "=INDEX(A2:A200, MATCH(C37, A2:XX200, 0))")
            
        Returns:
            Evaluated result
            
        Raises:
            ParseError: If formula syntax is invalid
            EvaluationError: If formula evaluation fails
        """
        formula = formula.strip()
        if formula.startswith('='):
            formula = formula[1:]
            
        try:
            return self._evaluate_expression(formula)
        except (ParseError, EvaluationError, CircularReferenceError):
            # Re-raise formula-specific errors as-is
            raise
        except Exception as e:
            logger.error(f"Fehler bei Formelauswertung: {formula}, Fehler: {str(e)}")
            raise EvaluationError(f"Formelauswertung fehlgeschlagen: {str(e)}")
    
    def _evaluate_expression(self, expr: str) -> Any:
        """Evaluate an expression"""
        expr = expr.strip()
        
        # Check for function calls
        if '(' in expr:
            func_match = re.match(r'([A-Z]+)\((.*)\)$', expr, re.DOTALL)
            if func_match:
                func_name = func_match.group(1)
                args_str = func_match.group(2)
                return self._evaluate_function(func_name, args_str)
        
        # Check for cell reference
        if re.match(r'^[A-Z]+\d+$', expr):
            return self.get_value(expr)
        
        # Check for number
        try:
            return float(expr)
        except ValueError:
            pass
        
        # Check for string
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        
        raise ParseError(f"Ungültiger Ausdruck: {expr}")
    
    def _evaluate_function(self, func_name: str, args_str: str) -> Any:
        """Evaluate a function call"""
        if func_name == 'INDEX':
            return self._evaluate_index(args_str)
        elif func_name == 'MATCH':
            return self._evaluate_match(args_str)
        else:
            raise ParseError(f"Unbekannte Funktion: {func_name}")
    
    def _parse_arguments(self, args_str: str) -> List[str]:
        """
        Parse function arguments, handling nested functions.
        
        Args:
            args_str: Argument string (e.g., "A2:A200, MATCH(C37, A2:XX200, 0), 2")
            
        Returns:
            List of argument strings
        """
        args = []
        current_arg = ""
        paren_depth = 0
        
        for char in args_str:
            if char == ',' and paren_depth == 0:
                args.append(current_arg.strip())
                current_arg = ""
            else:
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                current_arg += char
        
        if current_arg.strip():
            args.append(current_arg.strip())
        
        return args
    
    def _evaluate_index(self, args_str: str) -> Any:
        """
        Evaluate INDEX function.
        
        Syntax: INDEX(array, row_num, [col_num])
        
        Args:
            args_str: Arguments string
            
        Returns:
            Value at specified position
            
        Raises:
            EvaluationError: If indices are out of bounds
        """
        args = self._parse_arguments(args_str)
        
        if len(args) < 2:
            raise ParseError("INDEX benötigt mindestens 2 Argumente: array, row_num")
        
        # Parse array range
        array_range = args[0].strip()
        array_data = self._get_range_data(array_range)
        
        # Evaluate row index
        row_idx = self._evaluate_expression(args[1])
        if not isinstance(row_idx, (int, float)):
            raise EvaluationError(f"Zeilenindex muss eine Zahl sein, erhalten: {row_idx}")
        row_idx = int(row_idx)
        
        # Evaluate column index if provided
        col_idx = None
        if len(args) >= 3:
            col_idx = self._evaluate_expression(args[2])
            if not isinstance(col_idx, (int, float)):
                raise EvaluationError(f"Spaltenindex muss eine Zahl sein, erhalten: {col_idx}")
            col_idx = int(col_idx)
        
        # Validate indices (1-based indexing like Excel)
        if row_idx < 1 or row_idx > len(array_data):
            raise EvaluationError(
                f"Zeilenindex {row_idx} außerhalb des Bereichs (1-{len(array_data)})"
            )
        
        row_data = array_data[row_idx - 1]
        
        if col_idx is None:
            # Return entire row if no column specified
            return row_data[0] if len(row_data) == 1 else row_data
        
        if col_idx < 1 or col_idx > len(row_data):
            raise EvaluationError(
                f"Spaltenindex {col_idx} außerhalb des Bereichs (1-{len(row_data)})"
            )
        
        return row_data[col_idx - 1]
    
    def _evaluate_match(self, args_str: str) -> int:
        """
        Evaluate MATCH function.
        
        Syntax: MATCH(lookup_value, lookup_array, [match_type])
        
        Args:
            args_str: Arguments string
            
        Returns:
            1-based position of match (Excel-style)
            
        Raises:
            EvaluationError: If value not found
        """
        args = self._parse_arguments(args_str)
        
        if len(args) < 2:
            raise ParseError("MATCH benötigt mindestens 2 Argumente: lookup_value, lookup_array")
        
        # Evaluate lookup value
        lookup_value = self._evaluate_expression(args[0])
        
        # Parse lookup array
        array_range = args[1].strip()
        array_data = self._get_range_data(array_range)
        
        # Flatten array to 1D
        flat_array = []
        for row in array_data:
            if isinstance(row, list):
                flat_array.extend(row)
            else:
                flat_array.append(row)
        
        # Get match type (default: 0 = exact match)
        match_type = MatchType.EXACT
        if len(args) >= 3:
            match_type_val = self._evaluate_expression(args[2])
            if isinstance(match_type_val, (int, float)):
                match_type_val = int(match_type_val)
                if match_type_val == 0:
                    match_type = MatchType.EXACT
                elif match_type_val == 1:
                    match_type = MatchType.LESS_THAN_OR_EQUAL
                elif match_type_val == -1:
                    match_type = MatchType.GREATER_THAN_OR_EQUAL
        
        # Perform match
        if match_type == MatchType.EXACT:
            try:
                # Try exact match
                position = flat_array.index(lookup_value) + 1  # 1-based
                logger.debug(f"MATCH gefunden: {lookup_value} an Position {position}")
                return position
            except ValueError:
                # Try string comparison for case-insensitive match
                lookup_str = str(lookup_value).lower()
                for i, val in enumerate(flat_array):
                    if str(val).lower() == lookup_str:
                        position = i + 1
                        logger.debug(f"MATCH gefunden (case-insensitive): {lookup_value} an Position {position}")
                        return position
                
                raise EvaluationError(
                    f"Wert '{lookup_value}' nicht gefunden in Array. "
                    f"Verfügbare Werte: {flat_array[:10]}..."
                )
        
        # For sorted arrays (match_type 1 or -1)
        # Not commonly used in price matrix, but included for completeness
        raise EvaluationError(f"Match-Typ {match_type.value} noch nicht implementiert")
    
    def _get_range_data(self, range_ref: str) -> List[List[Any]]:
        """
        Get data from a range reference.
        
        Args:
            range_ref: Range reference (e.g., "A2:A200", "B2:XX2")
            
        Returns:
            2D list of values
        """
        # Parse range (e.g., "A2:XX200")
        match = re.match(r'([A-Z]+)(\d+):([A-Z]+)(\d+)', range_ref)
        if not match:
            raise ParseError(f"Ungültiger Bereich: {range_ref}")
        
        start_col, start_row, end_col, end_row = match.groups()
        start_row = int(start_row)
        end_row = int(end_row)
        
        # Convert column letters to numbers
        start_col_num = self._col_letter_to_num(start_col)
        end_col_num = self._col_letter_to_num(end_col)
        
        # Extract data
        data = []
        for row in range(start_row, end_row + 1):
            row_data = []
            for col in range(start_col_num, end_col_num + 1):
                cell_ref = f"{self._col_num_to_letter(col)}{row}"
                value = self.values.get(cell_ref)
                row_data.append(value)
            data.append(row_data)
        
        return data
    
    @staticmethod
    def _col_letter_to_num(col_letter: str) -> int:
        """Convert column letter to number (A=1, B=2, ..., Z=26, AA=27, ...)"""
        num = 0
        for char in col_letter:
            num = num * 26 + (ord(char) - ord('A') + 1)
        return num
    
    @staticmethod
    def _col_num_to_letter(col_num: int) -> str:
        """Convert column number to letter (1=A, 2=B, ..., 26=Z, 27=AA, ...)"""
        letter = ""
        while col_num > 0:
            col_num -= 1
            letter = chr(col_num % 26 + ord('A')) + letter
            col_num //= 26
        return letter


class PriceMatrixFormulaEngine(FormulaEngine):
    """
    Specialized formula engine for price matrix lookups.
    
    Handles the specific INDEX/MATCH pattern used in price matrices:
    =INDEX(A2:A200, MATCH(module_count, A2:XX200, 0), MATCH(battery_model, B2:XX2, 0))
    
    Features:
    - Automatic "kein Speicher" (no storage) handling
    - German number formatting for prices
    - Optimized for large matrices (200x200)
    - Comprehensive error messages in German
    """
    
    def __init__(self):
        super().__init__()
        self.matrix_data: Optional[List[List[Any]]] = None
        self.module_counts: Optional[List[int]] = None
        self.battery_models: Optional[List[str]] = None
        
    def load_matrix(
        self,
        matrix_data: List[List[Any]],
        module_counts: List[int],
        battery_models: List[str]
    ) -> None:
        """
        Load price matrix data.
        
        Args:
            matrix_data: 2D array of prices (rows=module counts, cols=battery models)
            module_counts: List of module counts (row headers)
            battery_models: List of battery models (column headers)
        """
        self.matrix_data = matrix_data
        self.module_counts = module_counts
        self.battery_models = battery_models
        
        # Populate values for formula evaluation
        # Row 2: Battery models (starting at column B)
        for j, model in enumerate(battery_models, start=0):
            col_letter = self._col_num_to_letter(j + 2)  # B, C, D, ...
            self.set_value(f"{col_letter}2", model)
        
        # Column A and matrix data (starting at row 3)
        for i, (count, row) in enumerate(zip(module_counts, matrix_data), start=3):
            # Module count in column A
            self.set_value(f"A{i}", count)
            # Prices in columns B, C, D, ...
            for j, value in enumerate(row, start=0):
                col_letter = self._col_num_to_letter(j + 2)  # B, C, D, ...
                self.set_value(f"{col_letter}{i}", value)
    
    def lookup_price(
        self,
        module_count: int,
        battery_model: str
    ) -> float:
        """
        Lookup price using INDEX/MATCH formula.
        
        Args:
            module_count: Number of PV modules
            battery_model: Battery storage model (or "kein Speicher")
            
        Returns:
            Price in EUR
            
        Raises:
            EvaluationError: If lookup fails
        """
        if self.matrix_data is None:
            raise EvaluationError("Matrix-Daten nicht geladen")
        
        # Handle "kein Speicher" - use last column
        if battery_model.lower() in ["kein speicher", "ohne speicher", "none"]:
            battery_model = self.battery_models[-1] if self.battery_models else battery_model
            logger.info(f"'kein Speicher' erkannt, verwende letzte Spalte: {battery_model}")
        
        # Build and evaluate formula
        # =INDEX(A3:XX200, MATCH(module_count, A3:A200, 0), MATCH(battery_model, B2:XX2, 0))
        # Note: Data starts at row 3, headers at row 2
        max_row = len(self.module_counts) + 2  # +2 because we start at row 3
        max_col_letter = self._col_num_to_letter(len(self.battery_models) + 1)
        
        formula = (
            f'INDEX(A3:{max_col_letter}{max_row}, '
            f'MATCH({module_count}, A3:A{max_row}, 0), '
            f'MATCH("{battery_model}", B2:{max_col_letter}2, 0))'
        )
        
        logger.info(f"Preisabfrage-Formel: {formula}")
        
        try:
            price = self.evaluate(formula)
            if price is None:
                raise EvaluationError(
                    f"Kein Preis gefunden für {module_count} Module und {battery_model}"
                )
            return float(price)
        except Exception as e:
            logger.error(f"Preisabfrage fehlgeschlagen: {str(e)}")
            raise EvaluationError(
                f"Preisabfrage fehlgeschlagen für {module_count} Module und {battery_model}: {str(e)}"
            )
    
    def format_price_german(self, price: float) -> str:
        """
        Format price in German format.
        
        Args:
            price: Price value
            
        Returns:
            Formatted string (e.g., "16.999,00 €")
        """
        # Format with 2 decimal places
        formatted = f"{price:,.2f}"
        
        # Replace comma with temp, dot with comma, temp with dot
        formatted = formatted.replace(',', 'TEMP')
        formatted = formatted.replace('.', ',')
        formatted = formatted.replace('TEMP', '.')
        
        return f"{formatted} €"


# Debugging and performance tools
class FormulaDebugger:
    """Tools for debugging formula evaluation"""
    
    @staticmethod
    def trace_evaluation(engine: FormulaEngine, formula: str) -> Dict[str, Any]:
        """
        Trace formula evaluation step by step.
        
        Args:
            engine: Formula engine instance
            formula: Formula to trace
            
        Returns:
            Trace information
        """
        trace = {
            "formula": formula,
            "steps": [],
            "result": None,
            "error": None
        }
        
        try:
            # TODO: Implement detailed step-by-step tracing
            result = engine.evaluate(formula)
            trace["result"] = result
        except Exception as e:
            trace["error"] = str(e)
        
        return trace
    
    @staticmethod
    def validate_circular_references(engine: FormulaEngine) -> List[str]:
        """
        Detect circular references in formulas.
        
        Args:
            engine: Formula engine instance
            
        Returns:
            List of cells with circular references
        """
        circular_refs = []
        
        def has_cycle(cell: str, visited: set, rec_stack: set) -> bool:
            visited.add(cell)
            rec_stack.add(cell)
            
            for dep in engine.dependencies.get(cell, []):
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(cell)
            return False
        
        visited = set()
        for cell in engine.formulas:
            if cell not in visited:
                if has_cycle(cell, visited, set()):
                    circular_refs.append(cell)
        
        return circular_refs


class FormulaOptimizer:
    """Performance optimization for formula evaluation"""
    
    def __init__(self, engine: FormulaEngine):
        self.engine = engine
        self.cache: Dict[str, Any] = {}
        
    def optimize_matrix_lookup(self, matrix_size: Tuple[int, int]) -> None:
        """
        Optimize for large matrix lookups.
        
        Args:
            matrix_size: (rows, cols) tuple
        """
        rows, cols = matrix_size
        logger.info(f"Optimierung für Matrix-Größe: {rows}x{cols}")
        
        # For large matrices, consider:
        # 1. Indexing strategies
        # 2. Caching frequently accessed values
        # 3. Lazy evaluation
        
        if rows * cols > 10000:
            logger.warning(
                f"Große Matrix erkannt ({rows}x{cols}). "
                "Erwäge Verwendung von Indizes für bessere Performance."
            )
    
    def clear_cache(self) -> None:
        """Clear evaluation cache"""
        self.cache.clear()
