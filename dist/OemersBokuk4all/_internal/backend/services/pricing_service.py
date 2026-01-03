"""
PricingService - FastAPI Backend Service for Price Matrix

This service wraps the existing price_matrix_*.py modules and provides
a clean API interface for price calculations with Excel INDEX/MATCH logic.

Requirements: 1.3, 4.5, 14.1, 14.2
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

# Add parent directory to path to import legacy modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)


class PricingService:
    """
    Service for price matrix operations with Excel INDEX/MATCH logic
    
    This service provides:
    - Price calculation with INDEX/MATCH logic
    - Matrix upload and validation
    - Price lookup with caching
    - Matrix export functionality
    - CRUD operations on matrix data
    """
    
    def __init__(self):
        """Initialize the pricing service"""
        self.logger = logger
        self._cache = {}
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            "service": "PricingService",
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }

    # ========================================================================
    # Excel INDEX/MATCH Logic Implementation
    # ========================================================================
    
    def calculate_price(
        self,
        module_count: int,
        storage_model: Optional[str] = None,
        matrix_id: Optional[int] = None,
        enable_fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate price using Excel INDEX/MATCH logic
        
        Logic:
        1. MATCH(module_count, column_A, 0) -> finds row index
        2. MATCH(storage_model, row_1, 0) -> finds column index
        3. INDEX(matrix, row_index, col_index) -> returns price
        
        Special handling:
        - "kein Speicher" uses last column
        - Floor logic for module count (nächst-kleinere Zahl)
        
        Args:
            module_count: Number of PV modules
            storage_model: Battery storage model name or None for "kein Speicher"
            matrix_id: Optional matrix ID (None = active matrix)
            enable_fallback: Enable fallback strategies
            
        Returns:
            Dictionary with price and metadata
        """
        try:
            # Import here to avoid circular imports
            import price_matrix_lookup
            
            # Use safe calculation with comprehensive error handling
            result = price_matrix_lookup.calculate_price_from_matrix_safe(
                module_count=module_count,
                storage_model=storage_model,
                matrix_id=matrix_id,
                enable_fallback=enable_fallback,
                notify_admin=True
            )
            
            return result
            
        except Exception as e:
            self.logger.exception(f"Error calculating price: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'system_error',
                'user_message': f"Fehler bei der Preisberechnung: {str(e)}"
            }

    # ========================================================================
    # Matrix Management
    # ========================================================================
    
    def create_matrix(
        self,
        name: str,
        description: str = "",
        pricing_mode: str = 'pauschal',
        include_accessories: bool = True,
        include_misc: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new price matrix
        
        Args:
            name: Matrix name
            description: Matrix description
            pricing_mode: 'pauschal' or 'additiv'
            include_accessories: Include accessories in price
            include_misc: Include miscellaneous items in price
            
        Returns:
            Dictionary with matrix_id and status
        """
        try:
            import price_matrix_store
            
            matrix_id = price_matrix_store.create_matrix(
                name=name,
                description=description,
                pricing_mode=pricing_mode,
                include_accessories=include_accessories,
                include_misc=include_misc
            )
            
            if matrix_id:
                return {
                    'success': True,
                    'matrix_id': matrix_id,
                    'message': f'Matrix "{name}" erfolgreich erstellt'
                }
            else:
                return {
                    'success': False,
                    'error': 'Matrix konnte nicht erstellt werden'
                }
                
        except Exception as e:
            self.logger.exception(f"Error creating matrix: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_matrices(self) -> Dict[str, Any]:
        """
        List all price matrices
        
        Returns:
            Dictionary with list of matrices
        """
        try:
            import price_matrix_store
            
            matrices = price_matrix_store.list_matrices()
            
            return {
                'success': True,
                'matrices': matrices,
                'count': len(matrices)
            }
            
        except Exception as e:
            self.logger.exception(f"Error listing matrices: {e}")
            return {
                'success': False,
                'error': str(e),
                'matrices': []
            }

    def get_matrix(self, matrix_id: int) -> Dict[str, Any]:
        """
        Get full matrix data
        
        Args:
            matrix_id: Matrix ID
            
        Returns:
            Dictionary with complete matrix data
        """
        try:
            import price_matrix_store
            
            matrix_data = price_matrix_store.get_matrix_full(matrix_id)
            
            if matrix_data:
                return {
                    'success': True,
                    'matrix': matrix_data
                }
            else:
                return {
                    'success': False,
                    'error': f'Matrix mit ID {matrix_id} nicht gefunden'
                }
                
        except Exception as e:
            self.logger.exception(f"Error getting matrix: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def set_active_matrix(self, matrix_id: int) -> Dict[str, Any]:
        """
        Set active matrix
        
        Args:
            matrix_id: Matrix ID to activate
            
        Returns:
            Dictionary with success status
        """
        try:
            import price_matrix_store
            
            success = price_matrix_store.set_active_matrix(matrix_id)
            
            if success:
                return {
                    'success': True,
                    'message': f'Matrix {matrix_id} ist jetzt aktiv'
                }
            else:
                return {
                    'success': False,
                    'error': f'Matrix {matrix_id} konnte nicht aktiviert werden'
                }
                
        except Exception as e:
            self.logger.exception(f"Error setting active matrix: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_matrix(self, matrix_id: int) -> Dict[str, Any]:
        """
        Delete a matrix
        
        Args:
            matrix_id: Matrix ID to delete
            
        Returns:
            Dictionary with success status
        """
        try:
            import price_matrix_store
            
            success = price_matrix_store.delete_matrix(matrix_id)
            
            if success:
                return {
                    'success': True,
                    'message': f'Matrix {matrix_id} wurde gelöscht'
                }
            else:
                return {
                    'success': False,
                    'error': f'Matrix {matrix_id} konnte nicht gelöscht werden'
                }
                
        except Exception as e:
            self.logger.exception(f"Error deleting matrix: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # Matrix Upload and Validation
    # ========================================================================
    
    def upload_matrix_csv(
        self,
        name: str,
        csv_content: str,
        delimiter: str = ';'
    ) -> Dict[str, Any]:
        """
        Upload matrix from CSV
        
        Args:
            name: Matrix name
            csv_content: CSV content as string
            delimiter: CSV delimiter (default: ';')
            
        Returns:
            Dictionary with matrix_id and validation results
        """
        try:
            import price_matrix_store
            import price_matrix_validation
            
            # Import matrix
            matrix_id = price_matrix_store.import_matrix_csv(
                name=name,
                csv_text=csv_content,
                delimiter=delimiter
            )
            
            if not matrix_id:
                return {
                    'success': False,
                    'error': 'Matrix konnte nicht importiert werden'
                }
            
            # Validate matrix
            validation_result = price_matrix_validation.validate_matrix_for_pricing(matrix_id)
            
            return {
                'success': True,
                'matrix_id': matrix_id,
                'validation': validation_result,
                'message': f'Matrix "{name}" erfolgreich hochgeladen'
            }
            
        except Exception as e:
            self.logger.exception(f"Error uploading CSV matrix: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_matrix(self, matrix_id: int) -> Dict[str, Any]:
        """
        Validate matrix structure and data
        
        Args:
            matrix_id: Matrix ID to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            import price_matrix_error_handling
            
            result = price_matrix_error_handling.validate_matrix_with_error_handling(matrix_id)
            
            return result
            
        except Exception as e:
            self.logger.exception(f"Error validating matrix: {e}")
            return {
                'valid': False,
                'error': str(e)
            }

    # ========================================================================
    # Matrix Export
    # ========================================================================
    
    def export_matrix_csv(
        self,
        matrix_id: int,
        delimiter: str = ';'
    ) -> Dict[str, Any]:
        """
        Export matrix to CSV
        
        Args:
            matrix_id: Matrix ID to export
            delimiter: CSV delimiter (default: ';')
            
        Returns:
            Dictionary with CSV content
        """
        try:
            import price_matrix_store
            
            csv_content = price_matrix_store.export_matrix_csv(
                matrix_id=matrix_id,
                delimiter=delimiter
            )
            
            if csv_content is not None:
                return {
                    'success': True,
                    'csv_content': csv_content,
                    'matrix_id': matrix_id
                }
            else:
                return {
                    'success': False,
                    'error': f'Matrix {matrix_id} konnte nicht exportiert werden'
                }
                
        except Exception as e:
            self.logger.exception(f"Error exporting matrix to CSV: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ========================================================================
    # CRUD Operations on Matrix Data
    # ========================================================================
    
    def add_row(
        self,
        matrix_id: int,
        label: str,
        position: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Add row to matrix
        
        Args:
            matrix_id: Matrix ID
            label: Row label (e.g., module count)
            position: Optional position (None = append)
            
        Returns:
            Dictionary with row_id
        """
        try:
            import price_matrix_store
            
            row_id = price_matrix_store.add_row(
                matrix_id=matrix_id,
                label=label,
                position=position
            )
            
            if row_id:
                return {
                    'success': True,
                    'row_id': row_id,
                    'message': f'Zeile "{label}" hinzugefügt'
                }
            else:
                return {
                    'success': False,
                    'error': 'Zeile konnte nicht hinzugefügt werden'
                }
                
        except Exception as e:
            self.logger.exception(f"Error adding row: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def add_column(
        self,
        matrix_id: int,
        label: str,
        position: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Add column to matrix
        
        Args:
            matrix_id: Matrix ID
            label: Column label (e.g., storage model)
            position: Optional position (None = append)
            
        Returns:
            Dictionary with column_id
        """
        try:
            import price_matrix_store
            
            column_id = price_matrix_store.add_column(
                matrix_id=matrix_id,
                label=label,
                position=position
            )
            
            if column_id:
                return {
                    'success': True,
                    'column_id': column_id,
                    'message': f'Spalte "{label}" hinzugefügt'
                }
            else:
                return {
                    'success': False,
                    'error': 'Spalte konnte nicht hinzugefügt werden'
                }
                
        except Exception as e:
            self.logger.exception(f"Error adding column: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def remove_row(self, row_id: int) -> Dict[str, Any]:
        """
        Remove row from matrix
        
        Args:
            row_id: Row ID to remove
            
        Returns:
            Dictionary with success status
        """
        try:
            import price_matrix_store
            
            success = price_matrix_store.remove_row(row_id)
            
            if success:
                return {
                    'success': True,
                    'message': f'Zeile {row_id} wurde entfernt'
                }
            else:
                return {
                    'success': False,
                    'error': f'Zeile {row_id} konnte nicht entfernt werden'
                }
                
        except Exception as e:
            self.logger.exception(f"Error removing row: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def remove_column(self, column_id: int) -> Dict[str, Any]:
        """
        Remove column from matrix
        
        Args:
            column_id: Column ID to remove
            
        Returns:
            Dictionary with success status
        """
        try:
            import price_matrix_store
            
            success = price_matrix_store.remove_column(column_id)
            
            if success:
                return {
                    'success': True,
                    'message': f'Spalte {column_id} wurde entfernt'
                }
            else:
                return {
                    'success': False,
                    'error': f'Spalte {column_id} konnte nicht entfernt werden'
                }
                
        except Exception as e:
            self.logger.exception(f"Error removing column: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def set_cell_value(
        self,
        matrix_id: int,
        row_id: int,
        column_id: int,
        value: Optional[float],
        raw_input: Optional[str] = None,
        data_type: str = 'number'
    ) -> Dict[str, Any]:
        """
        Set cell value in matrix
        
        Args:
            matrix_id: Matrix ID
            row_id: Row ID
            column_id: Column ID
            value: Numeric value
            raw_input: Raw input string
            data_type: Data type ('text', 'number', 'formula', 'date')
            
        Returns:
            Dictionary with success status
        """
        try:
            import price_matrix_store
            
            success = price_matrix_store.set_cell_value(
                matrix_id=matrix_id,
                row_id=row_id,
                column_id=column_id,
                value=value,
                raw_input=raw_input,
                data_type=data_type
            )
            
            if success:
                return {
                    'success': True,
                    'message': f'Zellwert gesetzt: Zeile {row_id}, Spalte {column_id}'
                }
            else:
                return {
                    'success': False,
                    'error': 'Zellwert konnte nicht gesetzt werden'
                }
                
        except Exception as e:
            self.logger.exception(f"Error setting cell value: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ========================================================================
    # Caching
    # ========================================================================
    
    def clear_cache(self) -> Dict[str, Any]:
        """
        Clear price lookup cache
        
        Returns:
            Dictionary with success status
        """
        try:
            self._cache.clear()
            
            return {
                'success': True,
                'message': 'Cache wurde geleert'
            }
            
        except Exception as e:
            self.logger.exception(f"Error clearing cache: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        return {
            'cache_size': len(self._cache),
            'cache_keys': list(self._cache.keys())
        }


# Singleton instance
_pricing_service_instance = None


def get_pricing_service() -> PricingService:
    """Get singleton instance of PricingService"""
    global _pricing_service_instance
    if _pricing_service_instance is None:
        _pricing_service_instance = PricingService()
    return _pricing_service_instance
