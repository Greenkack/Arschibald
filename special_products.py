"""special_products.py

Modul zur Identifizierung und Verwaltung von Sonderprodukten für die Preismatrix-Berechnung.

Sonderprodukte sind Produkte, die im Preismatrix-Modus zusätzlich zum Basispreis
berechnet werden. Standardprodukte (Module, Wechselrichter, Speicher) sind bereits
im Basispreis enthalten und werden NICHT zusätzlich berechnet.

Beispiele für Sonderprodukte:
- Spezielle Montagesysteme
- Zusätzliche Optimierer
- Sonderausstattungen
- Zusatzkomponenten
"""

from typing import Any, Optional
import sqlite3


def get_db_connection():
    """Get database connection - imports from database.py"""
    try:
        from database import get_db_connection as get_conn
        return get_conn()
    except ImportError:
        return None


def is_special_product(product_id: int) -> bool:
    """
    Prüft ob ein Produkt als Sonderprodukt markiert ist.
    
    Args:
        product_id: ID des Produkts
        
    Returns:
        True wenn Produkt als Sonderprodukt markiert ist, sonst False
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT is_special_product FROM products WHERE id = ?",
            (product_id)
        )
        row = cursor.fetchone()
        
        if row and row[0]:
            return bool(row[0])
        return False
    except Exception as e:
        print(f"Fehler bei is_special_product: {e}")
        return False
    finally:
        conn.close()


def is_special_product_by_name(model_name: str) -> bool:
    """
    Prüft ob ein Produkt anhand des Modellnamens als Sonderprodukt markiert ist.
    
    Args:
        model_name: Modellname des Produkts
        
    Returns:
        True wenn Produkt als Sonderprodukt markiert ist, sonst False
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT is_special_product FROM products WHERE model_name = ?",
            (model_name)
        )
        row = cursor.fetchone()
        
        if row and row[0]:
            return bool(row[0])
        return False
    except Exception as e:
        print(f"Fehler bei is_special_product_by_name: {e}")
        return False
    finally:
        conn.close()


def get_special_products(category: Optional[str] = None) -> list[dict[str, Any]]:
    """
    Holt alle Sonderprodukte aus der Datenbank.
    
    Args:
        category: Optional - Filter nach Kategorie
        
    Returns:
        Liste von Sonderprodukt-Dictionaries
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT id, category, model_name, brand, price_euro, 
                       calculate_per, additional_cost_netto
                FROM products 
                WHERE is_special_product = 1 AND category = ?
                ORDER BY category, model_name
            """, (category))
        else:
            cursor.execute("""
                SELECT id, category, model_name, brand, price_euro,
                       calculate_per, additional_cost_netto
                FROM products 
                WHERE is_special_product = 1
                ORDER BY category, model_name
            """)
        
        rows = cursor.fetchall()
        
        products = []
        for row in rows:
            products.append({
                'id': row[0],
                'category': row[1],
                'model_name': row[2],
                'brand': row[3],
                'price_euro': row[4] or 0.0,
                'calculate_per': row[5],
                'additional_cost_netto': row[6] or 0.0
            })
        
        return products
    except Exception as e:
        print(f"Fehler bei get_special_products: {e}")
        return []
    finally:
        conn.close()


def mark_product_as_special(product_id: int, is_special: bool = True) -> bool:
    """
    Markiert ein Produkt als Sonderprodukt oder entfernt die Markierung.
    
    Args:
        product_id: ID des Produkts
        is_special: True um als Sonderprodukt zu markieren, False um Markierung zu entfernen
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET is_special_product = ? WHERE id = ?",
            (1 if is_special else 0, product_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Fehler bei mark_product_as_special: {e}")
        return False
    finally:
        conn.close()


def get_standard_product_categories() -> list[str]:
    """
    Gibt die Kategorien zurück, die als Standardprodukte gelten.
    
    Standardprodukte sind im Preismatrix-Basispreis enthalten und werden
    NICHT zusätzlich berechnet.
    
    Returns:
        Liste von Kategorie-Namen
    """
    return [
        'PV-Module',
        'Wechselrichter',
        'Batteriespeicher',
        'Speicher',
        'Storage'
    ]


def is_standard_product_category(category: str) -> bool:
    """
    Prüft ob eine Kategorie zu den Standardprodukten gehört.
    
    Args:
        category: Kategorie-Name
        
    Returns:
        True wenn Standardprodukt-Kategorie, sonst False
    """
    if not category:
        return False
    
    standard_categories = get_standard_product_categories()
    return category.strip() in standard_categories


def filter_special_products_from_selection(selected_products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Filtert Sonderprodukte aus einer Liste von ausgewählten Produkten.
    
    Diese Funktion wird verwendet, um im Preismatrix-Modus nur die Sonderprodukte
    zu identifizieren, die zusätzlich zum Basispreis berechnet werden sollen.
    
    Args:
        selected_products: Liste von Produkt-Dictionaries mit 'id' oder 'model_name'
        
    Returns:
        Liste von Sonderprodukt-Dictionaries
    """
    special_products = []
    
    for product in selected_products:
        # Prüfe anhand ID
        if 'id' in product and product['id']:
            if is_special_product(product['id']):
                special_products.append(product)
        # Fallback: Prüfe anhand Modellname
        elif 'model_name' in product and product['model_name']:
            if is_special_product_by_name(product['model_name']):
                special_products.append(product)
    
    return special_products


__all__ = [
    'is_special_product',
    'is_special_product_by_name',
    'get_special_products',
    'mark_product_as_special',
    'get_standard_product_categories',
    'is_standard_product_category',
    'filter_special_products_from_selection'
]
