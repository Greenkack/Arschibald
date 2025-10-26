# === AUTO-GENERATED INSERT PATCH ===
# target_module: migrate_logo_database.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func migrate_logo_database ---
def migrate_logo_database():
    """Führt die Datenbank-Migration für Logo-Tabelle durch"""
    try:
        from database import get_db_connection

        conn = get_db_connection()
        if not conn:
            print("❌ Keine Datenbankverbindung möglich")
            return False

        cursor = conn.cursor()

        # Prüfe welche Spalten bereits existieren
        cursor.execute("PRAGMA table_info(brand_logos)")
        existing_columns = [row[1] for row in cursor.fetchall()]

        print(f"Vorhandene Spalten: {existing_columns}")

        # Neue Spalten hinzufügen falls sie nicht existieren
        new_columns = [
            ("file_size_bytes", "INTEGER DEFAULT 0"),
            ("logo_position_x", "REAL DEFAULT 0"),
            ("logo_position_y", "REAL DEFAULT 0"),
            ("logo_width", "REAL DEFAULT 100"),
            ("logo_height", "REAL DEFAULT 50"),
            ("is_active", "INTEGER DEFAULT 1")
        ]

        added_columns = 0
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(
                        f"ALTER TABLE brand_logos ADD COLUMN {column_name} {column_def}")
                    print(f"✅ Spalte '{column_name}' hinzugefügt")
                    added_columns += 1
                except Exception as e:
                    print(
                        f"❌ Fehler beim Hinzufügen der Spalte '{column_name}': {e}")
            else:
                print(f"⏭️ Spalte '{column_name}' bereits vorhanden")

        conn.commit()
        conn.close()

        if added_columns > 0:
            print(
                f"✅ Migration abgeschlossen: {added_columns} neue Spalten hinzugefügt")
        else:
            print("✅ Migration nicht erforderlich: Alle Spalten bereits vorhanden")

        return True

    except Exception as e:
        print(f"❌ Migration fehlgeschlagen: {e}")
        return False
# --- DEF BLOCK END ---
