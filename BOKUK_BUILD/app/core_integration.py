"""
Core Integration Module
=======================

Sichere Integration der core/ Module in die Hauptapp.
Alle Features sind optional und haben Fallbacks.
"""

import os
import sys
from pathlib import Path

# Feature Flags
FEATURES = {
    'config': os.getenv('FEATURE_CONFIG', 'true').lower() == 'true',
    'logging': os.getenv('FEATURE_LOGGING', 'true').lower() == 'true',
    'cache': os.getenv('FEATURE_CACHE', 'true').lower() == 'true',
    'session': os.getenv('FEATURE_SESSION_PERSISTENCE', 'true').lower() == 'true',
    'database': os.getenv('FEATURE_DATABASE_POOLING', 'true').lower() == 'true',
    # Phase 5-12: Advanced Features
    'security': os.getenv('FEATURE_SECURITY', 'true').lower() == 'true',
    'router': os.getenv('FEATURE_ROUTER', 'true').lower() == 'true',
    'forms': os.getenv('FEATURE_FORMS', 'true').lower() == 'true',
    'widgets': os.getenv('FEATURE_WIDGETS', 'true').lower() == 'true',
    'navigation': os.getenv('FEATURE_NAVIGATION_HISTORY', 'true').lower() == 'true',
    'jobs': os.getenv('FEATURE_JOBS', 'true').lower() == 'true',
    'migrations': os.getenv('FEATURE_MIGRATIONS', 'true').lower() == 'true',
    'cache_ext': os.getenv('FEATURE_CACHE_EXTENSIONS', 'true').lower() == 'true',
    'db_ext': os.getenv('FEATURE_DB_EXTENSIONS', 'true').lower() == 'true',
    'di': os.getenv('FEATURE_DI_CONTAINER', 'true').lower() == 'true',
}

# Global instances
_config = None
_logger = None
_cache = None
_session_manager = None
_database_manager = None
# Phase 5-12 instances
_security_manager = None
_router = None
_form_manager = None
_widget_manager = None
_navigation_history = None
_job_manager = None
_migration_manager = None
_cache_invalidator = None
_cache_monitor = None
_cache_warmer = None
_db_performance_monitor = None
_di_container = None


def init_core_integration(enable_logging=True):
    """
    Initialisiere core-Module basierend auf Feature Flags.
    
    Diese Funktion ist SAFE - wenn ein Modul fehlschlägt,
    wird es einfach deaktiviert ohne die App zu crashen.
    
    Args:
        enable_logging: Ob Logging aktiviert werden soll
    
    Returns:
        dict: Status der initialisierten Module
    """
    global _config, _logger, _cache, _session_manager
    
    status = {
        'config': False,
        'logging': False,
        'cache': False,
        'session': False,
        'database': False,
        'errors': []
    }
    
    # 1. CONFIG - Immer versuchen zu laden (Fundament)
    if FEATURES['config']:
        try:
            from core.config import get_config
            _config = get_config(reload_if_needed=False)
            status['config'] = True
            print("✅ Core Config initialized")
        except Exception as e:
            status['errors'].append(f"Config init failed: {e}")
            print(f"⚠️ Core Config disabled: {e}")
    
    # 2. LOGGING - Nur wenn Config erfolgreich
    if FEATURES['logging'] and enable_logging:
        try:
            from core.logging_config import init_logging_from_config
            
            if _config:
                init_logging_from_config(_config)
            else:
                # Fallback ohne config
                from core.logging_system import setup_structured_logging
                setup_structured_logging(
                    env='dev',
                    log_level='INFO',
                    log_dir=Path('./logs')
                )
            
            from core.logging_system import get_logger
            _logger = get_logger('bokuk2')
            _logger.info("core_integration_initialized", features=FEATURES)
            status['logging'] = True
            print("✅ Core Logging initialized")
        except Exception as e:
            status['errors'].append(f"Logging init failed: {e}")
            print(f"⚠️ Core Logging disabled: {e}")
    
    # 3. CACHE - Optional, nur wenn explizit aktiviert
    if FEATURES['cache']:
        try:
            from core.cache import get_cache
            _cache = get_cache()
            status['cache'] = True
            print("✅ Core Cache initialized")
            if _logger:
                _logger.info("cache_initialized")
        except Exception as e:
            status['errors'].append(f"Cache init failed: {e}")
            print(f"⚠️ Core Cache disabled: {e}")
    
    # 4. SESSION MANAGER - Optional, für Browser-Refresh-Recovery
    if FEATURES['session']:
        try:
            from core.session_manager import SessionManager
            _session_manager = SessionManager()
            status['session'] = True
            print("✅ Core Session Manager initialized")
            if _logger:
                _logger.info("session_manager_initialized")
        except Exception as e:
            status['errors'].append(f"Session Manager init failed: {e}")
            print(f"⚠️ Core Session Manager disabled: {e}")
    
    # 5. DATABASE POOLING - Optional, erweiterte DB-Features
    if FEATURES['database']:
        try:
            from core.database import DatabaseManager
            _database_manager = DatabaseManager(use_enhanced_connection_manager=True)
            status['database'] = True
            print("✅ Core Database Manager initialized (Pooling, Leak Detection, Health Monitoring)")
            if _logger:
                _logger.info("database_manager_initialized", 
                            pool_size=_database_manager._connection_pool_size,
                            enhanced=True)
        except Exception as e:
            status['errors'].append(f"Database Manager init failed: {e}")
            print(f"⚠️ Core Database Manager disabled: {e}")
    
    # Initialize advanced modules (Phase 5-12)
    _init_advanced_modules(status)
    
    return status


