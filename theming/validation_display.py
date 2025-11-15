"""
Validation Display

Zeigt Theme-Validierungs-Fehler in Echtzeit an.
"""

from typing import List, Dict, Any, Optional
import streamlit as st
from datetime import datetime


class ValidationDisplay:
    """Zeigt Validierungs-Fehler in der UI an"""
    
    def __init__(self):
        """Initialisiert ValidationDisplay"""
        self.error_history: List[Dict[str, Any]] = []
        self.max_history = 50
    
    def show_validation_errors(
        self,
        theme_name: str,
        errors: List[str],
        warnings: List[str] = None
    ) -> None:
        """
        Zeigt Validierungs-Fehler in der UI an
        
        Args:
            theme_name: Name des Themes
            errors: Liste von Fehlermeldungen
            warnings: Liste von Warnungen (optional)
        """
        if warnings is None:
            warnings = []
        
        # Speichere in History
        self._add_to_history(theme_name, errors, warnings)
        
        # Zeige Fehler
        if errors:
            with st.expander(
                f"❌ Validierungs-Fehler in Theme '{theme_name}' ({len(errors)})",
                expanded=True
            ):
                st.error(
                    f"**Theme '{theme_name}' hat {len(errors)} Validierungs-Fehler:**"
                )
                
                for i, error in enumerate(errors, 1):
                    st.markdown(f"{i}. {error}")
                
                st.info(
                    "💡 **Tipp:** Behebe die Fehler in der Theme-Datei. "
                    "Das Theme wird automatisch neu geladen."
                )
        
        # Zeige Warnungen
        if warnings:
            with st.expander(
                f"⚠️ Warnungen in Theme '{theme_name}' ({len(warnings)})",
                expanded=False
            ):
                st.warning(
                    f"**Theme '{theme_name}' hat {len(warnings)} Warnungen:**"
                )
                
                for i, warning in enumerate(warnings, 1):
                    st.markdown(f"{i}. {warning}")
    
    def show_validation_success(self, theme_name: str) -> None:
        """
        Zeigt Erfolgs-Meldung bei erfolgreicher Validierung
        
        Args:
            theme_name: Name des Themes
        """
        st.success(f"✅ Theme '{theme_name}' erfolgreich validiert und geladen!")
    
    def show_realtime_validation(
        self,
        theme_name: str,
        is_valid: bool,
        errors: List[str] = None,
        warnings: List[str] = None
    ) -> None:
        """
        Zeigt Echtzeit-Validierung während Theme-Entwicklung
        
        Args:
            theme_name: Name des Themes
            is_valid: Ob Theme valide ist
            errors: Liste von Fehlern (optional)
            warnings: Liste von Warnungen (optional)
        """
        if errors is None:
            errors = []
        if warnings is None:
            warnings = []
        
        # Status-Badge
        if is_valid:
            st.success(f"✅ **{theme_name}** - Valide")
        else:
            st.error(f"❌ **{theme_name}** - Ungültig ({len(errors)} Fehler)")
        
        # Details
        if errors or warnings:
            col1, col2 = st.columns(2)
            
            with col1:
                if errors:
                    st.metric("Fehler", len(errors), delta=None)
            
            with col2:
                if warnings:
                    st.metric("Warnungen", len(warnings), delta=None)
            
            # Zeige Details
            if errors:
                self.show_validation_errors(theme_name, errors, warnings)
            elif warnings:
                self.show_validation_errors(theme_name, [], warnings)
    
    def show_validation_history(self, limit: int = 10) -> None:
        """
        Zeigt Historie der Validierungs-Fehler
        
        Args:
            limit: Maximale Anzahl anzuzeigender Einträge
        """
        if not self.error_history:
            st.info("Keine Validierungs-Historie verfügbar")
            return
        
        st.subheader("📋 Validierungs-Historie")
        
        # Zeige letzte N Einträge
        recent = self.error_history[-limit:]
        
        for entry in reversed(recent):
            timestamp = entry['timestamp'].strftime('%H:%M:%S')
            theme_name = entry['theme_name']
            error_count = len(entry['errors'])
            warning_count = len(entry['warnings'])
            
            # Status-Icon
            if error_count > 0:
                icon = "❌"
                status = "Fehler"
            elif warning_count > 0:
                icon = "⚠️"
                status = "Warnungen"
            else:
                icon = "✅"
                status = "OK"
            
            with st.expander(
                f"{icon} {timestamp} - {theme_name} ({status})",
                expanded=False
            ):
                if error_count > 0:
                    st.error(f"**{error_count} Fehler:**")
                    for error in entry['errors']:
                        st.markdown(f"- {error}")
                
                if warning_count > 0:
                    st.warning(f"**{warning_count} Warnungen:**")
                    for warning in entry['warnings']:
                        st.markdown(f"- {warning}")
                
                if error_count == 0 and warning_count == 0:
                    st.success("Keine Probleme gefunden")
    
    def clear_history(self) -> None:
        """Löscht Validierungs-Historie"""
        self.error_history.clear()
    
    def _add_to_history(
        self,
        theme_name: str,
        errors: List[str],
        warnings: List[str]
    ) -> None:
        """Fügt Eintrag zur Historie hinzu"""
        entry = {
            'timestamp': datetime.now(),
            'theme_name': theme_name,
            'errors': errors.copy(),
            'warnings': warnings.copy()
        }
        
        self.error_history.append(entry)
        
        # Begrenze Historie-Größe
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Gibt Zusammenfassung der Fehler zurück
        
        Returns:
            Dictionary mit Fehler-Statistiken
        """
        if not self.error_history:
            return {
                'total_validations': 0,
                'total_errors': 0,
                'total_warnings': 0,
                'themes_with_errors': []
            }
        
        total_errors = sum(len(e['errors']) for e in self.error_history)
        total_warnings = sum(len(e['warnings']) for e in self.error_history)
        
        # Themes mit Fehlern
        themes_with_errors = set()
        for entry in self.error_history:
            if entry['errors']:
                themes_with_errors.add(entry['theme_name'])
        
        return {
            'total_validations': len(self.error_history),
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'themes_with_errors': list(themes_with_errors)
        }


def create_validation_display() -> ValidationDisplay:
    """
    Factory function zum Erstellen eines ValidationDisplay
    
    Returns:
        ValidationDisplay-Instanz
    """
    return ValidationDisplay()
