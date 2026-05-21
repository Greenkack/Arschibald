"""
Extended Core Integration Status Dashboard
===========================================

Zeigt Status und Performance-Metriken aller 31 Core-Module an.
"""

import streamlit as st
from datetime import datetime
from pathlib import Path

try:
    from core_integration import (
        # Phase 1-4
        get_app_config,
        get_app_logger,
        get_app_cache,
        get_session_manager,
        get_current_session,
        get_database_manager,
        get_database_metrics,
        run_database_health_check,
        # Phase 5-12
        get_security_manager,
        get_router,
        get_form_manager,
        get_widget_manager,
        get_navigation_history,
        get_job_manager,
        get_migration_manager,
        get_cache_invalidator,
        get_cache_monitor,
        get_cache_warmer,
        get_db_performance_monitor,
        get_di_container,
        # Helpers
        is_feature_enabled,
        FEATURES)
    CORE_AVAILABLE = True
except ImportError as e:
    CORE_AVAILABLE = False
    print(f"Import error: {e}")


def render_extended_core_status_dashboard():
    """Rendere erweiterte Core-Integration Status Dashboard"""
    
    st.markdown("## Extended Core System Status")
    st.caption("Zeigt alle 31 integrierten Core-Module")
    
    if not CORE_AVAILABLE:
        st.error("Core-Integration nicht verfügbar")
        st.info("Core-Module sind nicht installiert oder konnten nicht geladen werden.")
        return
    
    # Statistics
    enabled_count = sum(1 for v in FEATURES.values() if v)
    total_count = len(FEATURES)
    coverage = (enabled_count / total_count * 100) if total_count > 0 else 0
    
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("Aktivierte Module", enabled_count, delta=f"{coverage:.0f}%")
    with col_stats2:
        st.metric("Verfügbare Module", total_count)
    with col_stats3:
        integration_status = "🟢 FULL" if coverage == 100 else "🟡 PARTIAL" if coverage > 30 else " MINIMAL"
        st.metric("Integration Status", integration_status)
    
    st.markdown("---")
    
    # Tabs für verschiedene Phasen
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Phase 1-4 (Basis)",
        " Phase 5-7 (UI & Auth)",
        " Phase 8-9 (Jobs & Migrations)",
        "Phase 10-12 (Extensions)",
        "Performance Metrics"
    ])
    
    with tab1:
        _render_phase_1_4()
    
    with tab2:
        _render_phase_5_7()
    
    with tab3:
        _render_phase_8_9()
    
    with tab4:
        _render_phase_10_12()
    
    with tab5:
        _render_performance_metrics()