def _init_advanced_modules(status: dict):
    """Initialize Phase 5-12 advanced modules"""
    global _security_manager, _router, _form_manager, _widget_manager
    global _navigation_history, _job_manager, _migration_manager
    global _cache_invalidator, _cache_monitor, _cache_warmer
    global _db_performance_monitor, _di_container
    
    # PHASE 5: SECURITY & AUTHENTICATION
    if FEATURES['security']:
        try:
            from core.security import SecurityMonitor
            _security_manager = SecurityMonitor()
            status['security'] = True
            print("✅ Security Manager initialized (Auth, RBAC, Token Management)")
            if _logger:
                _logger.info("security_manager_initialized")
        except Exception as e:
            status['errors'].append(f"Security Manager init failed: {e}")
            print(f"⚠️ Security Manager disabled: {e}")
            status['security'] = False
    
    if FEATURES['router']:
        try:
            from core.router import Router
            _router = Router()
            status['router'] = True
            print("✅ Router initialized (Navigation, Guards, Middleware)")
            if _logger:
                _logger.info("router_initialized")
        except Exception as e:
            status['errors'].append(f"Router init failed: {e}")
            print(f"⚠️ Router disabled: {e}")
            status['router'] = False
    
    # PHASE 6: FORMS & WIDGETS
    if FEATURES['forms']:
        try:
            from core.form_manager import FormManager
            _form_manager = FormManager()
            status['forms'] = True
            print("✅ Form Manager initialized (Multi-Step Forms, Validation)")
            if _logger:
                _logger.info("form_manager_initialized")
        except Exception as e:
            status['errors'].append(f"Form Manager init failed: {e}")
            print(f"⚠️ Form Manager disabled: {e}")
            status['forms'] = False
    
    if FEATURES['widgets']:
        try:
            from core.widgets import WidgetRegistry
            _widget_manager = WidgetRegistry()
            status['widgets'] = True
            print("✅ Widget Manager initialized (Custom Widgets, Persistence)")
            if _logger:
                _logger.info("widget_manager_initialized")
        except Exception as e:
            status['errors'].append(f"Widget Manager init failed: {e}")
            print(f"⚠️ Widget Manager disabled: {e}")
            status['widgets'] = False
    
    # PHASE 7: NAVIGATION
    if FEATURES['navigation']:
        try:
            from core.navigation_history import NavigationHistory
            _navigation_history = NavigationHistory()
            status['navigation'] = True
            print("✅ Navigation History initialized (Tracking, Breadcrumbs)")
            if _logger:
                _logger.info("navigation_history_initialized")
        except Exception as e:
            status['errors'].append(f"Navigation History init failed: {e}")
            print(f"⚠️ Navigation History disabled: {e}")
            status['navigation'] = False
    
    # PHASE 8: JOBS & BACKGROUND TASKS
    if FEATURES['jobs']:
        try:
            from core.jobs import JobManager
            _job_manager = JobManager()
            status['jobs'] = True
            print("✅ Job Manager initialized (Background Tasks, Scheduling, Notifications)")
            if _logger:
                _logger.info("job_manager_initialized")
        except Exception as e:
            status['errors'].append(f"Job Manager init failed: {e}")
            print(f"⚠️ Job Manager disabled: {e}")
            status['jobs'] = False
    
    # PHASE 9: DATABASE MIGRATIONS
    if FEATURES['migrations']:
        try:
            from core.migration_manager import MigrationManager
            _migration_manager = MigrationManager()
            status['migrations'] = True
            print("✅ Migration Manager initialized (Schema Migrations, Rollback)")
            if _logger:
                _logger.info("migration_manager_initialized")
        except Exception as e:
            status['errors'].append(f"Migration Manager init failed: {e}")
            print(f"⚠️ Migration Manager disabled: {e}")
            status['migrations'] = False
    
    # PHASE 10: CACHE EXTENSIONS
    if FEATURES['cache_ext'] and _cache:
        try:
            from core.cache_invalidation import CacheDependencyTracker
            from core.cache_monitoring import CacheMonitor
            from core.cache_warming import CacheWarmingEngine  # ✅ Korrekter Name
            
            _cache_invalidator = CacheDependencyTracker(_cache)
            _cache_monitor = CacheMonitor(_cache)
            _cache_warmer = CacheWarmingEngine(_cache)  # ✅ Korrekter Name
            
            status['cache_extensions'] = True
            print("✅ Cache Extensions initialized (Invalidation, Monitoring, Warming)")
            if _logger:
                _logger.info("cache_extensions_initialized")
        except ImportError as e:
            status['errors'].append(f"Cache Extensions import failed: {e}")
            print(f"⚠️ Cache Extensions disabled (import error): {e}")
            status['cache_extensions'] = False
            _cache_invalidator = None
            _cache_monitor = None
            _cache_warmer = None
        except Exception as e:
            status['errors'].append(f"Cache Extensions init failed: {e}")
            print(f"⚠️ Cache Extensions disabled: {e}")
            status['cache_extensions'] = False
            _cache_invalidator = None
            _cache_monitor = None
            _cache_warmer = None
    
    # PHASE 11: DATABASE EXTENSIONS
    if FEATURES['db_ext'] and _database_manager:
        try:
            from core.db_performance_monitor import DBPerformanceMonitor
            _db_performance_monitor = DBPerformanceMonitor(_database_manager)
            status['db_extensions'] = True
            print("✅ DB Performance Monitor initialized (Query Tracking, Optimization)")
            if _logger:
                _logger.info("db_performance_monitor_initialized")
        except Exception as e:
            status['errors'].append(f"DB Performance Monitor init failed: {e}")
            print(f"⚠️ DB Performance Monitor disabled: {e}")
            status['db_extensions'] = False
    
    # PHASE 12: DEPENDENCY INJECTION (DISABLED - containers.py is for UI, not DI)
    # NOTE: containers.py is a UI module (StableContainer), not a DI container
    # To enable DI, create a separate core/di_container.py module
    status['di'] = False


