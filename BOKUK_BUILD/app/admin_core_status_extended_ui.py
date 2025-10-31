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
        FEATURES,
    )
    CORE_AVAILABLE = True
except ImportError as e:
    CORE_AVAILABLE = False
    print(f"Import error: {e}")


def render_extended_core_status_dashboard():
    """Rendere erweiterte Core-Integration Status Dashboard"""
    
    st.markdown("## 🔧 Extended Core System Status")
    st.caption("Zeigt alle 31 integrierten Core-Module")
    
    if not CORE_AVAILABLE:
        st.error("❌ Core-Integration nicht verfügbar")
        st.info("💡 Core-Module sind nicht installiert oder konnten nicht geladen werden.")
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
        integration_status = "🟢 FULL" if coverage == 100 else "🟡 PARTIAL" if coverage > 30 else "🔴 MINIMAL"
        st.metric("Integration Status", integration_status)
    
    st.markdown("---")
    
    # Tabs für verschiedene Phasen
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📦 Phase 1-4 (Basis)",
        "🔐 Phase 5-7 (UI & Auth)",
        "⚙️ Phase 8-9 (Jobs & Migrations)",
        "🚀 Phase 10-12 (Extensions)",
        "📊 Performance Metrics"
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
    st.markdown("### 📦 Phase 1-4: Basis-Integration")
    
    # Phase 1: Config & Logging
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚙️ Configuration")
        if is_feature_enabled('config'):
            config = get_app_config()
            if config:
                st.success("✅ Aktiv")
                with st.expander("Details"):
                    st.json({
                        'env': config.env,
                        'mode': config.mode,
                        'debug': config.debug,
                        'database': config.get_database_url()[:30] + '...',
                    })
            else:
                st.warning("⚠️ Initialisierung fehlgeschlagen")
        else:
            st.info("ℹ️ Deaktiviert")
    
    with col2:
        st.markdown("#### 📝 Logging")
        if is_feature_enabled('logging'):
            logger = get_app_logger()
            if logger:
                st.success("✅ Aktiv")
                with st.expander("Details"):
                    config = get_app_config()
                    if config:
                        st.write(f"**Log Level:** {config.log_level}")
                        st.write(f"**Log Directory:** {config.log_dir}")
            else:
                st.warning("⚠️ Logger nicht verfügbar")
        else:
            st.info("ℹ️ Deaktiviert")
    
    # Phase 2: Cache
    st.markdown("#### 💾 Cache System")
    if is_feature_enabled('cache'):
        cache = get_app_cache()
        if cache:
            st.success("✅ Aktiv")
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
            st.warning("⚠️ Cache nicht initialisiert")
    else:
        st.info("ℹ️ Deaktiviert (optional)")
    
    # Phase 3: Session
    st.markdown("#### 🔄 Session Persistence")
    if is_feature_enabled('session'):
        session_mgr = get_session_manager()
        if session_mgr:
            st.success("✅ Aktiv - Browser Refresh Recovery")
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
            st.warning("⚠️ Session Manager nicht verfügbar")
    else:
        st.info("ℹ️ Deaktiviert (optional)")
    
    # Phase 4: Database
    st.markdown("#### 🗄️ Database Connection Pooling")
    if is_feature_enabled('database'):
        db_mgr = get_database_manager()
        if db_mgr:
            st.success("✅ Aktiv - Enhanced Connection Manager")
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
                        st.metric("Health", "✅ OK")
                    else:
                        st.metric("Health", "❌ Error")
            except Exception as e:
                st.error(f"Metriken-Fehler: {e}")
        else:
            st.warning("⚠️ Database Manager nicht verfügbar")
    else:
        st.info("ℹ️ Standard Mode (optional)")


def _render_phase_5_7():
    """Phase 5-7: Security, Forms, Navigation"""
    st.markdown("### 🔐 Phase 5-7: UI & Authentication")
    
    # Phase 5: Security
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔐 Security Manager")
        if is_feature_enabled('security'):
            sec_mgr = get_security_manager()
            if sec_mgr:
                st.success("✅ Aktiv")
                st.caption("- User Authentication")
                st.caption("- RBAC (Roles & Permissions)")
                st.caption("- Token Management")
                st.caption("- Password Hashing")
            else:
                st.warning("⚠️ Nicht initialisiert")
        else:
            st.info("ℹ️ Deaktiviert")
    
    with col2:
        st.markdown("#### 🧭 Router")
        if is_feature_enabled('router'):
            router = get_router()
            if router:
                st.success("✅ Aktiv")
                st.caption("- URL-basiertes Routing")
                st.caption("- Route Guards")
                st.caption("- Navigation Middleware")
            else:
                st.warning("⚠️ Nicht initialisiert")
        else:
            st.info("ℹ️ Deaktiviert")
    
    # Phase 6: Forms & Widgets
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### 📝 Form Manager")
        if is_feature_enabled('forms'):
            form_mgr = get_form_manager()
            if form_mgr:
                st.success("✅ Aktiv")
                st.caption("- Multi-Step Forms")
                st.caption("- Form Validation")
                st.caption("- Auto-Save")
            else:
                st.warning("⚠️ Nicht initialisiert")
        else:
            st.info("ℹ️ Deaktiviert")
    
    with col4:
        st.markdown("#### 🎨 Widget Manager")
        if is_feature_enabled('widgets'):
            widget_mgr = get_widget_manager()
            if widget_mgr:
                st.success("✅ Aktiv")
                st.caption("- Custom Widgets")
                st.caption("- Widget Persistence")
                st.caption("- Widget Validation")
            else:
                st.warning("⚠️ Nicht initialisiert")
        else:
            st.info("ℹ️ Deaktiviert")
    
    # Phase 7: Navigation History
    st.markdown("#### 📍 Navigation History")
    if is_feature_enabled('navigation'):
        nav_hist = get_navigation_history()
        if nav_hist:
            st.success("✅ Aktiv")
            st.caption("- User Navigation Tracking")
            st.caption("- Breadcrumbs")
            st.caption("- Back/Forward Navigation")
        else:
            st.warning("⚠️ Nicht initialisiert")
    else:
        st.info("ℹ️ Deaktiviert")


