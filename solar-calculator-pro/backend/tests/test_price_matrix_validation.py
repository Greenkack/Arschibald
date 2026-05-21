"""
Tests for Price Matrix Validation Service

Tests all validation aspects:
- Structure validation
- Data type validation
- Range validation
- Formula validation
- Consistency checks
"""

import pytest
from services.price_matrix_validation_service import (
    PriceMatrixValidationService,
    ValidationResult
)


@pytest.fixture
def validator():
    """Create validator instance"""
    return PriceMatrixValidationService()


@pytest.fixture
def valid_matrix():
    """Create a valid matrix for testing"""
    return {
        'rows': [
            {'id': 1, 'position': 0, 'label': 'Header'},
            {'id': 2, 'position': 1, 'label': '10'},
            {'id': 3, 'position': 2, 'label': '15'},
            {'id': 4, 'position': 3, 'label': '20'},
        ],
        'columns': [
            {'id': 1, 'position': 0, 'label': 'Modulanzahl'},
            {'id': 2, 'position': 1, 'label': '10kWh'},
            {'id': 3, 'position': 2, 'label': '15kWh'},
            {'id': 4, 'position': 3, 'label': 'Kein Speicher'},
        ],
        'cells': {
            # Header row
            (1, 1): {'raw_input': 'Modulanzahl', 'value': None},
            (1, 2): {'raw_input': '10kWh', 'value': None},
            (1, 3): {'raw_input': '15kWh', 'value': None},
            (1, 4): {'raw_input': 'Kein Speicher', 'value': None},
            # Data rows
            (2, 1): {'raw_input': '10', 'value': 10},
            (2, 2): {'raw_input': '15000', 'value': 15000},
            (2, 3): {'raw_input': '17500', 'value': 17500},
            (2, 4): {'raw_input': '12000', 'value': 12000},
            (3, 1): {'raw_input': '15', 'value': 15},
            (3, 2): {'raw_input': '18000', 'value': 18000},
            (3, 3): {'raw_input': '20500', 'value': 20500},
            (3, 4): {'raw_input': '15000', 'value': 15000},
            (4, 1): {'raw_input': '20', 'value': 20},
            (4, 2): {'raw_input': '21000', 'value': 21000},
            (4, 3): {'raw_input': '23500', 'value': 23500},
            (4, 4): {'raw_input': '18000', 'value': 18000},
        }
    }


class TestStructureValidation:
    """Test structure validation"""
    
    def test_valid_structure(self, validator, valid_matrix):
        """Test validation of valid structure"""
        result = validator.validate_matrix(valid_matrix)
        assert result.valid
        assert len(result.errors) == 0
        assert result.info['total_rows'] == 4
        assert result.info['total_columns'] == 4
    
    def test_empty_matrix(self, validator):
        """Test validation of empty matrix"""
        result = validator.validate_matrix({'rows': [], 'columns': [], 'cells': {}})
        assert not result.valid
        assert any('empty' in error.lower() for error in result.errors)
    
    def test_insufficient_rows(self, validator):
        """Test validation with insufficient rows"""
        matrix = {
            'rows': [{'id': 1, 'position': 0, 'label': 'Header'}],
            'columns': [
                {'id': 1, 'position': 0, 'label': 'A'},
                {'id': 2, 'position': 1, 'label': 'B'}
            ],
            'cells': {}
        }
        result = validator.validate_matrix(matrix)
        assert not result.valid
        assert any('at least 2 rows' in error.lower() for error in result.errors)
    
    def test_insufficient_columns(self, validator):
        """Test validation with insufficient columns"""
        matrix = {
            'rows': [
                {'id': 1, 'position': 0, 'label': 'Header'},
                {'id': 2, 'position': 1, 'label': 'Data'}
            ],
            'columns': [{'id': 1, 'position': 0, 'label': 'A'}],
            'cells': {}
        }
        result = validator.validate_matrix(matrix)
        assert not result.valid
        assert any('at least 2 columns' in error.lower() for error in result.errors)