def _register_di_services():
    """Register all services in DI container"""
    if not _di_container:
        return
    
    services = {
        'config': _config,
        'logger': _logger,
        'cache': _cache,
        'session_manager': _session_manager,
        'database_manager': _database_manager,
        'security_manager': _security_manager,
        'router': _router,
        'form_manager': _form_manager,
        'widget_manager': _widget_manager,
        'navigation_history': _navigation_history,
        'job_manager': _job_manager,
        'migration_manager': _migration_manager,
        'cache_invalidator': _cache_invalidator,
        'cache_monitor': _cache_monitor,
        'cache_warmer': _cache_warmer,
        'db_performance_monitor': _db_performance_monitor,
    }
    
    for name, service in services.items():
        if service is not None:
            _di_container.register(name, service)


def get_app_config():
    """
    Hole App-Konfiguration.
    
    Returns:
        AppConfig oder None wenn nicht verfügbar
    """
    return _config


def get_app_logger(name=None):
    """
    Hole Logger-Instanz.
    
    Args:
        name: Logger-Name (optional)
    
    Returns:
        Logger oder None wenn nicht verfügbar
    """
    if _logger and name:
        from core.logging_system import get_logger
        return get_logger(name)
    return _logger


def get_app_cache():
    """
    Hole Cache-Instanz.
    
    Returns:
        Cache oder None wenn nicht verfügbar
    """
    return _cache