def _render_phase_8_9():
    """Phase 8-9: Jobs & Migrations"""
    st.markdown("### ⚙️ Phase 8-9: Jobs & Migrations")
    
    # Phase 8: Jobs
    st.markdown("#### ⚙️ Job Manager")
    if is_feature_enabled('jobs'):
        job_mgr = get_job_manager()
        if job_mgr:
            st.success("✅ Aktiv - Background Task System")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption("✅ Job Scheduling")
            with col2:
                st.caption("✅ Job Notifications")
            with col3:
                st.caption("✅ Job Management UI")
            
            # Show job stats if available
            try:
                if hasattr(job_mgr, 'get_stats'):
                    stats = job_mgr.get_stats()
                    with st.expander("📊 Job Statistics"):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Jobs", stats.get('total', 0))
                        with col2:
                            st.metric("Running", stats.get('running', 0))
                        with col3:
                            st.metric("Completed", stats.get('completed', 0))
                        with col4:
                            st.metric("Failed", stats.get('failed', 0))
            except:
                pass
        else:
            st.warning("⚠️ Nicht initialisiert")
    else:
        st.info("ℹ️ Deaktiviert")
    
    # Phase 9: Migrations
    st.markdown("#### 🔄 Migration Manager")
    if is_feature_enabled('migrations'):
        mig_mgr = get_migration_manager()
        if mig_mgr:
            st.success("✅ Aktiv - Schema Migration System")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption("✅ Up/Down Migrations")
            with col2:
                st.caption("✅ Rollback Support")
            with col3:
                st.caption("✅ CLI Integration")
            
            # Show migration status if available
            try:
                if hasattr(mig_mgr, 'get_current_version'):
                    version = mig_mgr.get_current_version()
                    with st.expander("📊 Migration Status"):
                        st.write(f"**Current Version:** {version}")
            except:
                pass
        else:
            st.warning("⚠️ Nicht initialisiert")
    else:
        st.info("ℹ️ Deaktiviert")


def _render_phase_10_12():
    """Phase 10-12: Cache Extensions, DB Extensions, DI"""
    st.markdown("### 🚀 Phase 10-12: Advanced Extensions")
    
    # Phase 10: Cache Extensions
    st.markdown("#### 🚀 Cache Extensions")
    if is_feature_enabled('cache_ext'):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Cache Invalidator**")
            invalidator = get_cache_invalidator()
            if invalidator:
                st.success("✅ Aktiv")
                st.caption("Tag-basierte Invalidierung")
            else:
                st.warning("⚠️ Nicht verfügbar")
        
        with col2:
            st.markdown("**Cache Monitor**")
            monitor = get_cache_monitor()
            if monitor:
                st.success("✅ Aktiv")
                st.caption("Performance Tracking")
            else:
                st.warning("⚠️ Nicht verfügbar")
        
        with col3:
            st.markdown("**Cache Warmer**")
            warmer = get_cache_warmer()
            if warmer:
                st.success("✅ Aktiv")
                st.caption("Pre-Population")
            else:
                st.warning("⚠️ Nicht verfügbar")
    else:
        st.info("ℹ️ Deaktiviert")
    
    # Phase 11: DB Extensions
    st.markdown("#### 🗄️ Database Extensions")
    if is_feature_enabled('db_ext'):
        perf_mon = get_db_performance_monitor()
        if perf_mon:
            st.success("✅ DB Performance Monitor Aktiv")
            st.caption("- Query Performance Tracking")
            st.caption("- Slow Query Detection")
            st.caption("- Optimization Hints")
        else:
            st.warning("⚠️ Nicht initialisiert")
    else:
        st.info("ℹ️ Deaktiviert")
    
    # Phase 12: DI Container
    st.markdown("#### 🔧 Dependency Injection")
    if is_feature_enabled('di'):
        di_container = get_di_container()
        if di_container:
            st.success("✅ DI Container Aktiv")
            try:
                if hasattr(di_container, 'get_registered_services'):
                    services = di_container.get_registered_services()
                    with st.expander("📦 Registered Services"):
                        for service in services:
                            st.caption(f"- {service}")
            except:
                st.caption("Service Locator Pattern")
        else:
            st.warning("⚠️ Nicht initialisiert")
    else:
        st.info("ℹ️ Deaktiviert")


def _render_performance_metrics():
    """Performance Metrics Tab"""
    st.markdown("### 📊 Performance Metrics")
    
    # Overall system health
    st.markdown("#### 🏥 System Health")
    
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
                health_metrics['DB Health'] = "✅ Healthy" if health.healthy else "❌ Unhealthy"
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
    st.markdown("#### 📋 Feature Summary")
    
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
    tab1, tab2 = st.tabs(["🔧 Standard Dashboard", "📊 Extended Dashboard"])
    
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
