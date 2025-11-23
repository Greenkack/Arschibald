"""
Price Matrix Validation API Endpoints

Provides REST API for price matrix validation

Requirements: 1.3, 4.4
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel

from services.price_matrix_validation_service import (
    PriceMatrixValidationService,
    ValidationResult
)


router = APIRouter(prefix="/api/v1/price-matrix", tags=["price-matrix-validation"])


class MatrixValidationRequest(BaseModel):
    """Request model for matrix validation"""
    rows: list
    columns: list
    cells: dict


class MatrixValidationResponse(BaseModel):
    """Response model for matrix validation"""
    valid: bool
    errors: list
    warnings: list
    info: dict
    timestamp: str
    report: str


@router.post("/validate", response_model=MatrixValidationResponse)
async def validate_matrix(request: MatrixValidationRequest):
    """
    Validate price matrix structure and data
    
    Performs comprehensive validation including:
    - Structure validation (rows, columns, cells)
    - Data type validation (numeric, text)
    - Range validation (min/max values)
    - Formula validation (if present)
    - Consistency checks (no gaps, proper ordering)
    
    Args:
        request: Matrix data to validate
        
    Returns:
        Validation result with errors, warnings, and info
        
    Example:
        ```
        POST /api/v1/price-matrix/validate
        {
            "rows": [...],
            "columns": [...],
            "cells": {...}
        }
        ```
    """
    try:
        # Initialize validator
        validator = PriceMatrixValidationService()
        
        # Prepare matrix data
        matrix_data = {
            'rows': request.rows,
            'columns': request.columns,
            'cells': request.cells
        }
        
        # Validate
        result = validator.validate_matrix(matrix_data)
        
        # Generate report
        report = validator.get_validation_report(result)
        
        # Return response
        return MatrixValidationResponse(
            valid=result.valid,
            errors=result.errors,
            warnings=result.warnings,
            info=result.info,
            timestamp=result.timestamp,
            report=report
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/validate/quick")
async def quick_validate(request: MatrixValidationRequest):
    """
    Quick validation - returns only valid/invalid status
    
    Faster validation that only checks critical errors
    
    Args:
        request: Matrix data to validate
        
    Returns:
        Simple valid/invalid response
    """
    try:
        validator = PriceMatrixValidationService()
        
        matrix_data = {
            'rows': request.rows,
            'columns': request.columns,
            'cells': request.cells
        }
        
        result = validator.validate_matrix(matrix_data)
        
        return {
            'valid': result.valid,
            'error_count': len(result.errors),
            'warning_count': len(result.warnings)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quick validation failed: {str(e)}"
        )


@router.post("/validate/report")
async def get_validation_report(request: MatrixValidationRequest):
    """
    Get detailed validation report as text
    
    Returns a formatted text report of validation results
    
    Args:
        request: Matrix data to validate
        
    Returns:
        Formatted text report
    """
    try:
        validator = PriceMatrixValidationService()
        
        matrix_data = {
            'rows': request.rows,
            'columns': request.columns,
            'cells': request.cells
        }
        
        result = validator.validate_matrix(matrix_data)
        report = validator.get_validation_report(result)
        
        return {
            'report': report,
            'valid': result.valid
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )


@router.get("/validation/rules")
async def get_validation_rules():
    """
    Get validation rules and requirements
    
    Returns documentation of all validation rules
    
    Returns:
        Dictionary of validation rules
    """
    return {
        'structure_rules': {
            'min_rows': 2,
            'min_columns': 2,
            'description': 'Matrix must have at least 2 rows (header + data) and 2 columns (module count + storage)'
        },
        'data_type_rules': {
            'column_a': 'numeric (module counts)',
            'row_1': 'text (storage model names)',
            'price_cells': 'numeric or empty',
            'description': 'Column A must contain numeric module counts, Row 1 must contain storage model names, price cells must be numeric'
        },
        'range_rules': {
            'module_count_min': 1,
            'module_count_max': 1000,
            'price_min': 0,
            'price_max': 1000000,
            'description': 'Module counts must be between 1-1000, prices must be between 0-1,000,000'
        },
        'consistency_rules': {
            'no_storage_column': 'required',
            'monotonic_module_counts': 'recommended',
            'no_empty_price_cells': 'recommended',
            'description': 'Matrix must have a "No Storage" column, module counts should be in ascending order, price cells should not be empty'
        },
        'formula_rules': {
            'syntax': 'Excel-like formulas starting with =',
            'supported_functions': ['SUM', 'AVERAGE', 'MIN', 'MAX', 'IF', 'INDEX', 'MATCH', 'VLOOKUP', 'HLOOKUP'],
            'description': 'Formulas must start with = and use valid Excel-like syntax'
        }
    }


@router.get("/validation/examples")
async def get_validation_examples():
    """
    Get examples of valid and invalid matrices
    
    Returns example matrices for testing
    
    Returns:
        Dictionary with valid and invalid matrix examples
    """
    return {
        'valid_matrix': {
            'description': 'Example of a valid price matrix',
            'rows': [
                {'id': 1, 'position': 0, 'label': 'Header'},
                {'id': 2, 'position': 1, 'label': '10'},
                {'id': 3, 'position': 2, 'label': '15'},
            ],
            'columns': [
                {'id': 1, 'position': 0, 'label': 'Modulanzahl'},
                {'id': 2, 'position': 1, 'label': '10kWh'},
                {'id': 3, 'position': 2, 'label': 'Kein Speicher'},
            ],
            'cells': {
                '(1, 1)': {'raw_input': 'Modulanzahl', 'value': None},
                '(1, 2)': {'raw_input': '10kWh', 'value': None},
                '(1, 3)': {'raw_input': 'Kein Speicher', 'value': None},
                '(2, 1)': {'raw_input': '10', 'value': 10},
                '(2, 2)': {'raw_input': '15000', 'value': 15000},
                '(2, 3)': {'raw_input': '12000', 'value': 12000},
                '(3, 1)': {'raw_input': '15', 'value': 15},
                '(3, 2)': {'raw_input': '18000', 'value': 18000},
                '(3, 3)': {'raw_input': '15000', 'value': 15000},
            }
        },
        'invalid_matrices': [
            {
                'description': 'Empty matrix',
                'error': 'Matrix is empty',
                'rows': [],
                'columns': [],
                'cells': {}
            },
            {
                'description': 'Non-numeric module count',
                'error': 'Column A must contain numeric values',
                'rows': [
                    {'id': 1, 'position': 0, 'label': 'Header'},
                    {'id': 2, 'position': 1, 'label': 'abc'},
                ],
                'columns': [
                    {'id': 1, 'position': 0, 'label': 'Modulanzahl'},
                    {'id': 2, 'position': 1, 'label': '10kWh'},
                ],
                'cells': {
                    '(2, 1)': {'raw_input': 'abc', 'value': None},
                }
            },
            {
                'description': 'Negative price',
                'error': 'Prices cannot be negative',
                'rows': [
                    {'id': 1, 'position': 0, 'label': 'Header'},
                    {'id': 2, 'position': 1, 'label': '10'},
                ],
                'columns': [
                    {'id': 1, 'position': 0, 'label': 'Modulanzahl'},
                    {'id': 2, 'position': 1, 'label': '10kWh'},
                ],
                'cells': {
                    '(2, 1)': {'raw_input': '10', 'value': 10},
                    '(2, 2)': {'raw_input': '-1000', 'value': -1000},
                }
            }
        ]
    }


__all__ = ['router']