def _render_phase_1_4():
    """Phase 1-4: Basis-Module"""
    st.markdown("### Phase 1-4: Basis-Integration")
    
    # Phase 1: Config & Logging
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("####  Configuration")
        if is_feature_enabled('config'):
            config = get_app_config()
            if config:
                st.success("Aktiv")
                with st.expander("Details"):
                    st.json({
                        'env': config.env,
                        'mode': config.mode,
                        'debug': config.debug,
                        'database': config.get_database_url()[:30] + '...',
                    })
            else:
                st.warning("Initialisierung fehlgeschlagen")
        else:
            st.info("Deaktiviert")
    
    with col2:
        st.markdown("#### Logging")
        if is_feature_enabled('logging'):
            logger = get_app_logger()
            if logger:
                st.success("Aktiv")
                with st.expander("Details"):
                    config = get_app_config()
                    if config:
                        st.write(f"**Log Level:** {config.log_level}")
                        st.write(f"**Log Directory:** {config.log_dir}")
            else:
                st.warning("Logger nicht verfügbar")
        else:
            st.info("Deaktiviert")
    
    # Phase 2: Cache
    st.markdown("####  Cache System")
    if is_feature_enabled('cache'):
        cache = get_app_cache()
        if cache:
            st.success("Aktiv")
            try:
                stats = cache.get_stats()
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Hits", stats.get('hits', 0))
                with col2:
                    st.metric("Misses", stats.get('misses', 0))
                with col3:
                    hits = stats.get('hits', 0)
                    misses = stats.get('misses', 0)
                    total = hits + misses
                    hit_rate = (hits / total * 100) if total > 0 else 0
                    st.metric("Hit Rate", f"{hit_rate:.1f}%")
                with col4:
                    st.metric("Entries", stats.get('size', 0))
            except:
                st.caption("Stats nicht verfügbar")
        else:
            st.warning("Cache nicht initialisiert")
    else:
        st.info("Deaktiviert (optional)")
    
    # Phase 3: Session
    st.markdown("####  Session Persistence")
    if is_feature_enabled('session'):
        session_mgr = get_session_manager()
        if session_mgr:
            st.success("Aktiv - Browser Refresh Recovery")
            session = get_current_session()
            if session:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Session ID", f"...{session.session_id[-8:]}")
                with col2:
                    st.metric("Forms", len(session.form_states))
                with col3:
                    st.metric("User", session.user_id or "Anonymous")
            else:
                st.caption("Keine aktive Session")
        else:
            st.warning("Session Manager nicht verfügbar")
    else:
        st.info("Deaktiviert (optional)")
    
    # Phase 4: Database
    st.markdown("####  Database Connection Pooling")
    if is_feature_enabled('database'):
        db_mgr = get_database_manager()
        if db_mgr:
            st.success("Aktiv - Enhanced Connection Manager")
            try:
                metrics = get_database_metrics()
                health = run_database_health_check()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Pool Size", metrics.get('checked_out', 0) if metrics else "N/A")
                with col2:
                    st.metric("Utilization", metrics.get('utilization', 'N/A') if metrics else "N/A")
                with col3:
                    leaked = metrics.get('leaked_connections', 0) if metrics else 0
                    st.metric("Leaked", leaked, delta=-leaked if leaked > 0 else 0, delta_color="inverse")
                with col4:
                    if health and health.healthy:
                        st.metric("Health", "OK")
                    else:
                        st.metric("Health", "Error")
            except Exception as e:
                st.error(f"Metriken-Fehler: {e}")
        else:
            st.warning("Database Manager nicht verfügbar")
    else:
        st.info("Standard Mode (optional)")


def _render_phase_5_7():
    """Phase 5-7: Security, Forms, Navigation"""
    st.markdown("###  Phase 5-7: UI & Authentication")
    
    # Phase 5: Security
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("####  Security Manager")
        if is_feature_enabled('security'):
            sec_mgr = get_security_manager()
            if sec_mgr:
                st.success("Aktiv")
                st.caption("- User Authentication")
                st.caption("- RBAC (Roles & Permissions)")
                st.caption("- Token Management")
                st.caption("- Password Hashing")
            else:
                st.warning("Nicht initialisiert")
        else:
            st.info("Deaktiviert")
    
    with col2:
        st.markdown("####  Router")
        if is_feature_enabled('router'):
            router = get_router()
            if router:
                st.success("Aktiv")
                st.caption("- URL-basiertes Routing")
                st.caption("- Route Guards")
                st.caption("- Navigation Middleware")
            else:
                st.warning("Nicht initialisiert")
        else:
            st.info("Deaktiviert")
    
    # Phase 6: Forms & Widgets
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### Form Manager")
        if is_feature_enabled('forms'):
            form_mgr = get_form_manager()
            if form_mgr:
                st.success("Aktiv")
                st.caption("- Multi-Step Forms")
                st.caption("- Form Validation")
                st.caption("- Auto-Save")
            else:
                st.warning("Nicht initialisiert")
        else:
            st.info("Deaktiviert")
    
    with col4:
        st.markdown("#### Widget Manager")
        if is_feature_enabled('widgets'):
            widget_mgr = get_widget_manager()
            if widget_mgr:
                st.success("Aktiv")
                st.caption("- Custom Widgets")
                st.caption("- Widget Persistence")
                st.caption("- Widget Validation")
            else:
                st.warning("Nicht initialisiert")
        else:
            st.info("Deaktiviert")
    
    # Phase 7: Navigation History
    st.markdown("####  Navigation History")
    if is_feature_enabled('navigation'):
        nav_hist = get_navigation_history()
        if nav_hist:
            st.success("Aktiv - User Navigation Tracking System")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption("Navigation Tracking")
            with col2:
                st.caption("Breadcrumbs")
            with col3:
                st.caption("Back/Forward Navigation")
            
            # Show navigation stats if available
            try:
                if hasattr(nav_hist, 'history') and hasattr(nav_hist, 'current_index'):
                    history_size = len(nav_hist.history)
                    current_idx = nav_hist.current_index
                    can_back = nav_hist.can_go_back()
                    can_forward = nav_hist.can_go_forward()
                    
                    with st.expander("Navigation Statistics"):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("History Size", history_size)
                        with col2:
                            st.metric("Current Position", current_idx + 1 if current_idx >= 0 else 0)
                        with col3:
                            st.metric("Can Go Back", "Ja" if can_back else "Nein")
                        with col4:
                            st.metric("Can Go Forward", "Ja" if can_forward else "Nein")
                        
                        # Show page visit counts
                        if hasattr(nav_hist, 'get_page_visits'):
                            page_visits = nav_hist.get_page_visits()
                            if page_visits:
                                st.markdown("**Seiten-Besuche:**")
                                visit_data = sorted(page_visits.items(), key=lambda x: x[1], reverse=True)
                                for page, count in visit_data[:10]:  # Top 10
                                    st.text(f"  {page}: {count} Besuche")
                        
                        # Show current breadcrumbs
                        if hasattr(nav_hist, 'get_breadcrumbs'):
                            breadcrumbs = nav_hist.get_breadcrumbs()
                            if breadcrumbs:
                                st.markdown("**Aktuelle Breadcrumbs:**")
                                for bc in breadcrumbs:
                                    icon = f"{bc.icon} " if bc.icon else ""
                                    current = " (aktuell)" if bc.is_current else ""
                                    st.text(f"  {icon}{bc.label}{current}")
            except Exception as e:
                st.error(f"Fehler beim Abrufen der Navigations-Statistiken: {e}")
        else:
            st.warning("Nicht initialisiert")
    else:
        st.info("Deaktiviert")


