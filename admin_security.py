"""
Admin Security System - Passwortschutz für Admin-Bereiche
Ermöglicht passwortgeschützte Admin-Bereiche mit Admin-User-Authentifizierung
"""
import hashlib
import streamlit as st
from typing import Optional, Callable, Any
import database


def hash_password(password: str) -> str:
    """Hasht ein Passwort mit SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def is_owner(username: str, password: str) -> bool:
    """
    Prüft ob es der Besitzer ist (Bypass für alle Sicherheitschecks)
    
    Args:
        username: Benutzername
        password: Passwort
    
    Returns:
        bool: True wenn Besitzer
    """
    # Besitzer-Credentials (hardcoded für direkten Zugriff)
    OWNER_USERNAME = "TSchwarz"
    OWNER_PASSWORD = "Timur2014"
    
    return username == OWNER_USERNAME and password == OWNER_PASSWORD


def verify_admin_password(username: str, password: str) -> bool:
    """
    Verifiziert Admin-Passwort gegen Datenbank
    
    Args:
        username: Admin-Benutzername
        password: Eingegebenes Passwort
    
    Returns:
        bool: True wenn Passwort korrekt
    """
    # Besitzer-Bypass (hat immer Zugriff)
    if is_owner(username, password):
        return True
    
    try:
        conn = database.get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT password_hash, is_admin 
            FROM users 
            WHERE username = ? AND is_admin = 1
        """, (username,))
        
        result = cursor.fetchone()
        
        if not result:
            return False
        
        stored_hash, is_admin = result
        
        # Wenn kein Hash gespeichert, vergleiche Klartext (Legacy-Support)
        if not stored_hash:
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            plain_pw = cursor.fetchone()
            if plain_pw:
                return plain_pw[0] == password
            return False
        
        # Vergleiche Hashes
        input_hash = hash_password(password)
        return stored_hash == input_hash
        
    except Exception as e:
        st.error(f"Fehler bei Passwort-Verifizierung: {e}")
        return False