class TestDataTypeValidation:
    """Test data type validation"""
    
    def test_valid_data_types(self, validator, valid_matrix):
        """Test validation of valid data types"""
        result = validator.validate_matrix(valid_matrix)
        assert result.valid
        assert len(result.errors) == 0
    
    def test_non_numeric_module_count(self, validator, valid_matrix):
        """Test validation with non-numeric module count"""
        # Make module count non-numeric
        valid_matrix['cells'][(2, 1)] = {'raw_input': 'abc', 'value': None}
        
        result = validator.validate_matrix(valid_matrix)
        assert not result.valid
        assert any('column a' in error.lower() and 'numeric' in error.lower() 
                  for error in result.errors)
    
    def test_empty_header(self, validator, valid_matrix):
        """Test validation with empty header cell"""
        # Remove header cell
        del valid_matrix['cells'][(1, 2)]
        
        result = validator.validate_matrix(valid_matrix)
        assert not result.valid
        assert any('row 1' in error.lower() and 'storage model' in error.lower() 
                  for error in result.errors)
    
    def test_non_numeric_price(self, validator, valid_matrix):
        """Test validation with non-numeric price"""
        # Make price non-numeric
        valid_matrix['cells'][(2, 2)] = {'raw_input': 'invalid', 'value': None}
        
        result = validator.validate_matrix(valid_matrix)
        assert not result.valid
        assert any('price cells' in error.lower() and 'numeric' in error.lower() 
                  for error in result.errors)


class TestRangeValidation:
    """Test range validation"""
    
    def test_valid_ranges(self, validator, valid_matrix):
        """Test validation of valid ranges"""
        result = validator.validate_matrix(valid_matrix)
        assert result.valid
        assert len(result.errors) == 0
    
    def test_module_count_too_low(self, validator, valid_matrix):
        """Test validation with module count below minimum"""
        valid_matrix['cells'][(2, 1)] = {'raw_input': '0', 'value': 0}
        
        result = validator.validate_matrix(valid_matrix)
        assert not result.valid
        assert any('module counts out of valid range' in error.lower() 
                  for error in result.errors)
    
    def test_module_count_too_high(self, validator, valid_matrix):
        """Test validation with module count above maximum"""
        valid_matrix['cells'][(2, 1)] = {'raw_input': '2000', 'value': 2000}
        
        result = validator.validate_matrix(valid_matrix)
        assert not result.valid
        assert any('module counts out of valid range' in error.lower() 
                  for error in result.errors)
    
    def test_negative_price(self, validator, valid_matrix):
        """Test validation with negative price"""
        valid_matrix['cells'][(2, 2)] = {'raw_input': '-1000', 'value': -1000}
        
        result = validator.validate_matrix(valid_matrix)
        assert not result.valid
        assert any('negative prices' in error.lower() for error in result.errors)
    
    def test_price_too_high(self, validator, valid_matrix):
        """Test validation with price above maximum"""
        valid_matrix['cells'][(2, 2)] = {'raw_input': '2000000', 'value': 2000000}
        
        result = validator.validate_matrix(valid_matrix)
        assert len(result.warnings) > 0
        assert any('exceed maximum' in warning.lower() for warning in result.warnings)


class TestFormulaValidation:
    """Test formula validation"""
    
    def test_valid_formula(self, validator):
        """Test validation of valid formula"""
        assert validator._is_valid_formula('=A1+B1')
        assert validator._is_valid_formula('=SUM(A1:A10)')
        assert validator._is_valid_formula('=AVERAGE(B2:B20)')
        assert validator._is_valid_formula('=IF(A1>10, B1, C1)')
    
    def test_invalid_formula_no_equals(self, validator):
        """Test validation of formula without equals sign"""
        assert not validator._is_valid_formula('A1+B1')
    
    def test_invalid_formula_unbalanced_parens(self, validator):
        """Test validation of formula with unbalanced parentheses"""
        assert not validator._is_valid_formula('=SUM(A1:A10')
        assert not validator._is_valid_formula('=SUM A1:A10)')
    
    def test_invalid_formula_invalid_chars(self, validator):
        """Test validation of formula with invalid characters"""
        assert not validator._is_valid_formula('=A1+B1#')
        assert not validator._is_valid_formula('=A1+B1@')
    
    def test_matrix_with_formulas(self, validator, valid_matrix):
        """Test validation of matrix with formulas"""
        # Add formula to a cell
        valid_matrix['cells'][(2, 2)]['formula'] = '=A2*1000'
        
        result = validator.validate_matrix(valid_matrix)
        assert result.valid
        assert 'formula_count' in result.info
        assert result.info['formula_count'] == 1


