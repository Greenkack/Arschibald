#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ENTFERNE ALLE WÄRMEPUMPEN AUSSER Viessmann, Buderus, Vaillant
"""

from product_db import get_db_connection

def main():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("=" * 80)
    print("WÄRMEPUMPEN-HERSTELLER IN DATENBANK")
    print("=" * 80)
    
    # Zeige alle Hersteller
    cursor.execute("""
        SELECT DISTINCT manufacturer, COUNT(*) as count
        FROM products 
        WHERE category LIKE '%Wärmepumpe%'
        GROUP BY manufacturer
        ORDER BY count DESC
    """)
    
    manufacturers = cursor.fetchall()
    
    print("\nVOR DEM LÖSCHEN:")
    total_before = 0
    for mfr, count in manufacturers:
        print(f"  {mfr}: {count} Produkte")
        total_before += count
    print(f"\nGESAMT: {total_before} Wärmepumpen")
    
    # ERLAUBTE Hersteller
    allowed = ['Viessmann', 'Buderus', 'Vaillant']
    
    print("\n" + "=" * 80)
    print("LÖSCHE ALLE HERSTELLER AUSSER:", ", ".join(allowed))
    print("=" * 80)
    
    # Lösche alle NICHT erlaubten Hersteller
    cursor.execute("""
        DELETE FROM products 
        WHERE category LIKE '%Wärmepumpe%'
        AND manufacturer NOT IN (?, ?, ?)
    """, allowed)
    
    deleted = cursor.rowcount
    conn.commit()
    
    print(f"\nGELÖSCHT: {deleted} Produkte")
    
    # Zeige was übrig bleibt
    print("\n" + "=" * 80)
    print("NACH DEM LÖSCHEN:")
    print("=" * 80)
    
    cursor.execute("""
        SELECT DISTINCT manufacturer, COUNT(*) as count
        FROM products 
        WHERE category LIKE '%Wärmepumpe%'
        GROUP BY manufacturer
        ORDER BY manufacturer
    """)
    
    remaining = cursor.fetchall()
    total_after = 0
    for mfr, count in remaining:
        print(f"  {mfr}: {count} Produkte")
        total_after += count
    
    print(f"\nGESAMT: {total_after} Wärmepumpen")
    print(f"\nNUR NOCH Viessmann, Buderus, Vaillant!")
    
    conn.close()

if __name__ == "__main__":
    main()