def log_info(message, **kwargs):
    """
    Sicheres Logging - fällt zurück auf print wenn Logger nicht verfügbar.
    
    Args:
        message: Log-Nachricht
        **kwargs: Zusätzliche Context-Felder
    """
    if _logger:
        _logger.info(message, **kwargs)
    else:
        print(f"INFO: {message}", kwargs if kwargs else "")


def log_error(message, error=None, **kwargs):
    """
    Sicheres Error-Logging.
    
    Args:
        message: Fehler-Nachricht
        error: Exception (optional)
        **kwargs: Zusätzliche Context-Felder
    """
    if _logger:
        if error:
            _logger.error(message, error=str(error), **kwargs)
        else:
            _logger.error(message, **kwargs)
    else:
        print(f"ERROR: {message}", f"Error: {error}" if error else "", kwargs if kwargs else "")


def log_warning(message, **kwargs):
    """
    Sicheres Warning-Logging.
    
    Args:
        message: Warning-Nachricht
        **kwargs: Zusätzliche Context-Felder
    """
    if _logger:
        _logger.warning(message, **kwargs)
    else:
        print(f"WARNING: {message}", kwargs if kwargs else "")


def cache_get(key):
    """
    Sicherer Cache-Zugriff.
    
    Args:
        key: Cache-Key
    
    Returns:
        Cached value oder None
    """
    if _cache:
        try:
            return _cache.get(key)
        except Exception as e:
            log_error("cache_get_failed", error=e, key=key)
    return None


def cache_set(key, value, ttl=None, tags=None):
    """
    Sicheres Cache-Schreiben.
    
    Args:
        key: Cache-Key
        value: Wert zum Cachen
        ttl: Time-to-live in Sekunden
        tags: Tags für Invalidation
    
    Returns:
        bool: True wenn erfolgreich
    """
    if _cache:
        try:
            _cache.set(key, value, ttl=ttl, tags=tags or set())
            return True
        except Exception as e:
            log_error("cache_set_failed", error=e, key=key)
    return False


def is_feature_enabled(feature_name):
    """
    Prüfe ob Feature aktiviert ist.
    
    Args:
        feature_name: Name des Features
    
    Returns:
        bool: True wenn aktiviert
    """
    return FEATURES.get(feature_name, False)


# ============================================================================
# SESSION MANAGEMENT FUNCTIONS (Phase 3)
# ============================================================================

def get_session_manager():
    """
    Get the SessionManager instance.
    
    Returns:
        SessionManager or None
    """
    return _session_manager


def bootstrap_session(session_id=None, user_id=None):
    """
    Initialize or recover user session.
    
    This provides browser-refresh recovery and form state restoration.
    
    Args:
        session_id: Optional session ID to recover
        user_id: Optional user ID for new sessions
    
    Returns:
        UserSession or None
    """
    if _session_manager:
        try:
            session = _session_manager.bootstrap_session(
                session_id=session_id,
                user_id=user_id
            )
            log_info("session_bootstrapped", session_id=session.session_id)
            return session
        except Exception as e:
            log_error("session_bootstrap_failed", error=e)
    return None