def _render_phase_8_9():
    """Phase 8-9: Jobs & Migrations"""
    st.markdown("###  Phase 8-9: Jobs & Migrations")
    
    # Phase 8: Jobs
    st.markdown("####  Job Manager")
    if is_feature_enabled('jobs'):
        job_mgr = get_job_manager()
        if job_mgr:
            st.success("Aktiv - Background Task System")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption("Job Scheduling")
            with col2:
                st.caption("Priority Queues")
            with col3:
                st.caption("Retry & DLQ")
            
            # Show job stats
            try:
                if hasattr(job_mgr, 'get_stats'):
                    stats = job_mgr.get_stats()
                    with st.expander("Job Statistics & Management"):
                        # Main Statistics
                        st.markdown("**Übersicht:**")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Jobs", stats.get('total', 0))
                        with col2:
                            pending = stats.get('pending', 0)
                            st.metric("Pending", pending, 
                                     delta="In Queue" if pending > 0 else None)
                        with col3:
                            running = stats.get('running', 0)
                            st.metric("Running", running,
                                     delta="Aktiv" if running > 0 else None)
                        with col4:
                            completed = stats.get('completed', 0)
                            st.metric("Completed", completed)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            failed = stats.get('failed', 0)
                            st.metric("Failed", failed,
                                     delta="Fehler" if failed > 0 else None,
                                     delta_color="inverse" if failed > 0 else "off")
                        with col2:
                            cancelled = stats.get('cancelled', 0)
                            st.metric("Cancelled", cancelled)
                        with col3:
                            dlq = stats.get('dead_letter', 0)
                            st.metric("Dead Letter Queue", dlq,
                                     delta="Benötigt Review" if dlq > 0 else None,
                                     delta_color="inverse" if dlq > 0 else "off")
                        with col4:
                            workers_active = stats.get('workers_active', 0)
                            workers_total = stats.get('workers', 0)
                            st.metric("Workers", f"{workers_active}/{workers_total}")
                        
                        # Success Rate
                        total = stats.get('total', 0)
                        if total > 0:
                            success_rate = (completed / total) * 100
                            st.markdown(f"**Erfolgsquote:** {success_rate:.1f}%")
                            st.progress(success_rate / 100)
                        
                        # Recent Jobs
                        if hasattr(job_mgr, 'get_job_history'):
                            st.markdown("---")
                            st.markdown("**Letzte Jobs:**")
                            
                            history = job_mgr.get_job_history(limit=10)
                            if history:
                                for job, result in history:
                                    status_emoji = {
                                        'completed': '✅',
                                        'failed': '❌',
                                        'running': '⏳',
                                        'pending': '⏸️',
                                        'cancelled': '🚫',
                                    }.get(result.status.value if hasattr(result.status, 'value') else str(result.status), '❓')
                                    
                                    duration = ""
                                    if result.duration_seconds:
                                        duration = f" ({result.duration_seconds:.2f}s)"
                                    
                                    timestamp = ""
                                    if result.completed_at:
                                        timestamp = result.completed_at.strftime("%H:%M:%S")
                                    elif result.started_at:
                                        timestamp = result.started_at.strftime("%H:%M:%S")
                                    
                                    st.text(f"{status_emoji} {job.name or job.id[:8]} - {timestamp}{duration}")
                                    
                                    if result.error:
                                        st.caption(f"   Error: {result.error[:100]}")
                            else:
                                st.caption("Keine Jobs vorhanden")
                        
                        # Management Actions
                        st.markdown("---")
                        st.markdown("**Management:**")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if hasattr(job_mgr, 'clear_dead_letter_queue'):
                                if st.button("🗑️ DLQ Leeren", key="clear_dlq"):
                                    job_mgr.clear_dead_letter_queue()
                                    st.success("Dead Letter Queue geleert")
                                    st.rerun()
                        
                        with col2:
                            if hasattr(job_mgr, 'cleanup_old_results'):
                                if st.button("🧹 Alte Jobs löschen", key="cleanup_jobs"):
                                    count = job_mgr.cleanup_old_results(retention_days=7)
                                    st.success(f"{count} alte Jobs gelöscht")
                                    st.rerun()
                        
                        with col3:
                            if st.button("🔄 Statistiken aktualisieren", key="refresh_stats"):
                                st.rerun()
            except Exception as e:
                st.error(f"Fehler beim Abrufen der Job-Statistiken: {e}")
        else:
            st.warning("Nicht initialisiert")
    else:
        st.info("Deaktiviert")
    
    # Phase 9: Migrations
    st.markdown("####  Migration Manager")
    if is_feature_enabled('migrations'):
        mig_mgr = get_migration_manager()
        if mig_mgr:
            st.success("Aktiv - Schema Migration System")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption("Up/Down Migrations")
            with col2:
                st.caption("Rollback Support")
            with col3:
                st.caption("Auto-Detection")
            
            # Show migration statistics
            try:
                if hasattr(mig_mgr, 'get_stats'):
                    stats = mig_mgr.get_stats()
                    
                    with st.expander("Migration Statistics & Management"):
                        # Status Badge
                        status = stats.get('status', 'unknown')
                        if status == 'ok':
                            st.success("✅ Datenbank-Schema ist aktuell")
                        elif status == 'pending':
                            st.warning(f"⚠️ {stats.get('pending_count', 0)} ausstehende Migration(en)")
                        elif status == 'uninitialized':
                            st.info("ℹ️ Datenbank nicht initialisiert")
                        else:
                            st.error(f"❌ Fehler: {stats.get('error', 'Unbekannt')}")
                        
                        # Main Statistics
                        st.markdown("**Übersicht:**")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            current = stats.get('current_version', 'None')
                            st.metric("Aktuelle Version", current)
                        with col2:
                            pending = stats.get('pending_count', 0)
                            st.metric("Ausstehend", pending,
                                     delta="Migration erforderlich" if pending > 0 else None,
                                     delta_color="inverse" if pending > 0 else "off")
                        with col3:
                            total = stats.get('total_migrations', 0)
                            st.metric("Total Migrationen", total)
                        with col4:
                            tables = stats.get('database_tables', 0)
                            st.metric("DB-Tabellen", tables)
                        
                        # Last Migration
                        last_mig = stats.get('last_migration')
                        if last_mig:
                            st.markdown("---")
                            st.markdown("**Letzte Migration:**")
                            st.text(f"📝 {last_mig.get('revision', 'N/A')}: {last_mig.get('message', 'N/A')}")
                            if last_mig.get('is_current'):
                                st.caption("   ✅ Aktuell angewendet")
                        
                        # Migration History
                        if hasattr(mig_mgr, 'get_migration_history'):
                            st.markdown("---")
                            st.markdown("**Migrations-Historie (letzte 10):**")
                            
                            history = mig_mgr.get_migration_history()
                            if history:
                                for i, migration in enumerate(history[:10]):
                                    is_current = migration.get('is_current', False)
                                    marker = "➤" if is_current else " "
                                    rev = migration.get('revision', 'N/A')[:8]
                                    msg = migration.get('message', 'No description')
                                    
                                    status_text = " (CURRENT)" if is_current else ""
                                    st.text(f"{marker} {rev}: {msg}{status_text}")
                            else:
                                st.caption("Keine Migrationen vorhanden")
                        
                        # Pending Migrations
                        if stats.get('pending_count', 0) > 0:
                            st.markdown("---")
                            st.markdown("**⚠️ Ausstehende Migrationen:**")
                            
                            if hasattr(mig_mgr, 'get_pending_migrations'):
                                pending_list = mig_mgr.get_pending_migrations()
                                for pending in pending_list:
                                    st.text(f"  🔄 {pending}")
                                
                                st.info("Diese Migrationen müssen noch angewendet werden. Verwende: `alembic upgrade head`")
                        
                        # Validation
                        if hasattr(mig_mgr, 'validate_migrations'):
                            st.markdown("---")
                            st.markdown("**Validierung:**")
                            
                            if st.button("🔍 Schema validieren", key="validate_migrations"):
                                with st.spinner("Validiere Datenbank-Schema..."):
                                    validation = mig_mgr.validate_migrations()
                                    
                                    if validation.get('status') == 'success':
                                        st.success("✅ Validierung erfolgreich")
                                    else:
                                        st.error("❌ Validierung fehlgeschlagen")
                                    
                                    # Errors
                                    errors = validation.get('errors', [])
                                    if errors:
                                        st.markdown("**Fehler:**")
                                        for error in errors:
                                            st.error(f"  {error}")
                                    
                                    # Warnings
                                    warnings = validation.get('warnings', [])
                                    if warnings:
                                        st.markdown("**Warnungen:**")
                                        for warning in warnings:
                                            st.warning(f"  {warning}")
                        
                        # Management Actions
                        st.markdown("---")
                        st.markdown("**Management:**")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("🔄 Statistiken aktualisieren", key="refresh_migrations"):
                                st.rerun()
                        
                        with col2:
                            if pending > 0:
                                if st.button("⬆️ Migrationen anwenden", key="run_migrations"):
                                    try:
                                        with st.spinner("Führe Migrationen aus..."):
                                            mig_mgr.run_migrations()
                                        st.success("Migrationen erfolgreich angewendet!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Fehler: {e}")
                        
                        with col3:
                            if st.button("📋 Historie anzeigen", key="show_history"):
                                st.info("Siehe 'Migrations-Historie' oben")
                        
                        # CLI Commands
                        st.markdown("---")
                        st.markdown("**CLI-Befehle:**")
                        st.code("""
# Migrationen anwenden
alembic upgrade head

# Migration erstellen (Auto-detect)
alembic revision --autogenerate -m "description"

# Rollback zur vorherigen Version
alembic downgrade -1

# Aktuelle Version anzeigen
alembic current

# Historie anzeigen
alembic history
                        """.strip(), language="bash")
                        
            except Exception as e:
                st.error(f"Fehler beim Abrufen der Migrations-Statistiken: {e}")
        else:
            st.warning("Nicht initialisiert")
    else:
        st.info("Deaktiviert")


