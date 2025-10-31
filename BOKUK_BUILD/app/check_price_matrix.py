#!/usr/bin/env python3
"""Prüft ob Preismatrizen in der Datenbank vorhanden sind"""

import os
import sqlite3

db_path = os.path.join('data', 'app_data.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("PREISMATRIX-TABELLEN")
print("=" * 80)

# Prüfe price_matrix_sets
cursor.execute("SELECT COUNT(*) FROM price_matrix_sets WHERE is_active = 1")
active_matrices = cursor.fetchone()[0]
print(f"Aktive Preismatrix-Sets: {active_matrices}")

cursor.execute("SELECT COUNT(*) FROM price_matrix_cells")
matrix_cells = cursor.fetchone()[0]
print(f"Preismatrix-Zellen: {matrix_cells}")

cursor.execute("SELECT COUNT(*) FROM price_matrix_rows")
matrix_rows = cursor.fetchone()[0]
print(f"Preismatrix-Zeilen: {matrix_rows}")

cursor.execute("SELECT COUNT(*) FROM price_matrix_columns")
matrix_cols = cursor.fetchone()[0]
print(f"Preismatrix-Spalten: {matrix_cols}")

if active_matrices == 0 and matrix_cells == 0:
    print("\n⚠️  KEINE PREISMATRIZEN VORHANDEN!")
    print("   → Berechnungen MÜSSEN Produktpreise aus DB verwenden!")
else:
    print(f"\n✓ Preismatrizen vorhanden: {active_matrices} aktive Sets")

conn.close()