def persist_session_input(key, value, form_id=None, immediate=False):
    """
    Persist input to session with automatic recovery.
    
    This ensures data isn't lost on browser refresh.
    
    Args:
        key: Widget key
        value: Widget value
        form_id: Optional form ID for grouping
        immediate: If True, write to DB immediately
    
    Returns:
        bool: True if successful
    """
    if _session_manager:
        try:
            _session_manager.persist_input(
                key=key,
                value=value,
                form_id=form_id,
                immediate=immediate
            )
            return True
        except Exception as e:
            log_error("session_persist_failed", error=e, key=key)
    return False


def get_current_session():
    """
    Get current user session.
    
    Returns:
        UserSession or None
    """
    if _session_manager:
        try:
            return _session_manager.get_current_session()
        except Exception as e:
            log_error("get_session_failed", error=e)
    return None


# ============================================================================
# DATABASE MANAGEMENT FUNCTIONS (Phase 4)
# ============================================================================

def get_database_manager():
    """
    Get the DatabaseManager instance with connection pooling.
    
    Returns:
        DatabaseManager or None
    """
    return _database_manager


def get_database_session():
    """
    Get a database session from the connection pool.
    
    This is a context manager that ensures connections are returned to pool.
    
    Usage:
        with get_database_session() as session:
            result = session.query(Model).all()
    
    Returns:
        Context manager or None
    """
    if _database_manager:
        try:
            return _database_manager.get_session()
        except Exception as e:
            log_error("get_db_session_failed", error=e)
    return None


def get_database_metrics():
    """
    Get database connection pool metrics.
    
    Returns:
        dict with pool metrics or None
    """
    if _database_manager and _database_manager.connection_manager:
        try:
            metrics = _database_manager.connection_manager.get_pool_metrics()
            return metrics.to_dict()
        except Exception as e:
            log_error("get_db_metrics_failed", error=e)
    return None


def run_database_health_check():
    """
    Run database health check.
    
    Returns:
        HealthCheckResult or None
    """
    if _database_manager and _database_manager.connection_manager:
        try:
            return _database_manager.connection_manager.health_check()
        except Exception as e:
            log_error("db_health_check_failed", error=e)
    return None


# ============================================================================
# PHASE 5-12: ADVANCED MODULE GETTERS
# ============================================================================

# PHASE 5: Security & Authentication
def get_security_manager():
    """Get SecurityManager instance"""
    return _security_manager


def authenticate_user(email, password):
    """Authenticate user credentials"""
    if _security_manager:
        try:
            return _security_manager.authenticate(email, password)
        except Exception as e:
            log_error("authentication_failed", error=e)
    return None


def check_permission(user_id, permission):
    """Check if user has permission"""
    if _security_manager:
        try:
            return _security_manager.check_permission(user_id, permission)
        except Exception as e:
            log_error("permission_check_failed", error=e)
    return False


def get_router():
    """Get Router instance"""
    return _router


def navigate_to(page, params=None):
    """Navigate to page with params"""
    if _router:
        try:
            return _router.navigate(page, params or {})
        except Exception as e:
            log_error("navigation_failed", error=e)
    return False


# PHASE 6: Forms & Widgets
def get_form_manager():
    """Get FormManager instance"""
    return _form_manager


def create_form(form_id, steps=None):
    """Create multi-step form"""
    if _form_manager:
        try:
            return _form_manager.create_form(form_id, steps or [])
        except Exception as e:
            log_error("form_creation_failed", error=e)
    return None


def get_widget_manager():
    """Get WidgetManager instance"""
    return _widget_manager


def render_widget(widget_type, **kwargs):
    """Render custom widget"""
    if _widget_manager:
        try:
            return _widget_manager.render(widget_type, **kwargs)
        except Exception as e:
            log_error("widget_render_failed", error=e)
    return None


# PHASE 7: Navigation
def get_navigation_history():
    """Get NavigationHistory instance"""
    return _navigation_history


def track_navigation(page, user_id=None):
    """Track user navigation"""
    if _navigation_history:
        try:
            _navigation_history.track(page, user_id)
        except Exception as e:
            log_error("navigation_tracking_failed", error=e)


# PHASE 8: Jobs & Background Tasks
def get_job_manager():
    """Get JobManager instance"""
    return _job_manager


def queue_job(job_type, data, priority=None):
    """Queue background job"""
    if _job_manager:
        try:
            return _job_manager.queue(job_type, data, priority)
        except Exception as e:
            log_error("job_queue_failed", error=e)
    return None


