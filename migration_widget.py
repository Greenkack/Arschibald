"""
Migration Widget Library

Wiederverwendbare Streamlit-Widgets für Migration Management UI.

Author: ARSCHIBALD Development Team
Date: 2025-01-18
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Callable
from core_integration import get_migration_manager, is_feature_enabled


def render_migration_status_widget(
    key_suffix: str = "",
    show_actions: bool = True,
    auto_refresh_seconds: Optional[int] = None
) -> dict:
    """
    Zeigt aktuellen Migrations-Status als kompaktes Widget.
    
    Args:
        key_suffix: Suffix für eindeutige Widget-Keys
        show_actions: Zeige Action-Buttons (Apply, Refresh)
        auto_refresh_seconds: Auto-Refresh-Intervall (None = kein Auto-Refresh)
    
    Returns:
        dict mit aktuellen Stats
    """
    if not is_feature_enabled('migrations'):
        st.info("ℹ️ Migration Manager nicht aktiviert (FEATURE_MIGRATIONS=false)")
        return {}
    
    mig_mgr = get_migration_manager()
    
    # Stats holen
    try:
        stats = mig_mgr.get_stats()
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Migrations-Statistiken: {e}")
        return {}
    
    # Status Badge
    status = stats.get('status', 'unknown')
    status_map = {
        'ok': ('✅', 'Aktuell', 'success'),
        'pending': ('⚠️', 'Ausstehend', 'warning'),
        'uninitialized': ('ℹ️', 'Nicht initialisiert', 'info'),
        'error': ('❌', 'Fehler', 'error'),
        'unknown': ('❓', 'Unbekannt', 'error')
    }
    emoji, status_text, status_type = status_map.get(status, status_map['unknown'])
    
    # Header mit Status
    st.markdown(f"### 🔄 Migrations-Status {emoji} {status_text}")
    
    # Metrics in Columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Aktuelle Version",
            stats.get('current_version', 'Keine')[:8] if stats.get('current_version') else '-'
        )
    
    with col2:
        pending_count = stats.get('pending_count', 0)
        st.metric(
            "Ausstehend",
            pending_count,
            delta=f"{pending_count} zu migrieren" if pending_count > 0 else None
        )
    
    with col3:
        st.metric(
            "Total Migrationen",
            stats.get('total_migrations', 0)
        )
    
    with col4:
        st.metric(
            "DB-Tabellen",
            stats.get('database_tables', 0)
        )
    
    # Actions
    if show_actions:
        st.markdown("---")
        col_a, col_b, col_c = st.columns([2, 2, 2])
        
        with col_a:
            if st.button("🔄 Refresh", key=f"mig_refresh_{key_suffix}", use_container_width=True):
                st.rerun()
        
        with col_b:
            if stats.get('pending_count', 0) > 0:
                if st.button("⬆️ Apply Migrations", key=f"mig_apply_{key_suffix}", use_container_width=True, type="primary"):
                    with st.spinner("Migrationen werden angewendet..."):
                        try:
                            mig_mgr.run_migrations()
                            st.success("✅ Migrationen erfolgreich angewendet!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Fehler beim Anwenden: {e}")
        
        with col_c:
            if st.button("🔍 Validate", key=f"mig_validate_{key_suffix}", use_container_width=True):
                with st.spinner("Schema wird validiert..."):
                    validation = mig_mgr.validate_migrations()
                    if validation.get('errors'):
                        st.error("❌ Validierung fehlgeschlagen")
                        for error in validation['errors']:
                            st.error(f"  - {error}")
                    else:
                        st.success("✅ Schema ist valide")
    
    # Auto-Refresh
    if auto_refresh_seconds:
        st.empty()  # Placeholder für Auto-Refresh
        import time
        time.sleep(auto_refresh_seconds)
        st.rerun()
    
    return stats


def render_migration_history_widget(
    max_items: int = 10,
    key_suffix: str = "",
    show_details: bool = True
) -> None:
    """
    Zeigt Migrations-Historie mit aktueller Version markiert.
    
    Args:
        max_items: Maximale Anzahl Einträge
        key_suffix: Suffix für eindeutige Widget-Keys
        show_details: Zeige Details-Expander
    """
    if not is_feature_enabled('migrations'):
        return
    
    mig_mgr = get_migration_manager()
    
    try:
        history = mig_mgr.get_migration_history()
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Historie: {e}")
        return
    
    if not history:
        st.info("ℹ️ Keine Migrations-Historie vorhanden")
        return
    
    st.markdown(f"### 📜 Migrations-Historie (letzte {max_items})")
    
    # Limitiere auf max_items
    display_history = history[:max_items]
    
    # Tabelle erstellen
    for i, migration in enumerate(display_history):
        revision = migration.get('revision', 'unknown')
        message = migration.get('message', 'No message')
        is_current = migration.get('is_current', False)
        
        # Marker für aktuelle Version
        marker = "➤" if is_current else "  "
        
        # Zeile
        col1, col2, col3 = st.columns([1, 3, 8])
        
        with col1:
            if is_current:
                st.markdown(f"**{marker}**")
            else:
                st.markdown(marker)
        
        with col2:
            if is_current:
                st.markdown(f"**`{revision[:8]}`**")
            else:
                st.markdown(f"`{revision[:8]}`")
        
        with col3:
            if is_current:
                st.markdown(f"**{message}** (aktuell)")
            else:
                st.markdown(message)
        
        # Details-Expander (optional)
        if show_details and i < 3:  # Nur für erste 3 Einträge
            with st.expander(f"Details: {revision[:8]}"):
                st.json({
                    "Revision": revision,
                    "Message": message,
                    "Is Current": is_current,
                    "Down Revision": migration.get('down_revision', 'None')
                })


def render_pending_migrations_widget(
    key_suffix: str = "",
    show_apply_button: bool = True
) -> list[str]:
    """
    Zeigt ausstehende Migrationen mit Apply-Option.
    
    Args:
        key_suffix: Suffix für eindeutige Widget-Keys
        show_apply_button: Zeige "Apply"-Button
    
    Returns:
        Liste ausstehender Migration-Revision-IDs
    """
    if not is_feature_enabled('migrations'):
        return []
    
    mig_mgr = get_migration_manager()
    
    try:
        pending = mig_mgr.get_pending_migrations()
    except Exception as e:
        st.error(f"❌ Fehler beim Laden ausstehender Migrationen: {e}")
        return []
    
    if not pending:
        st.success("✅ Keine ausstehenden Migrationen")
        return []
    
    st.markdown(f"### ⚠️ Ausstehende Migrationen ({len(pending)})")
    
    # Liste anzeigen
    for i, revision_id in enumerate(pending, 1):
        st.markdown(f"{i}. `{revision_id[:8]}...`")
    
    # Apply-Button
    if show_apply_button:
        st.markdown("---")
        if st.button(
            f"⬆️ Alle {len(pending)} Migration(en) anwenden",
            key=f"apply_pending_{key_suffix}",
            type="primary",
            use_container_width=True
        ):
            with st.spinner("Migrationen werden angewendet..."):
                try:
                    mig_mgr.run_migrations()
                    st.success(f"✅ {len(pending)} Migration(en) erfolgreich angewendet!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Fehler beim Anwenden: {e}")
    
    return pending


def render_migration_validation_widget(
    key_suffix: str = "",
    auto_validate: bool = False
) -> dict:
    """
    Zeigt Schema-Validierung mit Errors/Warnings.
    
    Args:
        key_suffix: Suffix für eindeutige Widget-Keys
        auto_validate: Führe Validierung automatisch aus
    
    Returns:
        Validierungs-Ergebnis dict
    """
    if not is_feature_enabled('migrations'):
        return {}
    
    mig_mgr = get_migration_manager()
    
    st.markdown("### 🔍 Schema-Validierung")
    
    # Auto-Validate oder Button
    do_validate = auto_validate
    if not auto_validate:
        if st.button("🔍 Schema validieren", key=f"validate_{key_suffix}"):
            do_validate = True
    
    if not do_validate:
        st.info("ℹ️ Klicke auf 'Schema validieren' um die Validierung zu starten")
        return {}
    
    # Validierung durchführen
    with st.spinner("Schema wird validiert..."):
        try:
            validation = mig_mgr.validate_migrations()
        except Exception as e:
            st.error(f"❌ Validierung fehlgeschlagen: {e}")
            return {'status': 'error', 'errors': [str(e)]}
    
    # Status
    status = validation.get('status', 'unknown')
    if status == 'ok':
        st.success("✅ Schema ist valide")
    elif status == 'pending':
        st.warning("⚠️ Ausstehende Migrationen vorhanden")
    elif status == 'uninitialized':
        st.info("ℹ️ Datenbank nicht initialisiert")
    else:
        st.error("❌ Validierung fehlgeschlagen")
    
    # Current Revision
    st.markdown(f"**Aktuelle Version:** `{validation.get('current_revision', 'Keine')}`")
    
    # Pending Migrations
    pending = validation.get('pending_migrations', [])
    if pending:
        st.markdown(f"**Ausstehende Migrationen:** {len(pending)}")
        for rev in pending:
            st.markdown(f"  - `{rev[:8]}...`")
    
    # Errors
    errors = validation.get('errors', [])
    if errors:
        st.markdown("#### ❌ Fehler")
        for error in errors:
            st.error(error)
    
    # Warnings
    warnings = validation.get('warnings', [])
    if warnings:
        st.markdown("#### ⚠️ Warnungen")
        for warning in warnings:
            st.warning(warning)
    
    return validation


def render_migration_manager_admin(
    key_suffix: str = "admin",
    show_cli_commands: bool = True
) -> None:
    """
    Vollständiges Admin-Panel für Migrations-Management.
    
    Args:
        key_suffix: Suffix für eindeutige Widget-Keys
        show_cli_commands: Zeige CLI-Befehle
    """
    st.markdown("## 🔄 Migration Manager - Admin Panel")
    
    if not is_feature_enabled('migrations'):
        st.warning("⚠️ Migration Manager ist deaktiviert")
        st.info("Aktiviere mit: `FEATURE_MIGRATIONS=true` in .env")
        return
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Status",
        "📜 Historie",
        "⚠️ Ausstehend",
        "🔧 Management"
    ])
    
    # Tab 1: Status
    with tab1:
        render_migration_status_widget(
            key_suffix=f"{key_suffix}_status",
            show_actions=True
        )
        
        st.markdown("---")
        
        # Validation
        render_migration_validation_widget(
            key_suffix=f"{key_suffix}_validation",
            auto_validate=False
        )
    
    # Tab 2: Historie
    with tab2:
        render_migration_history_widget(
            max_items=20,
            key_suffix=f"{key_suffix}_history",
            show_details=True
        )
    
    # Tab 3: Ausstehende Migrationen
    with tab3:
        render_pending_migrations_widget(
            key_suffix=f"{key_suffix}_pending",
            show_apply_button=True
        )
    
    # Tab 4: Management
    with tab4:
        st.markdown("### 🔧 Management Actions")
        
        mig_mgr = get_migration_manager()
        
        # Aktionen in Columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⬆️ Migration erstellen")
            
            message = st.text_input(
                "Migration Message",
                key=f"mig_message_{key_suffix}",
                placeholder="z.B. Add user table"
            )
            
            autogenerate = st.checkbox(
                "Auto-generate (SQLAlchemy Models)",
                value=True,
                key=f"mig_autogen_{key_suffix}"
            )
            
            if st.button(
                "➕ Migration erstellen",
                key=f"mig_create_{key_suffix}",
                type="primary",
                disabled=not message
            ):
                with st.spinner("Migration wird erstellt..."):
                    try:
                        revision_id = mig_mgr.create_migration(
                            message=message,
                            autogenerate=autogenerate
                        )
                        st.success(f"✅ Migration erstellt: `{revision_id}`")
                        st.info(f"Datei: `core/alembic/versions/{revision_id}_*.py`")
                    except Exception as e:
                        st.error(f"❌ Fehler: {e}")
        
        with col2:
            st.markdown("#### ⬇️ Rollback")
            
            rollback_target = st.selectbox(
                "Rollback zu",
                options=["-1 (vorherige Version)", "base (alles zurück)"],
                key=f"mig_rollback_target_{key_suffix}"
            )
            
            target = "-1" if "-1" in rollback_target else "base"
            
            if st.button(
                "⬇️ Rollback durchführen",
                key=f"mig_rollback_{key_suffix}",
                type="secondary"
            ):
                confirm = st.checkbox(
                    "Ich bestätige den Rollback",
                    key=f"mig_rollback_confirm_{key_suffix}"
                )
                
                if confirm:
                    with st.spinner(f"Rollback zu '{target}' wird durchgeführt..."):
                        try:
                            mig_mgr.rollback_migration(target)
                            st.success(f"✅ Rollback zu '{target}' erfolgreich!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Fehler: {e}")
                else:
                    st.warning("⚠️ Bitte bestätige den Rollback")
        
        # CLI Commands
        if show_cli_commands:
            st.markdown("---")
            st.markdown("### 💻 CLI-Befehle")
            
            with st.expander("Alembic CLI-Referenz"):
                st.markdown("""
                **Basis-Befehle:**
                ```bash
                # Migration erstellen (auto)
                alembic revision --autogenerate -m "Message"
                
                # Migration erstellen (leer)
                alembic revision -m "Message"
                
                # Migrationen anwenden
                alembic upgrade head
                
                # Rollback (eine Version)
                alembic downgrade -1
                
                # Rollback (alles)
                alembic downgrade base
                
                # Status
                alembic current
                
                # Historie
                alembic history
                ```
                
                **Erweitert:**
                ```bash
                # SQL-Preview
                alembic upgrade head --sql
                
                # Offline-SQL
                alembic upgrade head --sql > migration.sql
                
                # Details
                alembic show <revision>
                ```
                """)


def render_migration_creation_form(
    key_suffix: str = "",
    on_create: Optional[Callable[[str], None]] = None
) -> Optional[str]:
    """
    Formular zum Erstellen neuer Migrationen.
    
    Args:
        key_suffix: Suffix für eindeutige Widget-Keys
        on_create: Callback nach erfolgreicher Erstellung (bekommt revision_id)
    
    Returns:
        Revision-ID der erstellten Migration oder None
    """
    if not is_feature_enabled('migrations'):
        return None
    
    st.markdown("### ➕ Neue Migration erstellen")
    
    mig_mgr = get_migration_manager()
    
    # Formular
    with st.form(key=f"migration_form_{key_suffix}"):
        message = st.text_input(
            "Migration Message *",
            placeholder="z.B. Add customer phone field",
            help="Beschreibende Nachricht für die Migration"
        )
        
        autogenerate = st.checkbox(
            "Auto-generate aus SQLAlchemy Models",
            value=True,
            help="Automatisch Schema-Änderungen aus Models erkennen"
        )
        
        sql_preview = st.checkbox(
            "SQL-Preview generieren",
            value=False,
            help="Generiere SQL-Preview ohne Anwendung"
        )
        
        submitted = st.form_submit_button("➕ Migration erstellen", type="primary")
        
        if submitted:
            if not message:
                st.error("❌ Bitte gib eine Migration Message ein")
                return None
            
            with st.spinner("Migration wird erstellt..."):
                try:
                    revision_id = mig_mgr.create_migration(
                        message=message,
                        autogenerate=autogenerate,
                        sql=sql_preview
                    )
                    
                    st.success(f"✅ Migration erstellt: `{revision_id}`")
                    
                    # Datei-Info
                    version_file = f"core/alembic/versions/{revision_id}_*.py"
                    st.info(f"📄 Datei: `{version_file}`")
                    
                    # Callback
                    if on_create:
                        on_create(revision_id)
                    
                    return revision_id
                    
                except Exception as e:
                    st.error(f"❌ Fehler beim Erstellen: {e}")
                    return None
    
    return None


# Beispiel-Usage im Docstring
__doc__ += """

