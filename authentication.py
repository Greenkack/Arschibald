"""authentication.py - Authentication System"""
import hashlib
import secrets
from typing import Optional, Dict, Any
import sqlite3
from pathlib import Path

class AuthenticationManager:
    """Verwaltung von Benutzer-Authentifizierung"""
    
    def __init__(self, db_path: str = "data/app_data.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialisiere Datenbank-Tabellen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hashe Passwort mit Salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        
        return password_hash, salt
    
    def create_user(self, username: str, password: str, email: Optional[str] = None, role: str = 'user') -> bool:
        """Erstelle neuen Benutzer"""
        try:
            password_hash, salt = self.hash_password(password)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, salt, email, role) VALUES (?, ?, ?, ?, ?)",
                (username, password_hash, salt, email, role)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def verify_credentials(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verifiziere Benutzer-Credentials"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ? AND active = 1", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user is None:
            return None
        
        password_hash, _ = self.hash_password(password, user['salt'])
        
        if password_hash == user['password_hash']:
            return dict(user)
        
        return None
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Ändere Benutzer-Passwort"""
        user = self.verify_credentials(username, old_password)
        if user is None:
            return False
        
        password_hash, salt = self.hash_password(new_password)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ?, salt = ? WHERE username = ?",
            (password_hash, salt, username)
        )
        conn.commit()
        conn.close()
        return True
