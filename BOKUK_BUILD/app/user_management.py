"""
user_management.py
Zweck: Vollständiges Benutzerverwaltungssystem mit allen Funktionen
"""
import hashlib
import json
import secrets
import sqlite3
from datetime import datetime
from pathlib import Path


class UserManagement:
    """Vollständiges Benutzerverwaltungssystem"""

    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialisiert die Benutzerdatenbank"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Benutzer-Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT,
                email TEXT,
                phone TEXT,
                company_id INTEGER,
                rank TEXT DEFAULT 'Mitarbeiter',
                role TEXT DEFAULT 'user',
                permissions TEXT DEFAULT '{}',
                commission_rate REAL DEFAULT 0.0,
                status TEXT DEFAULT 'active',
                is_super_admin INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                notes TEXT
            )
        ''')

        # Super-Admin Rechteübertragung Tabelle
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

        # Super-Admin Rechteübertragung Tabelle
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

        # Neue Spalten zur users Tabelle hinzufügen (falls nicht vorhanden)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN phone_mobile TEXT")
        except sqlite3.OperationalError:
            pass  # Spalte existiert bereits

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN phone_extension TEXT")
        except sqlite3.OperationalError:
            pass  # Spalte existiert bereits

        try:
            cursor.execute(
                "ALTER TABLE users ADD COLUMN user_status TEXT DEFAULT 'Offline'")
        except sqlite3.OperationalError:
            pass  # Spalte existiert bereits

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN about_me TEXT")
        except sqlite3.OperationalError:
            pass  # Spalte existiert bereits

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN profile_image TEXT")
        except sqlite3.OperationalError:
            pass  # Spalte existiert bereits

        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            salt = secrets.token_hex(32)
            password_hash = self._hash_password("admin", salt)
            cursor.execute('''
                INSERT INTO users (username, password_hash, salt, full_name, rank, role, permissions, is_super_admin)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ("admin", password_hash, salt, "Administrator", "Administrator", "admin",
                  json.dumps({"all": True}), 0))

        conn.commit()
        conn.close()

    def _hash_password(self, password: str, salt: str) -> str:
        """Hasht ein Passwort mit Salt"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000).hex()

    def create_user(
            self,
            username: str,
            password: str,
            full_name: str = "",
            email: str = "",
            phone: str = "",
            company_id: int | None = None,
            rank: str = "Mitarbeiter",
            role: str = "user",
            permissions: dict = None,
            commission_rate: float = 0.0) -> int | None:
        """Erstellt einen neuen Benutzer"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            salt = secrets.token_hex(32)
            password_hash = self._hash_password(password, salt)

            if permissions is None:
                permissions = {}

            cursor.execute(
                '''
                INSERT INTO users (username, password_hash, salt, full_name, email, phone,
                                 company_id, rank, role, permissions, commission_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
                (username,
                 password_hash,
                 salt,
                 full_name,
                 email,
                 phone,
                 company_id,
                 rank,
                 role,
                 json.dumps(permissions),
                    commission_rate))

            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            return None

    def authenticate(self, username: str, password: str) -> dict | None:
        """Authentifiziert einen Benutzer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM users WHERE username = ? AND status = "active"', (username,))
        row = cursor.fetchone()

        if row:
            columns = [desc[0] for desc in cursor.description]
            user = dict(zip(columns, row))

            # Passwort prüfen
            password_hash = self._hash_password(password, user['salt'])
            if password_hash == user['password_hash']:
                # Letzten Login aktualisieren
                cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                               (datetime.now().isoformat(), user['id']))
                conn.commit()
                conn.close()

                # Passwort und Salt nicht zurückgeben
                del user['password_hash']
                del user['salt']
                user['permissions'] = json.loads(user['permissions'])
                return user

        conn.close()
        return None

    def get_user(self, user_id: int) -> dict | None:
        """Holt einen Benutzer nach ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()

        if row:
            columns = [desc[0] for desc in cursor.description]
            user = dict(zip(columns, row))
            del user['password_hash']
            del user['salt']
            user['permissions'] = json.loads(user['permissions'])
            conn.close()
            return user

        conn.close()
        return None

    def get_user_by_username(self, username: str) -> dict | None:
        """Holt einen Benutzer nach Benutzername"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()

        if row:
            columns = [desc[0] for desc in cursor.description]
            user = dict(zip(columns, row))
            del user['password_hash']
            del user['salt']
            user['permissions'] = json.loads(user['permissions'])
            conn.close()
            return user

        conn.close()
        return None

    def list_users(self, status: str = None) -> list[dict]:
        """Listet alle Benutzer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if status:
            cursor.execute(
                'SELECT * FROM users WHERE status = ? ORDER BY username', (status,))
        else:
            cursor.execute('SELECT * FROM users ORDER BY username')

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        users = []
        for row in rows:
            user = dict(zip(columns, row))
            del user['password_hash']
            del user['salt']
            user['permissions'] = json.loads(user['permissions'])
            users.append(user)

        conn.close()
        return users

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Aktualisiert Benutzerdaten"""
        allowed_fields = [
            'full_name',
            'email',
            'phone',
            'phone_mobile',
            'phone_extension',
            'company_id',
            'rank',
            'role',
            'permissions',
            'commission_rate',
            'status',
            'user_status',
            'notes',
            'about_me',
            'profile_image']

        updates = []
        values = []

        for key, value in kwargs.items():
            if key in allowed_fields:
                if key == 'permissions' and isinstance(value, dict):
                    value = json.dumps(value)
                updates.append(f"{key} = ?")
                values.append(value)

        if not updates:
            return False

        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(user_id)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)

            conn.commit()
            conn.close()
            return True
        except BaseException:
            return False

    def change_password(self, user_id: int, new_password: str) -> bool:
        """Ändert das Passwort eines Benutzers"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            salt = secrets.token_hex(32)
            password_hash = self._hash_password(new_password, salt)

            cursor.execute('''
                UPDATE users SET password_hash = ?, salt = ?, updated_at = ?
                WHERE id = ?
            ''', (password_hash, salt, datetime.now().isoformat(), user_id))

            conn.commit()
            conn.close()
            return True
        except BaseException:
            return False

    def delete_user(self, user_id: int, hard_delete: bool = False) -> bool:
        """Löscht einen Benutzer (soft oder hard delete)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if hard_delete:
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            else:
                cursor.execute(
                    'UPDATE users SET status = "deleted" WHERE id = ?', (user_id,))

            conn.commit()
            conn.close()
            return True
        except BaseException:
            return False

    def promote_user(self, user_id: int, new_rank: str) -> bool:
        """Befördert einen Benutzer"""
        return self.update_user(
            user_id, rank=new_rank, notes=f"Befördert zu {new_rank} am {
                datetime.now().strftime('%d.%m.%Y')}")

    def demote_user(self, user_id: int, new_rank: str) -> bool:
        """Degradiert einen Benutzer"""
        return self.update_user(
            user_id, rank=new_rank, notes=f"Degradiert zu {new_rank} am {
                datetime.now().strftime('%d.%m.%Y')}")

    def terminate_user(self, user_id: int, reason: str = "") -> bool:
        """Kündigt einen Benutzer"""
        notes = f"Gekündigt am {datetime.now().strftime('%d.%m.%Y')}"
        if reason:
            notes += f" - Grund: {reason}"
        return self.update_user(user_id, status="terminated", notes=notes)

    def set_commission(self, user_id: int, commission_rate: float) -> bool:
        """Setzt die Provision für einen Benutzer"""
        return self.update_user(user_id, commission_rate=commission_rate)

    def set_permissions(self, user_id: int, permissions: dict) -> bool:
        """Setzt Berechtigungen für einen Benutzer"""
        return self.update_user(user_id, permissions=permissions)

    def export_users(self, filepath: str = "data/users_export.json") -> bool:
        """Exportiert alle Benutzer als JSON"""
        try:
            users = self.list_users()
            Path(filepath).parent.mkdir(exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2, ensure_ascii=False)
            return True
        except BaseException:
            return False

    def import_users(self, filepath: str, overwrite: bool = False) -> int:
        """Importiert Benutzer aus JSON"""
        try:
            with open(filepath, encoding='utf-8') as f:
                users = json.load(f)

            imported = 0
            for user in users:
                # Überspringe Admin beim Import
                if user.get('username') == 'admin':
                    continue

                existing = self.get_user_by_username(user['username'])

                if existing and not overwrite:
                    continue

                if existing and overwrite:
                    self.update_user(existing['id'],
                                     **{k: v for k,
                                        v in user.items() if k not in ['id',
                                                                       'username',
                                                                       'password_hash',
                                                                       'salt',
                                                                       'created_at']})
                    imported += 1
                else:
                    # Neuen Benutzer erstellen mit Standard-Passwort
                    self.create_user(
                        username=user['username'],
                        password="changeme123",  # Standard-Passwort
                        full_name=user.get('full_name', ''),
                        email=user.get('email', ''),
                        phone=user.get('phone', ''),
                        company_id=user.get('company_id'),
                        rank=user.get('rank', 'Mitarbeiter'),
                        role=user.get('role', 'user'),
                        permissions=user.get('permissions', {}),
                        commission_rate=user.get('commission_rate', 0.0)
                    )
                    imported += 1

            return imported
        except BaseException:
            return 0

    def get_statistics(self) -> dict:
        """Holt Benutzerstatistiken"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Gesamt
        cursor.execute('SELECT COUNT(*) FROM users')
        stats['total'] = cursor.fetchone()[0]

        # Nach Status
        cursor.execute('SELECT status, COUNT(*) FROM users GROUP BY status')
        stats['by_status'] = dict(cursor.fetchall())

        # Nach Rang
        cursor.execute('SELECT rank, COUNT(*) FROM users GROUP BY rank')
        stats['by_rank'] = dict(cursor.fetchall())

        # Nach Rolle
        cursor.execute('SELECT role, COUNT(*) FROM users GROUP BY role')
        stats['by_role'] = dict(cursor.fetchall())

        conn.close()
        return stats

    # ==================== SUPER-ADMIN FUNKTIONEN ====================

    def is_super_admin(self, user_id: int) -> bool:
        """Prüft ob ein Benutzer Super-Admin ist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT is_super_admin FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result and result[0] == 1

    def get_super_admin(self) -> dict | None:
        """Holt den aktuellen Super-Admin"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE is_super_admin = 1 AND status = "active"')
        row = cursor.fetchone()

        if row:
            columns = [desc[0] for desc in cursor.description]
            user = dict(zip(columns, row))
            del user['password_hash']
            del user['salt']
            user['permissions'] = json.loads(user['permissions'])
            conn.close()
            return user

        conn.close()
        return None

    def initiate_super_admin_transfer(self, from_user_id: int, to_user_id: int,
                                      current_password: str) -> str | None:
        """
        Initiiert eine Super-Admin-Rechteübertragung
        Erfordert aktuelles Passwort zur Bestätigung
        Gibt einen einmaligen Transfer-Code zurück
        """
        # Prüfe ob from_user Super-Admin ist
        if not self.is_super_admin(from_user_id):
            return None

        # Verifiziere Passwort
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT username, password_hash, salt FROM users WHERE id = ?', (from_user_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        username, stored_hash, salt = row
        password_hash = self._hash_password(current_password, salt)

        if password_hash != stored_hash:
            conn.close()
            return None

        # Generiere sicheren Transfer-Code (16-stellig)
        transfer_code = secrets.token_hex(8).upper()

        # Speichere Transfer-Anfrage
        expires_at = datetime.now().replace(hour=23, minute=59, second=59).isoformat()
        cursor.execute('''
            INSERT INTO super_admin_transfers
            (from_user_id, to_user_id, transfer_code, authorized_by, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (from_user_id, to_user_id, transfer_code, username, expires_at))

        conn.commit()
        conn.close()

        return transfer_code

    def complete_super_admin_transfer(
            self,
            to_user_id: int,
            transfer_code: str,
            new_password: str) -> bool:
        """
        Schließt eine Super-Admin-Rechteübertragung ab
        Erfordert Transfer-Code und neues Passwort vom Empfänger
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Prüfe Transfer-Code
        cursor.execute('''
            SELECT id, from_user_id, expires_at FROM super_admin_transfers
            WHERE to_user_id = ? AND transfer_code = ? AND status = 'pending'
        ''', (to_user_id, transfer_code))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return False

        transfer_id, from_user_id, expires_at = row

        # Prüfe Ablaufdatum
        if datetime.now() > datetime.fromisoformat(expires_at):
            cursor.execute(
                'UPDATE super_admin_transfers SET status = "expired" WHERE id = ?',
                (transfer_id,
                 ))
            conn.commit()
            conn.close()
            return False

        # Entferne Super-Admin vom alten Benutzer
        cursor.execute(
            'UPDATE users SET is_super_admin = 0 WHERE id = ?', (from_user_id,))

        # Setze neuen Super-Admin
        salt = secrets.token_hex(32)
        password_hash = self._hash_password(new_password, salt)
        cursor.execute('''
            UPDATE users
            SET is_super_admin = 1,
                password_hash = ?,
                salt = ?,
                role = 'admin',
                rank = 'Geschäftsführer',
                permissions = ?,
                updated_at = ?
            WHERE id = ?
        ''', (password_hash, salt, json.dumps({"all": True, "super_admin": True}),
              datetime.now().isoformat(), to_user_id))

        # Markiere Transfer als abgeschlossen
        cursor.execute('''
            UPDATE super_admin_transfers
            SET status = 'completed', completed_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), transfer_id))

        conn.commit()
        conn.close()
        return True

    def create_super_admin(self, username: str, password: str, full_name: str,
                           email: str = "", phone: str = "") -> int | None:
        """Erstellt einen Super-Admin - nur möglich wenn noch keiner existiert"""
        # Prüfe ob bereits ein Super-Admin existiert
        if self.get_super_admin():
            return None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        salt = secrets.token_hex(32)
        password_hash = self._hash_password(password, salt)

        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, salt, full_name, email, phone,
                                 rank, role, permissions, is_super_admin)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, salt, full_name, email, phone,
                  "Geschäftsführer", "admin",
                  json.dumps({"all": True, "super_admin": True}), 1))

            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
