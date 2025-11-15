"""price_matrix_error_ui.py

UI-Komponenten für benutzerfreundliche Fehleranzeige im Preismatrix-System.

Dieses Modul stellt Streamlit-Komponenten bereit für:
- Anzeige von Fehlermeldungen mit Lösungsvorschlägen
- Interaktive Fehlerbehandlung
- Hilfe-Dialoge für spezifische Fehlertypen
- Admin-Benachrichtigungen

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from price_matrix_error_handling import (
    PriceMatrixErrorInfo,
    ErrorSeverity,
    ErrorCategory,
    FallbackResult,
    format_error_message_for_ui,
    get_error_help_text,
    classify_error
)


def display_error_message(
    error_info: PriceMatrixErrorInfo,
    show_suggestions: bool = True,
    show_help_button: bool = True,
    container: Optional[Any] = None
) -> None:
    """
    Zeigt Fehlermeldung in Streamlit UI an
    
    Args:
        error_info: Strukturierte Fehlerinformation
        show_suggestions: Lösungsvorschläge anzeigen
        show_help_button: Hilfe-Button anzeigen
        container: Streamlit-Container (None = st)
        
    Requirement 7.1, 7.2, 7.3, 7.4, 7.5
    """
    if container is None:
        container = st
    
    # Wähle Streamlit-Komponente basierend auf Severity
    if error_info.severity == ErrorSeverity.CRITICAL:
        container.error(error_info.user_message, icon="🚨")
    elif error_info.severity == ErrorSeverity.ERROR:
        container.error(error_info.user_message, icon="")
    elif error_info.severity == ErrorSeverity.WARNING:
        container.warning(error_info.user_message, icon="")
    else:
        container.info(error_info.user_message, icon="")
    
    # Lösungsvorschläge
    if show_suggestions and error_info.suggestions:
        with container.expander("Lösungsvorschläge", expanded=True):
            for i, suggestion in enumerate(error_info.suggestions, 1):
                st.markdown(f"{i}. {suggestion}")
    
    # Hilfe-Button
    if show_help_button:
        if container.button("❓ Detaillierte Hilfe anzeigen", key=f"help_{error_info.category.value}"):
            show_error_help_dialog(error_info.category)


def display_error_with_fallback(
    error_result: Dict[str, Any],
    container: Optional[Any] = None
) -> None:
    """
    Zeigt Fehler mit Fallback-Information an
    
    Args:
        error_result: Ergebnis von handle_error_with_fallback()
        container: Streamlit-Container (None = st)
        
    Requirement 8.5
    """
    if container is None:
        container = st
    
    # Rekonstruiere ErrorInfo aus Dict
    error_dict = error_result.get('error_info', {})
    error_info = PriceMatrixErrorInfo(
        category=ErrorCategory(error_dict.get('category', 'system_error')),
        severity=ErrorSeverity(error_dict.get('severity', 'error')),
        message=error_dict.get('message', ''),
        user_message=error_dict.get('user_message', ''),
        details=error_dict.get('details', {}),
        suggestions=error_dict.get('suggestions', []),
        fallback_available=error_dict.get('fallback_available', False)
    )
    
    # Zeige Fallback-Warnung wenn verwendet
    if error_result.get('fallback_used'):
        fallback_result = error_result.get('fallback_result', {})
        container.warning(
            f"**Automatischer Fallback aktiviert**\n\n"
            f"{fallback_result.get('message', 'Fallback wurde verwendet')}\n\n"
            f"Strategie: {fallback_result.get('strategy', 'unbekannt')}",
            icon="🔄"
        )
    
    # Zeige Hauptfehler
    display_error_message(error_info, container=container)
    
    # Admin-Benachrichtigung Hinweis
    if error_result.get('admin_notified'):
        container.info(
            "📧 Der Administrator wurde über diesen Fehler benachrichtigt.",
            icon=""
        )


def show_error_help_dialog(category: ErrorCategory) -> None:
    """
    Zeigt detaillierten Hilfe-Dialog für Fehlertyp
    
    Args:
        category: Fehlerkategorie
        
    Requirement 7.1, 7.2, 7.3, 7.4, 7.5
    """
    help_text = get_error_help_text(category)
    
    # Verwende Modal-Dialog (Streamlit 1.23+)
    with st.expander("📖 Detaillierte Hilfe", expanded=True):
        st.markdown(help_text)
        
        # Zusätzliche Aktionen basierend auf Fehlertyp
        if category == ErrorCategory.MATRIX_NOT_FOUND:
            if st.button("Zum Admin-Bereich", key="goto_admin_matrix"):
                st.session_state['navigate_to'] = 'admin_matrix'
                st.rerun()
        
        elif category in [ErrorCategory.MODULE_COUNT_MISSING, ErrorCategory.STORAGE_MODEL_MISSING]:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Matrix anzeigen", key="show_matrix"):
                    st.session_state['show_matrix_details'] = True
                    st.rerun()
            with col2:
                if st.button("Matrix bearbeiten", key="edit_matrix"):
                    st.session_state['navigate_to'] = 'admin_matrix'
                    st.rerun()


def display_validation_results(
    validation_result: Dict[str, Any],
    container: Optional[Any] = None
) -> None:
    """
    Zeigt Matrix-Validierungsergebnisse an
    
    Args:
        validation_result: Ergebnis von validate_matrix_with_error_handling()
        container: Streamlit-Container (None = st)
        
    Requirement 7.1, 8.1
    """
    if container is None:
        container = st
    
    if validation_result.get('valid'):
        container.success(
            "Matrix ist gültig für Preisberechnung",
            icon=""
        )
        
        # Zeige Informationen
        info = validation_result.get('validation_result', {}).get('info', {})
        if info:
            with container.expander("Matrix-Informationen"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Zeilen", info.get('total_rows', 0))
                with col2:
                    st.metric("Spalten", info.get('total_columns', 0))
                with col3:
                    st.metric("Zellen", info.get('total_cells', 0))
                
                if 'module_counts' in info and info['module_counts']:
                    st.write("**Verfügbare Modulanzahlen:**")
                    st.write(", ".join(str(c) for c in info['module_counts']))
                
                if 'storage_models' in info and info['storage_models']:
                    st.write("**Verfügbare Speichermodelle:**")
                    st.write(", ".join(info['storage_models']))
    else:
        container.error(
            "Matrix-Validierung fehlgeschlagen",
            icon=""
        )
        
        # Zeige Fehler
        val_result = validation_result.get('validation_result', {})
        errors = val_result.get('errors', [])
        warnings = val_result.get('warnings', [])
        
        if errors:
            with container.expander("🚨 Fehler", expanded=True):
                for error in errors:
                    st.markdown(f"• {error}")
        
        if warnings:
            with container.expander("Warnungen"):
                for warning in warnings:
                    st.markdown(f"• {warning}")
        
        # Aktions-Buttons
        col1, col2 = container.columns(2)
        with col1:
            if st.button("Matrix korrigieren", key="fix_matrix"):
                st.session_state['navigate_to'] = 'admin_matrix'
                st.rerun()
        with col2:
            if st.button("📖 Hilfe anzeigen", key="show_validation_help"):
                show_validation_help()


def show_validation_help() -> None:
    """Zeigt Hilfe für Matrix-Validierung"""
    with st.expander("📖 Matrix-Validierung Hilfe", expanded=True):
        st.markdown("""