class TestConsistencyValidation:
    """Test consistency validation"""
    
    def test_no_storage_column_present(self, validator, valid_matrix):
        """Test validation with no storage column present"""
        result = validator.validate_matrix(valid_matrix)
        assert result.valid
        assert 'no_storage_column' in result.info
        assert 'kein speicher' in result.info['no_storage_column'].lower()
    
    def test_no_storage_column_missing(self, validator, valid_matrix):
        """Test validation without no storage column"""
        # Remove "Kein Speicher" column
        valid_matrix['columns'] = [col for col in valid_matrix['columns'] if col['id'] != 4]
        # Remove cells in that column
        valid_matrix['cells'] = {k: v for k, v in valid_matrix['cells'].items() if k[1] != 4}
        
        result = validator.validate_matrix(valid_matrix)
        assert not result.valid
        assert any('kein speicher' in error.lower() for error in result.errors)
    
    def test_empty_price_cells(self, validator, valid_matrix):
        """Test validation with empty price cells"""
        # Remove some price cells
        del valid_matrix['cells'][(2, 2)]
        del valid_matrix['cells'][(3, 3)]
        
        result = validator.validate_matrix(valid_matrix)
        assert len(result.warnings) > 0
        assert any('empty price cells' in warning.lower() for warning in result.warnings)
        assert 'empty_price_cell_count' in result.info
    
    def test_non_monotonic_module_counts(self, validator, valid_matrix):
        """Test validation with non-monotonic module counts"""
        # Make module counts non-monotonic
        valid_matrix['cells'][(3, 1)] = {'raw_input': '5', 'value': 5}  # Less than previous
        
        result = validator.validate_matrix(valid_matrix)
        assert len(result.warnings) > 0
        assert any('not in ascending order' in warning.lower() for warning in result.warnings)


class TestStatisticsGeneration:
    """Test statistics generation"""
    
    def test_statistics_generated(self, validator, valid_matrix):
        """Test that statistics are generated"""
        result = validator.validate_matrix(valid_matrix)
        
        assert 'storage_models' in result.info
        assert 'storage_model_count' in result.info
        assert 'price_statistics' in result.info
        assert 'module_counts' in result.info
        assert 'module_count_range' in result.info
    
    def test_price_statistics_correct(self, validator, valid_matrix):
        """Test that price statistics are correct"""
        result = validator.validate_matrix(valid_matrix)
        
        stats = result.info['price_statistics']
        assert stats['min'] == 12000
        assert stats['max'] == 23500
        assert stats['count'] == 9  # 3 rows x 3 price columns
        assert 12000 <= stats['avg'] <= 23500


class TestValidationReport:
    """Test validation report generation"""
    
    def test_report_for_valid_matrix(self, validator, valid_matrix):
        """Test report generation for valid matrix"""
        result = validator.validate_matrix(valid_matrix)
        report = validator.get_validation_report(result)
        
        assert 'VALIDATION PASSED' in report
        assert 'PRICE MATRIX VALIDATION REPORT' in report
        assert 'MATRIX INFORMATION' in report
    
    def test_report_for_invalid_matrix(self, validator):
        """Test report generation for invalid matrix"""
        invalid_matrix = {'rows': [], 'columns': [], 'cells': {}}
        result = validator.validate_matrix(invalid_matrix)
        report = validator.get_validation_report(result)
        
        assert 'VALIDATION FAILED' in report
        assert 'ERRORS:' in report
    
    def test_report_includes_warnings(self, validator, valid_matrix):
        """Test that report includes warnings"""
        # Create a warning condition
        del valid_matrix['cells'][(2, 2)]
        
        result = validator.validate_matrix(valid_matrix)
        report = validator.get_validation_report(result)
        
        assert 'WARNINGS:' in report


class TestColumnLetterConversion:
    """Test column letter conversion"""
    
    def test_single_letter_columns(self, validator):
        """Test conversion for single letter columns"""
        assert validator._get_column_letter(0) == 'A'
        assert validator._get_column_letter(1) == 'B'
        assert validator._get_column_letter(25) == 'Z'
    
    def test_double_letter_columns(self, validator):
        """Test conversion for double letter columns"""
        assert validator._get_column_letter(26) == 'AA'
        assert validator._get_column_letter(27) == 'AB'
        assert validator._get_column_letter(51) == 'AZ'
    
    def test_triple_letter_columns(self, validator):
        """Test conversion for triple letter columns"""
        assert validator._get_column_letter(702) == 'AAA'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
