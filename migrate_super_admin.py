"""
migrate_super_admin.py
Fügt Super-Admin Spalte zur bestehenden Datenbank hinzu
"""
import sqlite3
from pathlib import Path


def migrate_database():
    """Migriert die Datenbank für Super-Admin Support"""
    db_path = Path("data/users.db")

    if not db_path.exists():
        print("❌ Datenbank nicht gefunden!")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Prüfe ob Spalte bereits existiert
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'is_super_admin' in columns:
            print("✅ Spalte 'is_super_admin' existiert bereits")
        else:
            # Füge Spalte hinzu
            cursor.execute(
                'ALTER TABLE users ADD COLUMN is_super_admin INTEGER DEFAULT 0')
            print("✅ Spalte 'is_super_admin' hinzugefügt")

        # Erstelle Super-Admin Transfer Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS super_admin_transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                transfer_code TEXT NOT NULL,
                authorized_by TEXT NOT NULL,
                authorized_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT,
                status TEXT DEFAULT 'pending',
                completed_at TEXT,
                FOREIGN KEY (from_user_id) REFERENCES users(id),
                FOREIGN KEY (to_user_id) REFERENCES users(id)
            )
        ''')
        print("✅ Tabelle 'super_admin_transfers' erstellt/geprüft")

        conn.commit()
        print("\n✅ Datenbank-Migration erfolgreich!")
        return True

    except Exception as e:
        print(f"❌ Fehler bei Migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_database()
