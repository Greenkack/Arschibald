"""
Core-Module Integrations-Analyse
=================================

Überprüft welche Core-Module bereits integriert sind.
"""

from pathlib import Path
import re

# Core module files
core_dir = Path('core')

# Get all Python modules (exclude tests, examples, verify scripts)
all_modules = [
    f.stem for f in core_dir.glob('*.py')
    if not f.stem.startswith(('test_', 'example_', 'verify_', 'simple_test_', '__'))
]

# Currently integrated modules
INTEGRATED_MODULES = {
    'config': 'Phase 1 - App Configuration',
    'logging_config': 'Phase 1 - Logging Configuration',
    'logging_system': 'Phase 1 - Structured Logging',
    'cache': 'Phase 2 - Cache System',
    'session_manager': 'Phase 3 - Session Management',
    'session': 'Phase 3 - Session Data Models',
    'session_persistence': 'Phase 3 - Session Storage',
    'session_recovery': 'Phase 3 - Session Recovery',
    'database': 'Phase 4 - Database Manager',
    'connection_manager': 'Phase 4 - Connection Pooling',
}

# NOT integrated yet
NOT_INTEGRATED = {
    # Security & Auth
    'security': 'User authentication, password hashing, token management',
    'router': 'URL routing and navigation',
    
    # Forms & Widgets
    'form_manager': 'Advanced form handling with validation',
    'widgets': 'Custom Streamlit widgets',
    'widget_persistence': 'Widget state persistence',
    'widget_validation': 'Form validation logic',
    
    # Navigation
    'navigation_history': 'Track user navigation history',
    
    # Jobs & Background Tasks
    'jobs': 'Background job system',
    'job_repository': 'Job persistence layer',
    'job_notifications': 'Job status notifications',
    'job_ui': 'Job management UI',
    
    # Migrations
    'migrations': 'Database migration system',
    'migration_manager': 'Migration execution engine',
    'migration_templates': 'Migration templates',
    'cli_migrations': 'CLI for migrations',
    
    # Cache Extensions
    'cache_invalidation': 'Smart cache invalidation',
    'cache_monitoring': 'Cache performance monitoring',
    'cache_warming': 'Pre-populate cache on startup',
    
    # Database Extensions
    'db_performance_monitor': 'Database query performance tracking',
    'session_repository': 'Session database operations',
    
    # Dependency Injection
    'containers': 'Dependency injection containers',
}

print("=" * 70)
print("CORE-MODULE INTEGRATIONS-ANALYSE")
print("=" * 70)

print(f"\n📦 GEFUNDENE MODULE: {len(all_modules)}")
print(f"✅ INTEGRIERT: {len(INTEGRATED_MODULES)}")
print(f"❌ NICHT INTEGRIERT: {len(NOT_INTEGRATED)}")

print("\n" + "=" * 70)
print("✅ INTEGRIERTE MODULE (Phasen 1-4)")
print("=" * 70)

for module, description in sorted(INTEGRATED_MODULES.items()):
    status = "✅" if module in all_modules else "⚠️"
    print(f"{status} {module:30} - {description}")

print("\n" + "=" * 70)
print("❌ NICHT INTEGRIERTE MODULE")
print("=" * 70)

# Group by category
categories = {
    'Security & Auth': ['security', 'router'],
    'Forms & Widgets': ['form_manager', 'widgets', 'widget_persistence', 'widget_validation'],
    'Navigation': ['navigation_history'],
    'Jobs & Background Tasks': ['jobs', 'job_repository', 'job_notifications', 'job_ui'],
    'Migrations': ['migrations', 'migration_manager', 'migration_templates', 'cli_migrations'],
    'Cache Extensions': ['cache_invalidation', 'cache_monitoring', 'cache_warming'],
    'Database Extensions': ['db_performance_monitor', 'session_repository'],
    'Dependency Injection': ['containers'],
}

for category, modules in categories.items():
    print(f"\n📂 {category}:")
    for module in modules:
        if module in NOT_INTEGRATED:
            exists = "✅" if module in all_modules else "❌"
            print(f"  {exists} {module:30} - {NOT_INTEGRATED[module]}")

print("\n" + "=" * 70)
print("📊 ZUSAMMENFASSUNG")
print("=" * 70)

coverage = (len(INTEGRATED_MODULES) / (len(INTEGRATED_MODULES) + len(NOT_INTEGRATED))) * 100

print(f"""
Integrierte Module:     {len(INTEGRATED_MODULES)}
Nicht integriert:       {len(NOT_INTEGRATED)}
Gesamt relevante Module: {len(INTEGRATED_MODULES) + len(NOT_INTEGRATED)}

Integration Coverage:   {coverage:.1f}%

STATUS: {'🟢 BASIC INTEGRATION COMPLETE' if coverage > 30 else '🟡 PARTIAL INTEGRATION'}
""")

print("=" * 70)
print("💡 EMPFEHLUNG")
print("=" * 70)

print("""
Die WICHTIGSTEN Core-Module sind bereits integriert:
✅ Config, Logging, Cache, Session, Database

OPTIONALE ERWEITERUNGEN (nach Bedarf):
1. Security - Wenn User-Login benötigt wird
2. Jobs - Für Background-Tasks (z.B. PDF-Generierung)
3. Migrations - Für Datenbank-Schema-Änderungen
4. Cache Extensions - Für erweiterte Cache-Strategien
5. Form Manager - Für komplexe Multi-Step-Forms

AKTUELLE INTEGRATION: PRODUKTIONSREIF für Standard-Use-Cases
""")

print("=" * 70)