### Matrix-Struktur Anforderungen

Eine gültige Preismatrix muss folgende Struktur haben:

**1. Spalte A (Modulanzahl)**
- Enthält numerische Werte
- Aufsteigend sortiert empfohlen
- Beispiel: 10, 15, 20, 25, 30

**2. Zeile 1 (Speichermodelle)**
- Enthält Text-Werte (Modellnamen)
- Mindestens eine "Kein Speicher" Spalte
- Beispiel: "10kWh", "15kWh", "Kein Speicher"

**3. Preis-Zellen**
- Enthalten numerische Werte (Preise)
- Können leer sein (wird als Fehler gemeldet)
- Müssen positiv sein

### Beispiel-Matrix

```
         A              B          C              D
    Modulanzahl    10kWh      15kWh      Kein Speicher
1   Modulanzahl    10kWh      15kWh      Kein Speicher
2   10             15000      17500      12000
3   15             18000      20500      15000
4   20             21000      23500      18000
```

### Häufige Fehler

**Fehler:** "Spalte A muss numerische Werte enthalten"
- **Lösung:** Stellen Sie sicher, dass Spalte A nur Zahlen enthält

**Fehler:** "Keine 'Kein Speicher' Spalte gefunden"
- **Lösung:** Fügen Sie eine Spalte mit "Kein Speicher" hinzu

