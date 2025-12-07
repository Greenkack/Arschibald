#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DIAGNOSE: Finde doppelte Modellnamen
"""

from product_db import get_db_connection

def main():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("=" * 80)
    print("DIAGNOSE: Doppelte Modellnamen in Datenbank")
    print("=" * 80)
    
    # Finde Modellnamen die mehrfach vorkommen
    cursor.execute("""
        SELECT model_name, COUNT(*) as count
        FROM products
        WHERE category LIKE '%Wärmepumpe%'
        GROUP BY model_name
        HAVING count > 1
        ORDER BY count DESC
        LIMIT 20
    """)
    
    duplicates = cursor.fetchall()
    
    print(f"\n📋 Doppelte Modellnamen: {len(duplicates)}")
    
    if duplicates:
        print("\nBeispiele:")
        for model, count in duplicates[:10]:
            print(f"  '{model}': {count}x")
            
            # Zeige welche Hersteller
            cursor.execute("""
                SELECT manufacturer
                FROM products
                WHERE model_name = ?
            """, (model,))
            
            mfrs = [row[0] for row in cursor.fetchall()]
            print(f"    Hersteller: {', '.join(mfrs)}")
    
    # Prüfe spezifische Modelle
    print("\n" + "=" * 80)
    print("SPEZIFISCHE MODELLE:")
    print("=" * 80)
    
    test_models = ["3868354", "350G", "Vitocal 350-G"]
    
    for model in test_models:
        cursor.execute("""
            SELECT manufacturer, model_name
            FROM products
            WHERE model_name LIKE ?
            ORDER BY manufacturer
            LIMIT 5
        """, (f"%{model}%",))
        
        results = cursor.fetchall()
        if results:
            print(f"\n'{model}':")
            for mfr, mdl in results:
                print(f"  {mfr}: {mdl}")
    
    conn.close()

if __name__ == "__main__":
    main()
