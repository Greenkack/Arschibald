#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Import aller Wärmepumpen aus heatpump_products_database.py in product_db.py
Damit können sie dem Kunden angeboten werden!
"""

from product_db import get_db_connection, get_product_by_model_name
from heatpump_products_database import HEATPUMP_PRODUCTS
import sqlite3

def import_heatpumps():
    """Importiert alle Wärmepumpen-Modelle in die Produktdatenbank"""
    
    print("=" * 80)
    print("IMPORT WAERMEPUMPEN IN PRODUKTDATENBANK")
    print("=" * 80)
    print()
    
    conn = get_db_connection()
    if not conn:
        print("[ERROR] Fehler: Konnte Datenbankverbindung nicht herstellen")
        return
    
    cursor = conn.cursor()
    
    imported = 0
    skipped = 0
    updated = 0
    
    for manufacturer, types in HEATPUMP_PRODUCTS.items():
        print(f"\nHersteller: {manufacturer}")
        
        for hp_type, models in types.items():
            print(f"  Typ: {hp_type}")
            
            for model in models:
                model_name = model.get("model", "Unknown")
                
                # Prüfe ob Produkt bereits existiert
                existing = get_product_by_model_name(model_name)
                
                if existing:
                    # Update existierendes Produkt
                    try:
                        cursor.execute("""
                            UPDATE products SET
                                category = ?,
                                manufacturer = ?,
                                description = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE model_name = ?
                        """, (
                            f"Wärmepumpe - {hp_type}",
                            manufacturer,
                            f"SCOP {model.get('scop', 0)} | Max. Vorlauf {model.get('max_flow_temp', 0)}°C | {model.get('refrigerant', '')}",
                            model_name
                        ))
                        conn.commit()
                        updated += 1
                        # print(f"    OK Aktualisiert: {model_name}")
                    except sqlite3.Error as e:
                        print(f"    FEHLER bei Update: {model_name} - {e}")
                        skipped += 1
                else:
                    # Neues Produkt einfügen
                    try:
                        # Erstelle Beschreibung mit allen wichtigen Daten
                        features_text = ", ".join(model.get('features', []))[:100]
                        awards_text = ", ".join(model.get('awards', []))[:100]
                        
                        description = f"SCOP {model.get('scop', 0)} | Max. Vorlauf {model.get('max_flow_temp', 0)}°C | {model.get('refrigerant', '')}"
                        if features_text:
                            description += f" | {features_text}"
                        if awards_text:
                            description += f" | {awards_text}"
                        
                        cursor.execute("""
                            INSERT INTO products (
                                model_name,
                                category,
                                manufacturer,
                                description,
                                price_euro,
                                rating,
                                created_at,
                                updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, (
                            model_name,
                            f"Wärmepumpe - {hp_type}",
                            manufacturer,
                            description[:500],  # SQLite TEXT limit
                            0.0,  # Preis wird in admin_heatpump_settings_ui.py konfiguriert
                            model.get('rating', 0.0)
                        ))
                        conn.commit()
                        imported += 1
                        # print(f"    OK Importiert: {model_name}")
                    except sqlite3.Error as e:
                        print(f"    FEHLER bei Import: {model_name} - {e}")
                        skipped += 1
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("IMPORT ABGESCHLOSSEN")
    print("=" * 80)
    print(f"Importiert:   {imported}")
    print(f"Aktualisiert: {updated}")
    print(f"Uebersprungen: {skipped}")
    print(f"GESAMT:       {imported + updated + skipped}")
    print("=" * 80)
    print()
    print("Jetzt koennen alle Waermepumpen dem Kunden angeboten werden!")
    print()

if __name__ == "__main__":
    import_heatpumps()