**Fehler:** "Preis-Zellen müssen numerische Werte enthalten"
- **Lösung:** Entfernen Sie Text aus Preis-Zellen
        """)


def display_price_lookup_error(
    error: Exception,
    module_count: int,
    storage_model: Optional[str],
    show_fallback_option: bool = True,
    container: Optional[Any] = None
) -> bool:
    """
    Zeigt Fehler bei Preis-Lookup an mit interaktiven Optionen
    
    Args:
        error: Aufgetretener Fehler
        module_count: Gesuchte Modulanzahl
        storage_model: Gesuchtes Speichermodell
        show_fallback_option: Fallback-Option anzeigen
        container: Streamlit-Container (None = st)
        
    Returns:
        True wenn Benutzer Fallback wählt, sonst False
        
    Requirement 7.1, 7.2, 7.3, 7.4, 7.5, 8.5
    """
    if container is None:
        container = st
    
    # Klassifiziere Fehler
    error_info = classify_error(error)
    
    # Zeige Fehler
    display_error_message(error_info, container=container)
    
    # Zeige Kontext
    with container.expander("Lookup-Details"):
        st.write(f"**Gesuchte Modulanzahl:** {module_count}")
        st.write(f"**Gesuchtes Speichermodell:** {storage_model or 'Kein Speicher'}")
        
        if error_info.details:
            st.write("**Zusätzliche Informationen:**")
            for key, value in error_info.details.items():
                if key == 'available_counts' and value:
                    st.write(f"• Verfügbare Modulanzahlen: {', '.join(map(str, value))}")
                elif key == 'available_models' and value:
                    st.write(f"• Verfügbare Speichermodelle: {', '.join(value[:10])}")
                    if len(value) > 10:
                        st.write(f"  ... und {len(value) - 10} weitere")
    
    # Fallback-Option
    use_fallback = False
    if show_fallback_option and error_info.fallback_available:
        container.info(
            "**Automatischer Fallback verfügbar**\n\n"
            "Das System kann automatisch einen alternativen Wert verwenden.",
            icon="🔄"
        )
        
        col1, col2 = container.columns(2)
        with col1:
            if st.button("Fallback verwenden", key="use_fallback", type="primary"):
                use_fallback = True
        with col2:
            if st.button("Abbrechen", key="cancel_fallback"):
                use_fallback = False
    
    return use_fallback


def display_admin_notification_banner(
    notifications: List[Dict[str, Any]],
    container: Optional[Any] = None
) -> None:
    """
    Zeigt Admin-Benachrichtigungen als Banner an
    
    Args:
        notifications: Liste von Benachrichtigungen
        container: Streamlit-Container (None = st)
        
    Requirement 8.5
    """
    if container is None:
        container = st
    
    if not notifications:
        return
    
    # Gruppiere nach Severity
    critical = [n for n in notifications if n.get('severity') == 'critical']
    errors = [n for n in notifications if n.get('severity') == 'error']
    warnings = [n for n in notifications if n.get('severity') == 'warning']
    
    # Zeige kritische Fehler
    if critical:
        with container.expander(f"🚨 {len(critical)} Kritische Fehler", expanded=True):
            for notif in critical:
                st.error(notif.get('message', ''), icon="🚨")
                if notif.get('recommended_actions'):
                    st.write("**Empfohlene Aktionen:**")
                    for action in notif['recommended_actions']:
                        st.markdown(f"• {action}")
                st.divider()
    
    # Zeige Fehler
    if errors:
        with container.expander(f"{len(errors)} Fehler"):
            for notif in errors:
                st.error(notif.get('message', ''), icon="")
                if notif.get('recommended_actions'):
                    st.write("**Empfohlene Aktionen:**")
                    for action in notif['recommended_actions']:
                        st.markdown(f"• {action}")
                st.divider()
    
    # Zeige Warnungen
    if warnings:
        with container.expander(f"{len(warnings)} Warnungen"):
            for notif in warnings:
                st.warning(notif.get('message', ''), icon="")
                st.divider()


def create_error_report_download(
    error_info: PriceMatrixErrorInfo,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Erstellt downloadbaren Fehlerbericht
    
    Args:
        error_info: Strukturierte Fehlerinformation
        context: Zusätzlicher Kontext
        
    Returns:
        Fehlerbericht als String
        
    Requirement 7.1, 7.2, 7.3, 7.4, 7.5
    """
    lines = [
        "=" * 80,
        "PREISMATRIX FEHLERBERICHT",
        "=" * 80,
        "",
        f"Zeitpunkt: {error_info.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Kategorie: {error_info.category.value}",
        f"Schweregrad: {error_info.severity.value}",
        "",
        "FEHLERMELDUNG",
        "-" * 80,
        error_info.message,
        "",
        "BENUTZER-MELDUNG",
        "-" * 80,
        error_info.user_message,
        "",
    ]
    
    if error_info.suggestions:
        lines.extend([
            "LÖSUNGSVORSCHLÄGE",
            "-" * 80,
        ])
        for i, suggestion in enumerate(error_info.suggestions, 1):
            lines.append(f"{i}. {suggestion}")
        lines.append("")
    
    if error_info.details:
        lines.extend([
            "TECHNISCHE DETAILS",
            "-" * 80,
        ])
        for key, value in error_info.details.items():
            lines.append(f"{key}: {value}")
        lines.append("")
    
    if context:
        lines.extend([
            "KONTEXT",
            "-" * 80,
        ])
        for key, value in context.items():
            lines.append(f"{key}: {value}")
        lines.append("")
    
    lines.extend([
        "=" * 80,
        "Ende des Berichts",
        "=" * 80,
    ])
    
    return "\n".join(lines)


__all__ = [
    'display_error_message',
    'display_error_with_fallback',
    'show_error_help_dialog',
    'display_validation_results',
    'show_validation_help',
    'display_price_lookup_error',
    'display_admin_notification_banner',
    'create_error_report_download'
]
