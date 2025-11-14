"""
Ensure Knowledge Base Tables Exist

Dieses Skript stellt sicher, dass die Wissensdatenbank-Tabellen existieren.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database import get_db_connection, create_knowledge_base_tables

def main():
    print("Überprüfe Wissensdatenbank-Tabellen...")
    
    conn = get_db_connection()
    if not conn:
        print("[ERROR] Keine Datenbankverbindung möglich")
        return 1
    
    cursor = conn.cursor()
    
    # Prüfe ob Tabellen existieren
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kb_articles'")
    if cursor.fetchone():
        print("[OK] Wissensdatenbank-Tabellen existieren bereits")
        conn.close()
        return 0
    
    # Tabellen erstellen
    print("[PACKAGE] Erstelle Wissensdatenbank-Tabellen...")
    try:
        create_knowledge_base_tables(conn)
        print("[OK] Wissensdatenbank-Tabellen erfolgreich erstellt!")
        conn.close()
        return 0
    except Exception as e:
        print(f"[ERROR] Fehler beim Erstellen der Tabellen: {e}")
        conn.close()
        return 1

if __name__ == "__main__":
    exit(main())
