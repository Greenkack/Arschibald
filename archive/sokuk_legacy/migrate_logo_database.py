# migrate_logo_database.py
"""
Migrations-Skript für die Logo-Datenbank
Fügt neue Spalten zur brand_logos Tabelle hinzu
"""

import sys


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


if __name__ == "__main__":
    print("🔄 LOGO-DATENBANK MIGRATION")
    print("=" * 40)

    success = migrate_logo_database()

    if success:
        print("\n🎉 Migration erfolgreich abgeschlossen!")

        # Teste die Migration
        print("\n🧪 Teste die Migration...")
        try:
            from brand_logo_db import add_brand_logo

            # Test-Logo hinzufügen
            test_logo_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAHdl6v5ygAAAABJRU5ErkJggg=="

            result = add_brand_logo(
                "MigrationTest",
                test_logo_b64,
                "PNG",
                file_size_bytes=100,
                position_x=100.0,
                position_y=200.0,
                width=60.0,
                height=30.0
            )

            if result:
                print("✅ Migration-Test erfolgreich!")
            else:
                print("❌ Migration-Test fehlgeschlagen!")

        except Exception as e:
            print(f"❌ Migration-Test Fehler: {e}")
    else:
        print("\n❌ Migration fehlgeschlagen!")
        sys.exit(1)
