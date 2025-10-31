"""
Core Integration Status Dashboard
==================================

Zeigt Status und Performance-Metriken der core-Module an.
"""

import streamlit as st
from datetime import datetime
from pathlib import Path

try:
    from core_integration import (
        get_app_config,
        get_app_logger,
        get_app_cache,
        get_session_manager,
        get_current_session,
        get_database_manager,
        get_database_metrics,
        run_database_health_check,
        is_feature_enabled,
        FEATURES,
    )
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False


def render_core_status_dashboard():
    """Rendere Core-Integration Status Dashboard"""
    
    st.markdown("## 🔧 Core System Status")
    
    if not CORE_AVAILABLE:
        st.error("❌ Core-Integration nicht verfügbar")
        st.info("💡 Core-Module sind nicht installiert oder konnten nicht geladen werden.")
        return
    
    # Feature Status
    st.markdown("### 📊 Feature Status")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        config_enabled = is_feature_enabled('config')
        if config_enabled:
            st.success("✅ **Config**")
            config = get_app_config()
            if config:
                st.caption(f"Environment: `{config.env}`")
                st.caption(f"Mode: `{config.mode}`")
                st.caption(f"Debug: `{config.debug}`")
        else:
            st.warning("⚠️ **Config**")
            st.caption("Deaktiviert")
    
    with col2:
        logging_enabled = is_feature_enabled('logging')
        if logging_enabled:
            st.success("✅ **Logging**")
            logger = get_app_logger()
            if logger:
                st.caption("Strukturiertes Logging")
                st.caption("Mit Rotation & Metrics")
        else:
            st.warning("⚠️ **Logging**")
            st.caption("Deaktiviert")
    
    with col3:
        cache_enabled = is_feature_enabled('cache')
        if cache_enabled:
            st.success("✅ **Cache**")
            cache = get_app_cache()
            if cache:
                try:
                    stats = cache.get_stats()
                    st.caption(f"Hits: {stats.get('hits', 0)}")
                    st.caption(f"Misses: {stats.get('misses', 0)}")
                except:
                    st.caption("Cache aktiv")
        else:
            st.info("ℹ️ **Cache**")
            st.caption("Deaktiviert (optional)")
    
    with col4:
        session_enabled = is_feature_enabled('session')
        if session_enabled:
            st.success("✅ **Session**")
            session = get_current_session()
            if session:
                st.caption(f"ID: `{session.session_id[:8]}...`")
                st.caption(f"Forms: {len(session.form_states)}")
            else:
                st.caption("Kein aktive Session")
        else:
            st.info("ℹ️ **Session**")
            st.caption("Deaktiviert (optional)")
    
    with col5:
        database_enabled = is_feature_enabled('database')
        if database_enabled:
            st.success("✅ **Database**")
            db_manager = get_database_manager()
            if db_manager:
                try:
                    metrics = get_database_metrics()
                    if metrics:
                        st.caption(f"Pool: {metrics.get('checked_out', 0)}/{metrics.get('size', 0)}")
                        st.caption(f"Util: {metrics.get('utilization', '0%')}")
                        leaked = metrics.get('leaked_connections', 0)
                        if leaked > 0:
                            st.caption(f"⚠️ Leaks: {leaked}")
                    else:
                        st.caption("Pool aktiv")
                except:
                    st.caption("Pooling aktiv")
        else:
            st.info("ℹ️ **Database**")
            st.caption("Standard Mode (optional)")
    
    st.markdown("---")
    
    # Detailed Status
    if config_enabled:
        st.markdown("### ⚙️ Konfiguration Details")
        config = get_app_config()
        if config:
            config_col1, config_col2 = st.columns(2)
            
            with config_col1:
                st.markdown("**App-Einstellungen:**")
                st.code(f"""
App Name: {config.app_name}
Version: {config.app_version}
Environment: {config.env}
Mode: {config.mode}
Theme: {config.theme}
Compute: {config.compute}
                """, language="text")
            
            with config_col2:
                st.markdown("**Performance:**")
                st.code(f"""
Response Target: {config.performance.response_time_target_ms}ms
Cache Warming: {config.performance.cache_warming_enabled}
Lazy Loading: {config.performance.lazy_loading_enabled}
Max Memory: {config.performance.max_memory_mb}MB
                """, language="text")
    
    if cache_enabled:
        st.markdown("### 💾 Cache Performance")
        cache = get_app_cache()
        if cache:
            try:
                stats = cache.get_stats()
                
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    st.metric("Cache Hits", stats.get('hits', 0))
                
                with metric_col2:
                    st.metric("Cache Misses", stats.get('misses', 0))
                
                with metric_col3:
                    total_requests = stats.get('hits', 0) + stats.get('misses', 0)
                    hit_rate = (stats.get('hits', 0) / total_requests * 100) if total_requests > 0 else 0
                    st.metric("Hit Rate", f"{hit_rate:.1f}%")
                
                with metric_col4:
                    st.metric("Evictions", stats.get('evictions', 0))
                
                # Cache Efficiency
                if hit_rate > 0:
                    if hit_rate >= 80:
                        st.success(f"🎯 Excellent Cache Efficiency: {hit_rate:.1f}%")
                    elif hit_rate >= 50:
                        st.info(f"✅ Good Cache Efficiency: {hit_rate:.1f}%")
                    else:
                        st.warning(f"⚠️ Low Cache Efficiency: {hit_rate:.1f}%")
                
            except Exception as e:
                st.error(f"Cache Stats Error: {e}")
    
    if logging_enabled:
        st.markdown("### 📝 Logging Status")
        
        config = get_app_config()
        if config:
            log_dir = config.log_dir
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Log Konfiguration:**")
                st.code(f"""
Log Directory: {log_dir}
Environment: {config.env}
Debug Mode: {config.debug}
                """, language="text")
            
            with col2:
                st.markdown("**Log Dateien:**")
                if log_dir.exists():
                    log_files = list(log_dir.glob("*.log"))
                    if log_files:
                        for log_file in sorted(log_files)[-5:]:  # Last 5 files
                            size_mb = log_file.stat().st_size / 1024 / 1024
                            st.caption(f"📄 {log_file.name} ({size_mb:.2f} MB)")
                    else:
                        st.caption("Keine Log-Dateien gefunden")
                else:
                    st.caption("Log-Verzeichnis existiert noch nicht")
    
    # Database Pool Status (Phase 4)
    if is_feature_enabled('database'):
        st.markdown("### 🗄️ Database Pool Status")
        
        db_manager = get_database_manager()
        if db_manager:
            try:
                metrics = get_database_metrics()
                health = run_database_health_check()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Pool Metriken:**")
                    if metrics:
                        st.metric("Pool Size", f"{metrics.get('checked_out', 0)}/{metrics.get('size', 0)}")
                        st.metric("Total Checkouts", metrics.get('total_checkouts', 0))
                        st.metric("Overflow", metrics.get('overflow', 0))
                
                with col2:
                    st.markdown("**Performance:**")
                    if metrics:
                        st.metric("Utilization", metrics.get('utilization', '0%'))
                        st.metric("Avg Checkout Time", f"{metrics.get('avg_checkout_time', 0):.2f}s")
                        leaked = metrics.get('leaked_connections', 0)
                        if leaked > 0:
                            st.metric("⚠️ Leaked Connections", leaked, delta=-leaked, delta_color="inverse")
                        else:
                            st.metric("✅ Leaked Connections", 0)
                
                with col3:
                    st.markdown("**Health Check:**")
                    if health:
                        if health.healthy:
                            st.success(f"✅ Healthy ({health.response_time:.2f}ms)")
                        else:
                            st.error(f"❌ Unhealthy: {health.error}")
                        st.caption(f"Last Check: {health.timestamp.strftime('%H:%M:%S')}")
                    else:
                        st.info("Health check not available")
                
                # Detailed metrics
                if metrics:
                    st.markdown("**Detailed Metrics:**")
                    st.json(metrics)
                
            except Exception as e:
                st.error(f"Database Metrics Error: {e}")
    
    # Feature Activation Guide
    st.markdown("---")
    st.markdown("### 🚀 Feature Aktivierung")
    
    st.info("""
    **So aktivieren Sie Features:**
    
    1. Öffnen Sie die `.env` Datei im Hauptverzeichnis
    2. Ändern Sie die Feature-Flags:
       - `FEATURE_CONFIG=true` (Empfohlen)
       - `FEATURE_LOGGING=true` (Empfohlen)
       - `FEATURE_CACHE=true` (Optional, für Performance)
       - `FEATURE_SESSION_PERSISTENCE=true` (Phase 3 - Browser Refresh Recovery)
       - `FEATURE_DATABASE_POOLING=true` (Phase 4 - Connection Pooling & Leak Detection)
    3. Starten Sie die App neu
    
    **Empfohlene Einstellungen für Produktion:**
    - ENV=prod
    - DEBUG=false
    - FEATURE_CONFIG=true
    - FEATURE_LOGGING=true
    - FEATURE_CACHE=true
    """)
    
    # All Features Status Table
    st.markdown("### 📋 Alle Features")
    
    feature_data = []
    for feature_name, enabled in FEATURES.items():
        status = "✅ Aktiv" if enabled else "⚠️ Inaktiv"
        feature_data.append({
            "Feature": feature_name.title(),
            "Status": status,
            "ENV Variable": f"FEATURE_{feature_name.upper()}"
        })
    
    st.table(feature_data)


if __name__ == "__main__":
    st.set_page_config(page_title="Core Status", page_icon="🔧", layout="wide")
    render_core_status_dashboard()