def get_admin_protected_areas() -> dict[str, bool]:
    """
    Lädt die konfigurierten geschützten Admin-Bereiche
    
    Returns:
        dict: {bereich_id: True/False} - Welche Bereiche geschützt sind
    """
    default_areas = {
        'build_infos': True,  # Build Infos immer geschützt
        'user_management': False,
        'company_management': False,
        'product_database': False,
        'economic_settings': False,
        'ui_customization': False,
        'logo_management': False,
        'intro_settings': False,
        'payment_terms': False,
        'services_management': False,
        'pdf_settings': False,
    }
    
    # Lade aus Session State oder Datenbank
    if 'admin_protected_areas' in st.session_state:
        return st.session_state.admin_protected_areas
    
    try:
        conn = database.get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT setting_value 
                FROM admin_settings 
                WHERE setting_key = 'protected_admin_areas'
            """)
            result = cursor.fetchone()
            
            if result and result[0]:
                import json
                loaded_areas = json.loads(result[0])
                # Merge mit defaults
                for key in default_areas:
                    if key not in loaded_areas:
                        loaded_areas[key] = default_areas[key]
                st.session_state.admin_protected_areas = loaded_areas
                return loaded_areas
    except Exception:
        pass
    
    st.session_state.admin_protected_areas = default_areas
    return default_areas


def save_admin_protected_areas(protected_areas: dict[str, bool]) -> bool:
    """
    Speichert die Konfiguration der geschützten Bereiche
    
    Args:
        protected_areas: Dictionary mit Bereich-IDs und Schutz-Status
    
    Returns:
        bool: True bei Erfolg
    """
    try:
        import json
        conn = database.get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Upsert
        cursor.execute("""
            INSERT OR REPLACE INTO admin_settings (setting_key, setting_value)
            VALUES ('protected_admin_areas', ?)
        """, (json.dumps(protected_areas),))
        
        conn.commit()
        st.session_state.admin_protected_areas = protected_areas
        return True
        
    except Exception as e:
        st.error(f"Fehler beim Speichern der Schutz-Konfiguration: {e}")
        return False


def require_admin_auth(area_id: str, area_name: str = None) -> bool:
    """
    Prüft ob Admin-Authentifizierung erforderlich ist und zeigt Login-Dialog
    
    Args:
        area_id: Eindeutige ID des Bereichs
        area_name: Anzeigename des Bereichs (optional)
    
    Returns:
        bool: True wenn Zugriff gewährt, False wenn gesperrt
    """
    if not area_name:
        area_name = area_id.replace('_', ' ').title()
    
    # Prüfe ob Bereich geschützt ist
    protected_areas = get_admin_protected_areas()
    if not protected_areas.get(area_id, False):
        return True  # Nicht geschützt, Zugriff erlaubt
    
    # Prüfe ob bereits authentifiziert
    auth_key = f'admin_auth_{area_id}'
    if st.session_state.get(auth_key, False):
        return True  # Bereits authentifiziert
    
    # Zeige Login-Dialog
    st.warning(f"🔒 Der Bereich **{area_name}** ist passwortgeschützt.")
    st.info("Bitte geben Sie Ihre Admin-Zugangsdaten ein:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        username = st.text_input(
            "Admin-Benutzername",
            key=f"{area_id}_username",
            placeholder="admin"
        )
    
    with col2:
        password = st.text_input(
            "Admin-Passwort",
            type="password",
            key=f"{area_id}_password",
            placeholder="Passwort eingeben"
        )
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        if st.button("🔓 Entsperren", key=f"{area_id}_unlock", type="primary"):
            if username and password:
                if verify_admin_password(username, password):
                    st.session_state[auth_key] = True
                    st.session_state[f'{auth_key}_user'] = username
                    st.success(f"✅ Zugriff gewährt für {username}")
                    st.rerun()
                else:
                    st.error("❌ Ungültiger Benutzername oder Passwort!")
            else:
                st.warning("⚠️ Bitte Benutzername und Passwort eingeben!")
    
    with col_btn2:
        if st.button("🚪 Abbrechen", key=f"{area_id}_cancel"):
            st.info("Zugriff verweigert. Kehre zurück...")
            return False
    
    return False  # Zugriff noch nicht gewährt


def render_admin_security_settings():
    """Rendert die Admin-Security-Einstellungen im Admin-Panel"""
    st.subheader("🔐 Sicherheitseinstellungen")
    
    st.markdown("""
    Hier können Sie festlegen, welche Admin-Bereiche ein Passwort erfordern.
    Nur Administratoren mit gültigem Passwort können diese Bereiche dann öffnen.
    """)
    
    protected_areas = get_admin_protected_areas()
    
    area_labels = {
        'build_infos': '📋 Build Infos & Dokumentation',
        'user_management': '👥 Benutzerverwaltung',
        'company_management': '🏢 Firmenverwaltung',
        'product_database': '📦 Produktdatenbank',
        'economic_settings': '💰 Wirtschaftlichkeitseinstellungen',
        'ui_customization': '🎨 UI-Anpassungen',
        'logo_management': '🖼️ Logo-Verwaltung',
        'intro_settings': '📝 Intro-Einstellungen',
        'payment_terms': '💳 Zahlungsbedingungen',
        'services_management': '🔧 Dienstleistungsverwaltung',
        'pdf_settings': '📄 PDF-Einstellungen',
    }
    
    st.write("### Geschützte Bereiche konfigurieren")
    
    changed = False
    new_areas = protected_areas.copy()
    
    col1, col2 = st.columns(2)
    
    for idx, (area_id, area_label) in enumerate(area_labels.items()):
        col = col1 if idx % 2 == 0 else col2
        
        with col:
            current_value = protected_areas.get(area_id, False)
            new_value = st.checkbox(
                area_label,
                value=current_value,
                key=f"protect_{area_id}",
                help=f"Aktivieren um {area_label} mit Passwort zu schützen"
            )
            
            if new_value != current_value:
                new_areas[area_id] = new_value
                changed = True
    
    if changed:
        st.divider()
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            if st.button("💾 Änderungen speichern", type="primary", use_container_width=True):
                if save_admin_protected_areas(new_areas):
                    st.success("✅ Sicherheitseinstellungen gespeichert!")
                    st.rerun()
                else:
                    st.error("❌ Fehler beim Speichern!")
        
        with col_cancel:
            if st.button("↩️ Abbrechen", use_container_width=True):
                st.rerun()
    
    # Aktuelle Authentifizierungen anzeigen
    st.divider()
    st.write("### 🔓 Aktive Sitzungen")
    
    active_auths = []
    for key in st.session_state.keys():
        if key.startswith('admin_auth_') and st.session_state.get(key):
            area = key.replace('admin_auth_', '')
            user = st.session_state.get(f'{key}_user', 'Unbekannt')
            active_auths.append((area, user))
    
    if active_auths:
        for area, user in active_auths:
            area_name = area_labels.get(area, area)
            col_info, col_logout = st.columns([3, 1])
            with col_info:
                st.info(f"✅ {area_name} - Authentifiziert als: **{user}**")
            with col_logout:
                if st.button("🚪 Abmelden", key=f"logout_{area}"):
                    del st.session_state[f'admin_auth_{area}']
                    if f'admin_auth_{area}_user' in st.session_state:
                        del st.session_state[f'admin_auth_{area}_user']
                    st.success(f"Abgemeldet von {area_name}")
                    st.rerun()
    else:
        st.info("Keine aktiven Authentifizierungen")
