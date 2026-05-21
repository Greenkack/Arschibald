"""
Data Validation System
Validates data integrity before and after migrations.
"""

import logging
from typing import Any, Dict, List, Callable, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class ValidationRule:
    """Base validation rule"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def validate(self, session: Session) -> Dict[str, Any]:
        """
        Execute validation
        
        Returns:
            Validation result with status and details
        """
        raise NotImplementedError


class TableExistsRule(ValidationRule):
    """Validate that a table exists"""
    
    def __init__(self, table_name: str):
        super().__init__(
            f"table_exists_{table_name}",
            f"Table {table_name} must exist"
        )
        self.table_name = table_name
    
    def validate(self, session: Session) -> Dict[str, Any]:
        inspector = inspect(session.bind)
        exists = self.table_name in inspector.get_table_names()
        
        return {
            'rule': self.name,
            'passed': exists,
            'message': f"Table {self.table_name} {'exists' if exists else 'does not exist'}"
        }


class ColumnExistsRule(ValidationRule):
    """Validate that a column exists in a table"""
    
    def __init__(self, table_name: str, column_name: str):
        super().__init__(
            f"column_exists_{table_name}_{column_name}",
            f"Column {column_name} must exist in table {table_name}"
        )
        self.table_name = table_name
        self.column_name = column_name
    
    def validate(self, session: Session) -> Dict[str, Any]:
        inspector = inspect(session.bind)
        
        try:
            columns = [col['name'] for col in inspector.get_columns(self.table_name)]
            exists = self.column_name in columns
            
            return {
                'rule': self.name,
                'passed': exists,
                'message': f"Column {self.column_name} {'exists' if exists else 'does not exist'} in {self.table_name}"
            }
        except Exception as e:
            return {
                'rule': self.name,
                'passed': False,
                'message': f"Error checking column: {str(e)}"
            }


class NotNullRule(ValidationRule):
    """Validate that a column has no NULL values"""
    
    def __init__(self, table_name: str, column_name: str):
        super().__init__(
            f"not_null_{table_name}_{column_name}",
            f"Column {column_name} in {table_name} must not have NULL values"
        )
        self.table_name = table_name
        self.column_name = column_name
    
    def validate(self, session: Session) -> Dict[str, Any]:
        query = f"""
            SELECT COUNT(*) FROM {self.table_name}
            WHERE {self.column_name} IS NULL
        """
        
        null_count = session.execute(text(query)).scalar()
        passed = null_count == 0
        
        return {
            'rule': self.name,
            'passed': passed,
            'message': f"Found {null_count} NULL values in {self.table_name}.{self.column_name}",
            'null_count': null_count
        }


class UniqueRule(ValidationRule):
    """Validate that column values are unique"""
    
    def __init__(self, table_name: str, column_name: str):
        super().__init__(
            f"unique_{table_name}_{column_name}",
            f"Column {column_name} in {table_name} must have unique values"
        )
        self.table_name = table_name
        self.column_name = column_name
    
    def validate(self, session: Session) -> Dict[str, Any]:
        query = f"""
            SELECT {self.column_name}, COUNT(*) as count
            FROM {self.table_name}
            GROUP BY {self.column_name}
            HAVING COUNT(*) > 1
        """
        
        duplicates = session.execute(text(query)).fetchall()
        passed = len(duplicates) == 0
        
        return {
            'rule': self.name,
            'passed': passed,
            'message': f"Found {len(duplicates)} duplicate values in {self.table_name}.{self.column_name}",
            'duplicate_count': len(duplicates),
            'duplicates': [dict(row._mapping) for row in duplicates[:10]]  # First 10
        }


class DataTypeRule(ValidationRule):
    """Validate that column values match expected data type"""
    
    def __init__(self, table_name: str, column_name: str, expected_type: type):
        super().__init__(
            f"data_type_{table_name}_{column_name}",
            f"Column {column_name} in {table_name} must contain {expected_type.__name__} values"
        )
        self.table_name = table_name
        self.column_name = column_name
        self.expected_type = expected_type
    
    def validate(self, session: Session) -> Dict[str, Any]:
        query = f"SELECT {self.column_name} FROM {self.table_name} WHERE {self.column_name} IS NOT NULL"
        rows = session.execute(text(query)).fetchall()
        
        invalid_count = 0
        invalid_samples = []
        
        for row in rows:
            value = row[0]
            
            try:
                # Try to convert to expected type
                self.expected_type(value)
            except (ValueError, TypeError):
                invalid_count += 1
                if len(invalid_samples) < 10:
                    invalid_samples.append(value)
        
        passed = invalid_count == 0
        
        return {
            'rule': self.name,
            'passed': passed,
            'message': f"Found {invalid_count} invalid {self.expected_type.__name__} values",
            'invalid_count': invalid_count,
            'samples': invalid_samples
        }


class RangeRule(ValidationRule):
    """Validate that numeric values are within a range"""
    
    def __init__(self, table_name: str, column_name: str, min_value: float, max_value: float):
        super().__init__(
            f"range_{table_name}_{column_name}",
            f"Column {column_name} in {table_name} must be between {min_value} and {max_value}"
        )
        self.table_name = table_name
        self.column_name = column_name
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, session: Session) -> Dict[str, Any]:
        query = f"""
            SELECT COUNT(*) FROM {self.table_name}
            WHERE {self.column_name} < :min_value OR {self.column_name} > :max_value
        """
        
        out_of_range = session.execute(
            text(query),
            {'min_value': self.min_value, 'max_value': self.max_value}
        ).scalar()
        
        passed = out_of_range == 0
        
        return {
            'rule': self.name,
            'passed': passed,
            'message': f"Found {out_of_range} values outside range [{self.min_value}, {self.max_value}]",
            'out_of_range_count': out_of_range
        }


class PatternRule(ValidationRule):
    """Validate that string values match a regex pattern"""
    
    def __init__(self, table_name: str, column_name: str, pattern: str):
        super().__init__(
            f"pattern_{table_name}_{column_name}",
            f"Column {column_name} in {table_name} must match pattern {pattern}"
        )
        self.table_name = table_name
        self.column_name = column_name
        self.pattern = re.compile(pattern)
    
    def validate(self, session: Session) -> Dict[str, Any]:
        query = f"SELECT {self.column_name} FROM {self.table_name} WHERE {self.column_name} IS NOT NULL"
        rows = session.execute(text(query)).fetchall()
        
        invalid_count = 0
        invalid_samples = []
        
        for row in rows:
            value = str(row[0])
            
            if not self.pattern.match(value):
                invalid_count += 1
                if len(invalid_samples) < 10:
                    invalid_samples.append(value)
        
        passed = invalid_count == 0
        
        return {
            'rule': self.name,
            'passed': passed,
            'message': f"Found {invalid_count} values not matching pattern",
            'invalid_count': invalid_count,
            'samples': invalid_samples
        }


class ForeignKeyRule(ValidationRule):
    """Validate foreign key relationships"""
    
    def __init__(self, table_name: str, column_name: str, 
                 ref_table: str, ref_column: str):
        super().__init__(
            f"foreign_key_{table_name}_{column_name}",
            f"Foreign key {table_name}.{column_name} must reference {ref_table}.{ref_column}"
        )
        self.table_name = table_name
        self.column_name = column_name
        self.ref_table = ref_table
        self.ref_column = ref_column
    
    def validate(self, session: Session) -> Dict[str, Any]:
        query = f"""
            SELECT COUNT(*) FROM {self.table_name} t
            WHERE t.{self.column_name} IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM {self.ref_table} r
                WHERE r.{self.ref_column} = t.{self.column_name}
            )
        """
        
        orphaned = session.execute(text(query)).scalar()
        passed = orphaned == 0
        
        return {
            'rule': self.name,
            'passed': passed,
            'message': f"Found {orphaned} orphaned foreign key references",
            'orphaned_count': orphaned
        }


class CustomRule(ValidationRule):
    """Custom validation rule with user-defined function"""
    
    def __init__(self, name: str, description: str, 
                 validation_func: Callable[[Session], bool]):
        super().__init__(name, description)
        self.validation_func = validation_func
    
    def validate(self, session: Session) -> Dict[str, Any]:
        try:
            passed = self.validation_func(session)
            
            return {
                'rule': self.name,
                'passed': passed,
                'message': f"Custom validation {'passed' if passed else 'failed'}"
            }
        except Exception as e:
            return {
                'rule': self.name,
                'passed': False,
                'message': f"Validation error: {str(e)}"
            }


class DataValidator:
    """
    Data validation engine
    
    Features:
    - Pre-migration validation
    - Post-migration validation
    - Multiple validation rules
    - Detailed reporting
    - Error tracking
    """
    
    def __init__(self, session: Session):
        """
        Initialize data validator
        
        Args:
            session: Database session
        """
        self.session = session
        self.rules: List[ValidationRule] = []
        self.results: List[Dict[str, Any]] = []
    
    def add_rule(self, rule: ValidationRule):
        """Add a validation rule"""
        self.rules.append(rule)
        logger.info(f"Added validation rule: {rule.name}")
    
    def add_table_exists(self, table_name: str):
        """Add table existence validation"""
        self.add_rule(TableExistsRule(table_name))
    
    def add_column_exists(self, table_name: str, column_name: str):
        """Add column existence validation"""
        self.add_rule(ColumnExistsRule(table_name, column_name))
    
    def add_not_null(self, table_name: str, column_name: str):
        """Add NOT NULL validation"""
        self.add_rule(NotNullRule(table_name, column_name))
    
    def add_unique(self, table_name: str, column_name: str):
        """Add uniqueness validation"""
        self.add_rule(UniqueRule(table_name, column_name))
    
    def add_data_type(self, table_name: str, column_name: str, expected_type: type):
        """Add data type validation"""
        self.add_rule(DataTypeRule(table_name, column_name, expected_type))
    
    def add_range(self, table_name: str, column_name: str, min_value: float, max_value: float):
        """Add range validation"""
        self.add_rule(RangeRule(table_name, column_name, min_value, max_value))
    
    def add_pattern(self, table_name: str, column_name: str, pattern: str):
        """Add pattern validation"""
        self.add_rule(PatternRule(table_name, column_name, pattern))
    
    def add_foreign_key(self, table_name: str, column_name: str, 
                       ref_table: str, ref_column: str):
        """Add foreign key validation"""
        self.add_rule(ForeignKeyRule(table_name, column_name, ref_table, ref_column))
    
    def add_custom(self, name: str, description: str, 
                   validation_func: Callable[[Session], bool]):
        """Add custom validation"""
        self.add_rule(CustomRule(name, description, validation_func))
    
    def validate(self) -> Dict[str, Any]:
        """
        Execute all validation rules
        
        Returns:
            Validation summary
        """
        logger.info(f"Running {len(self.rules)} validation rules")
        
        self.results = []
        passed_count = 0
        failed_count = 0
        
        for rule in self.rules:
            logger.info(f"Validating: {rule.description}")
            
            try:
                result = rule.validate(self.session)
                self.results.append(result)
                
                if result['passed']:
                    passed_count += 1
                else:
                    failed_count += 1
                    logger.warning(f"Validation failed: {result['message']}")
                
            except Exception as e:
                logger.error(f"Validation error for {rule.name}: {str(e)}")
                self.results.append({
                    'rule': rule.name,
                    'passed': False,
                    'message': f"Validation error: {str(e)}"
                })
                failed_count += 1
        
        all_passed = failed_count == 0
        
        summary = {
            'valid': all_passed,
            'total_rules': len(self.rules),
            'passed': passed_count,
            'failed': failed_count,
            'results': self.results,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Validation complete: {passed_count} passed, {failed_count} failed")
        
        return summary
    
    def get_failed_rules(self) -> List[Dict[str, Any]]:
        """Get list of failed validation rules"""
        return [r for r in self.results if not r['passed']]
    
    def export_report(self, output_file: str):
        """Export validation report to JSON file"""
        import json
        
        report = {
            'validation_date': datetime.now().isoformat(),
            'total_rules': len(self.rules),
            'results': self.results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Validation report exported to {output_file}")
