"""
Price Matrix Validation Service

Comprehensive validation system for price matrices including:
- Matrix structure validation
- Data type validation
- Range validation
- Formula validation
- Consistency checks
- Validation reporting

Requirements: 1.3, 4.4
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re


class ValidationResult:
    """Container for validation results"""
    
    def __init__(self):
        self.valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: Dict[str, Any] = {}
        self.timestamp = datetime.now().isoformat()
    
    def add_error(self, message: str):
        """Add an error message"""
        self.errors.append(message)
        self.valid = False
    
    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(message)
    
    def add_info(self, key: str, value: Any):
        """Add information"""
        self.info[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'valid': self.valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'timestamp': self.timestamp
        }


class PriceMatrixValidationService:
    """
    Comprehensive validation service for price matrices
    
    Validates:
    - Structure (rows, columns, cells)
    - Data types (numeric, text)
    - Ranges (min/max values)
    - Formulas (if present)
    - Consistency (no gaps, proper ordering)
    """
    
    def __init__(self):
        self.min_price = 0
        self.max_price = 1000000  # 1 million
        self.min_module_count = 1
        self.max_module_count = 1000
    
    def validate_matrix(self, matrix_data: Dict[str, Any]) -> ValidationResult:
        """
        Perform comprehensive validation on price matrix
        
        Args:
            matrix_data: Dictionary containing rows, columns, cells
            
        Returns:
            ValidationResult with all validation findings
        """
        result = ValidationResult()
        
        # Extract matrix components
        rows = matrix_data.get('rows', [])
        columns = matrix_data.get('columns', [])
        cells = matrix_data.get('cells', {})
        
        # 1. Structure validation
        self._validate_structure(rows, columns, cells, result)
        
        # 2. Data type validation
        self._validate_data_types(rows, columns, cells, result)
        
        # 3. Range validation
        self._validate_ranges(rows, columns, cells, result)
        
        # 4. Formula validation (if formulas present)
        self._validate_formulas(rows, columns, cells, result)
        
        # 5. Consistency checks
        self._validate_consistency(rows, columns, cells, result)
        
        # 6. Generate statistics
        self._generate_statistics(rows, columns, cells, result)
        
        return result

    
    def _validate_structure(
        self,
        rows: List[Dict[str, Any]],
        columns: List[Dict[str, Any]],
        cells: Dict[tuple, Dict[str, Any]],
        result: ValidationResult
    ):
        """Validate matrix structure"""
        # Check if matrix is empty
        if not rows or not columns:
            result.add_error('Matrix is empty - no rows or columns found')
            return
        
        # Check minimum dimensions
        if len(rows) < 2:
            result.add_error('Matrix must have at least 2 rows (header + data)')
        
        if len(columns) < 2:
            result.add_error('Matrix must have at least 2 columns (module count + storage)')
        
        # Check for duplicate positions
        row_positions = [r['position'] for r in rows]
        if len(row_positions) != len(set(row_positions)):
            result.add_error('Duplicate row positions found')
        
        column_positions = [c['position'] for c in columns]
        if len(column_positions) != len(set(column_positions)):
            result.add_error('Duplicate column positions found')
        
        # Check for gaps in positions
        expected_row_positions = set(range(len(rows)))
        actual_row_positions = set(row_positions)
        if expected_row_positions != actual_row_positions:
            result.add_warning('Gaps in row positions detected')
        
        expected_col_positions = set(range(len(columns)))
        actual_col_positions = set(column_positions)
        if expected_col_positions != actual_col_positions:
            result.add_warning('Gaps in column positions detected')
        
        result.add_info('total_rows', len(rows))
        result.add_info('total_columns', len(columns))
        result.add_info('total_cells', len(cells))
    
    def _validate_data_types(
        self,
        rows: List[Dict[str, Any]],
        columns: List[Dict[str, Any]],
        cells: Dict[tuple, Dict[str, Any]],
        result: ValidationResult
    ):
        """Validate data types in matrix"""
        if not columns or not rows:
            return
        
        # Column A (position 0) must contain numeric values (module counts)
        column_a = next((col for col in columns if col['position'] == 0), None)
        if not column_a:
            result.add_error('Column A (module count column) not found')
            return
        
        column_a_id = column_a['id']
        non_numeric_rows = []
        
        for row in rows:
            if row['position'] == 0:  # Skip header
                continue
            
            cell_key = (row['id'], column_a_id)
            if cell_key in cells:
                cell_data = cells[cell_key]
                value = cell_data.get('value')
                raw_input = cell_data.get('raw_input')
                
                if value is None and raw_input:
                    try:
                        float(str(raw_input).replace(',', '.'))
                    except (ValueError, TypeError):
                        non_numeric_rows.append(f"Row {row['position'] + 1}")
                elif value is None:
                    non_numeric_rows.append(f"Row {row['position'] + 1} (empty)")
        
        if non_numeric_rows:
            result.add_error(
                f"Column A must contain numeric module counts. "
                f"Invalid rows: {', '.join(non_numeric_rows)}"
            )
        
        # Row 1 (position 0) must contain text values (storage model names)
        row_1 = next((row for row in rows if row['position'] == 0), None)
        if not row_1:
            result.add_error('Row 1 (header row) not found')
            return
        
        row_1_id = row_1['id']
        empty_headers = []
        
        for column in columns:
            if column['position'] == 0:  # Skip module count column
                continue
            
            cell_key = (row_1_id, column['id'])
            if cell_key not in cells:
                empty_headers.append(f"Column {self._get_column_letter(column['position'])}")
            else:
                cell_data = cells[cell_key]
                raw_input = cell_data.get('raw_input')
                if not raw_input:
                    empty_headers.append(f"Column {self._get_column_letter(column['position'])}")
        
        if empty_headers:
            result.add_error(
                f"Row 1 must contain storage model names. "
                f"Empty columns: {', '.join(empty_headers)}"
            )
        
        # Price cells must be numeric or empty
        invalid_price_cells = []
        
        for row in rows:
            if row['position'] == 0:  # Skip header
                continue
            
            for column in columns:
                if column['position'] == 0:  # Skip module count column
                    continue
                
                cell_key = (row['id'], column['id'])
                if cell_key in cells:
                    cell_data = cells[cell_key]
                    value = cell_data.get('value')
                    raw_input = cell_data.get('raw_input')
                    
                    if value is None and raw_input:
                        try:
                            float(str(raw_input).replace(',', '.'))
                        except (ValueError, TypeError):
                            cell_ref = f"{self._get_column_letter(column['position'])}{row['position'] + 1}"
                            invalid_price_cells.append(f"{cell_ref} ('{raw_input}')")
        
        if invalid_price_cells:
            result.add_error(
                f"Price cells must contain numeric values. "
                f"Invalid cells: {', '.join(invalid_price_cells)}"
            )

    
    def _validate_ranges(
        self,
        rows: List[Dict[str, Any]],
        columns: List[Dict[str, Any]],
        cells: Dict[tuple, Dict[str, Any]],
        result: ValidationResult
    ):
        """Validate value ranges"""
        if not columns or not rows:
            return
        
        # Validate module count ranges
        column_a = next((col for col in columns if col['position'] == 0), None)
        if column_a:
            column_a_id = column_a['id']
            out_of_range_modules = []
            
            for row in rows:
                if row['position'] == 0:  # Skip header
                    continue
                
                cell_key = (row['id'], column_a_id)
                if cell_key in cells:
                    cell_data = cells[cell_key]
                    value = cell_data.get('value')
                    
                    if value is not None:
                        if value < self.min_module_count or value > self.max_module_count:
                            out_of_range_modules.append(
                                f"Row {row['position'] + 1}: {value} "
                                f"(valid range: {self.min_module_count}-{self.max_module_count})"
                            )
            
            if out_of_range_modules:
                result.add_error(
                    f"Module counts out of valid range. "
                    f"Issues: {', '.join(out_of_range_modules)}"
                )
        
        # Validate price ranges
        out_of_range_prices = []
        negative_prices = []
        
        for row in rows:
            if row['position'] == 0:  # Skip header
                continue
            
            for column in columns:
                if column['position'] == 0:  # Skip module count column
                    continue
                
                cell_key = (row['id'], column['id'])
                if cell_key in cells:
                    cell_data = cells[cell_key]
                    value = cell_data.get('value')
                    
                    if value is not None:
                        cell_ref = f"{self._get_column_letter(column['position'])}{row['position'] + 1}"
                        
                        if value < 0:
                            negative_prices.append(f"{cell_ref}: {value}")
                        elif value > self.max_price:
                            out_of_range_prices.append(
                                f"{cell_ref}: {value} (max: {self.max_price})"
                            )
        
        if negative_prices:
            result.add_error(
                f"Negative prices found. "
                f"Cells: {', '.join(negative_prices)}"
            )
        
        if out_of_range_prices:
            result.add_warning(
                f"Prices exceed maximum value. "
                f"Cells: {', '.join(out_of_range_prices)}"
            )
    
    def _validate_formulas(
        self,
        rows: List[Dict[str, Any]],
        columns: List[Dict[str, Any]],
        cells: Dict[tuple, Dict[str, Any]],
        result: ValidationResult
    ):
        """Validate formulas if present"""
        formula_cells = []
        invalid_formulas = []
        
        for cell_key, cell_data in cells.items():
            formula = cell_data.get('formula')
            if formula:
                row_id, col_id = cell_key
                row = next((r for r in rows if r['id'] == row_id), None)
                col = next((c for c in columns if c['id'] == col_id), None)
                
                if row and col:
                    cell_ref = f"{self._get_column_letter(col['position'])}{row['position'] + 1}"
                    formula_cells.append(cell_ref)
                    
                    # Validate formula syntax
                    if not self._is_valid_formula(formula):
                        invalid_formulas.append(f"{cell_ref}: {formula}")
        
        if formula_cells:
            result.add_info('formula_cells', formula_cells)
            result.add_info('formula_count', len(formula_cells))
        
        if invalid_formulas:
            result.add_error(
                f"Invalid formulas found. "
                f"Cells: {', '.join(invalid_formulas)}"
            )
    
    def _validate_consistency(
        self,
        rows: List[Dict[str, Any]],
        columns: List[Dict[str, Any]],
        cells: Dict[tuple, Dict[str, Any]],
        result: ValidationResult
    ):
        """Validate consistency across matrix"""
        if not columns or not rows:
            return
        
        # Check for "No Storage" column
        no_storage_found = False
        no_storage_keywords = [
            'kein speicher', 'ohne speicher', 'no storage', 'none', 'kein', 'ohne'
        ]
        
        for column in columns:
            label_lower = column['label'].lower().strip()
            if any(keyword in label_lower for keyword in no_storage_keywords):
                no_storage_found = True
                result.add_info('no_storage_column', column['label'])
                break
        
        if not no_storage_found:
            result.add_error(
                'No "Kein Speicher" (No Storage) column found. '
                'At least one column must represent the no-storage option.'
            )
        
        # Check for empty price cells
        empty_price_cells = []
        total_price_cells = 0
        
        for row in rows:
            if row['position'] == 0:  # Skip header
                continue
            
            for column in columns:
                if column['position'] == 0:  # Skip module count column
                    continue
                
                total_price_cells += 1
                cell_key = (row['id'], column['id'])
                
                if cell_key not in cells:
                    cell_ref = f"{self._get_column_letter(column['position'])}{row['position'] + 1}"
                    empty_price_cells.append(cell_ref)
                else:
                    cell_data = cells[cell_key]
                    value = cell_data.get('value')
                    raw_input = cell_data.get('raw_input')
                    
                    if value is None and not raw_input:
                        cell_ref = f"{self._get_column_letter(column['position'])}{row['position'] + 1}"
                        empty_price_cells.append(cell_ref)
        
        if empty_price_cells:
            empty_percentage = (len(empty_price_cells) / total_price_cells) * 100
            result.add_warning(
                f"{len(empty_price_cells)} empty price cells found "
                f"({empty_percentage:.1f}% of total). "
                f"This may cause calculation errors."
            )
            result.add_info('empty_price_cells', empty_price_cells[:10])  # First 10
            result.add_info('empty_price_cell_count', len(empty_price_cells))
        
        # Check for monotonic increase in module counts
        column_a = next((col for col in columns if col['position'] == 0), None)
        if column_a:
            module_counts = []
            for row in sorted(rows, key=lambda r: r['position']):
                if row['position'] == 0:  # Skip header
                    continue
                
                cell_key = (row['id'], column_a['id'])
                if cell_key in cells:
                    value = cells[cell_key].get('value')
                    if value is not None:
                        module_counts.append(value)
            
            if module_counts:
                is_monotonic = all(module_counts[i] <= module_counts[i+1] 
                                 for i in range(len(module_counts)-1))
                
                if not is_monotonic:
                    result.add_warning(
                        'Module counts are not in ascending order. '
                        'This may cause lookup issues.'
                    )
                
                result.add_info('module_counts', module_counts)
                result.add_info('module_count_range', 
                              f"{min(module_counts)}-{max(module_counts)}")

    
    def _generate_statistics(
        self,
        rows: List[Dict[str, Any]],
        columns: List[Dict[str, Any]],
        cells: Dict[tuple, Dict[str, Any]],
        result: ValidationResult
    ):
        """Generate statistics about the matrix"""
        if not columns or not rows:
            return
        
        # Extract storage models
        row_1 = next((row for row in rows if row['position'] == 0), None)
        if row_1:
            storage_models = []
            for column in columns:
                if column['position'] == 0:  # Skip module count column
                    continue
                
                cell_key = (row_1['id'], column['id'])
                if cell_key in cells:
                    raw_input = cells[cell_key].get('raw_input')
                    if raw_input:
                        storage_models.append(str(raw_input))
            
            result.add_info('storage_models', storage_models)
            result.add_info('storage_model_count', len(storage_models))
        
        # Calculate price statistics
        prices = []
        for row in rows:
            if row['position'] == 0:  # Skip header
                continue
            
            for column in columns:
                if column['position'] == 0:  # Skip module count column
                    continue
                
                cell_key = (row['id'], column['id'])
                if cell_key in cells:
                    value = cells[cell_key].get('value')
                    if value is not None and value >= 0:
                        prices.append(value)
        
        if prices:
            result.add_info('price_statistics', {
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices),
                'count': len(prices)
            })
    
    def _is_valid_formula(self, formula: str) -> bool:
        """
        Validate formula syntax
        
        Supports basic Excel-like formulas:
        - Arithmetic: +, -, *, /
        - Functions: SUM, AVERAGE, MIN, MAX, IF
        - Cell references: A1, B2, etc.
        - Ranges: A1:A10
        """
        if not formula:
            return False
        
        # Remove whitespace
        formula = formula.strip()
        
        # Must start with =
        if not formula.startswith('='):
            return False
        
        # Remove the = sign
        formula = formula[1:]
        
        # Check for balanced parentheses
        if formula.count('(') != formula.count(')'):
            return False
        
        # Check for valid characters (alphanumeric, operators, parentheses, colon, comma, comparison)
        valid_pattern = r'^[A-Za-z0-9+\-*/(),.:< >= ]+$'
        if not re.match(valid_pattern, formula):
            return False
        
        # Check for valid function names
        function_pattern = r'\b(SUM|AVERAGE|MIN|MAX|IF|INDEX|MATCH|VLOOKUP|HLOOKUP)\b'
        functions = re.findall(function_pattern, formula, re.IGNORECASE)
        
        # If functions found, validate they have parentheses
        for func in functions:
            if f"{func}(" not in formula.upper():
                return False
        
        return True
    
    def _get_column_letter(self, position: int) -> str:
        """Convert column position to Excel letter (A, B, C, ..., Z, AA, AB, ...)"""
        label = ""
        position += 1  # Excel is 1-based
        
        while position > 0:
            position -= 1
            label = chr(65 + (position % 26)) + label
            position //= 26
        
        return label
    
    def get_validation_report(self, validation_result: ValidationResult) -> str:
        """
        Generate a human-readable validation report
        
        Args:
            validation_result: ValidationResult object
            
        Returns:
            Formatted report string
        """
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append("PRICE MATRIX VALIDATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Timestamp: {validation_result.timestamp}")
        lines.append("")
        
        # Overall status
        if validation_result.valid:
            lines.append("✓ VALIDATION PASSED")
            lines.append("Matrix is valid and ready for use in price calculations.")
        else:
            lines.append("✗ VALIDATION FAILED")
            lines.append("Matrix has errors that must be fixed before use.")
        
        lines.append("")
        
        # Errors
        if validation_result.errors:
            lines.append("ERRORS:")
            lines.append("-" * 60)
            for i, error in enumerate(validation_result.errors, 1):
                lines.append(f"{i}. {error}")
            lines.append("")
        
        # Warnings
        if validation_result.warnings:
            lines.append("WARNINGS:")
            lines.append("-" * 60)
            for i, warning in enumerate(validation_result.warnings, 1):
                lines.append(f"{i}. {warning}")
            lines.append("")
        
        # Information
        if validation_result.info:
            lines.append("MATRIX INFORMATION:")
            lines.append("-" * 60)
            
            # Dimensions
            if 'total_rows' in validation_result.info:
                lines.append(f"Rows: {validation_result.info['total_rows']}")
            if 'total_columns' in validation_result.info:
                lines.append(f"Columns: {validation_result.info['total_columns']}")
            if 'total_cells' in validation_result.info:
                lines.append(f"Cells with values: {validation_result.info['total_cells']}")
            
            # Module counts
            if 'module_count_range' in validation_result.info:
                lines.append(f"Module count range: {validation_result.info['module_count_range']}")
            
            # Storage models
            if 'storage_model_count' in validation_result.info:
                lines.append(f"Storage models: {validation_result.info['storage_model_count']}")
            if 'storage_models' in validation_result.info:
                models = validation_result.info['storage_models']
                if len(models) <= 5:
                    lines.append(f"  - {', '.join(models)}")
                else:
                    lines.append(f"  - {', '.join(models[:5])}, ... ({len(models)} total)")
            
            # No storage column
            if 'no_storage_column' in validation_result.info:
                lines.append(f"No storage column: {validation_result.info['no_storage_column']}")
            
            # Price statistics
            if 'price_statistics' in validation_result.info:
                stats = validation_result.info['price_statistics']
                lines.append(f"Price range: {stats['min']:.2f} - {stats['max']:.2f}")
                lines.append(f"Average price: {stats['avg']:.2f}")
                lines.append(f"Price cells: {stats['count']}")
            
            # Empty cells
            if 'empty_price_cell_count' in validation_result.info:
                lines.append(f"Empty price cells: {validation_result.info['empty_price_cell_count']}")
            
            # Formulas
            if 'formula_count' in validation_result.info:
                lines.append(f"Formula cells: {validation_result.info['formula_count']}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)


# Example usage and documentation
VALIDATION_EXAMPLE = """
Example Usage:
--------------

from price_matrix_validation_service import PriceMatrixValidationService

# Initialize service
validator = PriceMatrixValidationService()

# Validate matrix
matrix_data = {
    'rows': [...],
    'columns': [...],
    'cells': {...}
}

result = validator.validate_matrix(matrix_data)

# Check if valid
if result.valid:
    print("Matrix is valid!")
else:
    print("Matrix has errors:")
    for error in result.errors:
        print(f"  - {error}")

# Generate report
report = validator.get_validation_report(result)
print(report)

# Access validation details
print(f"Total errors: {len(result.errors)}")
print(f"Total warnings: {len(result.warnings)}")
print(f"Matrix info: {result.info}")
"""


__all__ = [
    'PriceMatrixValidationService',
    'ValidationResult',
    'VALIDATION_EXAMPLE'
]