def _render_phase_10_12():
    """Phase 10-12: Cache Extensions, DB Extensions, DI"""
    st.markdown("### Phase 10-12: Advanced Extensions")
    
    # Phase 10: Cache Extensions
    with st.expander("📦 Phase 10: Cache Extensions", expanded=True):
        if is_feature_enabled('cache_ext'):
            try:
                invalidator = get_cache_invalidator()
                monitor = get_cache_monitor()
                warmer = get_cache_warmer()
                
                # Status
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**Cache Invalidator**")
                    if invalidator and hasattr(invalidator, 'get_stats'):
                        inv_stats = invalidator.get_stats()
                        st.success("✅ Aktiv")
                        st.metric("Total Invalidations", inv_stats.get('total_invalidations', 0))
                        st.metric("Rules", inv_stats.get('rules_count', 0))
                    else:
                        st.warning("Nicht verfügbar")
                
                with col2:
                    st.markdown("**Cache Monitor**")
                    if monitor and hasattr(monitor, 'get_stats'):
                        mon_stats = monitor.get_stats()
                        st.success("✅ Aktiv")
                        st.metric("Alerts", mon_stats.get('active_alerts', 0))
                        st.metric("Metrics Collected", mon_stats.get('total_metrics', 0))
                    else:
                        st.warning("Nicht verfügbar")
                
                with col3:
                    st.markdown("**Cache Warmer**")
                    if warmer and hasattr(warmer, 'get_stats'):
                        warm_stats = warmer.get_stats()
                        st.success("✅ Aktiv")
                        st.metric("Tasks", warm_stats.get('total_tasks', 0))
                        st.metric("Executed Today", warm_stats.get('executed_today', 0))
                    else:
                        st.warning("Nicht verfügbar")
                
                # Actions
                st.markdown("---")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button("🔄 Refresh Stats", key="cache_ext_refresh"):
                        st.rerun()
                with col_b:
                    if st.button("🗑️ Clear Cache", key="cache_ext_clear"):
                        if invalidator:
                            try:
                                invalidator.invalidate_all()
                                st.success("Cache cleared!")
                            except Exception as e:
                                st.error(f"Error: {e}")
                with col_c:
                    if st.button("🔥 Warm Cache", key="cache_ext_warm"):
                        if warmer:
                            try:
                                warmer.warm_all()
                                st.success("Cache warming started!")
                            except Exception as e:
                                st.error(f"Error: {e}")
            
            except Exception as e:
                st.error(f"Error loading Cache Extensions: {e}")
        else:
            st.info("ℹ️ Deaktiviert (FEATURE_CACHE_EXTENSIONS=false)")
    
    # Phase 11: DB Extensions
    with st.expander("🗄️ Phase 11: Database Extensions", expanded=True):
        if is_feature_enabled('db_ext'):
            try:
                perf_mon = get_db_performance_monitor()
                
                if perf_mon and hasattr(perf_mon, 'get_stats'):
                    stats = perf_mon.get_stats()
                    
                    # Status Badge
                    status = stats.get('status', 'unknown')
                    status_map = {
                        'ok': ('✅', 'OK', 'success'),
                        'degraded': ('⚠️', 'Degraded', 'warning'),
                        'warning': ('⚠️', 'Warning', 'warning'),
                        'critical': ('❌', 'Critical', 'error')
                    }
                    emoji, status_text, _ = status_map.get(status, ('❓', 'Unknown', 'info'))
                    st.markdown(f"**Status:** {emoji} {status_text}")
                    
                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Queries", stats.get('total_queries', 0))
                    with col2:
                        st.metric("Avg Duration", f"{stats.get('avg_duration_ms', 0):.1f}ms")
                    with col3:
                        st.metric("Slow Queries", stats.get('total_slow_queries', 0))
                    with col4:
                        st.metric("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
                    
                    # Slow Queries
                    st.markdown("**Slow Queries (letzte 5):**")
                    slow = perf_mon.get_slow_queries(limit=5)
                    if slow:
                        for q in slow:
                            st.markdown(f"- `{q.duration_ms:.0f}ms` - {q.sql[:80]}...")
                    else:
                        st.caption("Keine slow queries")
                    
                    # Actions
                    st.markdown("---")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("🔄 Refresh Stats", key="db_ext_refresh"):
                            st.rerun()
                    with col_b:
                        if st.button("🗑️ Clear Metrics", key="db_ext_clear"):
                            try:
                                perf_mon.clear()
                                st.success("Metrics cleared!")
                            except Exception as e:
                                st.error(f"Error: {e}")
                
                else:
                    st.warning("DB Performance Monitor nicht initialisiert")
            
            except Exception as e:
                st.error(f"Error loading DB Extensions: {e}")
        else:
            st.info("ℹ️ Deaktiviert (FEATURE_DB_EXTENSIONS=false)")
    
    # Phase 12: DI Container
    with st.expander("🔌 Phase 12: Dependency Injection", expanded=True):
        if is_feature_enabled('di'):
            try:
                di_container = get_di_container()
                
                if di_container and hasattr(di_container, 'get_stats'):
                    stats = di_container.get_stats()
                    
                    st.markdown(f"**Status:** ✅ {stats.get('status', 'unknown').upper()}")
                    
                    # Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Services", stats.get('total_services', 0))
                    with col2:
                        st.metric("Singletons", stats.get('singleton_count', 0))
                    with col3:
                        st.metric("Scoped", stats.get('scoped_count', 0))
                    with col4:
                        st.metric("Transient", stats.get('transient_count', 0))
                    
                    # Lifetime Breakdown
                    st.markdown("**Lifetime Distribution:**")
                    total = stats.get('total_services', 1)
                    st.progress(stats.get('singleton_count', 0) / total, text=f"Singleton: {stats.get('singleton_count', 0)}")
                    st.progress(stats.get('scoped_count', 0) / total, text=f"Scoped: {stats.get('scoped_count', 0)}")
                    st.progress(stats.get('transient_count', 0) / total, text=f"Transient: {stats.get('transient_count', 0)}")
                    
                    # Top Resolved Services
                    st.markdown("**Top Resolved Services:**")
                    top_resolved = stats.get('top_resolved', [])
                    if top_resolved:
                        for svc in top_resolved[:5]:
                            st.caption(f"- {svc.get('service', 'Unknown')}: {svc.get('count', 0)} resolutions ({svc.get('lifetime', 'unknown')})")
                    else:
                        st.caption("Keine Resolutions")
                    
                    # Registered Services
                    if st.checkbox("Show All Services", key="di_show_services"):
                        services = di_container.get_registered_services()
                        st.markdown(f"**All Registered Services ({len(services)}):**")
                        for service in services:
                            st.caption(f"- {service}")
                    
                    # Actions
                    st.markdown("---")
                    if st.button("🔄 Refresh Stats", key="di_refresh"):
                        st.rerun()
                
                else:
                    st.warning("DI Container nicht initialisiert")
            
            except Exception as e:
                st.error(f"Error loading DI Container: {e}")
        else:
            st.info("ℹ️ Deaktiviert (FEATURE_DI_CONTAINER=false)")


def _render_performance_metrics():
    """Performance Metrics Tab"""
    st.markdown("### Performance Metrics")
    
    # Overall system health
    st.markdown("####  System Health")
    
    health_metrics = {}
    
    # Cache health
    if is_feature_enabled('cache'):
        cache = get_app_cache()
        if cache:
            try:
                stats = cache.get_stats()
                hits = stats.get('hits', 0)
                misses = stats.get('misses', 0)
                total = hits + misses
                hit_rate = (hits / total * 100) if total > 0 else 0
                health_metrics['Cache Hit Rate'] = f"{hit_rate:.1f}%"
            except:
                pass
    
    # Database health
    if is_feature_enabled('database'):
        try:
            health = run_database_health_check()
            if health:
                health_metrics['DB Response Time'] = f"{health.response_time:.2f}ms"
                health_metrics['DB Health'] = "Healthy" if health.healthy else "Unhealthy"
        except:
            pass
    
    # Display metrics
    if health_metrics:
        cols = st.columns(len(health_metrics))
        for idx, (name, value) in enumerate(health_metrics.items()):
            with cols[idx]:
                st.metric(name, value)
    else:
        st.info("Keine Performance-Metriken verfügbar")
    
    st.markdown("---")
    
    # Feature summary
    st.markdown("####  Feature Summary")
    
    feature_groups = {
        'Basis (Phase 1-4)': ['config', 'logging', 'cache', 'session', 'database'],
        'UI & Auth (Phase 5-7)': ['security', 'router', 'forms', 'widgets', 'navigation'],
        'Jobs & Migrations (Phase 8-9)': ['jobs', 'migrations'],
        'Extensions (Phase 10-12)': ['cache_ext', 'db_ext', 'di'],
    }
    
    for group_name, features in feature_groups.items():
        enabled = sum(1 for f in features if is_feature_enabled(f))
        total = len(features)
        percentage = (enabled / total * 100) if total > 0 else 0
        
        st.write(f"**{group_name}:** {enabled}/{total} aktiv ({percentage:.0f}%)")
        
        # Progress bar
        st.progress(percentage / 100)


# Backward compatibility - render both dashboards
def render_core_status_dashboard():
    """Rendere beide Dashboards"""
    
    # Show tabs for both views
    tab1, tab2 = st.tabs(["Standard Dashboard", "Extended Dashboard"])
    
    with tab1:
        _render_standard_dashboard()
    
    with tab2:
        render_extended_core_status_dashboard()


def _render_standard_dashboard():
    """Original standard dashboard (Phase 1-4 only)"""
    from admin_core_status_ui import render_core_status_dashboard as _original
    try:
        _original()
    except:
        st.error("Original Dashboard konnte nicht geladen werden")
        st.info("Verwenden Sie das Extended Dashboard")


if __name__ == "__main__":
    st.set_page_config(page_title="Core Status Dashboard", layout="wide")
    render_core_status_dashboard()
