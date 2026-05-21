#!/usr/bin/env python3
"""
Bereinigt und optimiert SQLite-Datenbanken
"""
import os
import sqlite3


def clean_database(db_path="solar_app.db"):
    """Bereinigt und optimiert die Datenbank"""

    if not os.path.exists(db_path):
        print(f"Datenbank {db_path} nicht gefunden")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Hole alle Tabellen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        print(f"🗄️ DATENBANK-BEREINIGUNG für {db_path}")
        print(f"Gefundene Tabellen: {len(tables)}")

        for (table_name,) in tables:
            # Zähle Einträge
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  📋 {table_name}: {count} Einträge")

            # Finde leere/null Einträge
            cursor.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE id IS NULL")
            null_count = cursor.fetchone()[0]
            if null_count > 0:
                print(f"    {null_count} NULL-Einträge gefunden")

        # VACUUM für Optimierung
        print("🧹 Führe VACUUM aus...")
        cursor.execute("VACUUM")

        # Analysiere für bessere Query-Performance
        print("Führe ANALYZE aus...")
        cursor.execute("ANALYZE")

        print("Datenbank-Bereinigung abgeschlossen!")

    except Exception as e:
        print(f"Fehler bei Datenbank-Bereinigung: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    clean_database()
