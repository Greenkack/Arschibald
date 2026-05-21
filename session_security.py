"""session_security.py - Session Security Management"""
import streamlit as st
import secrets
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class SessionSecurity:
    """Session-Sicherheitsverwaltung"""
    
    def __init__(self, session_timeout_minutes: int = 30):
        self.session_timeout = session_timeout_minutes * 60  # in Sekunden
        
        if 'session_token' not in st.session_state:
            st.session_state.session_token = None
        if 'session_start' not in st.session_state:
            st.session_state.session_start = None
        if 'last_activity' not in st.session_state:
            st.session_state.last_activity = None
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None
    
    def create_session(self, user_data: Dict[str, Any]) -> str:
        """Erstelle neue Session"""
        session_token = secrets.token_urlsafe(32)
        st.session_state.session_token = session_token
        st.session_state.session_start = time.time()
        st.session_state.last_activity = time.time()
        st.session_state.user_data = user_data
        return session_token
    
    def is_session_valid(self) -> bool:
        """Prüfe ob Session gültig ist"""
        if st.session_state.session_token is None:
            return False
        
        if st.session_state.last_activity is None:
            return False
        
        # Timeout-Prüfung
        time_since_activity = time.time() - st.session_state.last_activity
        if time_since_activity > self.session_timeout:
            self.destroy_session()
            return False
        
        # Activity-Timestamp aktualisieren
        st.session_state.last_activity = time.time()
        return True
    
    def destroy_session(self):
        """Zerstöre Session"""
        st.session_state.session_token = None
        st.session_state.session_start = None
        st.session_state.last_activity = None
        st.session_state.user_data = None
    
    def get_user_data(self) -> Optional[Dict[str, Any]]:
        """Hole Benutzerdaten"""
        if self.is_session_valid():
            return st.session_state.user_data
        return None
    
    def get_session_info(self) -> Dict[str, Any]:
        """Hole Session-Informationen"""
        if not self.is_session_valid():
            return {'active': False}
        
        session_duration = time.time() - st.session_state.session_start
        time_until_timeout = self.session_timeout - (time.time() - st.session_state.last_activity)
        
        return {
            'active': True,
            'token': st.session_state.session_token[:10] + '...',
            'duration_seconds': int(session_duration),
            'timeout_in_seconds': int(time_until_timeout),
            'user': st.session_state.user_data.get('username', 'Unknown') if st.session_state.user_data else None
        }
    
    def require_authentication(self):
        """Decorator für Authentication-Requirement"""
        if not self.is_session_valid():
            st.warning("⚠️ Sitzung abgelaufen. Bitte melden Sie sich erneut an.")
            st.stop()
