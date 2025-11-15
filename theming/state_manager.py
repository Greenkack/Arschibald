"""
State Management System für Theme-Präferenzen

Dieses Modul implementiert ein robustes State-Management-System für Theme-Einstellungen
mit mehreren Backend-Optionen (Session State, Local Storage, Database).
"""

import streamlit as st
import json
import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
import logging


class StateBackend:
    """Basis-Klasse für State-Backends"""
    
    def save(self, user_id: str, theme_name: str) -> bool:
        """Speichert Theme-Präferenz"""
        raise NotImplementedError
    
    def load(self, user_id: str) -> Optional[str]:
        """Lädt Theme-Präferenz"""
        raise NotImplementedError
    
    def delete(self, user_id: str) -> bool:
        """Löscht Theme-Präferenz"""
        raise NotImplementedError
    
    def exists(self, user_id: str) -> bool:
        """Prüft ob Theme-Präferenz existiert"""
        raise NotImplementedError


class SessionStateBackend(StateBackend):
    """Session State Backend für Theme-Präferenzen"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def save(self, user_id: str, theme_name: str) -> bool:
        """Speichert Theme-Präferenz in Session State"""
        try:
            key = f'theme_preference_{user_id}'
            st.session_state[key] = {
                'theme_name': theme_name,
                'timestamp': datetime.now().isoformat(),
                'backend': 'session'
            }
            self.logger.debug(f"Saved theme '{theme_name}' for user '{user_id}' to session state")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save to session state: {e}")
            return False
    
    def load(self, user_id: str) -> Optional[str]:
        """Lädt Theme-Präferenz aus Session State"""
        try:
            key = f'theme_preference_{user_id}'
            data = st.session_state.get(key)
            if data and isinstance(data, dict):
                theme_name = data.get('theme_name')
                self.logger.debug(f"Loaded theme '{theme_name}' for user '{user_id}' from session state")
                return theme_name
            return None
        except Exception as e:
            self.logger.error(f"Failed to load from session state: {e}")
            return None
    
    def delete(self, user_id: str) -> bool:
        """Löscht Theme-Präferenz aus Session State"""
        try:
            key = f'theme_preference_{user_id}'
            if key in st.session_state:
                del st.session_state[key]
                self.logger.debug(f"Deleted theme preference for user '{user_id}' from session state")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete from session state: {e}")
            return False
    
    def exists(self, user_id: str) -> bool:
        """Prüft ob Theme-Präferenz in Session State existiert"""
        key = f'theme_preference_{user_id}'
        return key in st.session_state


class LocalStorageBackend(StateBackend):
    """Browser Local Storage Backend für Theme-Präferenzen"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._init_bridge()
    
    def _init_bridge(self):
        """Initialisiert JavaScript-Bridge für Local Storage"""
        # Erstelle Bridge-Key in Session State falls nicht vorhanden
        if 'ls_bridge_initialized' not in st.session_state:
            st.session_state.ls_bridge_initialized = True
            st.session_state.ls_data = {}
    
    def save(self, user_id: str, theme_name: str) -> bool:
        """Speichert Theme-Präferenz in Local Storage"""
        try:
            key = f'shadcn_theme_{user_id}'
            
            # JavaScript zum Speichern in Local Storage
            js_code = f"""
            <script>
            (function() {{
                try {{
                    const data = {{
                        theme_name: '{theme_name}',
                        timestamp: new Date().toISOString(),
                        backend: 'local_storage'
                    }};
                    localStorage.setItem('{key}', JSON.stringify(data));
                    
                    // Sende Event an andere Tabs
                    window.dispatchEvent(new StorageEvent('storage', {{
                        key: '{key}',
                        newValue: JSON.stringify(data),
                        url: window.location.href
                    }}));
                    
                    console.log('Theme saved to localStorage:', '{theme_name}');
                }} catch (e) {{
                    console.error('Failed to save to localStorage:', e);
                }}
            }})();
            </script>
            """
            
            st.components.v1.html(js_code, height=0)
            
            # Speichere auch in Session State als Backup
            st.session_state.ls_data[user_id] = theme_name
            
            self.logger.debug(f"Saved theme '{theme_name}' for user '{user_id}' to local storage")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save to local storage: {e}")
            return False
    
    def load(self, user_id: str) -> Optional[str]:
        """Lädt Theme-Präferenz aus Local Storage"""
        try:
            # Versuche zuerst aus Session State Bridge zu laden
            theme_name = st.session_state.ls_data.get(user_id)
            if theme_name:
                self.logger.debug(f"Loaded theme '{theme_name}' for user '{user_id}' from local storage bridge")
                return theme_name
            
            # Fallback: Lade via JavaScript beim nächsten Render
            key = f'shadcn_theme_{user_id}'
            
            # JavaScript zum Laden aus Local Storage
            js_code = f"""
            <script>
            (function() {{
                try {{
                    const data = localStorage.getItem('{key}');
                    if (data) {{
                        const parsed = JSON.parse(data);
                        console.log('Theme loaded from localStorage:', parsed.theme_name);
                        
                        // Sende an Streamlit via Query Parameter (Workaround)
                        // In Produktion würde man hier eine bessere Bridge verwenden
                    }}
                }} catch (e) {{
                    console.error('Failed to load from localStorage:', e);
                }}
            }})();
            </script>
            """
            
            st.components.v1.html(js_code, height=0)
            
            return None
        except Exception as e:
            self.logger.error(f"Failed to load from local storage: {e}")
            return None
    
    def delete(self, user_id: str) -> bool:
        """Löscht Theme-Präferenz aus Local Storage"""
        try:
            key = f'shadcn_theme_{user_id}'
            
            # JavaScript zum Löschen aus Local Storage
            js_code = f"""
            <script>
            (function() {{
                try {{
                    localStorage.removeItem('{key}');
                    console.log('Theme removed from localStorage');
                }} catch (e) {{
                    console.error('Failed to remove from localStorage:', e);
                }}
            }})();
            </script>
            """
            
            st.components.v1.html(js_code, height=0)
            
            # Lösche auch aus Session State Bridge
            if user_id in st.session_state.ls_data:
                del st.session_state.ls_data[user_id]
            
            self.logger.debug(f"Deleted theme preference for user '{user_id}' from local storage")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete from local storage: {e}")
            return False
    
    def exists(self, user_id: str) -> bool:
        """Prüft ob Theme-Präferenz in Local Storage existiert"""
        return user_id in st.session_state.ls_data
    
    def sync_listener(self):
        """Erstellt Storage Event Listener für Tab-Synchronisation"""
        js_code = """
        <script>
        (function() {
            // Listener für Storage Events (Tab-Synchronisation)
            window.addEventListener('storage', function(e) {
                if (e.key && e.key.startsWith('shadcn_theme_')) {
                    console.log('Theme changed in another tab:', e.newValue);
                    // Trigger Streamlit Rerun
                    window.location.reload();
                }
            });
            
            console.log('Local Storage sync listener initialized');
        })();
        </script>
        """
        st.components.v1.html(js_code, height=0)


