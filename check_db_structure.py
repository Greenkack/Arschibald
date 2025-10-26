#!/usr/bin/env python3
"""Prüft die Datenbankstruktur"""

import os
import sqlite3

db_path = os.path.join('data', 'app_data.db')

if not os.path.exists(db_path):
    print(f"❌ Datenbank nicht gefunden: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Alle Tabellen auflisten
print("=" * 80)
print("TABELLEN IN DER DATENBANK")
print("=" * 80)
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    print(f"\n📊 Tabelle: {table_name}")

    # Anzahl Zeilen
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"   Zeilen: {count}")

    # Schema
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"   Spalten: {len(columns)}")
    for col in columns[:5]:  # Erste 5 Spalten
        print(f"     - {col[1]} ({col[2]})")
    if len(columns) > 5:
        print(f"     ... und {len(columns) - 5} weitere")

conn.close()