## Verwendung

### Beispiel 1: Status Widget in Sidebar

```python
import streamlit as st
from migration_widget import render_migration_status_widget

st.sidebar.markdown("---")
render_migration_status_widget(
    key_suffix="sidebar",
    show_actions=False,  # Keine Actions in Sidebar
    auto_refresh_seconds=30  # Auto-Refresh alle 30s
)
```

### Beispiel 2: Admin Dashboard

```python
from migration_widget import render_migration_manager_admin

# Vollständiges Admin-Panel
render_migration_manager_admin(
    key_suffix="main_admin",
    show_cli_commands=True
)
```

### Beispiel 3: Custom Layout

```python
from migration_widget import (
    render_migration_status_widget,
    render_migration_history_widget,
    render_pending_migrations_widget
)

col1, col2 = st.columns([2, 1])

with col1:
    render_migration_status_widget(key_suffix="main")
    render_migration_history_widget(max_items=5)

with col2:
    render_pending_migrations_widget(key_suffix="sidebar")
```

### Beispiel 4: Migration Creation mit Callback

```python
from migration_widget import render_migration_creation_form

def on_migration_created(revision_id: str):
    st.session_state['last_created_migration'] = revision_id
    st.success(f"Migration {revision_id} bereit für Review!")

render_migration_creation_form(
    key_suffix="create_form",
    on_create=on_migration_created
)
```
"""
