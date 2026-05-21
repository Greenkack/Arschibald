"""
Excel Integration - Product Pricing Integration

Integration zwischen Excel-Matrizen und Produktpreisen.
Ermöglicht die Berechnung von Produktpreisen aus Preismatrizen.
"""

from typing import Any, Dict, Optional, List
from dataclasses import dataclass

from price_matrix_store import (
    lookup_price,
    lookup_price_with_meta,
    get_matrix_full,
    get_active_matrix_id
)


@dataclass
class ProductPriceResult:
    """
    Ergebnis einer Produktpreis-Berechnung aus Matrix
    """
    base_price: Optional[float] = None
    accessories_price: float = 0.0
    misc_price: float = 0.0
    total_price: Optional[float] = None
    matrix_id: Optional[int] = None
    matrix_name: Optional[str] = None
    pricing_mode: str = 'pauschal'
    row_used: Optional[str] = None
    column_used: Optional[str] = None
    row_floor_source: Optional[str] = None
    error: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Prüft ob die Berechnung erfolgreich war"""
        return self.total_price is not None and self.error is None


def calculate_product_price_from_matrix(
    row_label: str,
    column_label: str,
    matrix_id: Optional[int] = None,
    accessories_price: float = 0.0,
    misc_price: float = 0.0
) -> ProductPriceResult:
    """
    Berechnet Produktpreis aus aktiver oder angegebener Matrix
    
    Args:
        row_label: Zeilen-Label (z.B. Modulanzahl "20")
        column_label: Spalten-Label (z.B. Speicher-Variante "10kWh")
        matrix_id: Optionale Matrix-ID (None = aktive Matrix)
        accessories_price: Optionaler Zubehör-Preis
        misc_price: Optionaler Sonstiges-Preis
    
    Returns:
        ProductPriceResult mit berechneten Preisen und Metadaten
    
    Examples:
        >>> # Einfache Berechnung aus aktiver Matrix
        >>> result = calculate_product_price_from_matrix("20", "10kWh")
        >>> if result.is_valid():
        ...     print(f"Preis: {result.total_price}€")
        
        >>> # Mit Zubehör im Additiv-Modus
        >>> result = calculate_product_price_from_matrix(
        ...     "20", "10kWh",
        ...     accessories_price=500.0
        ... )
    """
    result = ProductPriceResult()
    
    try:
        # Bestimme Matrix-ID
        if matrix_id is None:
            matrix_id = get_active_matrix_id()
            if matrix_id is None:
                result.error = "Keine aktive Matrix gefunden"
                return result
        
        result.matrix_id = matrix_id
        
        # Lade Matrix-Metadaten
        matrix_data = get_matrix_full(matrix_id)
        if not matrix_data:
            result.error = f"Matrix mit ID {matrix_id} nicht gefunden"
            return result
        
        result.matrix_name = matrix_data['meta']['name']
        result.pricing_mode = matrix_data['meta'].get('pricing_mode', 'pauschal')
        
        # Lookup Preis mit Metadaten
        lookup_result = lookup_price_with_meta(matrix_id, row_label, column_label)
        
        if lookup_result['value'] is None:
            result.error = f"Kein Preis gefunden für Zeile '{row_label}', Spalte '{column_label}'"
            return result
        
        result.base_price = lookup_result['value']
        result.row_used = lookup_result['row_used']
        result.column_used = lookup_result['column_used']
        result.row_floor_source = lookup_result['row_floor_source']
        
        # Berechne Gesamtpreis basierend auf Pricing-Modus
        if result.pricing_mode == 'pauschal':
            # Pauschal-Modus: Nur Basis-Preis
            result.total_price = result.base_price
            
        elif result.pricing_mode == 'additiv':
            # Additiv-Modus: Basis + Zubehör + Sonstiges
            include_accessories = matrix_data['meta'].get('include_accessories', True)
            include_misc = matrix_data['meta'].get('include_misc', True)
            
            result.total_price = result.base_price
            
            if include_accessories:
                result.accessories_price = accessories_price
                result.total_price += accessories_price
            
            if include_misc:
                result.misc_price = misc_price
                result.total_price += misc_price
        else:
            # Unbekannter Modus: Nur Basis-Preis
            result.total_price = result.base_price
        
        return result
        
    except Exception as e:
        result.error = f"Fehler bei Preisberechnung: {str(e)}"
        return result


def calculate_product_price_for_product(
    product_id: int,
    row_label: str,
    column_label: str,
    matrix_id: Optional[int] = None
) -> ProductPriceResult:
    """
    Berechnet Produktpreis aus Matrix mit Produkt-Kontext
    
    Diese Funktion lädt automatisch Zubehör- und Sonstiges-Preise
    aus der Produktdatenbank und berücksichtigt diese bei der Berechnung.
    
    Args:
        product_id: Produkt-ID
        row_label: Zeilen-Label (z.B. Modulanzahl)
        column_label: Spalten-Label (z.B. Speicher-Variante)
        matrix_id: Optionale Matrix-ID (None = aktive Matrix)
    
    Returns:
        ProductPriceResult mit berechneten Preisen
    
    Examples:
        >>> result = calculate_product_price_for_product(
        ...     product_id=123,
        ...     row_label="20",
        ...     column_label="10kWh"
        ... )
    """
    try:
        from product_db import get_product_by_id
        
        # Lade Produkt
        product = get_product_by_id(product_id)
        if not product:
            result = ProductPriceResult()
            result.error = f"Produkt mit ID {product_id} nicht gefunden"
            return result
        
        # Extrahiere Zubehör- und Sonstiges-Preise
        accessories_price = float(product.get('accessories_price', 0.0) or 0.0)
        misc_price = float(product.get('misc_price', 0.0) or 0.0)
        
        # Berechne Preis
        return calculate_product_price_from_matrix(
            row_label=row_label,
            column_label=column_label,
            matrix_id=matrix_id,
            accessories_price=accessories_price,
            misc_price=misc_price
        )
        
    except ImportError:
        result = ProductPriceResult()
        result.error = "product_db Modul nicht verfügbar"
        return result
    except Exception as e:
        result = ProductPriceResult()
        result.error = f"Fehler beim Laden des Produkts: {str(e)}"
        return result


def get_price_preview(
    matrix_id: Optional[int] = None,
    row_labels: Optional[List[str]] = None,
    column_labels: Optional[List[str]] = None,
    max_rows: int = 10,
    max_cols: int = 10
) -> Dict[str, Any]:
    """
    Erstellt eine Vorschau der Preise aus einer Matrix
    
    Args:
        matrix_id: Matrix-ID (None = aktive Matrix)
        row_labels: Optionale Liste von Zeilen-Labels (None = alle)
        column_labels: Optionale Liste von Spalten-Labels (None = alle)
        max_rows: Maximale Anzahl Zeilen in Vorschau
        max_cols: Maximale Anzahl Spalten in Vorschau
    
    Returns:
        Dictionary mit Vorschau-Daten:
        {
            'matrix_id': int,
            'matrix_name': str,
            'pricing_mode': str,
            'rows': List[str],
            'columns': List[str],
            'prices': Dict[Tuple[str, str], float],
            'truncated': bool
        }
    
    Examples:
        >>> preview = get_price_preview()
        >>> print(f"Matrix: {preview['matrix_name']}")
        >>> for row in preview['rows']:
        ...     for col in preview['columns']:
        ...         price = preview['prices'].get((row, col))
        ...         print(f"{row} x {col}: {price}€")
    """
    try:
        # Bestimme Matrix-ID
        if matrix_id is None:
            matrix_id = get_active_matrix_id()
            if matrix_id is None:
                return {
                    'error': 'Keine aktive Matrix gefunden',
                    'matrix_id': None,
                    'matrix_name': None,
                    'pricing_mode': None,
                    'rows': [],
                    'columns': [],
                    'prices': {},
                    'truncated': False
                }
        
        # Lade Matrix
        matrix_data = get_matrix_full(matrix_id)
        if not matrix_data:
            return {
                'error': f'Matrix mit ID {matrix_id} nicht gefunden',
                'matrix_id': matrix_id,
                'matrix_name': None,
                'pricing_mode': None,
                'rows': [],
                'columns': [],
                'prices': {},
                'truncated': False
            }
        
        # Extrahiere Zeilen und Spalten
        all_rows = [r['label'] for r in matrix_data['rows']]
        all_cols = [c['label'] for c in matrix_data['columns']]
        
        # Filtere oder limitiere
        if row_labels:
            rows = [r for r in all_rows if r in row_labels][:max_rows]
        else:
            rows = all_rows[:max_rows]
        
        if column_labels:
            cols = [c for c in all_cols if c in column_labels][:max_cols]
        else:
            cols = all_cols[:max_cols]
        
        # Erstelle Preis-Dictionary
        prices = {}
        for row in rows:
            for col in cols:
                price = lookup_price(matrix_id, row, col)
                if price is not None:
                    prices[(row, col)] = price
        
        return {
            'matrix_id': matrix_id,
            'matrix_name': matrix_data['meta']['name'],
            'pricing_mode': matrix_data['meta'].get('pricing_mode', 'pauschal'),
            'rows': rows,
            'columns': cols,
            'prices': prices,
            'truncated': len(all_rows) > max_rows or len(all_cols) > max_cols
        }
        
    except Exception as e:
        return {
            'error': f'Fehler bei Vorschau-Erstellung: {str(e)}',
            'matrix_id': matrix_id,
            'matrix_name': None,
            'pricing_mode': None,
            'rows': [],
            'columns': [],
            'prices': {},
            'truncated': False
        }


def validate_matrix_for_product_pricing(matrix_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Validiert ob eine Matrix für Produktpreis-Berechnung geeignet ist
    
    Args:
        matrix_id: Matrix-ID (None = aktive Matrix)
    
    Returns:
        Dictionary mit Validierungs-Ergebnis:
        {
            'valid': bool,
            'errors': List[str],
            'warnings': List[str],
            'info': Dict[str, Any]
        }
    
    Examples:
        >>> validation = validate_matrix_for_product_pricing()
        >>> if validation['valid']:
        ...     print("Matrix ist bereit für Produktpreise")
        >>> else:
        ...     for error in validation['errors']:
        ...         print(f"Fehler: {error}")
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'info': {}
    }
    
    try:
        # Bestimme Matrix-ID
        if matrix_id is None:
            matrix_id = get_active_matrix_id()
            if matrix_id is None:
                result['valid'] = False
                result['errors'].append('Keine aktive Matrix gefunden')
                return result
        
        # Lade Matrix
        matrix_data = get_matrix_full(matrix_id)
        if not matrix_data:
            result['valid'] = False
            result['errors'].append(f'Matrix mit ID {matrix_id} nicht gefunden')
            return result
        
        result['info']['matrix_id'] = matrix_id
        result['info']['matrix_name'] = matrix_data['meta']['name']
        result['info']['pricing_mode'] = matrix_data['meta'].get('pricing_mode', 'pauschal')
        
        # Prüfe ob Matrix Zeilen hat
        if not matrix_data['rows']:
            result['valid'] = False
            result['errors'].append('Matrix hat keine Zeilen')
        else:
            result['info']['row_count'] = len(matrix_data['rows'])
        
        # Prüfe ob Matrix Spalten hat
        if not matrix_data['columns']:
            result['valid'] = False
            result['errors'].append('Matrix hat keine Spalten')
        else:
            result['info']['column_count'] = len(matrix_data['columns'])
        
        # Prüfe ob Matrix Werte hat
        if not matrix_data['cells']:
            result['warnings'].append('Matrix hat keine Werte')
        else:
            result['info']['cell_count'] = len(matrix_data['cells'])
            
            # Zähle leere Zellen
            empty_cells = sum(
                1 for cell_data in matrix_data['cells'].values()
                if cell_data.get('value') is None
            )
            if empty_cells > 0:
                result['warnings'].append(
                    f'{empty_cells} Zellen haben keine Werte'
                )
        
        # Prüfe Zeilen-Labels (sollten numerisch oder eindeutig sein)
        row_labels = [r['label'] for r in matrix_data['rows']]
        if len(row_labels) != len(set(row_labels)):
            result['warnings'].append('Zeilen-Labels sind nicht eindeutig')
        
        # Prüfe Spalten-Labels (sollten eindeutig sein)
        col_labels = [c['label'] for c in matrix_data['columns']]
        if len(col_labels) != len(set(col_labels)):
            result['warnings'].append('Spalten-Labels sind nicht eindeutig')
        
        return result
        
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f'Fehler bei Validierung: {str(e)}')
        return result


__all__ = [
    'ProductPriceResult',
    'calculate_product_price_from_matrix',
    'calculate_product_price_for_product',
    'get_price_preview',
    'validate_matrix_for_product_pricing'
]
