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
    
    col1, col2, col3 = st.columns(3)
    
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
       - `FEATURE_SESSION_PERSISTENCE=false` (Experimental)
       - `FEATURE_DATABASE_POOLING=false` (Experimental)
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
