#!/usr/bin/env python3
"""
Migration: Fügt profile_image Spalte zur users Tabelle hinzu
"""
import os
import sqlite3

db_path = 'data/users.db'

if not os.path.exists(db_path):
    print("❌ Datenbank nicht gefunden!")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Prüfe ob Spalte bereits existiert
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'profile_image' in columns:
        print("✅ Spalte 'profile_image' existiert bereits!")
    else:
        # Füge Spalte hinzu
        cursor.execute("ALTER TABLE users ADD COLUMN profile_image TEXT")
        conn.commit()
        print("✅ Spalte 'profile_image' erfolgreich hinzugefügt!")

    conn.close()

except Exception as e:
    print(f"❌ Fehler: {str(e)}")