def get_job_status(job_id):
    """Get job status"""
    if _job_manager:
        try:
            return _job_manager.get_status(job_id)
        except Exception as e:
            log_error("job_status_failed", error=e)
    return None


# PHASE 9: Database Migrations
def get_migration_manager():
    """Get MigrationManager instance"""
    return _migration_manager


def run_migrations(target_version=None):
    """Run database migrations"""
    if _migration_manager:
        try:
            return _migration_manager.migrate(target_version)
        except Exception as e:
            log_error("migration_failed", error=e)
    return False


def rollback_migration(steps=1):
    """Rollback migrations"""
    if _migration_manager:
        try:
            return _migration_manager.rollback(steps)
        except Exception as e:
            log_error("migration_rollback_failed", error=e)
    return False


# PHASE 10: Cache Extensions
def get_cache_invalidator():
    """Get CacheInvalidator instance"""
    return _cache_invalidator


def invalidate_cache_by_tag(tag):
    """Invalidate cache entries by tag"""
    if _cache_invalidator:
        try:
            _cache_invalidator.invalidate_by_tag(tag)
        except Exception as e:
            log_error("cache_invalidation_failed", error=e)


def get_cache_monitor():
    """Get CacheMonitor instance"""
    return _cache_monitor


def get_cache_stats():
    """Get cache performance statistics"""
    if _cache_monitor:
        try:
            return _cache_monitor.get_stats()
        except Exception as e:
            log_error("cache_stats_failed", error=e)
    return None


def get_cache_warmer():
    """Get CacheWarmer instance"""
    return _cache_warmer


def warm_cache(keys=None):
    """Pre-populate cache"""
    if _cache_warmer:
        try:
            _cache_warmer.warm(keys)
        except Exception as e:
            log_error("cache_warming_failed", error=e)


# PHASE 11: Database Extensions
def get_db_performance_monitor():
    """Get DBPerformanceMonitor instance"""
    return _db_performance_monitor


def get_slow_queries():
    """Get slow query report"""
    if _db_performance_monitor:
        try:
            return _db_performance_monitor.get_slow_queries()
        except Exception as e:
            log_error("slow_query_report_failed", error=e)
    return []


# PHASE 12: Dependency Injection
def get_di_container():
    """Get DI Container instance"""
    return _di_container


def resolve_service(service_name):
    """Resolve service from DI container"""
    if _di_container:
        try:
            return _di_container.resolve(service_name)
        except Exception as e:
            log_error("service_resolution_failed", error=e)
    return None


# Convenience exports
__all__ = [
    'init_core_integration',
    'get_app_config',
    'get_app_logger',
    'get_app_cache',
    'log_info',
    'log_error',
    'log_warning',
    'cache_get',
    'cache_set',
    'is_feature_enabled',
    'FEATURES',
    # Phase 3 exports
    'get_session_manager',
    'bootstrap_session',
    'persist_session_input',
    'get_current_session',
    # Phase 4 exports
    'get_database_manager',
    'get_database_session',
    'get_database_metrics',
    'run_database_health_check',
    # Phase 5: Security
    'get_security_manager',
    'authenticate_user',
    'check_permission',
    'get_router',
    'navigate_to',
    # Phase 6: Forms & Widgets
    'get_form_manager',
    'create_form',
    'get_widget_manager',
    'render_widget',
    # Phase 7: Navigation
    'get_navigation_history',
    'track_navigation',
    # Phase 8: Jobs
    'get_job_manager',
    'queue_job',
    'get_job_status',
    # Phase 9: Migrations
    'get_migration_manager',
    'run_migrations',
    'rollback_migration',
    # Phase 10: Cache Extensions
    'get_cache_invalidator',
    'invalidate_cache_by_tag',
    'get_cache_monitor',
    'get_cache_stats',
    'get_cache_warmer',
    'warm_cache',
    # Phase 11: DB Extensions
    'get_db_performance_monitor',
    'get_slow_queries',
    # Phase 12: DI Container
    'get_di_container',
    'resolve_service',
]
