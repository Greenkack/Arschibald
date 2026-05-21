#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('crm_database.db')
cursor = conn.cursor()

# Alle Tabellen anzeigen
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Verfügbare Tabellen:')
for table in tables:
    print(f'  {table[0]}')

# Struktur der Settings-Tabelle anzeigen
for table_name in [
        t[0] for t in tables if 'settings' in t[0].lower() or 'admin' in t[0].lower()]:
    print(f'\nTabelle: {table_name}')
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        print(f'  {col[1]} ({col[2]})')

conn.close()