class DatabaseBackend(StateBackend):
    """Datenbank Backend für Theme-Präferenzen"""
    
    def __init__(self, db_path: str = "theming/theme_preferences.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialisiert Datenbank-Tabelle"""
        try:
            # Erstelle Verzeichnis falls nicht vorhanden
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_theme_preferences (
                    user_id TEXT PRIMARY KEY,
                    theme_name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
            self.logger.debug(f"Database initialized at {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
    
    def save(self, user_id: str, theme_name: str, metadata: Optional[Dict] = None) -> bool:
        """Speichert Theme-Präferenz in Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute("""
                INSERT OR REPLACE INTO user_theme_preferences 
                (user_id, theme_name, created_at, updated_at, metadata)
                VALUES (?, ?, 
                    COALESCE((SELECT created_at FROM user_theme_preferences WHERE user_id = ?), ?),
                    ?, ?)
            """, (user_id, theme_name, user_id, now, now, metadata_json))
            
            conn.commit()
            conn.close()
            
            self.logger.debug(f"Saved theme '{theme_name}' for user '{user_id}' to database")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save to database: {e}")
            return False
    
    def load(self, user_id: str) -> Optional[str]:
        """Lädt Theme-Präferenz aus Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT theme_name FROM user_theme_preferences WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                theme_name = result[0]
                self.logger.debug(f"Loaded theme '{theme_name}' for user '{user_id}' from database")
                return theme_name
            
            return None
        except Exception as e:
            self.logger.error(f"Failed to load from database: {e}")
            return None
    
    def delete(self, user_id: str) -> bool:
        """Löscht Theme-Präferenz aus Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM user_theme_preferences WHERE user_id = ?
            """, (user_id,))
            
            conn.commit()
            conn.close()
            
            self.logger.debug(f"Deleted theme preference for user '{user_id}' from database")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete from database: {e}")
            return False
    
    def exists(self, user_id: str) -> bool:
        """Prüft ob Theme-Präferenz in Datenbank existiert"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 1 FROM user_theme_preferences WHERE user_id = ? LIMIT 1
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result is not None
        except Exception as e:
            self.logger.error(f"Failed to check existence in database: {e}")
            return False
    
    def get_all_preferences(self) -> List[Dict[str, Any]]:
        """Gibt alle Theme-Präferenzen zurück"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, theme_name, created_at, updated_at, metadata
                FROM user_theme_preferences
                ORDER BY updated_at DESC
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            preferences = []
            for row in results:
                preferences.append({
                    'user_id': row[0],
                    'theme_name': row[1],
                    'created_at': row[2],
                    'updated_at': row[3],
                    'metadata': json.loads(row[4]) if row[4] else None
                })
            
            return preferences
        except Exception as e:
            self.logger.error(f"Failed to get all preferences: {e}")
            return []


class ThemeStateManager:
    """
    Zentraler State Manager für Theme-Präferenzen
    
    Verwaltet Theme-Einstellungen über mehrere Backend-Optionen und
    implementiert Fallback-Mechanismen für maximale Zuverlässigkeit.
    """
    
    def __init__(
        self,
        backends: Optional[List[str]] = None,
        db_path: str = "theming/theme_preferences.db"
    ):
        """
        Initialisiert State Manager
        
        Args:
            backends: Liste der zu verwendenden Backends (default: ['session', 'local_storage'])
            db_path: Pfad zur Datenbank-Datei
        """
        self.logger = logging.getLogger(__name__)
        
        # Standard-Backends
        if backends is None:
            backends = ['session', 'local_storage']
        
        self.backend_names = backends
        
        # Initialisiere Backends
        self.backends: Dict[str, StateBackend] = {}
        
        if 'session' in backends:
            self.backends['session'] = SessionStateBackend()
        
        if 'local_storage' in backends:
            self.backends['local_storage'] = LocalStorageBackend()
        
        if 'database' in backends:
            self.backends['database'] = DatabaseBackend(db_path)
        
        self.logger.info(f"ThemeStateManager initialized with backends: {backends}")
    
    def save_theme_preference(
        self,
        user_id: str,
        theme_name: str,
        backends: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Speichert Theme-Präferenz in mehreren Backends
        
        Args:
            user_id: Benutzer-ID
            theme_name: Name des Themes
            backends: Liste der Backends (default: alle konfigurierten)
        
        Returns:
            Dict mit Backend-Namen und Erfolgs-Status
        """
        if backends is None:
            backends = self.backend_names
        
        results = {}
        
        for backend_name in backends:
            backend = self.backends.get(backend_name)
            if backend:
                success = backend.save(user_id, theme_name)
                results[backend_name] = success
                
                if success:
                    self.logger.info(
                        f"Saved theme '{theme_name}' for user '{user_id}' to {backend_name}"
                    )
                else:
                    self.logger.warning(
                        f"Failed to save theme '{theme_name}' for user '{user_id}' to {backend_name}"
                    )
            else:
                self.logger.warning(f"Backend '{backend_name}' not available")
                results[backend_name] = False
        
        return results
    
    def load_theme_preference(
        self,
        user_id: str,
        backends: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Lädt Theme-Präferenz aus Backends (in Reihenfolge)
        
        Args:
            user_id: Benutzer-ID
            backends: Liste der Backends in Prioritäts-Reihenfolge
        
        Returns:
            Theme-Name oder None
        """
        if backends is None:
            backends = self.backend_names
        
        for backend_name in backends:
            backend = self.backends.get(backend_name)
            if backend:
                theme_name = backend.load(user_id)
                if theme_name:
                    self.logger.info(
                        f"Loaded theme '{theme_name}' for user '{user_id}' from {backend_name}"
                    )
                    return theme_name
        
        self.logger.debug(f"No theme preference found for user '{user_id}'")
        return None
    
    def delete_theme_preference(
        self,
        user_id: str,
        backends: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Löscht Theme-Präferenz aus Backends
        
        Args:
            user_id: Benutzer-ID
            backends: Liste der Backends (default: alle konfigurierten)
        
        Returns:
            Dict mit Backend-Namen und Erfolgs-Status
        """
        if backends is None:
            backends = self.backend_names
        
        results = {}
        
        for backend_name in backends:
            backend = self.backends.get(backend_name)
            if backend:
                success = backend.delete(user_id)
                results[backend_name] = success
                
                if success:
                    self.logger.info(
                        f"Deleted theme preference for user '{user_id}' from {backend_name}"
                    )
        
        return results
    
    def sync_across_backends(self, user_id: str, source_backend: str) -> Dict[str, bool]:
        """
        Synchronisiert Theme-Präferenz über alle Backends
        
        Args:
            user_id: Benutzer-ID
            source_backend: Backend von dem synchronisiert wird
        
        Returns:
            Dict mit Backend-Namen und Erfolgs-Status
        """
        # Lade Theme aus Source-Backend
        source = self.backends.get(source_backend)
        if not source:
            self.logger.error(f"Source backend '{source_backend}' not found")
            return {}
        
        theme_name = source.load(user_id)
        if not theme_name:
            self.logger.warning(f"No theme found in source backend '{source_backend}'")
            return {}
        
        # Speichere in allen anderen Backends
        target_backends = [b for b in self.backend_names if b != source_backend]
        results = self.save_theme_preference(user_id, theme_name, target_backends)
        
        self.logger.info(
            f"Synced theme '{theme_name}' for user '{user_id}' from {source_backend} to {target_backends}"
        )
        
        return results
    
    def recover_state(self, user_id: str) -> Optional[str]:
        """
        Versucht State-Recovery bei Browser-Refresh
        
        Durchsucht alle Backends und gibt das erste gefundene Theme zurück.
        
        Args:
            user_id: Benutzer-ID
        
        Returns:
            Theme-Name oder None
        """
        self.logger.info(f"Attempting state recovery for user '{user_id}'")
        
        # Versuche in Reihenfolge: database -> local_storage -> session
        recovery_order = ['database', 'local_storage', 'session']
        
        for backend_name in recovery_order:
            if backend_name in self.backends:
                theme_name = self.backends[backend_name].load(user_id)
                if theme_name:
                    self.logger.info(
                        f"State recovered for user '{user_id}': theme '{theme_name}' from {backend_name}"
                    )
                    
                    # Synchronisiere zu anderen Backends
                    self.sync_across_backends(user_id, backend_name)
                    
                    return theme_name
        
        self.logger.warning(f"State recovery failed for user '{user_id}'")
        return None
    
    def get_backend_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Gibt Status aller Backends zurück
        
        Returns:
            Dict mit Backend-Status-Informationen
        """
        status = {}
        
        for backend_name, backend in self.backends.items():
            status[backend_name] = {
                'available': True,
                'type': type(backend).__name__
            }
        
        return status
    
    def enable_tab_sync(self):
        """Aktiviert Tab-Synchronisation für Local Storage Backend"""
        if 'local_storage' in self.backends:
            backend = self.backends['local_storage']
            if isinstance(backend, LocalStorageBackend):
                backend.sync_listener()
                self.logger.info("Tab synchronization enabled")
